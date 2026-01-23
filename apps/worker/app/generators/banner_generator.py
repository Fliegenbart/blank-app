"""Banner ads generator for theme assets."""
import io
import zipfile
from typing import Dict, Any, List, Tuple
import structlog

from app.providers.content_provider import get_content_provider

logger = structlog.get_logger()

# Standard banner sizes (width, height, name)
BANNER_SIZES: List[Tuple[int, int, str]] = [
    (300, 250, "medium-rectangle"),
    (336, 280, "large-rectangle"),
    (728, 90, "leaderboard"),
    (300, 600, "half-page"),
    (320, 50, "mobile-leaderboard"),
    (160, 600, "wide-skyscraper"),
    (970, 250, "billboard"),
    (300, 50, "mobile-banner"),
]


class BannerGenerator:
    """Generates responsive HTML banner ads in standard sizes."""

    def __init__(self):
        self.content_provider = get_content_provider()

    def generate(self, context: Dict[str, Any]) -> bytes:
        """Generate banner ads zip file with HTML for each size."""
        profile = context.get("profile", {})
        theme = context.get("theme", {})

        logger.info("Generating banner ads", theme=theme.get("name"))

        # Generate content using AI
        content = self._generate_content(profile, theme)

        # Create zip in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Shared CSS
            shared_css = self._generate_shared_css(profile)
            zf.writestr("shared/styles.css", shared_css)

            # Generate each banner size
            for width, height, name in BANNER_SIZES:
                banner_html = self._generate_banner_html(profile, content, width, height, name)
                zf.writestr(f"banners/{name}/index.html", banner_html)

                # Size-specific CSS
                size_css = self._generate_size_css(profile, width, height)
                zf.writestr(f"banners/{name}/styles.css", size_css)

            # Preview page
            preview_html = self._generate_preview_page(content)
            zf.writestr("preview.html", preview_html)

            # README
            readme = self._generate_readme(theme, content)
            zf.writestr("README.md", readme)

            # Content JSON
            import json
            zf.writestr("content.json", json.dumps(content, indent=2))

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _generate_content(self, profile: Dict[str, Any], theme: Dict[str, Any]) -> Dict[str, Any]:
        """Generate banner content using AI."""
        theme_name = theme.get("name", "Event")
        theme_desc = theme.get("description", "")
        brand_name = profile.get("identity", {}).get("name", "Brand")

        prompt = f"""Create banner ad content for "{theme_name}".

Brand: {brand_name}
Theme Description: {theme_desc}

Generate JSON with multiple headline/CTA variations for A/B testing:
{{
  "brand_name": "{brand_name}",
  "campaign_name": "{theme_name}",
  "variations": [
    {{
      "name": "primary",
      "headline": "Main headline (3-5 words)",
      "subheadline": "Supporting text (5-10 words)",
      "cta_text": "CTA button text (2-3 words)",
      "cta_url": "#"
    }},
    {{
      "name": "alternate",
      "headline": "Alternative headline",
      "subheadline": "Alternative supporting text",
      "cta_text": "Alternative CTA",
      "cta_url": "#"
    }}
  ],
  "tagline": "Brand tagline if applicable"
}}

Headlines must be punchy and work across different banner sizes."""

        try:
            result = self.content_provider.generate_json(prompt)
            return result
        except Exception as e:
            logger.error("Content generation failed, using defaults", error=str(e))
            return {
                "brand_name": brand_name,
                "campaign_name": theme_name,
                "variations": [
                    {
                        "name": "primary",
                        "headline": theme_name,
                        "subheadline": "Discover something amazing",
                        "cta_text": "Learn More",
                        "cta_url": "#"
                    }
                ],
                "tagline": brand_name
            }

    def _generate_shared_css(self, profile: Dict[str, Any]) -> str:
        """Generate shared CSS variables and base styles."""
        colors = profile.get("colors", {})
        typography = profile.get("typography", {})

        primary = colors.get("primary", {}).get("hex", "#0066CC")
        secondary = colors.get("secondary", [{}])[0].get("hex", "#333333") if colors.get("secondary") else "#333333"

        return f"""/* Brand Colors */
:root {{
  --color-primary: {primary};
  --color-secondary: {secondary};
  --color-text: #ffffff;
  --color-text-dark: #333333;
  --color-background: {primary};

  --font-heading: '{typography.get("heading_font", "Inter")}', system-ui, sans-serif;
  --font-body: '{typography.get("body_font", "Inter")}', system-ui, sans-serif;
}}

/* Base Reset */
* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: var(--font-body);
}}

/* Banner Base */
.banner {{
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  color: var(--color-text);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 10px;
  cursor: pointer;
}}

.banner:hover {{
  filter: brightness(1.05);
}}

/* Typography */
.headline {{
  font-family: var(--font-heading);
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 5px;
}}

.subheadline {{
  font-weight: 400;
  opacity: 0.9;
  margin-bottom: 8px;
}}

/* CTA Button */
.cta {{
  display: inline-block;
  background: #ffffff;
  color: var(--color-primary);
  font-family: var(--font-heading);
  font-weight: 700;
  text-decoration: none;
  border-radius: 4px;
  transition: transform 0.2s, box-shadow 0.2s;
}}

.cta:hover {{
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}}

/* Brand Logo */
.logo {{
  font-family: var(--font-heading);
  font-weight: 700;
  opacity: 0.8;
}}

/* Animation */
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(10px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

.banner .headline {{ animation: fadeIn 0.5s ease-out; }}
.banner .subheadline {{ animation: fadeIn 0.5s ease-out 0.1s backwards; }}
.banner .cta {{ animation: fadeIn 0.5s ease-out 0.2s backwards; }}
"""

    def _generate_size_css(self, profile: Dict[str, Any], width: int, height: int) -> str:
        """Generate size-specific CSS."""
        # Calculate responsive sizes based on banner dimensions
        is_horizontal = width > height
        is_vertical = height > width * 1.5
        is_small = width * height < 50000

        if is_small:
            headline_size = "14px"
            subheadline_size = "10px"
            cta_padding = "4px 10px"
            cta_size = "10px"
        elif is_vertical:
            headline_size = "24px"
            subheadline_size = "14px"
            cta_padding = "8px 16px"
            cta_size = "12px"
        elif is_horizontal and height < 100:
            headline_size = "18px"
            subheadline_size = "12px"
            cta_padding = "6px 14px"
            cta_size = "11px"
        else:
            headline_size = "22px"
            subheadline_size = "14px"
            cta_padding = "8px 18px"
            cta_size = "13px"

        return f"""/* {width}x{height} Banner Styles */
@import url('../shared/styles.css');

.banner {{
  width: {width}px;
  height: {height}px;
  {'flex-direction: row; text-align: left; padding: 0 15px;' if is_horizontal and height < 100 else ''}
}}

.headline {{
  font-size: {headline_size};
  {'margin-right: 15px; margin-bottom: 0;' if is_horizontal and height < 100 else ''}
}}

.subheadline {{
  font-size: {subheadline_size};
  {'display: none;' if is_small else ''}
  {'margin-right: 10px; margin-bottom: 0;' if is_horizontal and height < 100 else ''}
}}

.cta {{
  padding: {cta_padding};
  font-size: {cta_size};
}}

.logo {{
  {'position: absolute; bottom: 5px; right: 8px;' if not is_small else 'display: none;'}
  font-size: 10px;
}}
"""

    def _generate_banner_html(self, profile: Dict[str, Any], content: Dict[str, Any], width: int, height: int, name: str) -> str:
        """Generate HTML for a specific banner size."""
        variation = content.get("variations", [{}])[0]
        brand_name = content.get("brand_name", "Brand")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width={width}">
  <meta name="ad.size" content="width={width},height={height}">
  <title>{name} Banner - {content.get('campaign_name', 'Campaign')}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a href="{variation.get('cta_url', '#')}" target="_blank" class="banner" id="banner">
    <h1 class="headline">{variation.get('headline', 'Headline')}</h1>
    <p class="subheadline">{variation.get('subheadline', '')}</p>
    <span class="cta">{variation.get('cta_text', 'Learn More')}</span>
    <span class="logo">{brand_name}</span>
  </a>

  <script>
    // Click tracking (placeholder)
    document.getElementById('banner').addEventListener('click', function(e) {{
      // Add tracking code here
      console.log('Banner clicked: {name}');
    }});
  </script>
