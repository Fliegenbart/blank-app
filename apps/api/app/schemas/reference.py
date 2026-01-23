from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class ReferenceCreate(BaseModel):
    """Schema for creating a reference."""
    name: str
    description: Optional[str] = None
    urls: List[str]


class ReferenceUpdate(BaseModel):
    """Schema for updating a reference."""
    name: Optional[str] = None
    description: Optional[str] = None


class ReferenceResponse(BaseModel):
    """Schema for reference response."""
    id: str
    brand_id: str
    name: str
    description: Optional[str] = None
    urls: List[str]
    status: str
    error_message: Optional[str] = None
    page_count: Optional[int] = None
    total_word_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReferenceDetailResponse(ReferenceResponse):
    """Detailed reference response including structure."""
    structure: Optional[Dict[str, Any]] = None
    scraped_data: Optional[Dict[str, Any]] = None


class ScrapedSectionResponse(BaseModel):
    """Schema for a scraped section."""
    section_type: str
    heading: Optional[str] = None
    subheading: Optional[str] = None
    content: List[str] = []
    cta_text: Optional[str] = None
    images: List[str] = []
    items: List[Dict[str, Any]] = []
    order: int = 0


class ScrapedPageResponse(BaseModel):
    """Schema for a scraped page."""
    url: str
    title: str
    meta_description: Optional[str] = None
    sections: List[ScrapedSectionResponse] = []
    navigation: List[Dict[str, str]] = []
    word_count: int = 0


class ReferenceStructureResponse(BaseModel):
    """Schema for analyzed reference structure."""
    common_sections: List[str] = []
    section_order_pattern: List[str] = []
    key_messaging: List[str] = []
    navigation_structure: List[Dict[str, str]] = []
    content_themes: List[str] = []
    cta_patterns: List[str] = []
    total_word_count: int = 0
