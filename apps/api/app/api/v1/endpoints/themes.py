"""Theme API endpoints."""
import re
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_brand_member
from app.models import (
    User, Brand, BrandMember, BrandRole, BrandProfile,
    Theme, ThemeStatus, ThemeDocument, ThemeAsset, ThemeJob,
    AssetType, AssetStatus, DocumentType, Job, JobType, JobStatus
)
from app.schemas.theme import (
    ThemeCreate, ThemeUpdate, ThemeResponse, ThemeListResponse,
    ThemeDocumentCreate, ThemeDocumentResponse,
    ThemeAssetResponse, ThemeJobResponse,
    GenerateAllAssetsRequest, GenerateSingleAssetRequest, RegenerateAssetRequest,
)
from app.services.storage import get_storage_service
from app.services.job_queue import JobQueueService

router = APIRouter(prefix="/brands/{brand_id}/themes", tags=["themes"])


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


# === Theme CRUD ===

@router.post("", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
def create_theme(
    brand_id: str,
    theme_data: ThemeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Create a new theme for a brand."""
    if member.role not in [BrandRole.OWNER, BrandRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and editors can create themes"
        )

    # Generate slug if not provided
    slug = theme_data.slug or slugify(theme_data.name)

    # Check for duplicate slug
    existing = db.query(Theme).filter(
        Theme.brand_id == brand_id,
        Theme.slug == slug
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Theme with slug '{slug}' already exists"
        )

    theme = Theme(
        brand_id=brand_id,
        created_by=current_user.id,
        name=theme_data.name,
        slug=slug,
        description=theme_data.description,
        context_json=json.dumps(theme_data.context) if theme_data.context else None,
        asset_config_json=json.dumps(theme_data.asset_config) if theme_data.asset_config else None,
    )
    db.add(theme)
    db.commit()
    db.refresh(theme)

    return _theme_to_response(theme)


@router.get("", response_model=List[ThemeListResponse])
def list_themes(
    brand_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """List all themes for a brand."""
    themes = db.query(Theme).filter(Theme.brand_id == brand_id).order_by(Theme.created_at.desc()).all()

    result = []
    for theme in themes:
        doc_count = db.query(ThemeDocument).filter(ThemeDocument.theme_id == theme.id).count()
        asset_count = db.query(ThemeAsset).filter(ThemeAsset.theme_id == theme.id).count()
        result.append(ThemeListResponse(
            id=theme.id,
            brand_id=theme.brand_id,
            name=theme.name,
            slug=theme.slug,
            description=theme.description,
            status=theme.status,
            document_count=doc_count,
            asset_count=asset_count,
            created_at=theme.created_at,
            updated_at=theme.updated_at,
        ))

    return result


@router.get("/{theme_id}", response_model=ThemeResponse)
def get_theme(
    brand_id: str,
    theme_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Get a specific theme."""
    theme = db.query(Theme).filter(
        Theme.id == theme_id,
        Theme.brand_id == brand_id
    ).first()

    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )

    return _theme_to_response(theme)


@router.put("/{theme_id}", response_model=ThemeResponse)
def update_theme(
    brand_id: str,
    theme_id: str,
    theme_data: ThemeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Update a theme."""
    if member.role not in [BrandRole.OWNER, BrandRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and editors can update themes"
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

    # Update fields
    if theme_data.name is not None:
        theme.name = theme_data.name
    if theme_data.slug is not None:
        # Check for duplicate slug
        existing = db.query(Theme).filter(
            Theme.brand_id == brand_id,
            Theme.slug == theme_data.slug,
            Theme.id != theme_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Theme with slug '{theme_data.slug}' already exists"
            )
        theme.slug = theme_data.slug
    if theme_data.description is not None:
        theme.description = theme_data.description
    if theme_data.status is not None:
        theme.status = theme_data.status
    if theme_data.context is not None:
        theme.context_json = json.dumps(theme_data.context)
    if theme_data.asset_config is not None:
        theme.asset_config_json = json.dumps(theme_data.asset_config)

    db.commit()
    db.refresh(theme)

    return _theme_to_response(theme)


@router.delete("/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_theme(
    brand_id: str,
    theme_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Delete a theme."""
    if member.role != BrandRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can delete themes"
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

    db.delete(theme)
    db.commit()


# === Theme Documents ===

@router.post("/{theme_id}/documents", response_model=ThemeDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_theme_document(
    brand_id: str,
    theme_id: str,
    file: UploadFile = File(...),
    name: str = Form(...),
    document_type: str = Form(default="other"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Upload a document to a theme."""
    if member.role not in [BrandRole.OWNER, BrandRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and editors can upload documents"
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

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Determine file type
    file_type = file.filename.split(".")[-1].lower() if file.filename else "unknown"

    # Store file
    storage = get_storage_service()
    storage_path = f"themes/{theme_id}/documents/{file.filename}"
    storage.store(storage_path, content, file.content_type or "application/octet-stream")

    # Create document record
    document = ThemeDocument(
        theme_id=theme_id,
        uploaded_by=current_user.id,
        name=name,
        original_filename=file.filename,
        document_type=document_type,
        file_type=file_type,
        file_size=file_size,
        storage_path=storage_path,
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # TODO: Enqueue document extraction job
    # job_queue = JobQueueService(db)
    # job_queue.enqueue_extract_document(document.id)

    return _document_to_response(document)


@router.get("/{theme_id}/documents", response_model=List[ThemeDocumentResponse])
def list_theme_documents(
    brand_id: str,
    theme_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """List all documents for a theme."""
    theme = db.query(Theme).filter(
        Theme.id == theme_id,
        Theme.brand_id == brand_id
    ).first()

    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )

    documents = db.query(ThemeDocument).filter(
        ThemeDocument.theme_id == theme_id
    ).order_by(ThemeDocument.created_at.desc()).all()

    return [_document_to_response(doc) for doc in documents]


@router.delete("/{theme_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_theme_document(
    brand_id: str,
    theme_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Delete a theme document."""
    if member.role not in [BrandRole.OWNER, BrandRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and editors can delete documents"
        )

    document = db.query(ThemeDocument).filter(
        ThemeDocument.id == document_id,
        ThemeDocument.theme_id == theme_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete file from storage
    storage = get_storage_service()
    try:
        storage.delete(document.storage_path)
    except Exception:
        pass  # Ignore storage errors

    db.delete(document)
    db.commit()


# === Theme Assets ===

@router.get("/{theme_id}/assets", response_model=List[ThemeAssetResponse])
def list_theme_assets(
    brand_id: str,
    theme_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """List all generated assets for a theme."""
    theme = db.query(Theme).filter(
        Theme.id == theme_id,
        Theme.brand_id == brand_id
    ).first()

    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )

    assets = db.query(ThemeAsset).filter(
        ThemeAsset.theme_id == theme_id
    ).order_by(ThemeAsset.created_at.desc()).all()

    return [_asset_to_response(asset) for asset in assets]


@router.get("/{theme_id}/assets/{asset_id}", response_model=ThemeAssetResponse)
def get_theme_asset(
    brand_id: str,
    theme_id: str,
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Get a specific theme asset."""
    asset = db.query(ThemeAsset).filter(
        ThemeAsset.id == asset_id,
        ThemeAsset.theme_id == theme_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    return _asset_to_response(asset)


@router.get("/{theme_id}/assets/{asset_id}/download")
def download_theme_asset(
    brand_id: str,
    theme_id: str,
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """Download a theme asset file."""
    from fastapi.responses import FileResponse, StreamingResponse
    import os

    asset = db.query(ThemeAsset).filter(
        ThemeAsset.id == asset_id,
        ThemeAsset.theme_id == theme_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    if not asset.storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset file not found"
        )

    storage = get_storage_service()
    try:
        content = storage.get(asset.storage_path)

        # Determine filename
        filename = asset.name
        if asset.content_type:
            ext_map = {
                "text/html": ".html",
                "application/zip": ".zip",
                "application/pdf": ".pdf",
                "image/png": ".png",
                "image/jpeg": ".jpg",
            }
            ext = ext_map.get(asset.content_type, "")
            if ext and not filename.endswith(ext):
                filename += ext

        return StreamingResponse(
            iter([content]),
            media_type=asset.content_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download asset: {str(e)}"
        )


# === Theme Jobs ===

@router.get("/{theme_id}/jobs", response_model=List[ThemeJobResponse])
def list_theme_jobs(
    brand_id: str,
    theme_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: BrandMember = Depends(get_brand_member),
):
    """List all generation jobs for a theme."""
    theme = db.query(Theme).filter(
        Theme.id == theme_id,
        Theme.brand_id == brand_id
    ).first()

    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )

    jobs = db.query(ThemeJob).filter(
        ThemeJob.theme_id == theme_id
    ).order_by(ThemeJob.created_at.desc()).all()

    return [_theme_job_to_response(job) for job in jobs]


# === Helper Functions ===

def _theme_to_response(theme: Theme) -> ThemeResponse:
    """Convert theme model to response schema."""
    return ThemeResponse(
        id=theme.id,
        brand_id=theme.brand_id,
        created_by=theme.created_by,
        name=theme.name,
        slug=theme.slug,
        description=theme.description,
        status=theme.status,
        context=theme.context,
        asset_config=theme.asset_config,
        created_at=theme.created_at,
        updated_at=theme.updated_at,
    )


def _document_to_response(doc: ThemeDocument) -> ThemeDocumentResponse:
    """Convert document model to response schema."""
    return ThemeDocumentResponse(
        id=doc.id,
        theme_id=doc.theme_id,
        uploaded_by=doc.uploaded_by,
        name=doc.name,
        original_filename=doc.original_filename,
        document_type=doc.document_type,
        file_type=doc.file_type,
        file_size=doc.file_size,
        status=doc.status,
        extracted_text=doc.extracted_text,
        summary=doc.summary,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


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
