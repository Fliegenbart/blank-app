import json
import traceback
from datetime import datetime
import structlog

from app.database import get_db_context, Base
from app.scrapers import WebsiteScraper

logger = structlog.get_logger()


def scrape_reference(job_id: str) -> dict:
    """
    Scrape reference websites and analyze structure.

    Args:
        job_id: The job ID to process

    Returns:
        dict with reference_id and status
    """
    logger.info("Starting scrape_reference task", job_id=job_id)

    with get_db_context() as db:
        try:
            # Import models
            from app.tasks.scrape import Job, Reference

            # Get job
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            # Update status
            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting reference scraping...")
            db.commit()

            # Get params
            params = json.loads(job.params_json) if job.params_json else {}
            reference_id = params.get("reference_id")
            urls = params.get("urls", [])

            if not reference_id:
                raise ValueError("Missing reference_id in job params")

            if not urls:
                raise ValueError("No URLs to scrape")

            # Get reference
            reference = db.query(Reference).filter(Reference.id == reference_id).first()
            if not reference:
                raise ValueError(f"Reference not found: {reference_id}")

            # Update reference status
            reference.status = "scraping"
            db.commit()

            job.progress = 0.2
            job.logs = _append_log(job.logs, f"Scraping {len(urls)} URLs...")
            db.commit()

            # Scrape websites
            scraper = WebsiteScraper(headless=True)
            structure = scraper.scrape_urls(urls, take_screenshots=False)

            job.progress = 0.7
            job.logs = _append_log(job.logs, f"Scraped {len(structure.pages)} pages")
            db.commit()

            # Update reference status
            reference.status = "analyzing"
            db.commit()

            job.progress = 0.8
            job.logs = _append_log(job.logs, "Analyzing structure...")
            db.commit()

            # Store results
            reference.scraped_data_json = json.dumps({
                "pages": [p.to_dict() for p in structure.pages]
            })
            reference.structure_json = json.dumps({
                "common_sections": [s.value for s in structure.common_sections],
                "section_order_pattern": [s.value for s in structure.section_order_pattern],
                "key_messaging": structure.key_messaging,
                "navigation_structure": structure.navigation_structure,
                "content_themes": structure.content_themes,
                "cta_patterns": structure.cta_patterns,
                "total_word_count": structure.total_word_count,
            })
            reference.page_count = len(structure.pages)
            reference.total_word_count = structure.total_word_count
            reference.status = "completed"

            # Update job
            job.status = "completed"
            job.progress = 1.0
            job.result_json = json.dumps({
                "reference_id": reference_id,
                "page_count": len(structure.pages),
                "total_word_count": structure.total_word_count,
            })
            job.logs = _append_log(job.logs, "Reference scraping complete")

            db.commit()

            logger.info(
                "Reference scraping complete",
                job_id=job_id,
                reference_id=reference_id,
                page_count=len(structure.pages),
            )

            return {
                "reference_id": reference_id,
                "page_count": len(structure.pages),
            }

        except Exception as e:
            logger.error("Reference scraping failed", job_id=job_id, error=str(e))

            # Update job with error
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")
                db.commit()

                # Also update reference if we have it
                params = json.loads(job.params_json) if job.params_json else {}
                reference_id = params.get("reference_id")
                if reference_id:
                    reference = db.query(Reference).filter(Reference.id == reference_id).first()
                    if reference:
                        reference.status = "failed"
                        reference.error_message = str(e)
                        db.commit()

            raise


def _append_log(logs: str, message: str) -> str:
    """Append a message to the logs with timestamp."""
    timestamp = datetime.utcnow().isoformat()
    new_log = f"[{timestamp}] {message}"
    if logs:
        return f"{logs}\n{new_log}"
    return new_log


# Define Reference model for worker
def _define_reference_model():
    """Define Reference model for the worker."""
    from sqlalchemy import Column, String, Integer, Text, DateTime
    from sqlalchemy import func

    class Reference(Base):
        __tablename__ = "references"
        id = Column(String(36), primary_key=True)
        brand_id = Column(String(36), nullable=False)
        created_by = Column(String(36), nullable=False)
        name = Column(String(255), nullable=False)
        description = Column(String(1000), nullable=True)
        urls_json = Column(Text, nullable=False)
        status = Column(String(20), nullable=False, default="pending")
        error_message = Column(Text, nullable=True)
        scraped_data_json = Column(Text, nullable=True)
        structure_json = Column(Text, nullable=True)
        screenshots_path = Column(String(500), nullable=True)
        page_count = Column(Integer, nullable=True)
        total_word_count = Column(Integer, nullable=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    return Reference


# Import Job from analyze task and define Reference
from app.tasks.analyze import Job
Reference = _define_reference_model()
