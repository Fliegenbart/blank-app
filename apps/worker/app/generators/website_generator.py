import io
import zipfile
from typing import Dict, Any, List
import structlog
from jinja2 import Template

from app.providers.tone_provider import get_tone_provider

logger = structlog.get_logger()


class WebsiteGenerator:
    """Generates website output based on brand profile."""

    def __init__(self):
        self.tone_provider = get_tone_provider()

    def generate(
        self,
        profile: Dict[str, Any],
        topic: str,
        pages: List[Dict[str, Any]],
        brief: str = None,
    ) -> bytes:
        """Generate a website zip file."""
        logger.info("Generating website", topic=topic, page_count=len(pages))

        # Create zip in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Generate CSS tokens
            css = self._generate_css_tokens(profile)
            zf.writestr("tokens.css", css)

            # Generate base styles
            base_css = self._generate_base_styles(profile)
            zf.writestr("styles.css", base_css)

            # Generate pages
            for page_config in pages:
                html = self._generate_page(profile, topic, page_config, brief)
                filename = f"{page_config.get('slug', 'page')}.html"
                zf.writestr(filename, html)

            # Generate README
            readme = self._generate_readme(profile, topic, pages)
            zf.writestr("README.md", readme)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _generate_css_tokens(self, profile: Dict[str, Any]) -> str:
        """Generate CSS custom properties from brand profile."""
        colors = profile.get("colors", {})
        typography = profile.get("typography", {})
        layout = profile.get("layout_system", {})

        css_lines = [
            ":root {",
            "  /* Colors */",
        ]

        # Primary color
        primary = colors.get("primary", {})
        css_lines.append(f"  --color-primary: {primary.get('hex', '#0066CC')};")

        # Secondary colors
        secondary = colors.get("secondary", [])
        for i, color in enumerate(secondary):
            if color and color.get("hex"):
                css_lines.append(f"  --color-secondary-{i+1}: {color['hex']};")

        # Neutral colors
        neutrals = colors.get("neutrals", [])
        for i, color in enumerate(neutrals):
            if color and color.get("hex"):
                css_lines.append(f"  --color-neutral-{i+1}: {color['hex']};")

        css_lines.append("")
        css_lines.append("  /* Typography */")
        css_lines.append(f"  --font-heading: '{typography.get('heading_font', 'Arial')}', sans-serif;")
        css_lines.append(f"  --font-body: '{typography.get('body_font', 'Arial')}', sans-serif;")

        # Font scale
        scale = typography.get("scale", {})
        css_lines.append(f"  --font-size-h1: {scale.get('h1', '48px')};")
        css_lines.append(f"  --font-size-h2: {scale.get('h2', '36px')};")
        css_lines.append(f"  --font-size-h3: {scale.get('h3', '24px')};")
        css_lines.append(f"  --font-size-body: {scale.get('body', '16px')};")
        css_lines.append(f"  --font-size-caption: {scale.get('caption', '12px')};")

        # Font weights
        weights = typography.get("weights", {})
        css_lines.append(f"  --font-weight-normal: {weights.get('normal', 400)};")
        css_lines.append(f"  --font-weight-bold: {weights.get('bold', 700)};")

        css_lines.append("")
        css_lines.append("  /* Layout */")
        margins = layout.get("margins", {})
        css_lines.append(f"  --spacing-page-top: {margins.get('top', '40px')};")
        css_lines.append(f"  --spacing-page-right: {margins.get('right', '40px')};")
        css_lines.append(f"  --spacing-page-bottom: {margins.get('bottom', '40px')};")
        css_lines.append(f"  --spacing-page-left: {margins.get('left', '40px')};")
        css_lines.append(f"  --grid-unit: {layout.get('grid_unit', '8px')};")
        css_lines.append(f"  --max-width: {layout.get('max_width', '1200px')};")

        css_lines.append("}")

        return "\n".join(css_lines)

    def _generate_base_styles(self, profile: Dict[str, Any]) -> str:
        """Generate base CSS styles."""
        return """/* Base Styles */
@import url('tokens.css');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  line-height: 1.6;
  color: var(--color-neutral-1, #333);
  background-color: var(--color-neutral-3, #fff);
}

.container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: var(--spacing-page-top) var(--spacing-page-right) var(--spacing-page-bottom) var(--spacing-page-left);
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  font-weight: var(--font-weight-bold);
  line-height: 1.2;
  margin-bottom: calc(var(--grid-unit) * 2);
}

h1 { font-size: var(--font-size-h1); }
h2 { font-size: var(--font-size-h2); }
h3 { font-size: var(--font-size-h3); }

p {
  margin-bottom: calc(var(--grid-unit) * 2);
}

a {
  color: var(--color-primary);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.btn {
  display: inline-block;
  padding: calc(var(--grid-unit) * 2) calc(var(--grid-unit) * 4);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: calc(var(--grid-unit) / 2);
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-bold);
  cursor: pointer;
  text-decoration: none;
}

.btn:hover {
  opacity: 0.9;
  text-decoration: none;
}

.hero {
  text-align: center;
  padding: calc(var(--grid-unit) * 8) 0;
  background-color: var(--color-neutral-3, #f5f5f5);
}

.hero h1 {
  margin-bottom: calc(var(--grid-unit) * 3);
}

.hero p {
  font-size: calc(var(--font-size-body) * 1.25);
  max-width: 600px;
  margin: 0 auto calc(var(--grid-unit) * 4);
}

.section {
  padding: calc(var(--grid-unit) * 6) 0;
}

.section h2 {
  text-align: center;
  margin-bottom: calc(var(--grid-unit) * 4);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: calc(var(--grid-unit) * 4);
}

.feature {
  text-align: center;
  padding: calc(var(--grid-unit) * 3);
}

.feature h3 {
  margin-bottom: calc(var(--grid-unit) * 2);
}

.cta {
  text-align: center;
  padding: calc(var(--grid-unit) * 8) 0;
  background-color: var(--color-primary);
  color: white;
}

.cta h2, .cta p {
  color: white;
}

.cta .btn {
  background-color: white;
  color: var(--color-primary);
}

footer {
  text-align: center;
  padding: calc(var(--grid-unit) * 4) 0;
  background-color: var(--color-neutral-1, #333);
  color: white;
  font-size: var(--font-size-caption);
}
"""

    def _generate_page(
        self,
        profile: Dict[str, Any],
        topic: str,
        page_config: Dict[str, Any],
        brief: str = None,
    ) -> str:
        """Generate an HTML page."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        page_title = page_config.get("title", topic)
        page_slug = page_config.get("slug", "index")
        sections = page_config.get("sections", ["hero", "features", "cta"])

        # Generate content based on tone
        tone = profile.get("tone_of_voice", {})
        attributes = tone.get("attributes", [])
        is_friendly = "friendly" in attributes or "casual" in attributes

        # Simple content generation
        headline = f"{topic}" if page_slug == "index" else page_title
        subheadline = self._generate_subheadline(topic, attributes)
        cta_text = "Get Started" if is_friendly else "Learn More"

        # Build HTML
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            "  <meta charset=\"UTF-8\">",
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
            f"  <title>{page_title} | {brand_name}</title>",
            "  <link rel=\"stylesheet\" href=\"styles.css\">",
            "</head>",
            "<body>",
        ]

        # Generate sections
        for section in sections:
            if section == "hero":
                html_parts.extend([
                    "  <section class=\"hero\">",
                    "    <div class=\"container\">",
                    f"      <h1>{headline}</h1>",
                    f"      <p>{subheadline}</p>",
                    f"      <a href=\"#\" class=\"btn\">{cta_text}</a>",
                    "    </div>",
                    "  </section>",
                ])
            elif section == "features":
                features = self._generate_features(topic, attributes)
                html_parts.extend([
                    "  <section class=\"section\">",
                    "    <div class=\"container\">",
                    "      <h2>Features</h2>",
                    "      <div class=\"features\">",
                ])
                for feature in features:
                    html_parts.extend([
                        "        <div class=\"feature\">",
                        f"          <h3>{feature['title']}</h3>",
                        f"          <p>{feature['description']}</p>",
                        "        </div>",
                    ])
                html_parts.extend([
                    "      </div>",
                    "    </div>",
                    "  </section>",
                ])
            elif section == "cta":
                html_parts.extend([
                    "  <section class=\"cta\">",
                    "    <div class=\"container\">",
                    f"      <h2>Ready to get started?</h2>",
                    f"      <p>Join thousands of satisfied customers.</p>",
                    f"      <a href=\"#\" class=\"btn\">{cta_text}</a>",
                    "    </div>",
                    "  </section>",
                ])

        html_parts.extend([
            "  <footer>",
            f"    <p>&copy; 2025 {brand_name}. All rights reserved.</p>",
            "  </footer>",
            "</body>",
            "</html>",
        ])

        return "\n".join(html_parts)

    def _generate_subheadline(self, topic: str, attributes: List[str]) -> str:
        """Generate a subheadline based on topic and tone."""
        if "innovative" in attributes:
            return f"Discover the future of {topic.lower()}."
        elif "trustworthy" in attributes:
            return f"The reliable solution for {topic.lower()}."
        elif "friendly" in attributes:
            return f"We make {topic.lower()} simple and enjoyable."
        else:
            return f"Your complete solution for {topic.lower()}."

    def _generate_features(self, topic: str, attributes: List[str]) -> List[Dict[str, str]]:
        """Generate feature content."""
        base_features = [
            {"title": "Easy to Use", "description": "Get started in minutes with our intuitive interface."},
            {"title": "Powerful Features", "description": "Everything you need to succeed, all in one place."},
            {"title": "Always Reliable", "description": "Count on us for consistent, dependable performance."},
        ]

        # Customize based on tone
        if "technical" in attributes:
            base_features[1]["description"] = "Advanced capabilities designed for power users."
        if "friendly" in attributes:
            base_features[0]["description"] = "So simple, you'll wonder how you lived without it!"

        return base_features

    def _generate_readme(self, profile: Dict[str, Any], topic: str, pages: List[Dict]) -> str:
        """Generate README for the website output."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        return f"""# {brand_name} Website

Generated website for "{topic}"

## Files

- `tokens.css` - CSS custom properties (design tokens) from brand profile
- `styles.css` - Base styles using the design tokens
- `*.html` - Generated HTML pages

## Pages Generated

{chr(10).join([f"- `{p.get('slug', 'page')}.html` - {p.get('title', 'Page')}" for p in pages])}

## Usage

1. Open `index.html` in a browser to preview
2. Customize content as needed
3. Deploy to your hosting platform

## Brand Profile Applied

- **Primary Color:** {profile.get('colors', {}).get('primary', {}).get('hex', 'N/A')}
- **Heading Font:** {profile.get('typography', {}).get('heading_font', 'N/A')}
- **Body Font:** {profile.get('typography', {}).get('body_font', 'N/A')}
"""
