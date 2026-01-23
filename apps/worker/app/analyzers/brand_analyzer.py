import json
from typing import Dict, Any
import structlog

from app.parsers.base import ParsedDocument
from app.analyzers.color_analyzer import ColorAnalyzer
from app.analyzers.typography_analyzer import TypographyAnalyzer
from app.analyzers.layout_analyzer import LayoutAnalyzer
from app.providers import get_tone_provider, get_vision_provider

logger = structlog.get_logger()


class BrandAnalyzer:
    """Main analyzer that combines all analysis components."""

    def __init__(self):
        self.color_analyzer = ColorAnalyzer()
        self.typography_analyzer = TypographyAnalyzer()
        self.layout_analyzer = LayoutAnalyzer()
        self.tone_provider = get_tone_provider()
        self.vision_provider = get_vision_provider()

    def analyze(self, doc: ParsedDocument, brand_name: str = "Unknown Brand") -> Dict[str, Any]:
        """Perform complete brand analysis on a document."""
        logger.info("Starting brand analysis", brand=brand_name)

        # Run analyzers
        colors = self.color_analyzer.analyze(doc)
        typography = self.typography_analyzer.analyze(doc)
        layout = self.layout_analyzer.analyze(doc)

        # Analyze tone from text
        all_text = doc.get_all_text()
        tone = self.tone_provider.analyze_tone(all_text)

        # Analyze imagery style
        images = doc.get_rendered_pages() or doc.get_all_images()
        imagery = self.vision_provider.analyze_imagery(images)

        # Build profile
        profile = {
            "identity": {
                "name": brand_name,
                "sources": [doc.filename] if doc.filename else [],
            },
            "colors": {
                "primary": colors.get("primary", {"hex": "#0066CC", "name": "Blue"}),
                "secondary": colors.get("secondary", []),
                "neutrals": colors.get("neutrals", []),
                "accent": colors.get("secondary", [{}])[0] if colors.get("secondary") else None,
            },
            "typography": {
                "heading_font": typography.get("heading_font", "Arial"),
                "body_font": typography.get("body_font", "Arial"),
                "scale": typography.get("scale", {}),
                "weights": typography.get("weights", {"normal": 400, "bold": 700}),
            },
            "layout_system": {
                "margins": layout.get("margins", {}),
                "grid_unit": layout.get("grid_unit", "8px"),
                "max_width": layout.get("max_width", "1200px"),
                "columns": layout.get("columns", 12),
            },
            "imagery": {
                "photo_vs_illustration": imagery.get("style", "mixed"),
                "motifs": imagery.get("motifs", []),
                "mood": imagery.get("mood", []),
                "style_notes": imagery.get("notes"),
            },
            "tone_of_voice": {
                "attributes": tone.get("attributes", []),
                "do": tone.get("do", []),
                "dont": tone.get("dont", []),
                "example_phrases": tone.get("example_phrases", []),
            },
            "confidence": {
                "colors": colors.get("confidence", 0.0),
                "typography": typography.get("confidence", 0.0),
                "layout": layout.get("confidence", 0.0),
                "imagery": imagery.get("confidence", 0.0),
                "tone": tone.get("confidence", 0.0),
            },
        }

        logger.info(
            "Brand analysis complete",
            brand=brand_name,
            primary_color=profile["colors"]["primary"].get("hex"),
            heading_font=profile["typography"]["heading_font"],
        )

        return profile

    def generate_summary(self, profile: Dict[str, Any]) -> str:
        """Generate a markdown summary of the brand profile."""
        summary = []

        # Header
        brand_name = profile.get("identity", {}).get("name", "Brand")
        summary.append(f"# {brand_name} Brand Profile\n")

        # Colors
        summary.append("## Colors\n")
        colors = profile.get("colors", {})
        if colors.get("primary"):
            summary.append(f"**Primary:** {colors['primary'].get('hex', 'N/A')} ({colors['primary'].get('name', '')})\n")
        if colors.get("secondary"):
            sec_colors = ", ".join([c.get("hex", "") for c in colors["secondary"] if c])
            summary.append(f"**Secondary:** {sec_colors}\n")
        if colors.get("neutrals"):
            neu_colors = ", ".join([c.get("hex", "") for c in colors["neutrals"] if c])
            summary.append(f"**Neutrals:** {neu_colors}\n")

        # Typography
        summary.append("\n## Typography\n")
        typo = profile.get("typography", {})
        summary.append(f"**Heading Font:** {typo.get('heading_font', 'N/A')}\n")
        summary.append(f"**Body Font:** {typo.get('body_font', 'N/A')}\n")
        if typo.get("scale"):
            scale = typo["scale"]
            summary.append(f"**Scale:** H1: {scale.get('h1', 'N/A')}, H2: {scale.get('h2', 'N/A')}, Body: {scale.get('body', 'N/A')}\n")

        # Layout
        summary.append("\n## Layout\n")
        layout = profile.get("layout_system", {})
        summary.append(f"**Grid Unit:** {layout.get('grid_unit', '8px')}\n")
        summary.append(f"**Max Width:** {layout.get('max_width', '1200px')}\n")
        summary.append(f"**Columns:** {layout.get('columns', 12)}\n")

        # Tone of Voice
        summary.append("\n## Tone of Voice\n")
        tone = profile.get("tone_of_voice", {})
        if tone.get("attributes"):
            summary.append(f"**Attributes:** {', '.join(tone['attributes'])}\n")
        if tone.get("do"):
            summary.append("\n**Do:**\n")
            for item in tone["do"]:
                summary.append(f"- {item}\n")
        if tone.get("dont"):
            summary.append("\n**Don't:**\n")
            for item in tone["dont"]:
                summary.append(f"- {item}\n")

        # Imagery
        summary.append("\n## Imagery\n")
        imagery = profile.get("imagery", {})
        summary.append(f"**Style:** {imagery.get('photo_vs_illustration', 'mixed')}\n")
        if imagery.get("mood"):
            summary.append(f"**Mood:** {', '.join(imagery['mood'])}\n")
        if imagery.get("motifs"):
            summary.append(f"**Motifs:** {', '.join(imagery['motifs'])}\n")

        # Confidence Scores
        summary.append("\n## Analysis Confidence\n")
        confidence = profile.get("confidence", {})
        for key, value in confidence.items():
            bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
            summary.append(f"**{key.capitalize()}:** {bar} {value:.0%}\n")

        return "".join(summary)
