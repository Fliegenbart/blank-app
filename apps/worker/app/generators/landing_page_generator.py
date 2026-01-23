import io
import zipfile
from typing import Dict, Any, List, Optional
import structlog

from app.providers.content_provider import get_content_provider

logger = structlog.get_logger()


class LandingPageGenerator:
    """Generates landing page output based on brand profile and reference structure."""

    def __init__(self):
        self.content_provider = get_content_provider()

    def generate(
        self,
        profile: Dict[str, Any],
        topic: str,
        reference_structure: Optional[Dict[str, Any]] = None,
        sections: Optional[List[str]] = None,
    ) -> bytes:
        """Generate a landing page zip file."""
        logger.info("Generating landing page", topic=topic, has_reference=bool(reference_structure))

        # Generate content using AI
        content = self.content_provider.generate_landing_page_content(
            profile, topic, reference_structure, sections
        )

        # Create zip in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Generate CSS tokens
            css_tokens = self._generate_css_tokens(profile)
            zf.writestr("tokens.css", css_tokens)

            # Generate base styles
            base_css = self._generate_base_styles(profile)
            zf.writestr("styles.css", base_css)

            # Generate HTML page
            html = self._generate_html(profile, content)
            zf.writestr("index.html", html)

            # Generate README
            readme = self._generate_readme(profile, topic, content)
            zf.writestr("README.md", readme)

            # Generate content.json for reference
            import json
            zf.writestr("content.json", json.dumps(content, indent=2))

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _generate_css_tokens(self, profile: Dict[str, Any]) -> str:
        """Generate CSS custom properties from brand profile."""
        colors = profile.get("colors", {})
        typography = profile.get("typography", {})
        layout = profile.get("layout_system", {})

        css_lines = [":root {", "  /* Colors */"]

        # Primary color
        primary = colors.get("primary", {})
        css_lines.append(f"  --color-primary: {primary.get('hex', '#0066CC')};")
        css_lines.append(f"  --color-primary-light: {self._lighten_color(primary.get('hex', '#0066CC'))};")
        css_lines.append(f"  --color-primary-dark: {self._darken_color(primary.get('hex', '#0066CC'))};")

        # Secondary colors
        secondary = colors.get("secondary", [])
        for i, color in enumerate(secondary[:3]):
            if color and color.get("hex"):
                css_lines.append(f"  --color-secondary-{i+1}: {color['hex']};")

        # Neutral colors
        neutrals = colors.get("neutrals", [])
        for i, color in enumerate(neutrals[:5]):
            if color and color.get("hex"):
                css_lines.append(f"  --color-neutral-{i+1}: {color['hex']};")

        css_lines.append("")
        css_lines.append("  /* Typography */")
        css_lines.append(f"  --font-heading: '{typography.get('heading_font', 'Inter')}', system-ui, sans-serif;")
        css_lines.append(f"  --font-body: '{typography.get('body_font', 'Inter')}', system-ui, sans-serif;")

        # Font scale
        scale = typography.get("scale", {})
        css_lines.append(f"  --font-size-h1: {scale.get('h1', 'clamp(2.5rem, 5vw, 4rem)')};")
        css_lines.append(f"  --font-size-h2: {scale.get('h2', 'clamp(2rem, 4vw, 3rem)')};")
        css_lines.append(f"  --font-size-h3: {scale.get('h3', 'clamp(1.5rem, 3vw, 2rem)')};")
        css_lines.append(f"  --font-size-body: {scale.get('body', '1rem')};")
        css_lines.append(f"  --font-size-large: {scale.get('large', '1.25rem')};")
        css_lines.append(f"  --font-size-small: {scale.get('small', '0.875rem')};")

        css_lines.append("")
        css_lines.append("  /* Spacing */")
        margins = layout.get("margins", {})
        css_lines.append(f"  --spacing-xs: 0.5rem;")
        css_lines.append(f"  --spacing-sm: 1rem;")
        css_lines.append(f"  --spacing-md: 2rem;")
        css_lines.append(f"  --spacing-lg: 4rem;")
        css_lines.append(f"  --spacing-xl: 8rem;")
        css_lines.append(f"  --max-width: {layout.get('max_width', '1200px')};")

        css_lines.append("")
        css_lines.append("  /* Effects */")
        css_lines.append("  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);")
        css_lines.append("  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);")
        css_lines.append("  --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.15);")
        css_lines.append("  --radius-sm: 4px;")
        css_lines.append("  --radius-md: 8px;")
        css_lines.append("  --radius-lg: 16px;")

        css_lines.append("}")

        return "\n".join(css_lines)

    def _lighten_color(self, hex_color: str) -> str:
        """Lighten a hex color by 20%."""
        try:
            hex_color = hex_color.lstrip('#')
            r = min(255, int(hex_color[0:2], 16) + 40)
            g = min(255, int(hex_color[2:4], 16) + 40)
            b = min(255, int(hex_color[4:6], 16) + 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#4d8fd6"

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 20%."""
        try:
            hex_color = hex_color.lstrip('#')
            r = max(0, int(hex_color[0:2], 16) - 40)
            g = max(0, int(hex_color[2:4], 16) - 40)
            b = max(0, int(hex_color[4:6], 16) - 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#003d7a"

    def _generate_base_styles(self, profile: Dict[str, Any]) -> str:
        """Generate base CSS styles."""
        return """/* Base Styles */
@import url('tokens.css');

*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  line-height: 1.6;
  color: var(--color-neutral-1, #333);
  background-color: var(--color-neutral-5, #fff);
}

.container {
  width: 100%;
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 var(--spacing-sm);
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: var(--spacing-sm);
}

h1 { font-size: var(--font-size-h1); }
h2 { font-size: var(--font-size-h2); }
h3 { font-size: var(--font-size-h3); }

p {
  margin-bottom: var(--spacing-sm);
}

a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s ease;
}

a:hover {
  color: var(--color-primary-dark);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-sm) var(--spacing-md);
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  font-weight: 600;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}

