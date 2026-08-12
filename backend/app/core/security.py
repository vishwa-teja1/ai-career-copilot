"""
Security primitives: password hashing, JWT issuing/verification,
symmetric encryption for sensitive resume fields, and OTP generation.

Keeping all of this in one module means every other file imports
*behavior* ("hash_password", "create_access_token") rather than reaching
for jose/passlib/cryptography directly - so if we ever rotate algorithms
there is exactly one place to change.
"""
import random
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import bcrypt
from cryptography.fernet import Fernet
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

_fernet = Fernet(settings.FIELD_ENCRYPTION_KEY.encode())


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------
# Using the `bcrypt` library directly rather than passlib's CryptContext:
# passlib 1.7.x's bcrypt backend-detection code is incompatible with
# bcrypt>=4.1 (a long-standing unresolved upstream issue), so we talk to
# bcrypt directly to avoid pulling in that broken compatibility shim.
_BCRYPT_MAX_BYTES = 72  # bcrypt silently ignores bytes beyond this - reject instead of truncating


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > _BCRYPT_MAX_BYTES:
        raise ValueError("Password is too long.")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
def _create_token(subject: str, expires_delta: timedelta, token_type: Literal["access", "refresh"], extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": secrets.token_hex(16),  # unique id, enables future revocation/blacklist lookups
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str, role: str) -> str:
    return _create_token(
        subject=user_id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
        extra={"role": role},
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        subject=user_id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


def decode_token(token: str) -> dict:
    """Raises jose.JWTError on invalid/expired token - caller maps to HTTP 401."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


# ---------------------------------------------------------------------------
# Field-level encryption (used for storing raw parsed resume text, phone, etc.)
# ---------------------------------------------------------------------------
def encrypt_field(value: str) -> str:
    return _fernet.encrypt(value.encode()).decode()


def decrypt_field(token: str) -> str:
    return _fernet.decrypt(token.encode()).decode()


# ---------------------------------------------------------------------------
# OTP
# ---------------------------------------------------------------------------
def generate_otp(length: int = 6) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))