</body>
</html>
"""

    def _generate_preview_page(self, content: Dict[str, Any]) -> str:
        """Generate a preview page showing all banner sizes."""
        banners_html = ""
        for width, height, name in BANNER_SIZES:
            banners_html += f"""
      <div class="banner-preview">
        <h3>{name} ({width}x{height})</h3>
        <iframe src="banners/{name}/index.html" width="{width}" height="{height}" frameborder="0"></iframe>
      </div>
"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Banner Preview - {content.get('campaign_name', 'Campaign')}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: system-ui, sans-serif;
      background: #f5f5f5;
      padding: 40px;
    }}
    h1 {{
      text-align: center;
      margin-bottom: 40px;
      color: #333;
    }}
    .banner-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 30px;
      justify-content: center;
    }}
    .banner-preview {{
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .banner-preview h3 {{
      margin-bottom: 15px;
      color: #666;
      font-size: 14px;
    }}
    iframe {{
      display: block;
      border: 1px solid #ddd;
    }}
  </style>
</head>
<body>
  <h1>{content.get('campaign_name', 'Campaign')} - Banner Preview</h1>
  <div class="banner-grid">
{banners_html}
  </div>
</body>
</html>
"""

    def _generate_readme(self, theme: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate README."""
        sizes_list = "\n".join([f"- **{name}** ({w}x{h}px)" for w, h, name in BANNER_SIZES])

        return f"""# {theme.get('name', 'Theme')} Banner Ads

## Files

- `preview.html` - Preview all banners in one page
- `banners/` - Individual banner sizes
- `shared/` - Shared CSS styles
- `content.json` - Banner content data

## Banner Sizes

{sizes_list}

## How to Use

### Preview
Open `preview.html` in a browser to see all banner sizes.

### Individual Banners
Each size is in its own folder under `banners/`.
Open the `index.html` file directly or upload to ad platforms.

### Customization

1. Edit `shared/styles.css` to change colors and fonts
2. Edit `content.json` to update text content
3. Edit individual banner HTML files for size-specific changes

## Ad Platform Guidelines

### Google Ads
- File size: Max 150KB per banner
- Animation: Max 30 seconds
- Format: HTML5, GIF, or static image

### Facebook/Meta
- Recommended: 1200x628px for feed ads
- Use the rectangle sizes for right column

### LinkedIn
- Spotlight: 300x250
- Banner: 728x90

## Tracking

Add your tracking pixel or click tracking code in each banner's script section.
"""
