import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.dependencies.auth import get_current_active_user
from app.api.v1.dependencies.rbac import require_brand_editor
from app.models.user import User
from app.models.brand import BrandMember
from app.models.brand_profile import BrandProfile
from app.models.job import Job, JobStatus, JobType
from app.schemas.job import JobResponse
from app.schemas.generator import WebsiteGenerateRequest, NewsletterGenerateRequest
from app.services.job_queue import get_job_queue
from app.services.audit import AuditService

router = APIRouter(prefix="/brands/{brand_id}/generate", tags=["generate"])


def _get_profile_version(brand_id: str, requested_version: int | None, db: Session) -> int:
    """Get the profile version to use for generation."""
    if requested_version:
        profile = (
            db.query(BrandProfile)
            .filter(BrandProfile.brand_id == brand_id, BrandProfile.version == requested_version)
            .first()
        )
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile version {requested_version} not found",
            )
        return requested_version

    # Get latest version
    latest = (
        db.query(BrandProfile)
        .filter(BrandProfile.brand_id == brand_id)
        .order_by(BrandProfile.version.desc())
        .first()
    )
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No brand profile found. Please analyze a document first.",
        )
    return latest.version


@router.post("/website", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def generate_website(
    brand_id: str,
    request: WebsiteGenerateRequest,
    membership: BrandMember = Depends(require_brand_editor),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Generate a website based on the brand profile."""
    profile_version = _get_profile_version(brand_id, request.profile_version, db)

    # Create job
    job = Job(
        brand_id=brand_id,
        created_by=current_user.id,
        job_type=JobType.GENERATE_WEBSITE.value,
        status=JobStatus.PENDING.value,
        profile_version=profile_version,
        params_json=json.dumps({
            "topic": request.topic,
            "pages": [p.model_dump() for p in request.pages],
            "brief": request.brief,
        }),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue job
    job_queue = get_job_queue()
    rq_job_id = job_queue.enqueue_generate_website(job.id)

    # Update job with RQ ID
    job.rq_job_id = rq_job_id
    job.status = JobStatus.QUEUED.value
    db.commit()

    # Audit log
    audit = AuditService(db)
    audit.log_job_created(job.id, job.job_type, current_user.id, brand_id)

    return _job_to_response(job)


@router.post("/newsletter", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def generate_newsletter(
    brand_id: str,
    request: NewsletterGenerateRequest,
    membership: BrandMember = Depends(require_brand_editor),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Generate a newsletter based on the brand profile."""
    profile_version = _get_profile_version(brand_id, request.profile_version, db)

    # Create job
    job = Job(
        brand_id=brand_id,
        created_by=current_user.id,
        job_type=JobType.GENERATE_NEWSLETTER.value,
        status=JobStatus.PENDING.value,
        profile_version=profile_version,
        params_json=json.dumps({
            "topic": request.topic,
            "offer": request.offer,
            "cta": request.cta,
            "subject_line": request.subject_line,
            "preview_text": request.preview_text,
        }),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue job
    job_queue = get_job_queue()
    rq_job_id = job_queue.enqueue_generate_newsletter(job.id)

    # Update job with RQ ID
    job.rq_job_id = rq_job_id
    job.status = JobStatus.QUEUED.value
    db.commit()

    # Audit log
    audit = AuditService(db)
    audit.log_job_created(job.id, job.job_type, current_user.id, brand_id)

    return _job_to_response(job)


def _job_to_response(job: Job) -> JobResponse:
    """Convert a Job model to JobResponse."""
    result = None
    if job.result_json:
        try:
            result = json.loads(job.result_json)
        except json.JSONDecodeError:
            pass

    return JobResponse(
        id=job.id,
        brand_id=job.brand_id,
        job_type=job.job_type,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at,
        updated_at=job.updated_at,
        error_message=job.error_message,
        logs=job.logs,
        output_id=job.output_id,
        result=result,
    )
