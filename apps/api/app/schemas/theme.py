"""Pydantic schemas for Theme API."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# === Theme Schemas ===

class ThemeCreate(BaseModel):
    """Schema for creating a theme."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    asset_config: Optional[Dict[str, Any]] = None


class ThemeUpdate(BaseModel):
    """Schema for updating a theme."""
    name: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    asset_config: Optional[Dict[str, Any]] = None


class ThemeResponse(BaseModel):
    """Schema for theme response."""
    id: str
    brand_id: str
    created_by: str
    name: str
    slug: str
    description: Optional[str]
    status: str
    context: Optional[Dict[str, Any]]
    asset_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ThemeListResponse(BaseModel):
    """Schema for theme list response with counts."""
    id: str
    brand_id: str
    name: str
    slug: str
    description: Optional[str]
    status: str
    document_count: int = 0
    asset_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === Theme Document Schemas ===

class ThemeDocumentCreate(BaseModel):
    """Schema for creating a theme document (metadata only, file via form)."""
    name: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(default="other")


class ThemeDocumentResponse(BaseModel):
    """Schema for theme document response."""
    id: str
    theme_id: str
    uploaded_by: str
    name: str
    original_filename: str
    document_type: str
    file_type: str
    file_size: int
    status: str
    extracted_text: Optional[str]
    summary: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === Theme Asset Schemas ===

class ThemeAssetResponse(BaseModel):
    """Schema for theme asset response."""
    id: str
    theme_id: str
    job_id: Optional[str]
    asset_type: str
    name: str
    status: str
    storage_path: Optional[str]
    preview_path: Optional[str]
    file_size: Optional[int]
    content_type: Optional[str]
    print_pdf_path: Optional[str]
    figma_file_key: Optional[str]
    variants: Optional[List[Dict[str, Any]]]
    metadata: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === Theme Job Schemas ===

class ThemeJobResponse(BaseModel):
    """Schema for theme job response."""
    id: str
    theme_id: str
    created_by: str
    status: str
    total_assets: int
    completed_assets: int
    failed_assets: int
    progress: float
    asset_job_ids: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === Generation Request Schemas ===

class GenerateAllAssetsRequest(BaseModel):
    """Schema for generating all assets for a theme."""
    asset_types: List[str] = Field(
        ...,
        description="List of asset types to generate",
        example=["website", "newsletter", "flyer", "social_media"]
    )
    profile_version: Optional[int] = Field(
        None,
        description="Brand profile version to use"
    )


class GenerateSingleAssetRequest(BaseModel):
    """Schema for generating a single asset."""
    profile_version: Optional[int] = None
    params: Optional[Dict[str, Any]] = None


class RegenerateAssetRequest(BaseModel):
    """Schema for regenerating an asset."""
    profile_version: Optional[int] = None
    params: Optional[Dict[str, Any]] = None


# === Export Request Schemas ===

class ExportPrintRequest(BaseModel):
    """Schema for print export request."""
    format: str = Field(default="A4", description="Page format: A4, A5, Letter")
    bleed_mm: float = Field(default=3.0, description="Bleed in millimeters")
    include_crop_marks: bool = Field(default=True)
    color_profile: str = Field(default="CMYK", description="Color profile: CMYK, RGB")


class ExportFigmaRequest(BaseModel):
    """Schema for Figma export request."""
    figma_file_name: Optional[str] = Field(None, description="Name for the Figma file")


# === Batch Operations ===

class BatchExportRequest(BaseModel):
    """Schema for batch export request."""
    asset_ids: List[str]
    export_type: str = Field(..., description="Type of export: print, figma, zip")
    options: Optional[Dict[str, Any]] = None
