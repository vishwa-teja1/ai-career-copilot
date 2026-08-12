"""
Repository pattern: all direct SQLAlchemy querying for User lives here.
Services depend on this interface, never on `Session` + raw queries directly,
so persistence details can change without touching business logic.
"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import generate_otp
from app.models.otp import OTPCode
from app.models.user import User

settings = get_settings()


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, user: User) -> User:
        user.email = user.email.lower()
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_login(self, user: User) -> None:
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()

    def mark_email_verified(self, user: User) -> None:
        user.is_email_verified = True
        self.db.commit()
        self.db.refresh(user)

    # --- OTP ---
    def create_otp(self, user_id: uuid.UUID, purpose: str = "email_verification") -> OTPCode:
        otp = OTPCode(
            user_id=user_id,
            code=generate_otp(),
            purpose=purpose,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        )
        self.db.add(otp)
        self.db.commit()
        self.db.refresh(otp)
        return otp

    def get_valid_otp(self, user_id: uuid.UUID, code: str, purpose: str = "email_verification") -> OTPCode | None:
        stmt = select(OTPCode).where(
            OTPCode.user_id == user_id,
            OTPCode.code == code,
            OTPCode.purpose == purpose,
            OTPCode.is_used.is_(False),
            OTPCode.expires_at > datetime.now(timezone.utc),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def mark_otp_used(self, otp: OTPCode) -> None:
        otp.is_used = True
        self.db.commit()
