from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class SectionType(str, Enum):
    """Types of sections that can be identified on a page."""
    HERO = "hero"
    FEATURES = "features"
    CTA = "cta"
    CONTENT = "content"
    GALLERY = "gallery"
    TESTIMONIALS = "testimonials"
    PRICING = "pricing"
    TEAM = "team"
    FAQ = "faq"
    CONTACT = "contact"
    FOOTER = "footer"
    HEADER = "header"
    NAVIGATION = "navigation"
    UNKNOWN = "unknown"


@dataclass
class ScrapedSection:
    """A section extracted from a webpage."""
    section_type: SectionType
    heading: Optional[str] = None
    subheading: Optional[str] = None
    content: List[str] = field(default_factory=list)
    cta_text: Optional[str] = None
    cta_url: Optional[str] = None
    images: List[str] = field(default_factory=list)
    items: List[Dict[str, Any]] = field(default_factory=list)
    order: int = 0
    raw_html: Optional[str] = None
    css_classes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_type": self.section_type.value,
            "heading": self.heading,
            "subheading": self.subheading,
            "content": self.content,
            "cta_text": self.cta_text,
            "cta_url": self.cta_url,
            "images": self.images,
            "items": self.items,
            "order": self.order,
            "css_classes": self.css_classes,
        }


@dataclass
class ScrapedPage:
    """A complete scraped webpage."""
    url: str
    title: str
    meta_description: Optional[str] = None
    sections: List[ScrapedSection] = field(default_factory=list)
    navigation: List[Dict[str, str]] = field(default_factory=list)
    text_content: str = ""
    word_count: int = 0
    screenshot_path: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "meta_description": self.meta_description,
            "sections": [s.to_dict() for s in self.sections],
            "navigation": self.navigation,
            "text_content": self.text_content,
            "word_count": self.word_count,
            "screenshot_path": self.screenshot_path,
            "error": self.error,
        }


@dataclass
class ReferenceStructure:
    """Analyzed structure from reference websites."""
    pages: List[ScrapedPage] = field(default_factory=list)
    common_sections: List[SectionType] = field(default_factory=list)
    section_order_pattern: List[SectionType] = field(default_factory=list)
    key_messaging: List[str] = field(default_factory=list)
    navigation_structure: List[Dict[str, str]] = field(default_factory=list)
    content_themes: List[str] = field(default_factory=list)
    cta_patterns: List[str] = field(default_factory=list)
    total_word_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pages": [p.to_dict() for p in self.pages],
            "common_sections": [s.value for s in self.common_sections],
            "section_order_pattern": [s.value for s in self.section_order_pattern],
            "key_messaging": self.key_messaging,
            "navigation_structure": self.navigation_structure,
            "content_themes": self.content_themes,
            "cta_patterns": self.cta_patterns,
            "total_word_count": self.total_word_count,
        }
