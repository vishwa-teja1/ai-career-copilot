from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_profile_repository
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import CandidateProfileOut, ProfileUpdateRequest

router = APIRouter(prefix="/profile", tags=["Candidate Profile"])


@router.get("/me", response_model=CandidateProfileOut)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
):
    profile = profile_repo.get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No profile yet - upload a resume first.")
    return profile


@router.patch("/me", response_model=CandidateProfileOut)
def update_my_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
):
    """Manual corrections on top of AI-parsed data - parsing is a starting
    point the user stays in control of, not a locked-in result."""
    profile = profile_repo.get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No profile yet - upload a resume first.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile_repo.db.commit()
    profile_repo.db.refresh(profile)
    return profile
