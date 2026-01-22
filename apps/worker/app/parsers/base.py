from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from PIL import Image
import io


@dataclass
class TextRun:
    """A run of text with formatting."""
    text: str
    font_name: Optional[str] = None
    font_size: Optional[float] = None  # in points
    font_color: Optional[str] = None  # hex color
    bold: bool = False
    italic: bool = False


@dataclass
class ExtractedImage:
    """An extracted image with metadata."""
    data: bytes
    format: str  # png, jpg, etc.
    width: int
    height: int
    filename: Optional[str] = None


@dataclass
class ParsedPage:
    """A parsed page/slide."""
    page_number: int
    text_runs: List[TextRun] = field(default_factory=list)
    images: List[ExtractedImage] = field(default_factory=list)
    rendered_image: Optional[ExtractedImage] = None  # Full page render


@dataclass
class ThemeData:
    """Theme/style data extracted from document."""
    color_scheme: Dict[str, str] = field(default_factory=dict)  # name -> hex
    font_scheme: Dict[str, str] = field(default_factory=dict)  # usage -> font name
    accent_colors: List[str] = field(default_factory=list)  # hex colors


@dataclass
class ParsedDocument:
    """Result of parsing a document."""
    filename: str
    file_type: str
    pages: List[ParsedPage] = field(default_factory=list)
    theme: Optional[ThemeData] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_all_text(self) -> str:
        """Get all text from the document."""
        texts = []
        for page in self.pages:
            for run in page.text_runs:
                texts.append(run.text)
        return " ".join(texts)

    def get_all_images(self) -> List[ExtractedImage]:
        """Get all images from the document."""
        images = []
        for page in self.pages:
            images.extend(page.images)
        return images

    def get_rendered_pages(self) -> List[ExtractedImage]:
        """Get rendered page images."""
        return [p.rendered_image for p in self.pages if p.rendered_image]


class DocumentParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, data: bytes) -> ParsedDocument:
        """Parse document data and return structured result."""
        pass

    @abstractmethod
    def can_parse(self, file_type: str) -> bool:
        """Check if this parser can handle the file type."""
        pass
