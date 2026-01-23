from typing import Dict, List, Optional
from collections import Counter
import structlog

from app.parsers.base import ParsedDocument

logger = structlog.get_logger()


class TypographyAnalyzer:
    """Analyzes typography from documents."""

    # Common font mappings (embedded font names -> display names)
    FONT_NAME_MAP = {
        "arial": "Arial",
        "helvetica": "Helvetica",
        "times": "Times New Roman",
        "timesnewroman": "Times New Roman",
        "georgia": "Georgia",
        "verdana": "Verdana",
        "tahoma": "Tahoma",
        "trebuchet": "Trebuchet MS",
        "calibri": "Calibri",
        "cambria": "Cambria",
        "segoe": "Segoe UI",
        "roboto": "Roboto",
        "opensans": "Open Sans",
        "lato": "Lato",
        "montserrat": "Montserrat",
        "sourcesans": "Source Sans Pro",
        "nunito": "Nunito",
        "poppins": "Poppins",
        "inter": "Inter",
        "playfair": "Playfair Display",
    }

    def analyze(self, doc: ParsedDocument) -> Dict:
        """Analyze typography from a parsed document."""
        logger.info("Analyzing typography")

        # Collect font data
        fonts_from_theme = self._extract_theme_fonts(doc)
        fonts_from_text = self._extract_text_fonts(doc)
        sizes_from_text = self._extract_font_sizes(doc)

        # Determine heading and body fonts
        heading_font = self._determine_heading_font(fonts_from_theme, fonts_from_text, sizes_from_text)
        body_font = self._determine_body_font(fonts_from_theme, fonts_from_text, sizes_from_text, heading_font)

        # Determine scale
        scale = self._determine_scale(sizes_from_text)

        # Determine weights
        weights = self._determine_weights(doc)

        # Calculate confidence
        confidence = self._calculate_confidence(doc, heading_font, body_font)

        result = {
            "heading_font": heading_font,
            "body_font": body_font,
            "scale": scale,
            "weights": weights,
            "confidence": confidence,
        }

        logger.info(
            "Typography analysis complete",
            heading=heading_font,
            body=body_font,
        )

        return result

    def _extract_theme_fonts(self, doc: ParsedDocument) -> Dict[str, str]:
        """Extract fonts from document theme."""
        fonts = {}
        if doc.theme and doc.theme.font_scheme:
            fonts = doc.theme.font_scheme.copy()
        return fonts

    def _extract_text_fonts(self, doc: ParsedDocument) -> Counter:
        """Extract and count fonts from text runs."""
        font_counter = Counter()
        for page in doc.pages:
            for run in page.text_runs:
                if run.font_name:
                    normalized = self._normalize_font_name(run.font_name)
                    if normalized:
                        font_counter[normalized] += len(run.text)
        return font_counter

    def _extract_font_sizes(self, doc: ParsedDocument) -> List[Dict]:
        """Extract font sizes with their associated fonts."""
        sizes = []
        for page in doc.pages:
            for run in page.text_runs:
                if run.font_size and run.font_size > 0:
                    sizes.append({
                        "size": run.font_size,
                        "font": self._normalize_font_name(run.font_name),
                        "text_length": len(run.text),
                        "text": run.text[:50],  # Sample for context
                    })
        return sizes

    def _normalize_font_name(self, font_name: Optional[str]) -> Optional[str]:
        """Normalize font name to standard form."""
        if not font_name:
            return None

        # Clean up the name
        clean = font_name.lower().replace(" ", "").replace("-", "").replace("_", "")

        # Remove common suffixes
        for suffix in ["regular", "bold", "italic", "light", "medium", "semibold", "black"]:
            clean = clean.replace(suffix, "")

        # Try to match known fonts
        for key, value in self.FONT_NAME_MAP.items():
            if key in clean:
                return value

        # Return original name with basic cleanup
        return font_name.split("-")[0].split(",")[0].strip()

    def _determine_heading_font(
        self,
        theme_fonts: Dict[str, str],
        text_fonts: Counter,
        sizes: List[Dict],
    ) -> str:
        """Determine the heading font."""
        # Priority 1: Theme heading font
        if theme_fonts.get("heading"):
            return theme_fonts["heading"]

        # Priority 2: Font used at larger sizes
        large_size_fonts = Counter()
        if sizes:
            avg_size = sum(s["size"] for s in sizes) / len(sizes)
            for s in sizes:
                if s["size"] > avg_size * 1.2 and s["font"]:
                    large_size_fonts[s["font"]] += s["text_length"]

        if large_size_fonts:
            return large_size_fonts.most_common(1)[0][0]

        # Priority 3: Most common font
        if text_fonts:
            return text_fonts.most_common(1)[0][0]

        # Default
        return "Arial"

    def _determine_body_font(
        self,
        theme_fonts: Dict[str, str],
        text_fonts: Counter,
        sizes: List[Dict],
        heading_font: str,
    ) -> str:
        """Determine the body font."""
        # Priority 1: Theme body font
        if theme_fonts.get("body"):
            return theme_fonts["body"]

        # Priority 2: Font used at smaller/medium sizes
        body_size_fonts = Counter()
        if sizes:
            avg_size = sum(s["size"] for s in sizes) / len(sizes)
            for s in sizes:
                if s["size"] <= avg_size * 1.2 and s["font"]:
                    body_size_fonts[s["font"]] += s["text_length"]

        if body_size_fonts:
            most_common = body_size_fonts.most_common(2)
            # Prefer different font from heading if available
            for font, count in most_common:
                if font != heading_font:
                    return font
            return most_common[0][0]

        # Priority 3: Second most common font or same as heading
        if text_fonts:
            common = text_fonts.most_common(2)
            if len(common) > 1 and common[1][0] != heading_font:
                return common[1][0]
            return heading_font

        # Default
        return "Arial"

    def _determine_scale(self, sizes: List[Dict]) -> Dict[str, str]:
        """Determine the typography scale."""
        default_scale = {
            "h1": "48px",
            "h2": "36px",
            "h3": "24px",
            "body": "16px",
            "caption": "12px",
        }

        if not sizes:
            return default_scale

        # Get unique sizes and sort
        unique_sizes = sorted(set(s["size"] for s in sizes), reverse=True)

        if len(unique_sizes) < 2:
            return default_scale

        # Map sizes to scale levels
        scale = {}

        # H1: largest
        if unique_sizes:
            scale["h1"] = f"{int(unique_sizes[0])}px"

        # H2: second largest
        if len(unique_sizes) > 1:
            scale["h2"] = f"{int(unique_sizes[1])}px"

        # H3: third largest or interpolate
        if len(unique_sizes) > 2:
            scale["h3"] = f"{int(unique_sizes[2])}px"
        elif len(unique_sizes) > 1:
            scale["h3"] = f"{int((unique_sizes[0] + unique_sizes[1]) / 3)}px"

        # Body: most common size
        size_counts = Counter(s["size"] for s in sizes)
        most_common_size = size_counts.most_common(1)[0][0]
        scale["body"] = f"{int(most_common_size)}px"

        # Caption: smallest or 75% of body
        if unique_sizes:
            smallest = min(unique_sizes)
            scale["caption"] = f"{int(smallest * 0.85)}px"

        return scale

    def _determine_weights(self, doc: ParsedDocument) -> Dict[str, int]:
        """Determine font weights used."""
        weights = {"normal": 400, "bold": 700}

        bold_found = False
        for page in doc.pages:
            for run in page.text_runs:
                if run.bold:
                    bold_found = True
                    break

        if not bold_found:
            weights["bold"] = 600  # Semibold if no true bold found

        return weights

    def _calculate_confidence(self, doc: ParsedDocument, heading_font: str, body_font: str) -> float:
        """Calculate confidence score for typography analysis."""
        confidence = 0.0

        # Theme data available
        if doc.theme and doc.theme.font_scheme:
            confidence += 0.4

        # Font data found in text
        fonts_found = sum(1 for p in doc.pages for r in p.text_runs if r.font_name)
        if fonts_found > 10:
            confidence += 0.3
        elif fonts_found > 0:
            confidence += 0.15

        # Size data found
        sizes_found = sum(1 for p in doc.pages for r in p.text_runs if r.font_size)
        if sizes_found > 10:
            confidence += 0.3
        elif sizes_found > 0:
            confidence += 0.15

        return min(1.0, confidence)
