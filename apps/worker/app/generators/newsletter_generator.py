import io
import zipfile
from typing import Dict, Any
import structlog
from jinja2 import Template

logger = structlog.get_logger()


class NewsletterGenerator:
    """Generates newsletter output based on brand profile."""

    def generate(
        self,
        profile: Dict[str, Any],
        topic: str,
        offer: str = None,
        cta: str = "Learn More",
        subject_line: str = None,
        preview_text: str = None,
    ) -> bytes:
        """Generate a newsletter zip file with HTML and MJML."""
        logger.info("Generating newsletter", topic=topic)

        brand_name = profile.get("identity", {}).get("name", "Brand")
        colors = profile.get("colors", {})
        typography = profile.get("typography", {})
        tone = profile.get("tone_of_voice", {})

        # Generate subject line if not provided
        if not subject_line:
            subject_line = self._generate_subject_line(topic, tone.get("attributes", []))

        # Generate preview text if not provided
        if not preview_text:
            preview_text = self._generate_preview_text(topic, offer)

        # Create zip in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Generate HTML email
            html = self._generate_html(profile, topic, offer, cta, subject_line, preview_text)
            zf.writestr("newsletter.html", html)

            # Generate MJML source
            mjml = self._generate_mjml(profile, topic, offer, cta, subject_line, preview_text)
            zf.writestr("newsletter.mjml", mjml)

            # Generate subject.txt
            zf.writestr("subject.txt", subject_line)

            # Generate README
            readme = self._generate_readme(profile, topic, subject_line)
            zf.writestr("README.md", readme)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _generate_subject_line(self, topic: str, attributes: list) -> str:
        """Generate an email subject line."""
        if "energetic" in attributes:
            return f"🚀 {topic} - You Won't Want to Miss This!"
        elif "friendly" in attributes:
            return f"Hey there! Check out {topic}"
        elif "professional" in attributes:
            return f"{topic}: Your Comprehensive Guide"
        else:
            return f"{topic} - Important Update"

    def _generate_preview_text(self, topic: str, offer: str = None) -> str:
        """Generate email preview text."""
        if offer:
            return f"{offer} - Open to learn more about {topic}."
        return f"Discover everything you need to know about {topic}."

    def _generate_html(
        self,
        profile: Dict[str, Any],
        topic: str,
        offer: str,
        cta: str,
        subject_line: str,
        preview_text: str,
    ) -> str:
        """Generate HTML email."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        colors = profile.get("colors", {})
        typography = profile.get("typography", {})

        primary_color = colors.get("primary", {}).get("hex", "#0066CC")
        heading_font = typography.get("heading_font", "Arial")
        body_font = typography.get("body_font", "Arial")

        # Get neutral colors
        neutrals = colors.get("neutrals", [])
        text_color = neutrals[0].get("hex", "#333333") if neutrals else "#333333"
        bg_color = neutrals[-1].get("hex", "#ffffff") if neutrals else "#ffffff"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject_line}</title>
    <!--[if mso]>
    <style type="text/css">
        body, table, td {{font-family: Arial, sans-serif !important;}}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: '{body_font}', Arial, sans-serif;">
    <!-- Preview Text -->
    <div style="display: none; max-height: 0; overflow: hidden;">
        {preview_text}
    </div>

    <!-- Email Container -->
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <!-- Email Content -->
                <table role="presentation" style="width: 100%; max-width: 600px; border-collapse: collapse; background-color: {bg_color};">

                    <!-- Header -->
                    <tr>
                        <td style="padding: 30px; background-color: {primary_color}; text-align: center;">
                            <h1 style="margin: 0; font-family: '{heading_font}', Arial, sans-serif; font-size: 24px; color: #ffffff;">
                                {brand_name}
                            </h1>
                        </td>
                    </tr>

                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px; font-family: '{heading_font}', Arial, sans-serif; font-size: 28px; color: {text_color};">
                                {topic}
                            </h2>

                            <p style="margin: 0 0 20px; font-size: 16px; line-height: 1.6; color: {text_color};">
                                {preview_text}
                            </p>

                            {f'<p style="margin: 0 0 20px; font-size: 16px; line-height: 1.6; color: {text_color};"><strong>{offer}</strong></p>' if offer else ''}

                            <!-- CTA Button -->
                            <table role="presentation" style="margin: 30px 0;">
                                <tr>
                                    <td style="border-radius: 4px; background-color: {primary_color};">
                                        <a href="#" target="_blank" style="display: inline-block; padding: 16px 32px; font-family: '{body_font}', Arial, sans-serif; font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none;">
                                            {cta}
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 0; font-size: 14px; line-height: 1.6; color: {text_color};">
                                Thank you for being part of our community.
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px; background-color: #f8f8f8; text-align: center;">
                            <p style="margin: 0 0 10px; font-size: 12px; color: #888888;">
                                &copy; 2025 {brand_name}. All rights reserved.
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #888888;">
                                <a href="#" style="color: #888888;">Unsubscribe</a> |
                                <a href="#" style="color: #888888;">View in browser</a>
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
        return html

    def _generate_mjml(
        self,
        profile: Dict[str, Any],
        topic: str,
        offer: str,
        cta: str,
        subject_line: str,
        preview_text: str,
    ) -> str:
        """Generate MJML source."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        colors = profile.get("colors", {})
        typography = profile.get("typography", {})

        primary_color = colors.get("primary", {}).get("hex", "#0066CC")
        heading_font = typography.get("heading_font", "Arial")
        body_font = typography.get("body_font", "Arial")

        neutrals = colors.get("neutrals", [])
        text_color = neutrals[0].get("hex", "#333333") if neutrals else "#333333"

        mjml = f"""<mjml>
  <mj-head>
    <mj-title>{subject_line}</mj-title>
    <mj-preview>{preview_text}</mj-preview>
    <mj-attributes>
      <mj-all font-family="{body_font}, Arial, sans-serif" />
      <mj-text color="{text_color}" />
    </mj-attributes>
  </mj-head>

  <mj-body background-color="#f4f4f4">
    <!-- Header -->
    <mj-section background-color="{primary_color}" padding="30px">
      <mj-column>
        <mj-text align="center" font-family="{heading_font}, Arial, sans-serif" font-size="24px" color="#ffffff">
          {brand_name}
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Main Content -->
    <mj-section background-color="#ffffff" padding="40px 30px">
      <mj-column>
        <mj-text font-family="{heading_font}, Arial, sans-serif" font-size="28px" line-height="1.2">
          {topic}
        </mj-text>

        <mj-text font-size="16px" line-height="1.6">
          {preview_text}
        </mj-text>

        {f'<mj-text font-size="16px" font-weight="bold">{offer}</mj-text>' if offer else ''}

        <mj-button background-color="{primary_color}" color="#ffffff" font-size="16px" font-weight="bold" padding="30px 0">
          {cta}
        </mj-button>

        <mj-text font-size="14px">
          Thank you for being part of our community.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Footer -->
    <mj-section background-color="#f8f8f8" padding="30px">
      <mj-column>
        <mj-text align="center" font-size="12px" color="#888888">
          &copy; 2025 {brand_name}. All rights reserved.
        </mj-text>
        <mj-text align="center" font-size="12px" color="#888888">
          <a href="#" style="color: #888888;">Unsubscribe</a> |
          <a href="#" style="color: #888888;">View in browser</a>
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>"""
        return mjml

    def _generate_readme(self, profile: Dict[str, Any], topic: str, subject_line: str) -> str:
        """Generate README for the newsletter output."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        return f"""# {brand_name} Newsletter

Generated newsletter for "{topic}"

## Files

- `newsletter.html` - Ready-to-send HTML email
- `newsletter.mjml` - MJML source for further customization
- `subject.txt` - Email subject line

## Subject Line

{subject_line}

## Brand Profile Applied

- **Primary Color:** {profile.get('colors', {}).get('primary', {}).get('hex', 'N/A')}
- **Heading Font:** {profile.get('typography', {}).get('heading_font', 'N/A')}
- **Body Font:** {profile.get('typography', {}).get('body_font', 'N/A')}

## Usage

### Using the HTML file
The `newsletter.html` file is ready to use with most email service providers.
Simply copy the HTML content into your ESP's editor.

### Using MJML
If you need to make changes, edit `newsletter.mjml` and compile it:

```bash
npx mjml newsletter.mjml -o newsletter.html
```

## Testing

Always test your email in multiple clients before sending:
- Gmail (web and mobile)
- Outlook (desktop and web)
- Apple Mail
- Mobile email apps
"""
