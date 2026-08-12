import logging
import uuid

from fastapi import HTTPException, UploadFile, status

from app.ai.resume_parser import ResumeParsingError, parse_resume_text
from app.core.config import get_settings
from app.core.security import encrypt_field
from app.models.profile import CandidateProfile, ResumeVersion
from app.repositories.profile_repository import ProfileRepository
from app.utils.storage import get_storage_backend
from app.utils.text_extraction import CorruptFileError, EmptyResumeTextError, UnsupportedFileTypeError, extract_text

logger = logging.getLogger(__name__)
settings = get_settings()


class ResumeService:
    def __init__(self, profile_repo: ProfileRepository):
        self.profile_repo = profile_repo
        self.storage = get_storage_backend()

    async def upload_master_resume(self, user_id: uuid.UUID, file: UploadFile) -> tuple[ResumeVersion, CandidateProfile]:
        self._validate_file(file)
        file_bytes = await file.read()
        self._validate_size(len(file_bytes))

        profile = self.profile_repo.get_or_create(user_id)

        storage_path = self.storage.save(file_bytes, file.filename, prefix=f"resumes/{user_id}")

        try:
            raw_text = extract_text(file_bytes, file.content_type)
        except (UnsupportedFileTypeError, EmptyResumeTextError, CorruptFileError) as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc

        resume_version = ResumeVersion(
            profile_id=profile.id,
            is_master=True,
            file_name=file.filename,
            storage_path=storage_path,
            file_type=file.content_type,
            file_size_bytes=len(file_bytes),
            raw_text_encrypted=encrypt_field(raw_text),
        )
        resume_version = self.profile_repo.add_resume_version(resume_version)

        self.profile_repo.set_parsing_status(profile, "processing")

        try:
            parsed = parse_resume_text(raw_text)
        except ResumeParsingError as exc:
            logger.error("Resume parsing failed for user %s: %s", user_id, exc)
            self.profile_repo.set_parsing_status(profile, "failed", error=str(exc))
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                "We received your resume but AI parsing failed. You can retry, or fill in your profile manually.",
            ) from exc

        profile = self.profile_repo.replace_parsed_data(profile, parsed)

        return resume_version, profile

    # ------------------------------------------------------------------
    def _validate_file(self, file: UploadFile) -> None:
        if file.content_type not in settings.ALLOWED_RESUME_TYPES:
            raise HTTPException(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                "Only PDF and DOCX resumes are supported.",
            )

    def _validate_size(self, size_bytes: int) -> None:
        max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
        if size_bytes > max_bytes:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                f"Resume file exceeds the {settings.MAX_UPLOAD_MB}MB limit.",
            )
        if size_bytes == 0:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Uploaded file is empty.")
