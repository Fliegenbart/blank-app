import os
import io
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import get_settings
from app.api.v1.dependencies.auth import get_current_active_user
from app.api.v1.dependencies.rbac import require_brand_editor
from app.models.user import User
from app.models.brand import BrandMember
from app.models.upload import Upload
from app.schemas.upload import UploadResponse
from app.services.storage import get_storage_service
from app.services.audit import AuditService

settings = get_settings()
router = APIRouter(prefix="/brands/{brand_id}/uploads", tags=["uploads"])


def get_file_extension(filename: str) -> str:
    """Get the file extension."""
    return os.path.splitext(filename)[1].lower()


def validate_file(file: UploadFile) -> tuple[str, str]:
    """Validate the uploaded file and return (file_type, content_type)."""
    ext = get_file_extension(file.filename)
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    file_type_map = {
        ".pdf": ("pdf", "application/pdf"),
        ".pptx": ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
        ".ppt": ("ppt", "application/vnd.ms-powerpoint"),
    }

    return file_type_map.get(ext, ("unknown", "application/octet-stream"))


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    brand_id: str,
    file: UploadFile = File(...),
    membership: BrandMember = Depends(require_brand_editor),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upload a file for analysis."""
    # Validate file type
    file_type, content_type = validate_file(file)

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Check size limit
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Create upload record
    upload = Upload(
        brand_id=brand_id,
        uploaded_by=current_user.id,
        original_filename=file.filename,
        file_type=file_type,
        file_size=file_size,
        storage_path="",  # Will be set after storage
        status="uploading",
    )
    db.add(upload)
    db.flush()

    # Store file
    storage = get_storage_service()
    storage_path = storage.store_upload(
        brand_id=brand_id,
        upload_id=upload.id,
        filename=file.filename,
        data=io.BytesIO(content),
        content_type=content_type,
    )

    # Update upload record
    upload.storage_path = storage_path
    upload.status = "uploaded"
    db.commit()
    db.refresh(upload)

    # Audit log
    audit = AuditService(db)
    audit.log_upload_created(upload.id, file.filename, current_user.id, brand_id)

    return upload


@router.get("", response_model=List[UploadResponse])
def list_uploads(
    brand_id: str,
    membership: BrandMember = Depends(require_brand_editor),
    db: Session = Depends(get_db),
):
    """List uploads for a brand."""
    uploads = db.query(Upload).filter(Upload.brand_id == brand_id).order_by(Upload.created_at.desc()).all()
    return uploads


@router.get("/{upload_id}", response_model=UploadResponse)
def get_upload(
    brand_id: str,
    upload_id: str,
    membership: BrandMember = Depends(require_brand_editor),
    db: Session = Depends(get_db),
):
    """Get an upload by ID."""
    upload = db.query(Upload).filter(Upload.id == upload_id, Upload.brand_id == brand_id).first()
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )
    return upload


@router.delete("/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_upload(
    brand_id: str,
    upload_id: str,
    membership: BrandMember = Depends(require_brand_editor),
    db: Session = Depends(get_db),
):
    """Delete an upload."""
    upload = db.query(Upload).filter(Upload.id == upload_id, Upload.brand_id == brand_id).first()
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )

    # Delete from storage
    storage = get_storage_service()
    storage.delete_file(upload.storage_path)

    # Delete record
    db.delete(upload)
    db.commit()
