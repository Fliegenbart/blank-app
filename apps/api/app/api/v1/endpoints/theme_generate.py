"""Theme asset generation API endpoints."""
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.dependencies.auth import get_current_active_user as get_current_user
from app.api.v1.dependencies.rbac import require_brand_access as get_brand_member
from app.models import (
    User, BrandMember, BrandRole, BrandProfile,
    Theme, ThemeStatus, ThemeAsset, ThemeJob,
    AssetType, AssetStatus, Job, JobType, JobStatus
)
from app.schemas.theme import (
    GenerateAllAssetsRequest, GenerateSingleAssetRequest, RegenerateAssetRequest,
    ThemeJobResponse, ThemeAssetResponse,
)
from app.services.job_queue import JobQueueService

router = APIRouter(prefix="/brands/{brand_id}/themes/{theme_id}/generate", tags=["theme-generate"])


@router.post("/all", response_model=ThemeJobResponse, status_code=status.HTTP_201_CREATED)
def generate_all_assets(
    brand_id: str,
    theme_id: str,
    request: GenerateAllAssetsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Generate all selected assets for a theme."""
    if member.role not in [BrandRole.OWNER, BrandRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and editors can generate assets"
        )

    theme = db.query(Theme).filter(
        Theme.id == theme_id,
        Theme.brand_id == brand_id
    ).first()

    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )

    # Validate asset types
    valid_types = [t.value for t in AssetType]
    for asset_type in request.asset_types:
        if asset_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid asset type: {asset_type}"
            )

    # Get or validate profile version
    profile_version = request.profile_version
    if profile_version:
        profile = db.query(BrandProfile).filter(
            BrandProfile.brand_id == brand_id,
            BrandProfile.version == profile_version
        ).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile version {profile_version} not found"
            )
    else:
        # Use latest profile
        profile = db.query(BrandProfile).filter(
            BrandProfile.brand_id == brand_id
        ).order_by(BrandProfile.version.desc()).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No brand profile found. Please analyze a brand document first."
            )
        profile_version = profile.version

    # Update theme status
    theme.status = ThemeStatus.GENERATING.value

    # Create ThemeJob for batch tracking
    theme_job = ThemeJob(
        theme_id=theme_id,
        created_by=current_user.id,
        status="pending",
        total_assets=len(request.asset_types),
        completed_assets=0,
        failed_assets=0,
    )
    db.add(theme_job)
    db.flush()

    # Create individual assets and jobs
    asset_job_ids = []
    for asset_type in request.asset_types:
        # Create ThemeAsset record
        asset = ThemeAsset(
            theme_id=theme_id,
            asset_type=asset_type,
            name=f"{theme.name} - {_asset_type_label(asset_type)}",
            status=AssetStatus.PENDING.value,
            generation_params_json=json.dumps({
                "profile_version": profile_version,
                "theme_job_id": theme_job.id,
            }),
        )
        db.add(asset)
        db.flush()

        # Create Job for this asset
        job_type = _get_job_type_for_asset(asset_type)
        job = Job(
            brand_id=brand_id,
            created_by=current_user.id,
            job_type=job_type.value,
            status=JobStatus.PENDING.value,
            profile_version=profile_version,
            params_json=json.dumps({
                "theme_id": theme_id,
                "theme_job_id": theme_job.id,
                "asset_id": asset.id,
                "asset_type": asset_type,
            }),
        )
        db.add(job)
        db.flush()

        # Link asset to job
        asset.job_id = job.id
        asset_job_ids.append(job.id)

    # Store job IDs in theme job
    theme_job.asset_job_ids = asset_job_ids
    theme_job.status = "queued"

    db.commit()
    db.refresh(theme_job)

    # Enqueue jobs
    job_queue = JobQueueService(db)
    for job_id in asset_job_ids:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job_type = JobType(job.job_type)
            # Enqueue based on job type
            if job_type == JobType.GENERATE_FLYER:
                job_queue.enqueue_job(job_id, "generate_flyer")
            elif job_type == JobType.GENERATE_BROCHURE:
                job_queue.enqueue_job(job_id, "generate_brochure")
            elif job_type == JobType.GENERATE_TEASER_SCRIPT:
                job_queue.enqueue_job(job_id, "generate_teaser_script")
            elif job_type == JobType.GENERATE_PRESENTATION:
                job_queue.enqueue_job(job_id, "generate_presentation")
            elif job_type == JobType.GENERATE_BANNER_ADS:
                job_queue.enqueue_job(job_id, "generate_banner_ads")
            elif job_type == JobType.GENERATE_LANDING_PAGE:
                job_queue.enqueue_job(job_id, "generate_landing_page")
            elif job_type == JobType.GENERATE_NEWSLETTER:
                job_queue.enqueue_job(job_id, "generate_newsletter")
            elif job_type == JobType.GENERATE_SOCIAL_MEDIA:
                job_queue.enqueue_job(job_id, "generate_social_media")
            elif job_type == JobType.GENERATE_WEBSITE:
                job_queue.enqueue_job(job_id, "generate_website")

    return _theme_job_to_response(theme_job)


@router.post("/{asset_type}", response_model=ThemeAssetResponse, status_code=status.HTTP_201_CREATED)
def generate_single_asset(
    brand_id: str,
    theme_id: str,
    asset_type: str,
    request: GenerateSingleAssetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Generate a single asset type for a theme."""
    if member.role not in [BrandRole.OWNER, BrandRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and editors can generate assets"
        )

    theme = db.query(Theme).filter(
        Theme.id == theme_id,
        Theme.brand_id == brand_id
    ).first()

    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )

    # Validate asset type
    valid_types = [t.value for t in AssetType]
    if asset_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid asset type: {asset_type}"
        )

    # Get or validate profile version
    profile_version = request.profile_version
    if not profile_version:
        profile = db.query(BrandProfile).filter(
            BrandProfile.brand_id == brand_id
        ).order_by(BrandProfile.version.desc()).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No brand profile found"
            )
        profile_version = profile.version

    # Create ThemeAsset record
    asset = ThemeAsset(
        theme_id=theme_id,
        asset_type=asset_type,
        name=f"{theme.name} - {_asset_type_label(asset_type)}",
        status=AssetStatus.PENDING.value,
        generation_params_json=json.dumps({
            "profile_version": profile_version,
            **(request.params or {}),
        }),
    )
    db.add(asset)
    db.flush()

    # Create Job
    job_type = _get_job_type_for_asset(asset_type)
    job = Job(
        brand_id=brand_id,
        created_by=current_user.id,
        job_type=job_type.value,
        status=JobStatus.PENDING.value,
        profile_version=profile_version,
        params_json=json.dumps({
            "theme_id": theme_id,
            "asset_id": asset.id,
            "asset_type": asset_type,
            **(request.params or {}),
        }),
    )
    db.add(job)
    db.flush()

    asset.job_id = job.id
    db.commit()
    db.refresh(asset)

    # Enqueue job
    job_queue = JobQueueService(db)
    job_queue.enqueue_job(job.id, _get_task_name_for_asset(asset_type))

    return _asset_to_response(asset)


