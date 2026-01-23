"""Theme asset export API endpoints."""
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_brand_member
from app.models import (
    User, BrandMember, BrandRole,
    Theme, ThemeAsset, AssetStatus, Job, JobType, JobStatus
)
from app.schemas.theme import (
    ExportPrintRequest, ExportFigmaRequest, BatchExportRequest,
    ThemeAssetResponse,
)
from app.services.storage import get_storage_service
from app.services.job_queue import JobQueueService

router = APIRouter(prefix="/brands/{brand_id}/themes/{theme_id}/export", tags=["theme-export"])


@router.post("/print/{asset_id}", response_model=ThemeAssetResponse)
def export_print_pdf(
    brand_id: str,
    theme_id: str,
    asset_id: str,
    request: ExportPrintRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Export asset as print-ready PDF with bleed and crop marks."""
    if member.role not in [BrandRole.OWNER, BrandRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and editors can export assets"
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

    if asset.status != AssetStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset must be completed before exporting"
        )

    # Check if asset type supports print export
    printable_types = ["flyer", "brochure", "newsletter"]
    if asset.asset_type not in printable_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Asset type '{asset.asset_type}' does not support print export"
        )

    # Create export job
    job = Job(
        brand_id=brand_id,
        created_by=current_user.id,
        job_type=JobType.EXPORT_PRINT_PDF.value,
        status=JobStatus.PENDING.value,
        params_json=json.dumps({
            "theme_id": theme_id,
            "asset_id": asset_id,
            "format": request.format,
            "bleed_mm": request.bleed_mm,
            "crop_marks": request.crop_marks,
            "color_profile": request.color_profile,
        }),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue job
    job_queue = JobQueueService()
    job_queue.enqueue_job(job.id, "export_print_pdf")

    return _asset_to_response(asset)


@router.post("/figma/{asset_id}", response_model=ThemeAssetResponse)
def export_to_figma(
    brand_id: str,
    theme_id: str,
    asset_id: str,
    request: ExportFigmaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Export asset to Figma."""
    if member.role not in [BrandRole.OWNER, BrandRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and editors can export assets"
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

    if asset.status != AssetStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset must be completed before exporting"
        )

    if not request.figma_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Figma access token required"
        )

    # Create export job
    job = Job(
        brand_id=brand_id,
        created_by=current_user.id,
        job_type=JobType.EXPORT_FIGMA.value,
        status=JobStatus.PENDING.value,
        params_json=json.dumps({
            "theme_id": theme_id,
            "asset_id": asset_id,
            "figma_access_token": request.figma_access_token,
            "figma_file_name": request.file_name or asset.name,
            "figma_team_id": request.team_id,
        }),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue job
    job_queue = JobQueueService()
    job_queue.enqueue_job(job.id, "export_figma")

    return _asset_to_response(asset)


@router.get("/download-all")
def download_all_assets(
    brand_id: str,
    theme_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Download all completed assets as a single ZIP file."""
    import io
    import zipfile

    theme = db.query(Theme).filter(
        Theme.id == theme_id,
        Theme.brand_id == brand_id
    ).first()

    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )

    # Get all completed assets
    assets = db.query(ThemeAsset).filter(
        ThemeAsset.theme_id == theme_id,
        ThemeAsset.status == AssetStatus.COMPLETED.value
    ).all()

    if not assets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed assets found"
        )

    storage = get_storage_service()
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for asset in assets:
            if asset.storage_path:
                try:
                    content = storage.get(asset.storage_path)
                    # Determine filename
                    ext = _get_extension(asset.content_type)
                    filename = f"{asset.asset_type}/{asset.name}{ext}"
                    zf.writestr(filename, content)
                except Exception as e:
                    # Skip assets that can't be retrieved
                    continue

        # Add README
        readme = f"""# {theme.name} Assets

Downloaded from Brand Engine

## Contents

"""
        for asset in assets:
            readme += f"- {asset.asset_type}: {asset.name}\n"

        zf.writestr("README.md", readme)

    zip_buffer.seek(0)

    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{theme.slug}-assets.zip"'
        }
    )


@router.get("/{asset_id}/print-preview")
def get_print_preview(
    brand_id: str,
    theme_id: str,
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Get print preview information for an asset."""
    asset = db.query(ThemeAsset).filter(
        ThemeAsset.id == asset_id,
        ThemeAsset.theme_id == theme_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    # Get print specs based on asset type
    print_specs = {
        "flyer": {
            "page_size": "A4",
            "dimensions": {"width": 210, "height": 297, "unit": "mm"},
            "bleed": 3,
            "safe_margin": 10,
            "orientation": "portrait",
            "color_profile": "CMYK",
        },
        "brochure": {
            "page_size": "A4",
            "dimensions": {"width": 210, "height": 297, "unit": "mm"},
            "bleed": 3,
            "safe_margin": 12,
            "orientation": "portrait",
            "pages": 4,
            "binding": "saddle_stitch",
            "color_profile": "CMYK",
        },
        "newsletter": {
            "page_size": "Letter",
            "dimensions": {"width": 215.9, "height": 279.4, "unit": "mm"},
            "bleed": 0,
            "safe_margin": 12.7,
            "orientation": "portrait",
            "color_profile": "RGB",
        },
    }

    specs = print_specs.get(asset.asset_type, {})

    return {
        "asset_id": asset.id,
        "asset_type": asset.asset_type,
        "name": asset.name,
        "print_ready": asset.print_pdf_path is not None,
        "print_pdf_path": asset.print_pdf_path,
        "specifications": specs,
        "supported_formats": ["pdf", "pdf_x4"] if asset.asset_type in print_specs else [],
    }


def _get_extension(content_type: Optional[str]) -> str:
    """Get file extension from content type."""
    if not content_type:
        return ""
    ext_map = {
        "application/zip": ".zip",
        "application/pdf": ".pdf",
        "text/html": ".html",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    }
    return ext_map.get(content_type, "")


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
