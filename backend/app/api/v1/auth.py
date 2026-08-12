from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_auth_service, get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    OAuthLoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResendOTPRequest,
    TokenResponse,
    UserResponse,
    VerifyOTPRequest,
)
from app.services.auth_service import AuthService

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def register(request: Request, payload: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Creates the account and emails a 6-digit OTP for verification."""
    user = auth_service.register(payload)
    return user


@router.post("/verify-otp", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def verify_otp(request: Request, payload: VerifyOTPRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Verifies the OTP and logs the user in immediately (issues tokens)."""
    user = auth_service.verify_otp(payload.email, payload.code)
    return auth_service._issue_tokens(user)  # noqa: SLF001 - internal reuse within same service


@router.post("/resend-otp", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def resend_otp(request: Request, payload: ResendOTPRequest, auth_service: AuthService = Depends(get_auth_service)):
    auth_service.resend_otp(payload.email)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def login(request: Request, payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.login(payload)


@router.post("/oauth", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def oauth_login(request: Request, payload: OAuthLoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """
    Frontend verifies the Google/GitHub id_token client-side (or via the
    provider's userinfo endpoint) and sends us the verified claims here.
    In production, re-verify the token signature server-side too (e.g. via
    google-auth's id_token.verify_oauth2_token) before trusting the claims -
    this endpoint assumes that verification happened upstream.
    """
    # NOTE: wire up real google-auth / GitHub OAuth app verification here.
    raise NotImplementedError(
        "Plug in google-auth (Google) / GitHub OAuth App token verification, "
        "then call auth_service.login_oauth(provider, email, full_name, oauth_id)."
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.refresh(payload.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
