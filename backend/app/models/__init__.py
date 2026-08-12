"""
Import every model here so Alembic's autogenerate and Base.metadata.create_all
can discover them via a single `from app.models import *`-style import.
"""
from app.models.user import User, UserRole, AuthProvider  # noqa: F401
from app.models.otp import OTPCode  # noqa: F401
from app.models.profile import (  # noqa: F401
    CandidateProfile,
    ResumeVersion,
    ProfileSkill,
    Experience,
    Internship,
    Education,
    ProfileProject,
    Certification,
    Achievement,
)
