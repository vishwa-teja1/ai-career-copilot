from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import get_current_user, get_resume_service
from app.models.user import User
from app.schemas.profile import ResumeUploadResponse
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_master_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
):
    """
    Uploads (or replaces) the user's ONE master resume. Runs extraction +
    AI parsing synchronously and returns once the structured profile is
    ready. For very high traffic, swap this for a background job (RabbitMQ
    consumer) that flips parsing_status via a webhook/poll - the service
    layer is already structured to make that swap a router-only change.
    """
    resume_version, profile = await resume_service.upload_master_resume(current_user.id, file)
    return ResumeUploadResponse(
        resume_version_id=resume_version.id,
        profile_id=profile.id,
        parsing_status=profile.parsing_status,
        message="Resume uploaded and profile built successfully."
        if profile.parsing_status == "completed"
        else "Resume uploaded; parsing did not complete.",
    )
