import logging
import uuid

from fastapi import HTTPException, status
from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import AuthProvider, User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.email_service import send_otp_email

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # ------------------------------------------------------------------
    def register(self, payload: RegisterRequest) -> User:
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            # Deliberately vague message - don't leak which emails are registered.
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unable to register with these details.")

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            auth_provider=AuthProvider.EMAIL,
        )
        user = self.user_repo.create(user)

        otp = self.user_repo.create_otp(user.id, purpose="email_verification")
        send_otp_email(user.email, otp.code)

        return user

    # ------------------------------------------------------------------
    def verify_otp(self, email: str, code: str) -> User:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid verification request.")

        otp = self.user_repo.get_valid_otp(user.id, code, purpose="email_verification")
        if not otp:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired code.")

        self.user_repo.mark_otp_used(otp)
        self.user_repo.mark_email_verified(user)
        return user

    def resend_otp(self, email: str) -> None:
        user = self.user_repo.get_by_email(email)
        if not user:
            # Don't reveal whether the email exists.
            return
        if user.is_email_verified:
            return
        otp = self.user_repo.create_otp(user.id, purpose="email_verification")
        send_otp_email(user.email, otp.code)

    # ------------------------------------------------------------------
    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_email(payload.email)
        if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")

        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This account has been deactivated.")

        if not user.is_email_verified:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Please verify your email before logging in.")

        self.user_repo.update_last_login(user)
        return self._issue_tokens(user)

    # ------------------------------------------------------------------
    def login_oauth(self, provider: str, email: str, full_name: str, oauth_id: str) -> TokenResponse:
        """
        Called after the frontend has already validated the id_token with
        Google/GitHub's SDK and handed us the verified claims. Creates the
        account on first login (auto-verified, since the OAuth provider
        already confirmed the email).
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            user = User(
                email=email,
                full_name=full_name,
                hashed_password=None,
                auth_provider=AuthProvider(provider),
                oauth_id=oauth_id,
                is_email_verified=True,
            )
            user = self.user_repo.create(user)

        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This account has been deactivated.")

        self.user_repo.update_last_login(user)
        return self._issue_tokens(user)

    # ------------------------------------------------------------------
    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except JWTError as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token.") from exc

        if payload.get("type") != "refresh":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type.")

        try:
            user_id = uuid.UUID(payload["sub"])
        except (KeyError, ValueError) as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token subject.") from exc

        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User no longer active.")

        return self._issue_tokens(user)

    # ------------------------------------------------------------------
    def _issue_tokens(self, user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(str(user.id), user.role.value),
            refresh_token=create_refresh_token(str(user.id)),
        )
