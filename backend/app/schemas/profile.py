import uuid
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# These mirror the ORM child tables and double as the JSON-schema contract
# the AI parser is instructed to fill in (see app/ai/resume_parser.py).
# ---------------------------------------------------------------------------
class SkillOut(BaseModel):
    id: uuid.UUID
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None

    model_config = {"from_attributes": True}


class ExperienceOut(BaseModel):
    id: uuid.UUID
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    bullet_points: Optional[list[str]] = None

    model_config = {"from_attributes": True}


class InternshipOut(BaseModel):
    id: uuid.UUID
    organization: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class EducationOut(BaseModel):
    id: uuid.UUID
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    tech_stack: Optional[list[str]] = None
    url: Optional[str] = None

    model_config = {"from_attributes": True}


class CertificationOut(BaseModel):
    id: uuid.UUID
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    credential_url: Optional[str] = None

    model_config = {"from_attributes": True}


class AchievementOut(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    date: Optional[str] = None

    model_config = {"from_attributes": True}


class CandidateProfileOut(BaseModel):
    id: uuid.UUID
    full_name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    languages_spoken: Optional[list[str]] = None
    parsing_status: str

    skills: list[SkillOut] = []
    experiences: list[ExperienceOut] = []
    internships: list[InternshipOut] = []
    education: list[EducationOut] = []
    projects: list[ProjectOut] = []
    certifications: list[CertificationOut] = []
    achievements: list[AchievementOut] = []

    model_config = {"from_attributes": True}


class ResumeUploadResponse(BaseModel):
    resume_version_id: uuid.UUID
    profile_id: uuid.UUID
    parsing_status: str
    message: str


class ProfileUpdateRequest(BaseModel):
    """Manual corrections the user makes after AI parsing - parsing is a
    starting point, not a source of truth the user is locked into."""

    full_name: Optional[str] = None
    headline: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = None
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
