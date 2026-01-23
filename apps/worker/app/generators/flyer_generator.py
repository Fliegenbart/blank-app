"""Flyer generator for theme assets."""
import io
import zipfile
from typing import Dict, Any
import structlog

from app.providers.content_provider import get_content_provider

logger = structlog.get_logger()


class FlyerGenerator:
    """Generates print-ready A4 flyer with bleed margins."""

    def __init__(self):
        self.content_provider = get_content_provider()

    def generate(self, context: Dict[str, Any]) -> bytes:
        """Generate a flyer zip file with HTML, CSS, and print styles."""
        profile = context.get("profile", {})
        theme = context.get("theme", {})

        logger.info("Generating flyer", theme=theme.get("name"))

        # Generate content using AI
        content = self._generate_content(profile, theme)

        # Create zip in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # CSS tokens
            css_tokens = self._generate_css_tokens(profile)
            zf.writestr("tokens.css", css_tokens)

            # Base styles with print support
            base_css = self._generate_base_styles(profile)
            zf.writestr("styles.css", base_css)

            # Print-specific styles
            print_css = self._generate_print_styles()
            zf.writestr("print.css", print_css)

            # HTML flyer
            html = self._generate_html(profile, theme, content)
            zf.writestr("flyer.html", html)

            # README
            readme = self._generate_readme(theme, content)
            zf.writestr("README.md", readme)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _generate_content(self, profile: Dict[str, Any], theme: Dict[str, Any]) -> Dict[str, Any]:
        """Generate flyer content using AI."""
        theme_name = theme.get("name", "Event")
        theme_desc = theme.get("description", "")
        brand_name = profile.get("identity", {}).get("name", "Brand")

        # Build context from theme documents
        doc_context = ""
        for doc in theme.get("documents", []):
            if doc.get("text"):
                doc_context += f"\n{doc['name']}:\n{doc['text'][:1000]}\n"

        prompt = f"""Create compelling flyer content for "{theme_name}".

Brand: {brand_name}
Theme Description: {theme_desc}
{f"Additional Context: {doc_context}" if doc_context else ""}

Generate JSON with:
- headline: Main attention-grabbing headline (5-8 words)
- subheadline: Supporting text (10-15 words)
- key_points: Array of 3-4 bullet points (each 5-10 words)
- cta_text: Call to action button text
- cta_url: Suggested CTA URL
- footer_text: Contact or additional info
- tagline: Brand tagline if applicable"""

        try:
            result = self.content_provider.generate_json(prompt)
            return result
        except Exception as e:
            logger.error("Content generation failed, using defaults", error=str(e))
            return {
                "headline": f"{theme_name}",
                "subheadline": f"Join us for an amazing {theme_name} experience",
                "key_points": [
                    "Discover new opportunities",
                    "Connect with industry leaders",
                    "Learn cutting-edge insights"
                ],
                "cta_text": "Learn More",
                "cta_url": "#",
                "footer_text": f"{brand_name} - {theme_name}",
                "tagline": brand_name
            }

    def _generate_css_tokens(self, profile: Dict[str, Any]) -> str:
        """Generate CSS custom properties."""
        colors = profile.get("colors", {})
        typography = profile.get("typography", {})

        primary = colors.get("primary", {}).get("hex", "#0066CC")
        secondary = colors.get("secondary", [{}])[0].get("hex", "#333333") if colors.get("secondary") else "#333333"

        return f""":root {{
  /* Colors */
  --color-primary: {primary};
  --color-secondary: {secondary};
  --color-text: #333333;
  --color-text-light: #666666;
  --color-background: #ffffff;

  /* Typography */
  --font-heading: '{typography.get("heading_font", "Inter")}', system-ui, sans-serif;
  --font-body: '{typography.get("body_font", "Inter")}', system-ui, sans-serif;

  /* Spacing */
  --bleed: 3mm;
  --safe-margin: 10mm;
}}
"""

    def _generate_base_styles(self, profile: Dict[str, Any]) -> str:
        """Generate base CSS styles."""
        return """@import url('tokens.css');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-body);
  color: var(--color-text);
  background: var(--color-background);
  line-height: 1.5;
}

.flyer {
  width: 210mm;
  min-height: 297mm;
  padding: calc(var(--safe-margin) + var(--bleed));
  position: relative;
  overflow: hidden;
}

.flyer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 20mm;
}

.header {
  text-align: center;
  padding-top: 15mm;
}

.headline {
  font-family: var(--font-heading);
  font-size: 48pt;
  font-weight: 800;
  color: var(--color-primary);
  line-height: 1.1;
  margin-bottom: 8mm;
}

.subheadline {
  font-size: 18pt;
  color: var(--color-text-light);
  max-width: 80%;
  margin: 0 auto;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 10mm;
}

.key-points {
  list-style: none;
  padding: 0;
}

.key-points li {
  font-size: 16pt;
  padding: 6mm 0;
  padding-left: 15mm;
  position: relative;
  border-bottom: 1px solid #eee;
}

.key-points li:last-child {
  border-bottom: none;
}

.key-points li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 8mm;
  height: 8mm;
  background: var(--color-primary);
  border-radius: 50%;
}

.cta-section {
  text-align: center;
  padding: 15mm 0;
}

.cta-button {
  display: inline-block;
  background: var(--color-primary);
  color: white;
  font-family: var(--font-heading);
  font-size: 16pt;
  font-weight: 700;
  padding: 6mm 20mm;
  border-radius: 4mm;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.footer {
  text-align: center;
  padding: 10mm;
  border-top: 2px solid var(--color-primary);
}

.footer p {
  font-size: 12pt;
  color: var(--color-text-light);
}

.tagline {
  font-family: var(--font-heading);
  font-weight: 700;
  color: var(--color-primary);
  margin-top: 3mm;
}

/* Background decoration */
.flyer::before {
  content: "";
  position: absolute;
  top: -50mm;
  right: -50mm;
  width: 150mm;
  height: 150mm;
  background: var(--color-primary);
  opacity: 0.05;
  border-radius: 50%;
}

.flyer::after {
  content: "";
  position: absolute;
  bottom: -30mm;
  left: -30mm;
  width: 100mm;
  height: 100mm;
  background: var(--color-primary);
  opacity: 0.05;
  border-radius: 50%;
}
"""

    def _generate_print_styles(self) -> str:
        """Generate print-specific CSS."""
        return """@media print {
  @page {
    size: A4;
    margin: 0;
  }

  body {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  .flyer {
    width: 216mm; /* A4 + 3mm bleed each side */
    min-height: 303mm;
    padding: 13mm; /* safe margin + bleed */
  }

  /* Bleed marks */
  .bleed-marks {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
  }

  .bleed-marks::before,
  .bleed-marks::after {
    content: "";
    position: absolute;
    background: #000;
  }

  /* Crop marks */
  .crop-mark {
    position: absolute;
    width: 5mm;
    height: 0.25mm;
    background: #000;
  }

  .crop-mark.top-left { top: 0; left: 3mm; }
  .crop-mark.top-right { top: 0; right: 3mm; }
  .crop-mark.bottom-left { bottom: 0; left: 3mm; }
  .crop-mark.bottom-right { bottom: 0; right: 3mm; }
}

/* Screen preview */
@media screen {
  body {
    background: #f0f0f0;
    padding: 20px;
  }

  .flyer {
    margin: 0 auto;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  }
}
"""

    def _generate_html(self, profile: Dict[str, Any], theme: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate HTML flyer."""
        headline = content.get("headline", theme.get("name", "Event"))
        subheadline = content.get("subheadline", "")
        key_points = content.get("key_points", [])
        cta_text = content.get("cta_text", "Learn More")
        cta_url = content.get("cta_url", "#")
        footer_text = content.get("footer_text", "")
        tagline = content.get("tagline", "")

        key_points_html = "\n".join([f"      <li>{point}</li>" for point in key_points])

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{headline} - Flyer</title>
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="print.css">
</head>
<body>
  <div class="flyer">
    <div class="flyer-content">
      <header class="header">
        <h1 class="headline">{headline}</h1>
        <p class="subheadline">{subheadline}</p>
      </header>

      <main class="main-content">
        <ul class="key-points">
{key_points_html}
        </ul>
      </main>

      <section class="cta-section">
        <a href="{cta_url}" class="cta-button">{cta_text}</a>
      </section>

      <footer class="footer">
        <p>{footer_text}</p>
        {f'<p class="tagline">{tagline}</p>' if tagline else ''}
      </footer>
    </div>
  </div>
</body>
</html>
"""

    def _generate_readme(self, theme: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate README."""
        return f"""# {theme.get('name', 'Theme')} Flyer

## Files

- `flyer.html` - Main flyer file
- `styles.css` - Base styles
- `print.css` - Print-specific styles
- `tokens.css` - CSS custom properties

## Print Instructions

### For Professional Print:

1. Open `flyer.html` in a browser
2. Print to PDF with these settings:
   - Paper size: A4
   - Margins: None
   - Background graphics: Enabled
3. The flyer includes 3mm bleed on all sides

### Print Specifications:

- Size: A4 (210mm x 297mm)
- Bleed: 3mm
- Safe margin: 10mm from trim edge
- Color mode: CMYK recommended for offset printing

## Customization

Edit `tokens.css` to change:
- Colors
- Fonts
- Margins

## Content

Headline: {content.get('headline', 'N/A')}
CTA: {content.get('cta_text', 'N/A')}
"""
