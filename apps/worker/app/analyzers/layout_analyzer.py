from typing import Dict, List
from collections import Counter
import structlog

from app.parsers.base import ParsedDocument

logger = structlog.get_logger()


class LayoutAnalyzer:
    """Analyzes layout patterns from documents."""

    def analyze(self, doc: ParsedDocument) -> Dict:
        """Analyze layout from a parsed document."""
        logger.info("Analyzing layout")

        # Analyze margins from rendered pages
        margins = self._analyze_margins(doc)

        # Determine grid unit
        grid_unit = self._determine_grid_unit(doc)

        # Determine max width and columns
        max_width, columns = self._determine_grid_settings(doc)

        # Calculate confidence
        confidence = self._calculate_confidence(doc)

        result = {
            "margins": margins,
            "grid_unit": grid_unit,
            "max_width": max_width,
            "columns": columns,
            "confidence": confidence,
        }

        logger.info("Layout analysis complete", grid_unit=grid_unit)

        return result

    def _analyze_margins(self, doc: ParsedDocument) -> Dict[str, str]:
        """Analyze page margins from rendered images or metadata."""
        # Default margins based on common document standards
        default_margins = {
            "top": "40px",
            "right": "40px",
            "bottom": "40px",
            "left": "40px",
        }

        # Check for rendered pages
        rendered_pages = doc.get_rendered_pages()
        if not rendered_pages:
            return default_margins

        # Analyze first few pages
        margin_samples = {"top": [], "right": [], "bottom": [], "left": []}

        for img in rendered_pages[:5]:
            try:
                margins = self._detect_margins_from_image(img)
                if margins:
                    for key in margin_samples:
                        if key in margins:
                            margin_samples[key].append(margins[key])
            except Exception as e:
                logger.warning("Error analyzing margins from image", error=str(e))

        # Calculate average margins
        result = {}
        for key, samples in margin_samples.items():
            if samples:
                avg = sum(samples) / len(samples)
                # Round to nearest 8px (common grid unit)
                rounded = round(avg / 8) * 8
                result[key] = f"{max(24, int(rounded))}px"
            else:
                result[key] = default_margins[key]

        return result

    def _detect_margins_from_image(self, img) -> Dict[str, int]:
        """Detect margins from a rendered page image."""
        from PIL import Image
        import io
        import numpy as np

        image = Image.open(io.BytesIO(img.data)).convert("L")
        pixels = np.array(image)

        height, width = pixels.shape

        # Find content boundaries (non-white areas)
        threshold = 250  # Near-white threshold

        # Find top margin
        top = 0
        for i in range(height):
            if np.any(pixels[i, :] < threshold):
                top = i
                break

        # Find bottom margin
        bottom = 0
        for i in range(height - 1, -1, -1):
            if np.any(pixels[i, :] < threshold):
                bottom = height - i - 1
                break

        # Find left margin
        left = 0
        for i in range(width):
            if np.any(pixels[:, i] < threshold):
                left = i
                break

        # Find right margin
        right = 0
        for i in range(width - 1, -1, -1):
            if np.any(pixels[:, i] < threshold):
                right = width - i - 1
                break

        # Convert to reasonable scale (assuming ~150 DPI rendering)
        # and typical slide dimensions
        scale = 72 / 150  # Convert from 150 DPI to 72 DPI (points)

        return {
            "top": int(top * scale),
            "right": int(right * scale),
            "bottom": int(bottom * scale),
            "left": int(left * scale),
        }

    def _determine_grid_unit(self, doc: ParsedDocument) -> str:
        """Determine the grid unit from spacing patterns."""
        # Analyze font sizes for common factors
        sizes = []
        for page in doc.pages:
            for run in page.text_runs:
                if run.font_size and run.font_size > 0:
                    sizes.append(int(run.font_size))

        if not sizes:
            return "8px"

        # Find GCD-like common factor
        size_diffs = []
        sorted_sizes = sorted(set(sizes))
        for i in range(len(sorted_sizes) - 1):
            diff = sorted_sizes[i + 1] - sorted_sizes[i]
            if diff > 0:
                size_diffs.append(diff)

        if size_diffs:
            # Find most common difference
            common_diff = Counter(size_diffs).most_common(1)[0][0]
            # Round to common grid units
            if common_diff <= 4:
                return "4px"
            elif common_diff <= 8:
                return "8px"
            elif common_diff <= 12:
                return "12px"
            else:
                return "16px"

        return "8px"

    def _determine_grid_settings(self, doc: ParsedDocument) -> tuple:
        """Determine max width and column count."""
        # Default settings
        max_width = "1200px"
        columns = 12

        # Check for rendered pages to estimate content width
        rendered_pages = doc.get_rendered_pages()
        if rendered_pages:
            # Use first page dimensions as reference
            first_page = rendered_pages[0]
            aspect_ratio = first_page.width / first_page.height

            # Widescreen (16:9) suggests different max width
            if aspect_ratio > 1.5:
                max_width = "1400px"
            elif aspect_ratio < 0.8:
                # Portrait document
                max_width = "800px"
                columns = 6

        return max_width, columns

    def _calculate_confidence(self, doc: ParsedDocument) -> float:
        """Calculate confidence score for layout analysis."""
        confidence = 0.0

        # Rendered pages available
        rendered_pages = doc.get_rendered_pages()
        if rendered_pages:
            confidence += 0.5
            if len(rendered_pages) >= 3:
                confidence += 0.2

        # Font size data available
        sizes_found = sum(1 for p in doc.pages for r in p.text_runs if r.font_size)
        if sizes_found > 5:
            confidence += 0.3
        elif sizes_found > 0:
            confidence += 0.15

        return min(1.0, confidence)
