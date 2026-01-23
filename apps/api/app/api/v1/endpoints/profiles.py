import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.dependencies.rbac import require_brand_access
from app.models.brand import BrandMember
from app.models.brand_profile import BrandProfile
from app.schemas.brand_profile import BrandProfileResponse, BrandProfileSchema

router = APIRouter(prefix="/brands/{brand_id}/profiles", tags=["profiles"])


@router.get("", response_model=List[BrandProfileResponse])
def list_profiles(
    brand_id: str,
    membership: BrandMember = Depends(require_brand_access),
    db: Session = Depends(get_db),
):
    """List all profile versions for a brand."""
    profiles = (
        db.query(BrandProfile)
        .filter(BrandProfile.brand_id == brand_id)
        .order_by(BrandProfile.version.desc())
        .all()
    )
    return [_profile_to_response(p) for p in profiles]


@router.get("/latest", response_model=BrandProfileResponse)
def get_latest_profile(
    brand_id: str,
    membership: BrandMember = Depends(require_brand_access),
    db: Session = Depends(get_db),
):
    """Get the latest profile version for a brand."""
    profile = (
        db.query(BrandProfile)
        .filter(BrandProfile.brand_id == brand_id)
        .order_by(BrandProfile.version.desc())
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profiles found for this brand",
        )
    return _profile_to_response(profile)


@router.get("/{version}", response_model=BrandProfileResponse)
def get_profile(
    brand_id: str,
    version: int,
    membership: BrandMember = Depends(require_brand_access),
    db: Session = Depends(get_db),
):
    """Get a specific profile version."""
    profile = (
        db.query(BrandProfile)
        .filter(BrandProfile.brand_id == brand_id, BrandProfile.version == version)
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile version {version} not found",
        )
    return _profile_to_response(profile)


def _profile_to_response(profile: BrandProfile) -> BrandProfileResponse:
    """Convert a BrandProfile model to BrandProfileResponse."""
    profile_data = json.loads(profile.profile_json)
    return BrandProfileResponse(
        id=profile.id,
        brand_id=profile.brand_id,
        version=profile.version,
        profile=BrandProfileSchema(**profile_data),
        summary_md=profile.summary_md,
        source_upload_id=profile.source_upload_id,
        created_at=profile.created_at,
    )
