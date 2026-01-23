import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.dependencies.auth import get_current_active_user
from app.api.v1.dependencies.rbac import require_brand_editor, require_brand_access
from app.models.user import User
from app.models.brand import BrandMember
from app.models.job import Job, JobStatus, JobType
from app.models.upload import Upload
from app.schemas.job import JobResponse
from app.services.job_queue import get_job_queue
from app.services.audit import AuditService

router = APIRouter(tags=["jobs"])


@router.post("/brands/{brand_id}/analyze", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_analyze_job(
    brand_id: str,
    upload_id: str = Query(..., description="The upload ID to analyze"),
    membership: BrandMember = Depends(require_brand_editor),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create an analysis job for an upload."""
    # Verify upload exists and belongs to brand
    upload = db.query(Upload).filter(Upload.id == upload_id, Upload.brand_id == brand_id).first()
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )

    # Create job
    job = Job(
        brand_id=brand_id,
        created_by=current_user.id,
        job_type=JobType.ANALYZE.value,
        status=JobStatus.PENDING.value,
        upload_id=upload_id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue job
    job_queue = get_job_queue()
    rq_job_id = job_queue.enqueue_analyze(job.id)

    # Update job with RQ ID
    job.rq_job_id = rq_job_id
    job.status = JobStatus.QUEUED.value
    db.commit()

    # Audit log
    audit = AuditService(db)
    audit.log_job_created(job.id, job.job_type, current_user.id, brand_id)

    return _job_to_response(job)


@router.get("/brands/{brand_id}/jobs", response_model=List[JobResponse])
def list_jobs(
    brand_id: str,
    job_type: Optional[str] = None,
    status: Optional[str] = None,
    membership: BrandMember = Depends(require_brand_access),
    db: Session = Depends(get_db),
):
    """List jobs for a brand."""
    query = db.query(Job).filter(Job.brand_id == brand_id)

    if job_type:
        query = query.filter(Job.job_type == job_type)
    if status:
        query = query.filter(Job.status == status)

    jobs = query.order_by(Job.created_at.desc()).all()
    return [_job_to_response(j) for j in jobs]


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Check access (user must have access to the brand)
    if not current_user.is_superuser:
        membership = (
            db.query(BrandMember)
            .filter(BrandMember.brand_id == job.brand_id, BrandMember.user_id == current_user.id)
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this job",
            )

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
