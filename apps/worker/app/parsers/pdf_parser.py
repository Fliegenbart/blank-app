import io
import os
import subprocess
import tempfile
from typing import Optional, List
import structlog

import pdfplumber
from PIL import Image

from app.parsers.base import (
    DocumentParser,
    ParsedDocument,
    ParsedPage,
    TextRun,
    ExtractedImage,
)

logger = structlog.get_logger()


class PDFParser(DocumentParser):
    """Parser for PDF files."""

    def can_parse(self, file_type: str) -> bool:
        return file_type.lower() == "pdf"

    def parse(self, data: bytes) -> ParsedDocument:
        """Parse a PDF file."""
        logger.info("Parsing PDF document")

        doc = ParsedDocument(filename="", file_type="pdf")

        # Parse text using pdfplumber
        try:
            doc = self._parse_with_pdfplumber(data, doc)
        except Exception as e:
            logger.error("Error parsing with pdfplumber", error=str(e))

        # Render pages to images using poppler
        try:
            rendered_pages = self._render_pages(data)
            for i, img in enumerate(rendered_pages):
                if i < len(doc.pages):
                    doc.pages[i].rendered_image = img
                else:
                    # Create page if not enough from text parsing
                    page = ParsedPage(page_number=i + 1, rendered_image=img)
                    doc.pages.append(page)
        except Exception as e:
            logger.warning("Error rendering pages", error=str(e))

        logger.info("PDF parsing complete", pages=len(doc.pages))
        return doc

    def _parse_with_pdfplumber(self, data: bytes, doc: ParsedDocument) -> ParsedDocument:
        """Parse PDF text using pdfplumber."""
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                parsed_page = ParsedPage(page_number=page_num + 1)

                # Extract characters with font info
                chars = page.chars
                if chars:
                    # Group characters by font
                    current_text = ""
                    current_font = None
                    current_size = None

                    for char in chars:
                        font_name = char.get("fontname")
                        font_size = char.get("size")

                        # Check if font changed
                        if font_name != current_font or abs((font_size or 0) - (current_size or 0)) > 0.5:
                            if current_text.strip():
                                text_run = TextRun(
                                    text=current_text,
                                    font_name=self._clean_font_name(current_font),
                                    font_size=current_size,
                                )
                                parsed_page.text_runs.append(text_run)
                            current_text = ""
                            current_font = font_name
                            current_size = font_size

                        current_text += char.get("text", "")

                    # Add last run
                    if current_text.strip():
                        text_run = TextRun(
                            text=current_text,
                            font_name=self._clean_font_name(current_font),
                            font_size=current_size,
                        )
                        parsed_page.text_runs.append(text_run)

                # Fallback to simple text extraction
                if not parsed_page.text_runs:
                    text = page.extract_text()
                    if text and text.strip():
                        parsed_page.text_runs.append(TextRun(text=text))

                # Extract images
                for img in page.images:
                    try:
                        # pdfplumber gives us image metadata
                        # Full extraction would need additional processing
                        pass
                    except Exception:
                        pass

                doc.pages.append(parsed_page)

        return doc

    def _clean_font_name(self, font_name: Optional[str]) -> Optional[str]:
        """Clean up font name from PDF."""
        if not font_name:
            return None

        # Remove common prefixes
        prefixes = ["AAAAAA+", "BCDEEE+", "ABCDEF+"]
        for prefix in prefixes:
            if font_name.startswith(prefix):
                font_name = font_name[len(prefix):]

        # Remove subset indicators (6 chars + plus sign)
        if len(font_name) > 7 and font_name[6] == "+":
            font_name = font_name[7:]

        # Clean up common suffixes
        suffixes = ["-Bold", "-Italic", "-BoldItalic", "-Regular", ",Bold", ",Italic"]
        base_name = font_name
        for suffix in suffixes:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]

        return base_name or font_name

    def _render_pages(self, data: bytes, dpi: int = 150) -> List[ExtractedImage]:
        """Render PDF pages to images using poppler-utils."""
        images = []

        # Write PDF to temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "input.pdf")
            with open(pdf_path, "wb") as f:
                f.write(data)

            # Use pdftoppm to render pages
            output_prefix = os.path.join(tmpdir, "page")

            try:
                subprocess.run(
                    [
                        "pdftoppm",
                        "-png",
                        "-r", str(dpi),
                        pdf_path,
                        output_prefix,
                    ],
                    check=True,
                    capture_output=True,
                    timeout=120,
                )
            except subprocess.CalledProcessError as e:
                logger.error("pdftoppm failed", error=e.stderr.decode() if e.stderr else str(e))
                return images
            except subprocess.TimeoutExpired:
                logger.error("pdftoppm timed out")
                return images
            except FileNotFoundError:
                logger.warning("pdftoppm not found, skipping page rendering")
                return images

            # Read rendered images
            page_files = sorted([
                f for f in os.listdir(tmpdir)
                if f.startswith("page") and f.endswith(".png")
            ])

            for page_file in page_files:
                page_path = os.path.join(tmpdir, page_file)
                try:
                    with open(page_path, "rb") as f:
                        img_data = f.read()

                    img = Image.open(io.BytesIO(img_data))
                    width, height = img.size

                    images.append(
                        ExtractedImage(
                            data=img_data,
                            format="png",
                            width=width,
                            height=height,
                            filename=page_file,
                        )
                    )
                except Exception as e:
                    logger.warning("Error reading rendered page", file=page_file, error=str(e))

        return images
