import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.profile import (
    Achievement,
    CandidateProfile,
    Certification,
    Education,
    Experience,
    Internship,
    ProfileProject,
    ProfileSkill,
    ResumeVersion,
)


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> CandidateProfile | None:
        stmt = (
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .options(
                selectinload(CandidateProfile.skills),
                selectinload(CandidateProfile.experiences),
                selectinload(CandidateProfile.internships),
                selectinload(CandidateProfile.education),
                selectinload(CandidateProfile.projects),
                selectinload(CandidateProfile.certifications),
                selectinload(CandidateProfile.achievements),
                selectinload(CandidateProfile.resume_versions),
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_or_create(self, user_id: uuid.UUID) -> CandidateProfile:
        profile = self.get_by_user_id(user_id)
        if profile:
            return profile
        profile = CandidateProfile(user_id=user_id, parsing_status="pending")
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def add_resume_version(self, resume_version: ResumeVersion) -> ResumeVersion:
        self.db.add(resume_version)
        self.db.commit()
        self.db.refresh(resume_version)
        return resume_version

    def set_parsing_status(self, profile: CandidateProfile, status: str, error: str | None = None) -> None:
        profile.parsing_status = status
        profile.parsing_error = error
        self.db.commit()

    def replace_parsed_data(self, profile: CandidateProfile, parsed: dict) -> CandidateProfile:
        """
        Wipes and re-populates every child table from a fresh AI parse.
        Re-parsing (e.g. user re-uploads an updated master resume) is treated
        as a full replace rather than a diff/merge - simpler and matches the
        "one master resume, always current" model.
        """
        for collection in (
            profile.skills,
            profile.experiences,
            profile.internships,
            profile.education,
            profile.projects,
            profile.certifications,
            profile.achievements,
        ):
            for item in list(collection):
                self.db.delete(item)
        self.db.flush()

        profile.full_name = parsed.get("full_name")
        profile.headline = parsed.get("headline")
        profile.location = parsed.get("location")
        profile.summary = parsed.get("summary")
        profile.linkedin_url = parsed.get("linkedin_url")
        profile.github_url = parsed.get("github_url")
        profile.portfolio_url = parsed.get("portfolio_url")
        profile.languages_spoken = parsed.get("languages_spoken") or []

        profile.skills = [ProfileSkill(**s) for s in parsed.get("skills", [])]
        profile.experiences = [Experience(**e) for e in parsed.get("experiences", [])]
        profile.internships = [Internship(**i) for i in parsed.get("internships", [])]
        profile.education = [Education(**e) for e in parsed.get("education", [])]
        profile.projects = [
            ProfileProject(title=p["title"], description=p.get("description"), tech_stack=p.get("tech_stack") or [], url=p.get("url"))
            for p in parsed.get("projects", [])
        ]
        profile.certifications = [Certification(**c) for c in parsed.get("certifications", [])]
        profile.achievements = [Achievement(**a) for a in parsed.get("achievements", [])]

        profile.parsing_status = "completed"
        profile.parsing_error = None

        self.db.commit()
        self.db.refresh(profile)
        return profile
