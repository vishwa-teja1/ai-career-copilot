"""
Application configuration, loaded from environment variables.
Uses pydantic-settings so every value is validated at startup instead
of failing deep inside a request handler.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "AI Career Copilot"
    ENVIRONMENT: str = "development"  # development | staging | production
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # --- Security ---
    SECRET_KEY: str  # required, no default -> app refuses to boot without it
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"
    OTP_EXPIRE_MINUTES: int = 10
    FIELD_ENCRYPTION_KEY: str  # required, 32-byte urlsafe base64 key for Fernet

    # --- CORS ---
    # NOTE: kept as a plain string, not List[str]. pydantic-settings attempts to
    # JSON-decode any List[...] field read from a .env value *before* running
    # field_validators, so "CORS_ORIGINS=http://localhost:3000" would crash the
    # app at startup with a SettingsError. Splitting manually via the property
    # below sidesteps that entirely.
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- Database ---
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/career_copilot"

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Rate limiting ---
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"

    # --- File uploads ---
    MAX_UPLOAD_MB: int = 5
    ALLOWED_RESUME_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    UPLOAD_DIR: str = "./storage/resumes"  # swapped for S3 client in production via STORAGE_BACKEND
    STORAGE_BACKEND: str = "local"  # local | s3

    # --- AWS S3 (used when STORAGE_BACKEND=s3) ---
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: Optional[str] = None

    # --- AI provider ---
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"  # override in .env to whatever model you're provisioned for

    # --- Email (OTP delivery) ---
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "no-reply@careercopilot.ai"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
