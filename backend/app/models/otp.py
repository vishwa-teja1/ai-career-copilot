import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from app.core.db_types import GUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OTPCode(Base):
    """
    Short-lived one-time codes used for email verification and login.
    Codes are stored hashed-equivalent (they're random digits, not secrets
    tied to the account password) but are single-use and time-boxed.
    """

    __tablename__ = "otp_codes"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), default="email_verification")  # email_verification | login
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="otp_codes")
