import io
import json
import zipfile
from typing import Dict, Any, Optional
import structlog

from app.providers.content_provider import get_content_provider

logger = structlog.get_logger()


class EmailGenerator:
    """Generates email content based on brand profile and reference structure."""

    def __init__(self):
        self.content_provider = get_content_provider()

    def generate(
        self,
        profile: Dict[str, Any],
        topic: str,
        email_type: str = "newsletter",
        reference_structure: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """Generate email content zip file."""
        logger.info("Generating email content", topic=topic, email_type=email_type)

        # Generate content using AI
        content = self.content_provider.generate_email_content(
            profile, topic, email_type, reference_structure
        )

        brand_name = profile.get("identity", {}).get("name", "Brand")

        # Create zip in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Generate HTML email
            html = self._generate_html(profile, content)
            zf.writestr("email.html", html)

            # Generate MJML source
            mjml = self._generate_mjml(profile, content)
            zf.writestr("email.mjml", mjml)

            # Generate plain text version
            plain_text = self._generate_plain_text(profile, content)
            zf.writestr("email.txt", plain_text)

            # Write subject line
            zf.writestr("subject.txt", content.get("subject", topic))

            # Write preview text
            zf.writestr("preview.txt", content.get("preview_text", ""))

            # Write content.json
            zf.writestr("content.json", json.dumps(content, indent=2))

            # Generate README
            readme = self._generate_readme(profile, topic, email_type, content)
            zf.writestr("README.md", readme)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _generate_html(self, profile: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate HTML email."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        colors = profile.get("colors", {})
        typography = profile.get("typography", {})

        primary_color = colors.get("primary", {}).get("hex", "#0066CC")
        heading_font = typography.get("heading_font", "Arial")
        body_font = typography.get("body_font", "Arial")

        neutrals = colors.get("neutrals", [])
        text_color = neutrals[0].get("hex", "#333333") if neutrals else "#333333"
        bg_color = "#ffffff"

        subject = content.get("subject", "")
        preview_text = content.get("preview_text", "")
        greeting = content.get("greeting", "Hello,")
        body = content.get("body", [])
        sections = content.get("sections", [])
        cta = content.get("cta", {})
        closing = content.get("closing", f"Best regards,\nThe {brand_name} Team")

        # Build body paragraphs
        body_html = "\n".join([
            f'<p style="margin: 0 0 20px; font-size: 16px; line-height: 1.6; color: {text_color};">{p}</p>'
            for p in body
        ])

        # Build sections
        sections_html = ""
        for section in sections:
            sections_html += f"""
                            <div style="margin: 30px 0; padding: 20px; background-color: #f9f9f9; border-radius: 8px;">
                                <h3 style="margin: 0 0 10px; font-family: '{heading_font}', Arial, sans-serif; font-size: 18px; color: {text_color};">
                                    {section.get('heading', '')}
                                </h3>
                                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: {text_color};">
                                    {section.get('content', '')}
                                </p>
                            </div>"""

        # CTA button
        cta_html = ""
        if cta:
            cta_html = f"""
                            <table role="presentation" style="margin: 30px 0;">
                                <tr>
                                    <td style="border-radius: 8px; background-color: {primary_color};">
                                        <a href="{cta.get('url', '#')}" target="_blank" style="display: inline-block; padding: 16px 32px; font-family: '{body_font}', Arial, sans-serif; font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none;">
                                            {cta.get('text', 'Learn More')}
                                        </a>
                                    </td>
                                </tr>
                            </table>"""

        closing_html = closing.replace('\n', '<br>')

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
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
                <table role="presentation" style="width: 100%; max-width: 600px; border-collapse: collapse; background-color: {bg_color}; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 30px; background-color: {primary_color}; text-align: center;">
                            <h1 style="margin: 0; font-family: '{heading_font}', Arial, sans-serif; font-size: 28px; color: #ffffff;">
                                {brand_name}
                            </h1>
                        </td>
                    </tr>

                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="margin: 0 0 20px; font-size: 16px; color: {text_color};">
                                {greeting}
                            </p>

                            {body_html}

                            {sections_html}

                            {cta_html}

                            <p style="margin: 30px 0 0; font-size: 16px; line-height: 1.6; color: {text_color};">
                                {closing_html}
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px; background-color: #f8f8f8; text-align: center; border-top: 1px solid #eee;">
                            <p style="margin: 0 0 10px; font-size: 12px; color: #888888;">
                                &copy; 2025 {brand_name}. All rights reserved.
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #888888;">
                                <a href="#" style="color: #888888; text-decoration: underline;">Unsubscribe</a> |
                                <a href="#" style="color: #888888; text-decoration: underline;">View in browser</a> |
                                <a href="#" style="color: #888888; text-decoration: underline;">Privacy Policy</a>
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    def _generate_mjml(self, profile: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate MJML source."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        colors = profile.get("colors", {})
        typography = profile.get("typography", {})

        primary_color = colors.get("primary", {}).get("hex", "#0066CC")
        heading_font = typography.get("heading_font", "Arial")
        body_font = typography.get("body_font", "Arial")

        neutrals = colors.get("neutrals", [])
        text_color = neutrals[0].get("hex", "#333333") if neutrals else "#333333"

        subject = content.get("subject", "")
        preview_text = content.get("preview_text", "")
        greeting = content.get("greeting", "Hello,")
        body = content.get("body", [])
        sections = content.get("sections", [])
        cta = content.get("cta", {})
        closing = content.get("closing", f"Best regards,\nThe {brand_name} Team")

        # Build body paragraphs
        body_mjml = "\n".join([
            f'<mj-text font-size="16px" line-height="1.6">{p}</mj-text>'
            for p in body
        ])

        # Build sections
        sections_mjml = ""
        for section in sections:
            sections_mjml += f"""
        <mj-section background-color="#f9f9f9" border-radius="8px" padding="20px">
          <mj-column>
            <mj-text font-family="{heading_font}, Arial, sans-serif" font-size="18px" font-weight="bold">
              {section.get('heading', '')}
            </mj-text>
            <mj-text font-size="14px" line-height="1.6">
              {section.get('content', '')}
            </mj-text>
          </mj-column>
        </mj-section>"""

        # CTA button
        cta_mjml = ""
        if cta:
            cta_mjml = f"""
        <mj-button background-color="{primary_color}" color="#ffffff" font-size="16px" font-weight="bold" href="{cta.get('url', '#')}" border-radius="8px" padding="30px 0">
          {cta.get('text', 'Learn More')}
        </mj-button>"""

        return f"""<mjml>
  <mj-head>
    <mj-title>{subject}</mj-title>
    <mj-preview>{preview_text}</mj-preview>
    <mj-attributes>
      <mj-all font-family="{body_font}, Arial, sans-serif" />
      <mj-text color="{text_color}" />
    </mj-attributes>
  </mj-head>

  <mj-body background-color="#f4f4f4">
    <!-- Header -->
    <mj-section background-color="{primary_color}" padding="40px 30px">
      <mj-column>
        <mj-text align="center" font-family="{heading_font}, Arial, sans-serif" font-size="28px" color="#ffffff" font-weight="bold">
          {brand_name}
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Main Content -->
    <mj-section background-color="#ffffff" padding="40px 30px">
      <mj-column>
        <mj-text font-size="16px">
          {greeting}
        </mj-text>

        {body_mjml}
      </mj-column>
    </mj-section>

    {sections_mjml}

    <mj-section background-color="#ffffff" padding="0 30px 40px">
      <mj-column>
        {cta_mjml}

        <mj-text font-size="16px" padding-top="30px">
          {closing.replace(chr(10), '<br/>')}
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
          <a href="#" style="color: #888888;">View in browser</a> |
          <a href="#" style="color: #888888;">Privacy Policy</a>
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>"""

    def _generate_plain_text(self, profile: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate plain text version."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        greeting = content.get("greeting", "Hello,")
        body = content.get("body", [])
        sections = content.get("sections", [])
        cta = content.get("cta", {})
        closing = content.get("closing", f"Best regards,\nThe {brand_name} Team")

        lines = [
            brand_name.upper(),
            "=" * len(brand_name),
            "",
            greeting,
            "",
        ]

        for p in body:
            lines.append(p)
            lines.append("")

        for section in sections:
            lines.append(f"--- {section.get('heading', '')} ---")
            lines.append(section.get('content', ''))
            lines.append("")

        if cta:
            lines.append(f"[{cta.get('text', 'Learn More')}]: {cta.get('url', '#')}")
            lines.append("")

        lines.append(closing)
        lines.append("")
        lines.append("-" * 40)
        lines.append(f"(c) 2025 {brand_name}. All rights reserved.")
        lines.append("To unsubscribe, visit: [unsubscribe link]")

        return "\n".join(lines)

    def _generate_readme(
        self,
        profile: Dict[str, Any],
        topic: str,
        email_type: str,
        content: Dict[str, Any],
    ) -> str:
        """Generate README for the email output."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        subject = content.get("subject", topic)

        return f"""# {brand_name} Email Template

Generated {email_type} email for "{topic}"

## Files

- `email.html` - Ready-to-send HTML email
- `email.mjml` - MJML source for customization
- `email.txt` - Plain text version
- `subject.txt` - Email subject line
- `preview.txt` - Preview/preheader text
- `content.json` - Generated content data

## Subject Line

{subject}

## Preview Text

{content.get('preview_text', 'N/A')}

## Brand Profile Applied

- **Primary Color:** {profile.get('colors', {}).get('primary', {}).get('hex', 'N/A')}
- **Heading Font:** {profile.get('typography', {}).get('heading_font', 'N/A')}
- **Body Font:** {profile.get('typography', {}).get('body_font', 'N/A')}

## Usage

### Using the HTML file
The `email.html` file is ready to use with most email service providers.
Copy the HTML content into your ESP's editor.

### Using MJML
If you need to make changes, edit `email.mjml` and compile it:

```bash
npx mjml email.mjml -o email.html
```

### Plain Text
Include `email.txt` as the plain text alternative for better deliverability.

## Testing

Always test your email in multiple clients before sending:
- Gmail (web and mobile)
- Outlook (desktop and web)
- Apple Mail
- Yahoo Mail
- Mobile email apps

## Checklist

- [ ] Replace placeholder links with actual URLs
- [ ] Update unsubscribe link
- [ ] Add tracking pixels if needed
- [ ] Test all links
- [ ] Preview on multiple devices
- [ ] Check spam score
"""
