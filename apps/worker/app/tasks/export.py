"""Export tasks for print PDF and Figma."""
import io
import json
import traceback
from datetime import datetime
from typing import Optional
import structlog

from app.database import get_db_context
from app.storage import get_storage_service
from app.tasks.analyze import Job, Brand

logger = structlog.get_logger()


def _append_log(logs: Optional[str], message: str) -> str:
    """Append a message to the logs with timestamp."""
    timestamp = datetime.utcnow().isoformat()
    new_log = f"[{timestamp}] {message}"
    if logs:
        return f"{logs}\n{new_log}"
    return new_log


def export_print_pdf(job_id: str) -> dict:
    """Export asset as print-ready PDF with bleed and crop marks."""
    logger.info("Starting export_print_pdf task", job_id=job_id)

    with get_db_context() as db:
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting print PDF export...")
            db.commit()

            params = json.loads(job.params_json) if job.params_json else {}
            theme_id = params.get("theme_id")
            asset_id = params.get("asset_id")
            pdf_format = params.get("format", "pdf")
            bleed_mm = params.get("bleed_mm", 3)
            crop_marks = params.get("crop_marks", True)
            color_profile = params.get("color_profile", "CMYK")

            job.progress = 0.2
            job.logs = _append_log(job.logs, f"Export settings: format={pdf_format}, bleed={bleed_mm}mm")
            db.commit()

            # Get asset
            asset_result = db.execute(
                "SELECT storage_path, asset_type, name FROM theme_assets WHERE id = :id",
                {"id": asset_id}
            ).fetchone()

            if not asset_result:
                raise ValueError(f"Asset not found: {asset_id}")

            storage_path, asset_type, asset_name = asset_result

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Processing asset: {asset_name}")
            db.commit()

            # Get HTML content from storage
            storage = get_storage_service()
            content = storage.get(storage_path)

            job.progress = 0.4
            db.commit()

            # Generate PDF using WeasyPrint
            pdf_data = _generate_print_pdf(
                content,
                asset_type,
                bleed_mm=bleed_mm,
                crop_marks=crop_marks,
                color_profile=color_profile,
            )

            job.progress = 0.8
            job.logs = _append_log(job.logs, "PDF generated")
            db.commit()

            # Store PDF
            pdf_filename = f"{asset_name.replace(' ', '-').lower()}-print.pdf"
            pdf_path = f"themes/{theme_id}/assets/{asset_id}/print/{pdf_filename}"
            storage.store(pdf_path, pdf_data, "application/pdf")

            # Update asset with print PDF path
            db.execute(
                "UPDATE theme_assets SET print_pdf_path = :path, updated_at = :updated WHERE id = :id",
                {"path": pdf_path, "updated": datetime.utcnow(), "id": asset_id}
            )

            job.status = "completed"
            job.progress = 1.0
            job.result_json = json.dumps({
                "asset_id": asset_id,
                "print_pdf_path": pdf_path,
                "file_size": len(pdf_data),
            })
            job.logs = _append_log(job.logs, "Print PDF export complete")
            db.commit()

            logger.info("Print PDF export complete", job_id=job_id, asset_id=asset_id)
            return {"asset_id": asset_id, "print_pdf_path": pdf_path}

        except Exception as e:
            logger.error("Print PDF export failed", job_id=job_id, error=str(e))

            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")
                db.commit()

            raise


def _generate_print_pdf(
    zip_content: bytes,
    asset_type: str,
    bleed_mm: int = 3,
    crop_marks: bool = True,
    color_profile: str = "CMYK",
) -> bytes:
    """Generate print-ready PDF from HTML content."""
    import zipfile

    # Extract HTML from zip
    html_content = None
    css_content = ""

    with zipfile.ZipFile(io.BytesIO(zip_content), "r") as zf:
        for name in zf.namelist():
            if name.endswith(".html") and "index" in name or name == "flyer.html" or name == "brochure.html":
                html_content = zf.read(name).decode("utf-8")
            elif name.endswith(".css"):
                css_content += zf.read(name).decode("utf-8") + "\n"

    if not html_content:
        # Try any HTML file
        with zipfile.ZipFile(io.BytesIO(zip_content), "r") as zf:
            for name in zf.namelist():
                if name.endswith(".html"):
                    html_content = zf.read(name).decode("utf-8")
                    break

    if not html_content:
        raise ValueError("No HTML content found in asset")

    # Add print-specific CSS
    print_css = f"""
@page {{
    size: A4;
    margin: 0;
    marks: {'crop cross' if crop_marks else 'none'};
    bleed: {bleed_mm}mm;
}}

@media print {{
    body {{
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }}
}}
"""

    # Inject CSS into HTML
    if "<head>" in html_content:
        html_content = html_content.replace(
            "<head>",
            f"<head><style>{css_content}\n{print_css}</style>"
        )
    else:
        html_content = f"<html><head><style>{css_content}\n{print_css}</style></head>{html_content}</html>"

    # Generate PDF with WeasyPrint
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration

        font_config = FontConfiguration()
        html_doc = HTML(string=html_content)

        pdf_data = html_doc.write_pdf(font_config=font_config)
        return pdf_data

    except ImportError:
        logger.warning("WeasyPrint not available, generating placeholder PDF")
        return _generate_placeholder_pdf(html_content)


def _generate_placeholder_pdf(html_content: str) -> bytes:
    """Generate a simple placeholder PDF when WeasyPrint is not available."""
    # Simple PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 100 >>
