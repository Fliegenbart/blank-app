import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.dependencies.auth import get_current_active_user
from app.api.v1.dependencies.rbac import require_brand_editor
from app.models.user import User
from app.models.brand import BrandMember
from app.models.reference import Reference, ReferenceStatus
from app.models.job import Job, JobStatus, JobType
from app.schemas.reference import (
    ReferenceCreate,
    ReferenceUpdate,
    ReferenceResponse,
    ReferenceDetailResponse,
)
from app.schemas.job import JobResponse
from app.services.job_queue import get_job_queue
from app.services.audit import AuditService

router = APIRouter(prefix="/brands/{brand_id}/references", tags=["references"])


def _reference_to_response(ref: Reference) -> ReferenceResponse:
    """Convert Reference model to ReferenceResponse."""
    urls = []
    if ref.urls_json:
        try:
            urls = json.loads(ref.urls_json)
        except json.JSONDecodeError:
            pass

    return ReferenceResponse(
        id=ref.id,
        brand_id=ref.brand_id,
        name=ref.name,
        description=ref.description,
        urls=urls,
        status=ref.status,
        error_message=ref.error_message,
        page_count=ref.page_count,
        total_word_count=ref.total_word_count,
        created_at=ref.created_at,
        updated_at=ref.updated_at,
    )


def _reference_to_detail_response(ref: Reference) -> ReferenceDetailResponse:
    """Convert Reference model to ReferenceDetailResponse with full data."""
    urls = []
    if ref.urls_json:
        try:
            urls = json.loads(ref.urls_json)
        except json.JSONDecodeError:
            pass

    structure = None
    if ref.structure_json:
        try:
            structure = json.loads(ref.structure_json)
        except json.JSONDecodeError:
            pass

    scraped_data = None
    if ref.scraped_data_json:
        try:
            scraped_data = json.loads(ref.scraped_data_json)
        except json.JSONDecodeError:
            pass

    return ReferenceDetailResponse(
        id=ref.id,
        brand_id=ref.brand_id,
        name=ref.name,
        description=ref.description,
        urls=urls,
        status=ref.status,
        error_message=ref.error_message,
        page_count=ref.page_count,
        total_word_count=ref.total_word_count,
        created_at=ref.created_at,
        updated_at=ref.updated_at,
        structure=structure,
        scraped_data=scraped_data,
    )


@router.post("", response_model=ReferenceResponse, status_code=status.HTTP_201_CREATED)
def create_reference(
    brand_id: str,
    request: ReferenceCreate,
    membership: BrandMember = Depends(require_brand_editor),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new reference and start scraping."""
    # Validate URLs
    if not request.urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one URL is required",
        )

    if len(request.urls) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 URLs allowed per reference",
        )

    # Create reference
    reference = Reference(
        brand_id=brand_id,
        created_by=current_user.id,
        name=request.name,
        description=request.description,
        urls_json=json.dumps(request.urls),
        status=ReferenceStatus.PENDING.value,
    )
    db.add(reference)
    db.commit()
    db.refresh(reference)

    # Create scraping job
    job = Job(
        brand_id=brand_id,
        created_by=current_user.id,
        job_type=JobType.SCRAPE_REFERENCE.value,
        status=JobStatus.PENDING.value,
        params_json=json.dumps({
            "reference_id": reference.id,
            "urls": request.urls,
        }),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue job
    job_queue = get_job_queue()
    rq_job_id = job_queue.enqueue_scrape_reference(job.id)

    job.rq_job_id = rq_job_id
    job.status = JobStatus.QUEUED.value
    db.commit()

    # Audit log
    audit = AuditService(db)
    audit.log_action(
        action="reference_created",
        resource_type="reference",
        resource_id=reference.id,
        user_id=current_user.id,
        brand_id=brand_id,
        details={"name": reference.name, "url_count": len(request.urls)},
    )

    return _reference_to_response(reference)


@router.get("", response_model=List[ReferenceResponse])
def list_references(
    brand_id: str,
    membership: BrandMember = Depends(require_brand_editor),
    db: Session = Depends(get_db),
):
    """List all references for a brand."""
    references = (
        db.query(Reference)
        .filter(Reference.brand_id == brand_id)
        .order_by(Reference.created_at.desc())
        .all()
    )
    return [_reference_to_response(r) for r in references]


@router.get("/{reference_id}", response_model=ReferenceDetailResponse)
def get_reference(
    brand_id: str,
    reference_id: str,
    membership: BrandMember = Depends(require_brand_editor),
    db: Session = Depends(get_db),
):
    """Get a reference by ID with full details."""
    reference = (
        db.query(Reference)
        .filter(Reference.id == reference_id, Reference.brand_id == brand_id)
        .first()
    )
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found",
        )
    return _reference_to_detail_response(reference)


@router.patch("/{reference_id}", response_model=ReferenceResponse)
def update_reference(
    brand_id: str,
    reference_id: str,
    request: ReferenceUpdate,
    membership: BrandMember = Depends(require_brand_editor),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a reference."""
    reference = (
        db.query(Reference)
        .filter(Reference.id == reference_id, Reference.brand_id == brand_id)
        .first()
    )
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found",
        )

    if request.name is not None:
        reference.name = request.name
    if request.description is not None:
        reference.description = request.description

    db.commit()
    db.refresh(reference)

    return _reference_to_response(reference)


@router.delete("/{reference_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reference(
    brand_id: str,
    reference_id: str,
    membership: BrandMember = Depends(require_brand_editor),
    db: Session = Depends(get_db),
):
    """Delete a reference."""
    reference = (
        db.query(Reference)
        .filter(Reference.id == reference_id, Reference.brand_id == brand_id)
        .first()
    )
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found",
        )

    db.delete(reference)
    db.commit()


@router.post("/{reference_id}/rescrape", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def rescrape_reference(
    brand_id: str,
    reference_id: str,
    membership: BrandMember = Depends(require_brand_editor),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Re-scrape an existing reference."""
    reference = (
        db.query(Reference)
        .filter(Reference.id == reference_id, Reference.brand_id == brand_id)
        .first()
    )
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found",
        )

    urls = []
    if reference.urls_json:
        urls = json.loads(reference.urls_json)

    # Reset reference status
    reference.status = ReferenceStatus.PENDING.value
    reference.error_message = None

    # Create scraping job
    job = Job(
        brand_id=brand_id,
        created_by=current_user.id,
        job_type=JobType.SCRAPE_REFERENCE.value,
        status=JobStatus.PENDING.value,
        params_json=json.dumps({
            "reference_id": reference.id,
            "urls": urls,
        }),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue job
    job_queue = get_job_queue()
    rq_job_id = job_queue.enqueue_scrape_reference(job.id)

    job.rq_job_id = rq_job_id
    job.status = JobStatus.QUEUED.value
    db.commit()

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
