"""Brochure generator for theme assets."""
import io
import zipfile
from typing import Dict, Any, List
import structlog

from app.providers.content_provider import get_content_provider

logger = structlog.get_logger()


class BrochureGenerator:
    """Generates multi-page print-ready brochure with bleed margins."""

    def __init__(self):
        self.content_provider = get_content_provider()

    def generate(self, context: Dict[str, Any]) -> bytes:
        """Generate a brochure zip file with HTML, CSS, and print styles."""
        profile = context.get("profile", {})
        theme = context.get("theme", {})

        logger.info("Generating brochure", theme=theme.get("name"))

        # Generate content using AI
        content = self._generate_content(profile, theme)

        # Create zip in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # CSS tokens
            css_tokens = self._generate_css_tokens(profile)
            zf.writestr("tokens.css", css_tokens)

            # Base styles
            base_css = self._generate_base_styles(profile)
            zf.writestr("styles.css", base_css)

            # Print styles
            print_css = self._generate_print_styles()
            zf.writestr("print.css", print_css)

            # HTML brochure (multi-page)
            html = self._generate_html(profile, theme, content)
            zf.writestr("brochure.html", html)

            # Individual page HTMLs for separate printing
            for i, page in enumerate(content.get("pages", [])):
                page_html = self._generate_page_html(profile, theme, page, i + 1)
                zf.writestr(f"page-{i + 1}.html", page_html)

            # README
            readme = self._generate_readme(theme, content)
            zf.writestr("README.md", readme)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _generate_content(self, profile: Dict[str, Any], theme: Dict[str, Any]) -> Dict[str, Any]:
        """Generate brochure content using AI."""
        theme_name = theme.get("name", "Event")
        theme_desc = theme.get("description", "")
        brand_name = profile.get("identity", {}).get("name", "Brand")

        doc_context = ""
        for doc in theme.get("documents", []):
            if doc.get("text"):
                doc_context += f"\n{doc['name']}:\n{doc['text'][:1500]}\n"

        prompt = f"""Create compelling brochure content for "{theme_name}".

Brand: {brand_name}
Theme Description: {theme_desc}
{f"Additional Context: {doc_context}" if doc_context else ""}

Generate JSON with 4 pages:
{{
  "title": "Brochure title",
  "pages": [
    {{
      "type": "cover",
      "headline": "Main headline",
      "subheadline": "Tagline or subtitle",
      "image_placeholder": "Description of ideal cover image"
    }},
    {{
      "type": "overview",
      "headline": "Section headline",
      "intro": "1-2 sentences intro",
      "points": ["Point 1", "Point 2", "Point 3"],
      "image_placeholder": "Description of section image"
    }},
    {{
      "type": "details",
      "headline": "Details headline",
      "content": ["Paragraph 1", "Paragraph 2"],
      "highlights": ["Highlight 1", "Highlight 2", "Highlight 3"]
    }},
    {{
      "type": "contact",
      "headline": "Get in Touch / Next Steps",
      "cta_text": "Call to action",
      "contact_info": "Contact details or instructions",
      "closing": "Final message"
    }}
  ]
}}"""

        try:
            result = self.content_provider.generate_json(prompt)
            return result
        except Exception as e:
            logger.error("Content generation failed, using defaults", error=str(e))
            return self._default_content(theme_name, brand_name)

    def _default_content(self, theme_name: str, brand_name: str) -> Dict[str, Any]:
        """Return default content."""
        return {
            "title": f"{theme_name} Brochure",
            "pages": [
                {
                    "type": "cover",
                    "headline": theme_name,
                    "subheadline": f"Presented by {brand_name}",
                    "image_placeholder": "Cover image"
                },
                {
                    "type": "overview",
                    "headline": "About This Event",
                    "intro": f"Welcome to {theme_name}, an exciting opportunity to engage and connect.",
                    "points": [
                        "Discover innovative solutions",
                        "Network with industry leaders",
                        "Gain valuable insights"
                    ]
                },
                {
                    "type": "details",
                    "headline": "What to Expect",
                    "content": [
                        "Join us for an unforgettable experience filled with learning and networking opportunities.",
                        "Our carefully curated program ensures you get the most out of your participation."
                    ],
                    "highlights": ["Expert speakers", "Interactive sessions", "Networking opportunities"]
                },
                {
                    "type": "contact",
                    "headline": "Get Started",
                    "cta_text": "Register Now",
                    "contact_info": f"Visit our website or contact {brand_name}",
                    "closing": "We look forward to seeing you!"
                }
            ]
        }

    def _generate_css_tokens(self, profile: Dict[str, Any]) -> str:
        """Generate CSS custom properties."""
        colors = profile.get("colors", {})
        typography = profile.get("typography", {})

        primary = colors.get("primary", {}).get("hex", "#0066CC")
        secondary = colors.get("secondary", [{}])[0].get("hex", "#333333") if colors.get("secondary") else "#333333"

        return f""":root {{
  --color-primary: {primary};
  --color-secondary: {secondary};
  --color-text: #333333;
  --color-text-light: #666666;
  --color-background: #ffffff;
  --color-accent: {primary}22;

  --font-heading: '{typography.get("heading_font", "Inter")}', system-ui, sans-serif;
  --font-body: '{typography.get("body_font", "Inter")}', system-ui, sans-serif;

  --bleed: 3mm;
  --safe-margin: 12mm;
  --page-width: 210mm;
  --page-height: 297mm;
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
  line-height: 1.6;
}

.brochure {
  width: var(--page-width);
}

.page {
  width: var(--page-width);
  min-height: var(--page-height);
  padding: calc(var(--safe-margin) + var(--bleed));
  position: relative;
  page-break-after: always;
  overflow: hidden;
}

.page:last-child {
  page-break-after: avoid;
}

/* Cover Page */
.page-cover {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  color: white;
}

.page-cover .headline {
  font-family: var(--font-heading);
  font-size: 56pt;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 10mm;
}

.page-cover .subheadline {
  font-size: 20pt;
  opacity: 0.9;
  max-width: 70%;
}

/* Content Pages */
.page-content {
  padding: calc(var(--safe-margin) + var(--bleed) + 15mm) calc(var(--safe-margin) + var(--bleed));
}

.page-header {
  margin-bottom: 12mm;
  padding-bottom: 8mm;
  border-bottom: 3px solid var(--color-primary);
}

.page-header h2 {
  font-family: var(--font-heading);
  font-size: 32pt;
  font-weight: 700;
  color: var(--color-primary);
}

.intro {
  font-size: 14pt;
  color: var(--color-text-light);
  margin-bottom: 10mm;
  line-height: 1.7;
}

.points-list {
  list-style: none;
  padding: 0;
}

.points-list li {
  font-size: 13pt;
  padding: 5mm 0 5mm 12mm;
  position: relative;
  border-bottom: 1px solid #eee;
}

.points-list li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 8mm;
  width: 6mm;
  height: 6mm;
  background: var(--color-primary);
  border-radius: 2mm;
}

.content-section {
  margin-bottom: 10mm;
}

.content-section p {
  font-size: 12pt;
  margin-bottom: 5mm;
  text-align: justify;
}

.highlights {
  display: flex;
  gap: 5mm;
  margin-top: 10mm;
}

.highlight-item {
  flex: 1;
  background: var(--color-accent);
  padding: 6mm;
  border-radius: 3mm;
  text-align: center;
}

.highlight-item span {
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 11pt;
  color: var(--color-primary);
}

/* Contact Page */
.page-contact {
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.page-contact h2 {
  font-family: var(--font-heading);
  font-size: 36pt;
  color: var(--color-primary);
  margin-bottom: 15mm;
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
  margin-bottom: 15mm;
}

.contact-info {
  font-size: 12pt;
  color: var(--color-text-light);
  margin-bottom: 10mm;
}

.closing {
  font-size: 14pt;
  font-style: italic;
  color: var(--color-text);
}

/* Page numbers */
.page-number {
  position: absolute;
  bottom: var(--safe-margin);
  right: var(--safe-margin);
  font-size: 10pt;
  color: var(--color-text-light);
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

  .page {
    width: 216mm;
    min-height: 303mm;
    padding: 15mm;
  }
}

@media screen {
  body {
    background: #e0e0e0;
    padding: 20px;
  }

  .brochure {
    margin: 0 auto;
  }

  .page {
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    background: white;
  }
}
"""

    def _generate_html(self, profile: Dict[str, Any], theme: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate complete brochure HTML."""
        title = content.get("title", theme.get("name", "Brochure"))
        pages = content.get("pages", [])

        pages_html = ""
        for i, page in enumerate(pages):
            pages_html += self._render_page(page, i + 1)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="print.css">
</head>
<body>
  <div class="brochure">
{pages_html}
  </div>
</body>
</html>
"""

    def _render_page(self, page: Dict[str, Any], page_num: int) -> str:
        """Render a single page."""
        page_type = page.get("type", "content")

        if page_type == "cover":
            return f"""    <div class="page page-cover">
      <h1 class="headline">{page.get('headline', 'Title')}</h1>
      <p class="subheadline">{page.get('subheadline', '')}</p>
    </div>
"""
        elif page_type == "overview":
            points_html = "\n".join([f"        <li>{p}</li>" for p in page.get("points", [])])
            return f"""    <div class="page page-content">
      <div class="page-header">
        <h2>{page.get('headline', 'Overview')}</h2>
      </div>
      <p class="intro">{page.get('intro', '')}</p>
      <ul class="points-list">
{points_html}
      </ul>
      <span class="page-number">{page_num}</span>
    </div>
"""
        elif page_type == "details":
            content_html = "\n".join([f"        <p>{p}</p>" for p in page.get("content", [])])
            highlights_html = "\n".join([f'        <div class="highlight-item"><span>{h}</span></div>' for h in page.get("highlights", [])])
            return f"""    <div class="page page-content">
      <div class="page-header">
        <h2>{page.get('headline', 'Details')}</h2>
      </div>
      <div class="content-section">
{content_html}
      </div>
      <div class="highlights">
{highlights_html}
      </div>
      <span class="page-number">{page_num}</span>
    </div>
"""
        elif page_type == "contact":
            return f"""    <div class="page page-content page-contact">
      <h2>{page.get('headline', 'Contact')}</h2>
      <a href="#" class="cta-button">{page.get('cta_text', 'Learn More')}</a>
      <p class="contact-info">{page.get('contact_info', '')}</p>
      <p class="closing">{page.get('closing', '')}</p>
      <span class="page-number">{page_num}</span>
    </div>
"""
        else:
            return f"""    <div class="page page-content">
      <div class="page-header">
        <h2>{page.get('headline', 'Content')}</h2>
      </div>
      <span class="page-number">{page_num}</span>
    </div>
"""

    def _generate_page_html(self, profile: Dict[str, Any], theme: Dict[str, Any], page: Dict[str, Any], page_num: int) -> str:
        """Generate standalone HTML for a single page."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Page {page_num}</title>
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="print.css">
</head>
<body>
  <div class="brochure">
{self._render_page(page, page_num)}
  </div>
</body>
</html>
"""

    def _generate_readme(self, theme: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate README."""
        pages = content.get("pages", [])
        return f"""# {theme.get('name', 'Theme')} Brochure

## Files

- `brochure.html` - Complete brochure (all pages)
- `page-1.html` to `page-{len(pages)}.html` - Individual pages
- `styles.css` - Base styles
- `print.css` - Print-specific styles
- `tokens.css` - CSS custom properties

## Print Instructions

### For Professional Print:

1. Open `brochure.html` in a browser
2. Print to PDF with these settings:
   - Paper size: A4
   - Margins: None
   - Background graphics: Enabled
   - Pages: All

### Print Specifications:

- Size: A4 (210mm x 297mm)
- Bleed: 3mm
- Safe margin: 12mm from trim edge
- Pages: {len(pages)}
- Binding: Saddle stitch or perfect bind

## Pages

{chr(10).join([f"{i+1}. {p.get('type', 'content').title()} - {p.get('headline', 'Untitled')}" for i, p in enumerate(pages)])}
"""