.btn-secondary:hover {
  background-color: var(--color-primary);
  color: white;
}

.btn-white {
  background-color: white;
  color: var(--color-primary);
}

.btn-white:hover {
  background-color: var(--color-neutral-5, #f5f5f5);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* Sections */
section {
  padding: var(--spacing-xl) 0;
}

.section-header {
  text-align: center;
  max-width: 800px;
  margin: 0 auto var(--spacing-lg);
}

.section-header p {
  font-size: var(--font-size-large);
  color: var(--color-neutral-2, #666);
}

/* Hero Section */
.hero {
  min-height: 80vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  text-align: center;
}

.hero h1 {
  margin-bottom: var(--spacing-md);
}

.hero p {
  font-size: var(--font-size-large);
  max-width: 600px;
  margin: 0 auto var(--spacing-md);
  opacity: 0.9;
}

.hero .btn-group {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: center;
  flex-wrap: wrap;
}

/* Features Section */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-md);
}

.feature-card {
  padding: var(--spacing-md);
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.feature-card h3 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-xs);
}

.feature-card p {
  color: var(--color-neutral-2, #666);
  margin: 0;
}

/* Testimonials */
.testimonials {
  background-color: var(--color-neutral-5, #f9f9f9);
}

.testimonial-card {
  background: white;
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.testimonial-card blockquote {
  font-size: var(--font-size-large);
  font-style: italic;
  color: var(--color-neutral-1, #333);
  margin-bottom: var(--spacing-sm);
}

.testimonial-card cite {
  color: var(--color-neutral-2, #666);
  font-style: normal;
}

/* CTA Section */
.cta-section {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  text-align: center;
}

.cta-section h2,
.cta-section p {
  color: white;
}

.cta-section p {
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto var(--spacing-md);
}

/* Footer */
footer {
  background-color: var(--color-neutral-1, #333);
  color: white;
  padding: var(--spacing-lg) 0;
  text-align: center;
}

footer p {
  margin: 0;
  opacity: 0.8;
}

footer a {
  color: white;
  opacity: 0.8;
}

footer a:hover {
  opacity: 1;
}

/* Responsive */
@media (max-width: 768px) {
  section {
    padding: var(--spacing-lg) 0;
  }

  .hero {
    min-height: 60vh;
  }
}
"""

    def _generate_html(self, profile: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate HTML page from content."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        title = content.get("title", f"{brand_name} Landing Page")
        meta_desc = content.get("meta_description", "")
        sections = content.get("sections", [])

        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'  <meta name="description" content="{meta_desc}">',
            f"  <title>{title}</title>",
            '  <link rel="stylesheet" href="styles.css">',
            "</head>",
            "<body>",
        ]

        # Generate each section
        for section in sections:
            section_html = self._generate_section_html(section)
            html_parts.append(section_html)

        # Footer
        html_parts.extend([
            "  <footer>",
            "    <div class=\"container\">",
            f"      <p>&copy; 2025 {brand_name}. All rights reserved.</p>",
            "    </div>",
            "  </footer>",
            "</body>",
            "</html>",
        ])

        return "\n".join(html_parts)

    def _generate_section_html(self, section: Dict[str, Any]) -> str:
        """Generate HTML for a single section."""
        section_type = section.get("type", "content")

        if section_type == "hero":
            return self._generate_hero_html(section)
        elif section_type == "features":
            return self._generate_features_html(section)
        elif section_type == "testimonials":
            return self._generate_testimonials_html(section)
        elif section_type == "cta":
            return self._generate_cta_html(section)
        else:
            return self._generate_content_html(section)

    def _generate_hero_html(self, section: Dict[str, Any]) -> str:
        """Generate hero section HTML."""
        heading = section.get("heading", "Welcome")
        subheading = section.get("subheading", "")
        cta_text = section.get("cta_text", "Get Started")
        cta_url = section.get("cta_url", "#")

        return f"""  <section class="hero">
    <div class="container">
      <h1>{heading}</h1>
      <p>{subheading}</p>
      <div class="btn-group">
        <a href="{cta_url}" class="btn btn-white">{cta_text}</a>
        <a href="#features" class="btn btn-secondary" style="border-color: white; color: white;">Learn More</a>
      </div>
    </div>
  </section>"""

    def _generate_features_html(self, section: Dict[str, Any]) -> str:
        """Generate features section HTML."""
        heading = section.get("heading", "Features")
        items = section.get("items", [])

        features_html = []
        for item in items:
            features_html.append(f"""        <div class="feature-card">
          <h3>{item.get('title', '')}</h3>
          <p>{item.get('description', '')}</p>
        </div>""")

        return f"""  <section id="features">
    <div class="container">
      <div class="section-header">
        <h2>{heading}</h2>
      </div>
      <div class="features-grid">
{chr(10).join(features_html)}
      </div>
    </div>
  </section>"""

    def _generate_testimonials_html(self, section: Dict[str, Any]) -> str:
        """Generate testimonials section HTML."""
        heading = section.get("heading", "What Our Customers Say")
        items = section.get("items", [])

        testimonials_html = []
        for item in items:
            testimonials_html.append(f"""        <div class="testimonial-card">
          <blockquote>"{item.get('quote', '')}"</blockquote>
          <cite>— {item.get('author', 'Customer')}</cite>
        </div>""")

        return f"""  <section class="testimonials">
    <div class="container">
      <div class="section-header">
        <h2>{heading}</h2>
      </div>
      <div class="features-grid">
{chr(10).join(testimonials_html)}
      </div>
    </div>
  </section>"""

    def _generate_cta_html(self, section: Dict[str, Any]) -> str:
        """Generate CTA section HTML."""
        heading = section.get("heading", "Ready to Get Started?")
        subheading = section.get("subheading", "")
        cta_text = section.get("cta_text", "Start Now")
        cta_url = section.get("cta_url", "#")

        return f"""  <section class="cta-section">
    <div class="container">
      <h2>{heading}</h2>
      <p>{subheading}</p>
      <a href="{cta_url}" class="btn btn-white">{cta_text}</a>
    </div>
  </section>"""

    def _generate_content_html(self, section: Dict[str, Any]) -> str:
        """Generate generic content section HTML."""
        heading = section.get("heading", "")
        content = section.get("content", [])

        content_html = "\n".join([f"      <p>{p}</p>" for p in content])

        return f"""  <section>
    <div class="container">
      <div class="section-header">
        <h2>{heading}</h2>
      </div>
{content_html}
    </div>
  </section>"""

    def _generate_readme(self, profile: Dict[str, Any], topic: str, content: Dict[str, Any]) -> str:
        """Generate README for the landing page output."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        sections = content.get("sections", [])
        section_types = [s.get("type", "unknown") for s in sections]

        return f"""# {brand_name} Landing Page

Generated landing page for "{topic}"

## Files

- `index.html` - Main landing page
- `styles.css` - Base styles
- `tokens.css` - CSS custom properties (design tokens)
- `content.json` - Generated content data

## Sections

{chr(10).join([f"- {s}" for s in section_types])}

## Brand Profile Applied

- **Primary Color:** {profile.get('colors', {}).get('primary', {}).get('hex', 'N/A')}
- **Heading Font:** {profile.get('typography', {}).get('heading_font', 'N/A')}
- **Body Font:** {profile.get('typography', {}).get('body_font', 'N/A')}

## Usage

1. Open `index.html` in a browser to preview
2. Customize content in the HTML as needed
3. Modify `tokens.css` to adjust brand colors/fonts
4. Deploy to your hosting platform

## Customization

### Changing Colors
Edit `tokens.css` and update the color variables:
```css
--color-primary: #your-color;
--color-primary-light: #lighter-shade;
--color-primary-dark: #darker-shade;
```

### Changing Fonts
Update the font-family variables in `tokens.css`:
```css
--font-heading: 'Your Heading Font', sans-serif;
--font-body: 'Your Body Font', sans-serif;
```
"""
