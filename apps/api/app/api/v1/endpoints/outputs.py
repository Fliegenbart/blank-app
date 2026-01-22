import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session
import io

from app.core.database import get_db
from app.api.v1.dependencies.auth import get_current_active_user
from app.api.v1.dependencies.rbac import require_brand_access
from app.models.user import User
from app.models.brand import BrandMember
from app.models.output import Output
from app.schemas.output import OutputResponse
from app.services.storage import get_storage_service

router = APIRouter(tags=["outputs"])


@router.get("/brands/{brand_id}/outputs", response_model=List[OutputResponse])
def list_outputs(
    brand_id: str,
    membership: BrandMember = Depends(require_brand_access),
    db: Session = Depends(get_db),
):
    """List all outputs for a brand."""
    outputs = db.query(Output).filter(Output.brand_id == brand_id).order_by(Output.created_at.desc()).all()
    return [_output_to_response(o) for o in outputs]


@router.get("/outputs/{output_id}", response_model=OutputResponse)
def get_output(
    output_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get an output by ID."""
    output = db.query(Output).filter(Output.id == output_id).first()
    if not output:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output not found",
        )

    # Check access
    if not current_user.is_superuser:
        membership = (
            db.query(BrandMember)
            .filter(BrandMember.brand_id == output.brand_id, BrandMember.user_id == current_user.id)
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this output",
            )

    return _output_to_response(output)


@router.get("/outputs/{output_id}/download")
def download_output(
    output_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Download an output file."""
    output = db.query(Output).filter(Output.id == output_id).first()
    if not output:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output not found",
        )

    # Check access
    if not current_user.is_superuser:
        membership = (
            db.query(BrandMember)
            .filter(BrandMember.brand_id == output.brand_id, BrandMember.user_id == current_user.id)
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this output",
            )

    storage = get_storage_service()

    # Try to get presigned URL first
    presigned_url = storage.get_download_url(output.storage_path)
    if presigned_url:
        return RedirectResponse(url=presigned_url)

    # Fallback to streaming the file
    file_content = storage.get_file(output.storage_path)
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output file not found in storage",
        )

    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=output.content_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{output.name}"',
        },
    )


def _output_to_response(output: Output) -> OutputResponse:
    """Convert an Output model to OutputResponse."""
    metadata = None
    if output.metadata_json:
        try:
            metadata = json.loads(output.metadata_json)
        except json.JSONDecodeError:
            pass

    # Get download URL
    storage = get_storage_service()
    download_url = storage.get_download_url(output.storage_path)

    return OutputResponse(
        id=output.id,
        brand_id=output.brand_id,
        output_type=output.output_type,
        name=output.name,
        description=output.description,
        file_size=output.file_size,
        content_type=output.content_type,
        created_at=output.created_at,
        download_url=download_url,
        metadata=metadata,
    )
