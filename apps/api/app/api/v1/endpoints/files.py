import io
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.dependencies.auth import get_current_active_user
from app.models.brand import BrandMember
from app.models.theme import Theme
from app.models.user import User
from app.services.storage import get_storage_service

router = APIRouter(tags=["files"])


@router.get("/files/{path:path}")
def download_file(
    path: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Download a stored file by path with access checks."""
    path = path.lstrip("/")
    brand_id = None

    if path.startswith(("uploads/", "outputs/", "profiles/")):
        parts = path.split("/")
        if len(parts) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path",
            )
        brand_id = parts[1]
    elif path.startswith("themes/"):
        parts = path.split("/")
        if len(parts) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path",
            )
        theme_id = parts[1]
        theme = db.query(Theme).filter(Theme.id == theme_id).first()
        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Theme not found",
            )
        brand_id = theme.brand_id
    elif path.startswith("debug/"):
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access debug files",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if brand_id and not current_user.is_superuser:
        membership = (
            db.query(BrandMember)
            .filter(BrandMember.brand_id == brand_id, BrandMember.user_id == current_user.id)
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this file",
            )

    storage = get_storage_service()
    presigned_url = storage.get_download_url(path)
    if presigned_url:
        return RedirectResponse(url=presigned_url)

    content = storage.get_file(path)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    filename = os.path.basename(path) or "download"
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
