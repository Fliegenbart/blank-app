"""Theme models for campaign-specific asset generation."""
import enum
import json
from typing import List, Optional
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin, generate_uuid


class ThemeStatus(str, enum.Enum):
    """Status of a theme."""
    DRAFT = "draft"
    READY = "ready"
    GENERATING = "generating"
    COMPLETED = "completed"


class AssetType(str, enum.Enum):
    """Types of assets that can be generated for a theme."""
    WEBSITE = "website"
    LANDING_PAGE = "landing_page"
    NEWSLETTER = "newsletter"
    FLYER = "flyer"
    BROCHURE = "brochure"
    TEASER_SCRIPT = "teaser_script"
    SOCIAL_MEDIA = "social_media"
    PRESENTATION = "presentation"
    BANNER_ADS = "banner_ads"


class AssetStatus(str, enum.Enum):
    """Status of a theme asset."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, enum.Enum):
    """Types of documents that can be attached to a theme."""
    BRIEF = "brief"
    GUIDELINES = "guidelines"
    CONTENT = "content"
    REFERENCE = "reference"
    OTHER = "other"


class Theme(Base, TimestampMixin):
    """Theme model - campaigns or events under a brand."""
    __tablename__ = "themes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand_id = Column(String(36), ForeignKey("brands.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Theme info
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Status
    status = Column(String(20), default=ThemeStatus.DRAFT.value, nullable=False)

    # Context (JSON for flexibility)
    context_json = Column(Text, nullable=True)  # Additional context/brief

    # Configuration - which assets to generate
    asset_config_json = Column(Text, nullable=True)

    # Relationships
    brand = relationship("Brand", back_populates="themes")
    creator = relationship("User")
    documents = relationship("ThemeDocument", back_populates="theme", cascade="all, delete-orphan")
    assets = relationship("ThemeAsset", back_populates="theme", cascade="all, delete-orphan")
    jobs = relationship("ThemeJob", back_populates="theme", cascade="all, delete-orphan")

    @property
    def context(self) -> dict:
        """Get context as dict."""
        if self.context_json:
            return json.loads(self.context_json)
        return {}

    @context.setter
    def context(self, value: dict):
        """Set context from dict."""
        self.context_json = json.dumps(value) if value else None

    @property
    def asset_config(self) -> dict:
        """Get asset config as dict."""
        if self.asset_config_json:
            return json.loads(self.asset_config_json)
        return {}

    @asset_config.setter
    def asset_config(self, value: dict):
        """Set asset config from dict."""
        self.asset_config_json = json.dumps(value) if value else None


class ThemeDocument(Base, TimestampMixin):
    """Documents attached to a theme for context."""
    __tablename__ = "theme_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    theme_id = Column(String(36), ForeignKey("themes.id"), nullable=False)
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Document info
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    document_type = Column(String(50), default=DocumentType.OTHER.value, nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, etc.
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)

    # Extracted content
    extracted_text = Column(Text, nullable=True)
    summary_json = Column(Text, nullable=True)  # AI-extracted key points

    # Status
    status = Column(String(20), default="uploaded", nullable=False)

    # Relationships
    theme = relationship("Theme", back_populates="documents")
    uploader = relationship("User")

    @property
    def summary(self) -> dict:
        """Get summary as dict."""
        if self.summary_json:
            return json.loads(self.summary_json)
        return {}

    @summary.setter
    def summary(self, value: dict):
        """Set summary from dict."""
        self.summary_json = json.dumps(value) if value else None


class ThemeAsset(Base, TimestampMixin):
    """Generated assets for a theme."""
    __tablename__ = "theme_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    theme_id = Column(String(36), ForeignKey("themes.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=True)

    # Asset info
    asset_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(20), default=AssetStatus.PENDING.value, nullable=False)

    # Storage
    storage_path = Column(String(500), nullable=True)
    preview_path = Column(String(500), nullable=True)  # For preview images
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)

    # Export paths
    print_pdf_path = Column(String(500), nullable=True)
    figma_file_key = Column(String(100), nullable=True)

    # Output variants (different sizes/formats)
    variants_json = Column(Text, nullable=True)

    # Metadata
    metadata_json = Column(Text, nullable=True)
    generation_params_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    theme = relationship("Theme", back_populates="assets")
    job = relationship("Job")

    @property
    def variants(self) -> list:
        """Get variants as list."""
        if self.variants_json:
            return json.loads(self.variants_json)
        return []

    @variants.setter
    def variants(self, value: list):
        """Set variants from list."""
        self.variants_json = json.dumps(value) if value else None

    @property
    def asset_metadata(self) -> dict:
        """Get metadata as dict."""
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}

    @asset_metadata.setter
    def asset_metadata(self, value: dict):
        """Set metadata from dict."""
        self.metadata_json = json.dumps(value) if value else None


class ThemeJob(Base, TimestampMixin):
    """Batch job tracking for theme asset generation."""
    __tablename__ = "theme_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    theme_id = Column(String(36), ForeignKey("themes.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Batch info
    status = Column(String(20), default="pending", nullable=False)
    total_assets = Column(Integer, default=0, nullable=False)
    completed_assets = Column(Integer, default=0, nullable=False)
    failed_assets = Column(Integer, default=0, nullable=False)

    # Asset job IDs
    asset_job_ids_json = Column(Text, nullable=True)

    # Results
    error_messages_json = Column(Text, nullable=True)

    # RQ job tracking
    rq_job_id = Column(String(100), nullable=True)

    # Relationships
    theme = relationship("Theme", back_populates="jobs")
    creator = relationship("User")

    @property
    def asset_job_ids(self) -> list:
        """Get asset job IDs as list."""
        if self.asset_job_ids_json:
            return json.loads(self.asset_job_ids_json)
        return []

    @asset_job_ids.setter
    def asset_job_ids(self, value: list):
        """Set asset job IDs from list."""
        self.asset_job_ids_json = json.dumps(value) if value else None

    @property
    def progress(self) -> float:
        """Calculate progress percentage."""
        if self.total_assets == 0:
            return 0.0
        return (self.completed_assets + self.failed_assets) / self.total_assets