@router.post("/regenerate/{asset_id}", response_model=ThemeAssetResponse)
def regenerate_asset(
    brand_id: str,
    theme_id: str,
    asset_id: str,
    request: RegenerateAssetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Regenerate a specific asset."""
    if member.role not in [BrandRole.OWNER, BrandRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and editors can regenerate assets"
        )

    asset = db.query(ThemeAsset).filter(
        ThemeAsset.id == asset_id,
        ThemeAsset.theme_id == theme_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    # Get profile version
    profile_version = request.profile_version
    if not profile_version:
        profile = db.query(BrandProfile).filter(
            BrandProfile.brand_id == brand_id
        ).order_by(BrandProfile.version.desc()).first()
        if profile:
            profile_version = profile.version

    # Reset asset status
    asset.status = AssetStatus.PENDING.value
    asset.error_message = None
    asset.generation_params_json = json.dumps({
        "profile_version": profile_version,
        **(request.params or {}),
    })

    # Create new Job
    job_type = _get_job_type_for_asset(asset.asset_type)
    job = Job(
        brand_id=brand_id,
        created_by=current_user.id,
        job_type=job_type.value,
        status=JobStatus.PENDING.value,
        profile_version=profile_version,
        params_json=json.dumps({
            "theme_id": theme_id,
            "asset_id": asset.id,
            "asset_type": asset.asset_type,
            **(request.params or {}),
        }),
    )
    db.add(job)
    db.flush()

    asset.job_id = job.id
    db.commit()
    db.refresh(asset)

    # Enqueue job
    job_queue = JobQueueService(db)
    job_queue.enqueue_job(job.id, _get_task_name_for_asset(asset.asset_type))

    return _asset_to_response(asset)


# === Helper Functions ===

def _asset_type_label(asset_type: str) -> str:
    """Get human-readable label for asset type."""
    labels = {
        "website": "Website",
        "landing_page": "Landing Page",
        "newsletter": "Newsletter",
        "flyer": "Flyer",
        "brochure": "Brochure",
        "teaser_script": "Teaser Script",
        "social_media": "Social Media Kit",
        "presentation": "Presentation",
        "banner_ads": "Banner Ads",
    }
    return labels.get(asset_type, asset_type.replace("_", " ").title())


def _get_job_type_for_asset(asset_type: str) -> JobType:
    """Map asset type to job type."""
    mapping = {
        "website": JobType.GENERATE_WEBSITE,
        "landing_page": JobType.GENERATE_LANDING_PAGE,
        "newsletter": JobType.GENERATE_NEWSLETTER,
        "flyer": JobType.GENERATE_FLYER,
        "brochure": JobType.GENERATE_BROCHURE,
        "teaser_script": JobType.GENERATE_TEASER_SCRIPT,
        "social_media": JobType.GENERATE_SOCIAL_MEDIA,
        "presentation": JobType.GENERATE_PRESENTATION,
        "banner_ads": JobType.GENERATE_BANNER_ADS,
    }
    return mapping.get(asset_type, JobType.GENERATE_WEBSITE)


def _get_task_name_for_asset(asset_type: str) -> str:
    """Map asset type to worker task name."""
    mapping = {
        "website": "generate_website",
        "landing_page": "generate_landing_page",
        "newsletter": "generate_newsletter",
        "flyer": "generate_flyer",
        "brochure": "generate_brochure",
        "teaser_script": "generate_teaser_script",
        "social_media": "generate_social_media",
        "presentation": "generate_presentation",
        "banner_ads": "generate_banner_ads",
    }
    return mapping.get(asset_type, "generate_website")


def _asset_to_response(asset: ThemeAsset) -> ThemeAssetResponse:
    """Convert asset model to response schema."""
    return ThemeAssetResponse(
        id=asset.id,
        theme_id=asset.theme_id,
        job_id=asset.job_id,
        asset_type=asset.asset_type,
        name=asset.name,
        status=asset.status,
        storage_path=asset.storage_path,
        preview_path=asset.preview_path,
        file_size=asset.file_size,
        content_type=asset.content_type,
        print_pdf_path=asset.print_pdf_path,
        figma_file_key=asset.figma_file_key,
        variants=asset.variants,
        metadata=asset.metadata,
        error_message=asset.error_message,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


def _theme_job_to_response(job: ThemeJob) -> ThemeJobResponse:
    """Convert theme job model to response schema."""
    return ThemeJobResponse(
        id=job.id,
        theme_id=job.theme_id,
        created_by=job.created_by,
        status=job.status,
        total_assets=job.total_assets,
        completed_assets=job.completed_assets,
        failed_assets=job.failed_assets,
        progress=job.progress,
        asset_job_ids=job.asset_job_ids,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
