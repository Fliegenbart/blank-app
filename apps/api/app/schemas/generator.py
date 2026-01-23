from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


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


class LandingPageGenerateRequest(BaseModel):
    """Request schema for landing page generation."""

    topic: str
    sections: Optional[List[str]] = None  # e.g., ["hero", "features", "testimonials", "cta"]
    reference_id: Optional[str] = None  # Reference website to use for structure
    profile_version: Optional[int] = None


class SocialMediaPlatform(str, Enum):
    """Supported social media platforms."""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"


class SocialMediaGenerateRequest(BaseModel):
    """Request schema for social media content generation."""

    topic: str
    platforms: List[SocialMediaPlatform] = [
        SocialMediaPlatform.TWITTER,
        SocialMediaPlatform.LINKEDIN,
        SocialMediaPlatform.INSTAGRAM,
    ]
    reference_id: Optional[str] = None
    profile_version: Optional[int] = None


class EmailType(str, Enum):
    """Types of emails that can be generated."""
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"
    ANNOUNCEMENT = "announcement"
    WELCOME = "welcome"
    FOLLOWUP = "followup"


class EmailGenerateRequest(BaseModel):
    """Request schema for email content generation."""

    topic: str
    email_type: EmailType = EmailType.NEWSLETTER
    reference_id: Optional[str] = None
    profile_version: Optional[int] = None
