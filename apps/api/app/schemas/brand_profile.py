from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class BrandIdentity(BaseModel):
    """Brand identity information."""

    name: str
    sources: List[str] = Field(default_factory=list)  # List of source file names


class ColorValue(BaseModel):
    """Color with hex value and optional name."""

    hex: str
    name: Optional[str] = None
    usage: Optional[str] = None  # e.g., "background", "accent"


class BrandColors(BaseModel):
    """Brand color palette."""

    primary: ColorValue
    secondary: List[ColorValue] = Field(default_factory=list)
    neutrals: List[ColorValue] = Field(default_factory=list)
    accent: Optional[ColorValue] = None


class FontScale(BaseModel):
    """Typography scale values."""

    h1: str = "48px"
    h2: str = "36px"
    h3: str = "24px"
    body: str = "16px"
    caption: str = "12px"


class BrandTypography(BaseModel):
    """Brand typography settings."""

    heading_font: str
    body_font: str
    scale: FontScale = Field(default_factory=FontScale)
    weights: Dict[str, int] = Field(default_factory=lambda: {"normal": 400, "bold": 700})


class Margins(BaseModel):
    """Layout margins."""

    top: str = "40px"
    right: str = "40px"
    bottom: str = "40px"
    left: str = "40px"


class LayoutSystem(BaseModel):
    """Brand layout system."""

    margins: Margins = Field(default_factory=Margins)
    grid_unit: str = "8px"
    max_width: str = "1200px"
    columns: int = 12


class BrandImagery(BaseModel):
    """Brand imagery style."""

    photo_vs_illustration: str = "mixed"  # photo, illustration, mixed
    motifs: List[str] = Field(default_factory=list)
    mood: List[str] = Field(default_factory=list)
    style_notes: Optional[str] = None


class ToneOfVoice(BaseModel):
    """Brand tone of voice."""

    attributes: List[str] = Field(default_factory=list)  # e.g., ["professional", "friendly"]
    do: List[str] = Field(default_factory=list)  # Writing guidelines - do
    dont: List[str] = Field(default_factory=list)  # Writing guidelines - don't
    example_phrases: List[str] = Field(default_factory=list)


class ConfidenceScores(BaseModel):
    """Confidence scores for each analysis component (0.0 to 1.0)."""

    colors: float = 0.0
    typography: float = 0.0
    layout: float = 0.0
    imagery: float = 0.0
    tone: float = 0.0


class BrandProfileSchema(BaseModel):
    """Complete brand profile schema."""

    identity: BrandIdentity
    colors: BrandColors
    typography: BrandTypography
    layout_system: LayoutSystem
    imagery: BrandImagery
    tone_of_voice: ToneOfVoice
    confidence: ConfidenceScores

    class Config:
        json_schema_extra = {
            "example": {
                "identity": {"name": "Acme Corp", "sources": ["brand-guidelines.pdf"]},
                "colors": {
                    "primary": {"hex": "#0066CC", "name": "Acme Blue"},
                    "secondary": [{"hex": "#FF6600", "name": "Acme Orange"}],
                    "neutrals": [{"hex": "#333333"}, {"hex": "#F5F5F5"}],
                },
                "typography": {
                    "heading_font": "Montserrat",
                    "body_font": "Open Sans",
                    "scale": {"h1": "48px", "h2": "36px", "body": "16px", "caption": "12px"},
                },
                "layout_system": {
                    "margins": {"top": "40px", "right": "40px", "bottom": "40px", "left": "40px"},
                    "grid_unit": "8px",
                },
                "imagery": {
                    "photo_vs_illustration": "photo",
                    "motifs": ["technology", "people"],
                    "mood": ["professional", "innovative"],
                },
                "tone_of_voice": {
                    "attributes": ["professional", "innovative", "approachable"],
                    "do": ["Use active voice", "Be concise"],
                    "dont": ["Use jargon", "Be overly formal"],
                    "example_phrases": ["Innovate with confidence", "Solutions that work"],
                },
                "confidence": {
                    "colors": 0.85,
                    "typography": 0.7,
                    "layout": 0.6,
                    "imagery": 0.5,
                    "tone": 0.4,
                },
            }
        }


class BrandProfileResponse(BaseModel):
    """Brand profile API response."""

    id: str
    brand_id: str
    version: int
    profile: BrandProfileSchema
    summary_md: Optional[str] = None
    source_upload_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
