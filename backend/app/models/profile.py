import uuid
from datetime import datetime

from sqlalchemy import ARRAY, DateTime, ForeignKey, String, Text, func
from app.core.db_types import GUID, StringArray

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CandidateProfile(Base):
    """
    The single structured "Master Candidate Profile" derived from the
    uploaded resume. The original PDF/DOCX is stored once (see ResumeVersion)
    purely as an audit artifact - every downstream feature (matching,
    tailoring, cover letters) reads from THIS structured data, never the file.
    """

    __tablename__ = "candidate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )

    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    headline: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g. "Final-year IT student, ML focus"
    phone_encrypted: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    languages_spoken: Mapped[list[str] | None] = mapped_column(StringArray(), nullable=True)

    parsing_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | processing | completed | failed
    parsing_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="profile")
    resume_versions: Mapped[list["ResumeVersion"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", order_by="ResumeVersion.created_at.desc()"
    )
    skills: Mapped[list["ProfileSkill"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    experiences: Mapped[list["Experience"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", order_by="Experience.start_date.desc()"
    )
    education: Mapped[list["Education"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", order_by="Education.start_date.desc()"
    )
    projects: Mapped[list["ProfileProject"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    certifications: Mapped[list["Certification"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    achievements: Mapped[list["Achievement"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    internships: Mapped[list["Internship"]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class ResumeVersion(Base):
    """
    Audit record of every resume file ever uploaded. The MASTER version
    (is_master=True) is what parsing runs against. Tailored, job-specific
    resumes generated later (Module: Resume Tailoring) also live in this
    table with is_master=False and a foreign key to the target job.
    """

    __tablename__ = "resume_versions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id", ondelete="CASCADE"))

    is_master: Mapped[bool] = mapped_column(default=True)
    file_name: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(String(1000))  # local path or S3 key
    file_type: Mapped[str] = mapped_column(String(100))
    file_size_bytes: Mapped[int] = mapped_column()
    raw_text_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)  # extracted text, encrypted at rest

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    profile: Mapped["CandidateProfile"] = relationship(back_populates="resume_versions")


class ProfileSkill(Base):
    __tablename__ = "profile_skills"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # language | framework | tool | soft-skill
    proficiency: Mapped[str | None] = mapped_column(String(20), nullable=True)  # beginner | intermediate | advanced

    profile: Mapped["CandidateProfile"] = relationship(back_populates="skills")


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id", ondelete="CASCADE"))
    company: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)  # stored as "YYYY-MM" (resumes rarely give exact days)
    end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)  # null + is_current=True => "Present"
    is_current: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    bullet_points: Mapped[list[str] | None] = mapped_column(StringArray(), nullable=True)

    profile: Mapped["CandidateProfile"] = relationship(back_populates="experiences")


class Internship(Base):
    __tablename__ = "internships"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id", ondelete="CASCADE"))
    organization: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(255))
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    profile: Mapped["CandidateProfile"] = relationship(back_populates="internships")


class Education(Base):
    __tablename__ = "education"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id", ondelete="CASCADE"))
    institution: Mapped[str] = mapped_column(String(255))
    degree: Mapped[str] = mapped_column(String(255))
    field_of_study: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(50), nullable=True)  # GPA / percentage / CGPA as given on resume

    profile: Mapped["CandidateProfile"] = relationship(back_populates="education")


class ProfileProject(Base):
    __tablename__ = "profile_projects"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[list[str] | None] = mapped_column(StringArray(), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    profile: Mapped["CandidateProfile"] = relationship(back_populates="projects")


class Certification(Base):
    __tablename__ = "certifications"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    issuer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issue_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    profile: Mapped["CandidateProfile"] = relationship(back_populates="certifications")


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[str | None] = mapped_column(String(20), nullable=True)

    profile: Mapped["CandidateProfile"] = relationship(back_populates="achievements")
