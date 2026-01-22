from pydantic import BaseModel
from typing import Optional, List


class PageConfig(BaseModel):
    """Configuration for a website page."""

    slug: str
    title: str
    description: Optional[str] = None
    sections: Optional[List[str]] = None  # e.g., ["hero", "features", "cta"]


class WebsiteGenerateRequest(BaseModel):
    """Request schema for website generation."""

    topic: str
    pages: List[PageConfig]
    brief: Optional[str] = None
    profile_version: Optional[int] = None  # Use latest if not specified


class NewsletterGenerateRequest(BaseModel):
    """Request schema for newsletter generation."""

    topic: str
    offer: Optional[str] = None
    cta: str
    subject_line: Optional[str] = None
    preview_text: Optional[str] = None
    profile_version: Optional[int] = None  # Use latest if not specified
