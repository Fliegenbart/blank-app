import io
from typing import List, Dict, Tuple, Optional
from collections import Counter
import structlog
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from app.parsers.base import ParsedDocument, ExtractedImage

logger = structlog.get_logger()


class ColorAnalyzer:
    """Analyzes colors from documents."""

    def __init__(self, n_clusters: int = 8):
        self.n_clusters = n_clusters

    def analyze(self, doc: ParsedDocument) -> Dict:
        """Analyze colors from a parsed document."""
        logger.info("Analyzing colors")

        colors_from_theme = self._extract_theme_colors(doc)
        colors_from_text = self._extract_text_colors(doc)
        colors_from_images = self._extract_image_colors(doc)

        # Combine all color sources
        all_colors = []
        all_colors.extend(colors_from_theme)
        all_colors.extend(colors_from_text)
        all_colors.extend(colors_from_images)

        # Determine primary, secondary, and neutral colors
        result = self._categorize_colors(all_colors, doc)

        logger.info(
            "Color analysis complete",
            primary=result.get("primary", {}).get("hex"),
            secondary_count=len(result.get("secondary", [])),
        )

        return result

    def _extract_theme_colors(self, doc: ParsedDocument) -> List[str]:
        """Extract colors from document theme."""
        colors = []
        if doc.theme:
            colors.extend(doc.theme.color_scheme.values())
            colors.extend(doc.theme.accent_colors)
        return [c for c in colors if c and c.startswith("#")]

    def _extract_text_colors(self, doc: ParsedDocument) -> List[str]:
        """Extract colors from text formatting."""
        colors = []
        for page in doc.pages:
            for run in page.text_runs:
                if run.font_color and run.font_color.startswith("#"):
                    colors.append(run.font_color)
        return colors

    def _extract_image_colors(self, doc: ParsedDocument) -> List[str]:
        """Extract dominant colors from images using KMeans clustering."""
        colors = []

        # Use rendered pages if available
        images_to_analyze = doc.get_rendered_pages() or doc.get_all_images()

        for img in images_to_analyze[:5]:  # Limit to 5 images for performance
            try:
                extracted = self._extract_colors_from_image(img.data)
                colors.extend(extracted)
            except Exception as e:
                logger.warning("Error extracting colors from image", error=str(e))

        return colors

    def _extract_colors_from_image(self, img_data: bytes) -> List[str]:
        """Extract dominant colors from a single image."""
        img = Image.open(io.BytesIO(img_data))

        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Resize for performance
        img.thumbnail((200, 200))

        # Get pixel data
        pixels = np.array(img).reshape(-1, 3)

        # Filter out near-white and near-black pixels
        mask = ~(
            ((pixels[:, 0] > 240) & (pixels[:, 1] > 240) & (pixels[:, 2] > 240)) |
            ((pixels[:, 0] < 15) & (pixels[:, 1] < 15) & (pixels[:, 2] < 15))
        )
        filtered_pixels = pixels[mask]

        if len(filtered_pixels) < self.n_clusters:
            return []

        # Cluster colors
        kmeans = KMeans(n_clusters=min(self.n_clusters, len(filtered_pixels)), random_state=42, n_init=10)
        kmeans.fit(filtered_pixels)

        # Convert cluster centers to hex
        colors = []
        for center in kmeans.cluster_centers_:
            r, g, b = int(center[0]), int(center[1]), int(center[2])
            colors.append(f"#{r:02x}{g:02x}{b:02x}")

        return colors

    def _categorize_colors(self, all_colors: List[str], doc: ParsedDocument) -> Dict:
        """Categorize colors into primary, secondary, and neutrals."""
        if not all_colors:
            return self._get_default_colors()

        # Count color occurrences
        color_counts = Counter(all_colors)

        # Convert to HSL for better categorization
        colors_with_hsl = []
        for color, count in color_counts.items():
            try:
                hsl = self._hex_to_hsl(color)
                colors_with_hsl.append((color, count, hsl))
            except Exception:
                continue

        if not colors_with_hsl:
            return self._get_default_colors()

        # Separate into chromatic and neutral
        chromatic = []
        neutrals = []

        for color, count, (h, s, l) in colors_with_hsl:
            if s < 0.15 or l > 0.9 or l < 0.1:
                neutrals.append((color, count))
            else:
                chromatic.append((color, count, (h, s, l)))

        # Sort chromatic by saturation and count
        chromatic.sort(key=lambda x: (x[1], x[2][1]), reverse=True)

        # Determine primary color
        # Prefer theme colors or most frequent chromatic color
        primary_color = None
        if doc.theme and doc.theme.accent_colors:
            primary_color = doc.theme.accent_colors[0]
        elif chromatic:
            primary_color = chromatic[0][0]

        if not primary_color:
            primary_color = "#0066CC"  # Default blue

        # Secondary colors (different hues from primary)
        primary_hue = self._hex_to_hsl(primary_color)[0]
        secondary = []
        for color, count, (h, s, l) in chromatic[1:]:
            # Different hue from primary
            hue_diff = abs(h - primary_hue)
            if hue_diff > 30 or hue_diff < 330:
                secondary.append({"hex": color, "name": None, "usage": None})
                if len(secondary) >= 3:
                    break

        # Sort neutrals by lightness
        neutral_colors = []
        neutrals.sort(key=lambda x: self._hex_to_hsl(x[0])[2])
        for color, count in neutrals[:4]:
            neutral_colors.append({"hex": color, "name": None, "usage": None})

        # Confidence based on data quality
        confidence = min(1.0, len(all_colors) / 20) * (0.8 if doc.theme else 0.5)

        return {
            "primary": {"hex": primary_color, "name": self._get_color_name(primary_color), "usage": "primary"},
            "secondary": secondary or [{"hex": "#FF6600", "name": "Orange", "usage": "accent"}],
            "neutrals": neutral_colors or [{"hex": "#333333"}, {"hex": "#666666"}, {"hex": "#F5F5F5"}],
            "confidence": confidence,
        }

    def _hex_to_hsl(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to HSL."""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))

        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2

        if max_c == min_c:
            h = s = 0
        else:
            d = max_c - min_c
            s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)

            if max_c == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_c == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4

            h = h * 60

        return h, s, l

    def _get_color_name(self, hex_color: str) -> Optional[str]:
        """Get a simple name for a color based on hue."""
        h, s, l = self._hex_to_hsl(hex_color)

        if s < 0.1:
            if l > 0.9:
                return "White"
            elif l < 0.1:
                return "Black"
            else:
                return "Gray"

        # Basic hue names
        if h < 30 or h >= 330:
            return "Red"
        elif h < 60:
            return "Orange"
        elif h < 90:
            return "Yellow"
        elif h < 150:
            return "Green"
        elif h < 210:
            return "Cyan"
        elif h < 270:
            return "Blue"
        elif h < 330:
            return "Purple"

        return None

    def _get_default_colors(self) -> Dict:
        """Return default color scheme when analysis fails."""
        return {
            "primary": {"hex": "#0066CC", "name": "Blue", "usage": "primary"},
            "secondary": [{"hex": "#FF6600", "name": "Orange", "usage": "accent"}],
            "neutrals": [{"hex": "#333333"}, {"hex": "#666666"}, {"hex": "#F5F5F5"}],
            "confidence": 0.0,
        }