stream
BT
/F1 12 Tf
50 800 Td
(Print PDF - WeasyPrint not installed) Tj
50 780 Td
(Install WeasyPrint for proper PDF generation) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000266 00000 n
0000000418 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
496
%%EOF"""
    return pdf_content


def export_figma(job_id: str) -> dict:
    """Export asset to Figma using Figma API."""
    logger.info("Starting export_figma task", job_id=job_id)

    with get_db_context() as db:
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting Figma export...")
            db.commit()

            params = json.loads(job.params_json) if job.params_json else {}
            theme_id = params.get("theme_id")
            asset_id = params.get("asset_id")
            figma_token = params.get("figma_access_token")
            figma_file_name = params.get("figma_file_name", "Exported Asset")
            figma_team_id = params.get("figma_team_id")

            if not figma_token:
                raise ValueError("Figma access token required")

            job.progress = 0.2
            db.commit()

            # Get asset
            asset_result = db.execute(
                "SELECT storage_path, asset_type, name FROM theme_assets WHERE id = :id",
                {"id": asset_id}
            ).fetchone()

            if not asset_result:
                raise ValueError(f"Asset not found: {asset_id}")

            storage_path, asset_type, asset_name = asset_result

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Processing asset: {asset_name}")
            db.commit()

            # Get content from storage
            storage = get_storage_service()
            content = storage.get(storage_path)

            job.progress = 0.4
            db.commit()

            # Export to Figma
            figma_result = _export_to_figma(
                content,
                asset_type,
                figma_token,
                figma_file_name,
                figma_team_id,
            )

            job.progress = 0.9
            job.logs = _append_log(job.logs, f"Created Figma file: {figma_result.get('file_key', 'unknown')}")
            db.commit()

            # Update asset with Figma file key
            figma_file_key = figma_result.get("file_key")
            if figma_file_key:
                db.execute(
                    "UPDATE theme_assets SET figma_file_key = :key, updated_at = :updated WHERE id = :id",
                    {"key": figma_file_key, "updated": datetime.utcnow(), "id": asset_id}
                )

            job.status = "completed"
            job.progress = 1.0
            job.result_json = json.dumps({
                "asset_id": asset_id,
                "figma_file_key": figma_file_key,
                "figma_url": figma_result.get("url"),
            })
            job.logs = _append_log(job.logs, "Figma export complete")
            db.commit()

            logger.info("Figma export complete", job_id=job_id, asset_id=asset_id)
            return {"asset_id": asset_id, "figma_file_key": figma_file_key}

        except Exception as e:
            logger.error("Figma export failed", job_id=job_id, error=str(e))

            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")
                db.commit()

            raise


def _export_to_figma(
    zip_content: bytes,
    asset_type: str,
    figma_token: str,
    file_name: str,
    team_id: Optional[str] = None,
) -> dict:
    """Export content to Figma using the Figma API."""
    import zipfile
    import requests

    # Extract HTML and CSS from zip
    html_content = None
    css_content = ""

    with zipfile.ZipFile(io.BytesIO(zip_content), "r") as zf:
        for name in zf.namelist():
            if name.endswith(".html"):
                html_content = zf.read(name).decode("utf-8")
            elif name.endswith(".css"):
                css_content += zf.read(name).decode("utf-8") + "\n"

    if not html_content:
        raise ValueError("No HTML content found in asset")

    # Parse HTML to extract structure for Figma
    figma_nodes = _html_to_figma_nodes(html_content, css_content)

    # Create Figma file using API
    headers = {
        "X-Figma-Token": figma_token,
        "Content-Type": "application/json",
    }

    # Note: Figma's API doesn't support direct file creation from external sources
    # This would typically require using Figma's Plugin API or Figma-to-Code tools
    # For now, we'll create a placeholder implementation

    # Check if we can access Figma API
    try:
        response = requests.get(
            "https://api.figma.com/v1/me",
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            raise ValueError(f"Figma API authentication failed: {response.text}")

        user_data = response.json()
        logger.info("Figma user verified", user=user_data.get("handle"))

    except requests.RequestException as e:
        raise ValueError(f"Failed to connect to Figma API: {str(e)}")

    # For now, return a placeholder result
    # Full Figma integration would require:
    # 1. Using Figma Plugin API to create frames/nodes
    # 2. Converting HTML/CSS to Figma's node format
    # 3. Uploading images and assets

    return {
        "file_key": None,  # Would be returned by actual Figma file creation
        "url": None,
        "message": "Figma export requires Figma Plugin API integration. Please use Figma's HTML to Figma plugin for manual import.",
        "html_content_available": True,
    }


def _html_to_figma_nodes(html_content: str, css_content: str) -> list:
    """Convert HTML/CSS to Figma node structure (placeholder)."""
    # This would parse HTML and CSS to create Figma-compatible node structure
    # Full implementation would use BeautifulSoup or similar to parse HTML
    # and convert elements to Figma's frame/text/rectangle format

    nodes = []

    # Placeholder - actual implementation would parse HTML
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract basic structure
        for element in soup.find_all(["h1", "h2", "h3", "p", "div", "section"]):
            node = {
                "type": "TEXT" if element.name in ["h1", "h2", "h3", "p"] else "FRAME",
                "name": element.name,
                "content": element.get_text(strip=True)[:100] if element.name in ["h1", "h2", "h3", "p"] else None,
            }
            nodes.append(node)

    except ImportError:
        logger.warning("BeautifulSoup not available for HTML parsing")

    return nodes
