import io
import json
import traceback
from datetime import datetime
import structlog

from app.database import get_db_context
from app.storage import get_storage_service
from app.generators import WebsiteGenerator, NewsletterGenerator
from app.tasks.analyze import Job, Brand, BrandProfile, Output

logger = structlog.get_logger()


def generate_website(job_id: str) -> dict:
    """
    Generate a website based on brand profile.

    Args:
        job_id: The job ID to process

    Returns:
        dict with output_id
    """
    logger.info("Starting generate_website task", job_id=job_id)

    with get_db_context() as db:
        try:
            # Get job
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            # Update status
            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting website generation...")
            db.commit()

            # Get brand
            brand = db.query(Brand).filter(Brand.id == job.brand_id).first()
            if not brand:
                raise ValueError(f"Brand not found: {job.brand_id}")

            # Get profile
            profile = (
                db.query(BrandProfile)
                .filter(
                    BrandProfile.brand_id == brand.id,
                    BrandProfile.version == job.profile_version,
                )
                .first()
            )
            if not profile:
                raise ValueError(f"Profile version {job.profile_version} not found")

            profile_data = json.loads(profile.profile_json)

            job.progress = 0.2
            job.logs = _append_log(job.logs, f"Loaded profile v{profile.version}")
            db.commit()

            # Get job params
            params = json.loads(job.params_json) if job.params_json else {}
            topic = params.get("topic", "Website")
            pages = params.get("pages", [{"slug": "index", "title": "Home", "sections": ["hero", "features", "cta"]}])
            brief = params.get("brief")

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Generating {len(pages)} pages for '{topic}'")
            db.commit()

            # Generate website
            generator = WebsiteGenerator()
            zip_data = generator.generate(profile_data, topic, pages, brief)

            job.progress = 0.7
            job.logs = _append_log(job.logs, "Website generated")
            db.commit()

            # Store output
            storage = get_storage_service()

            output = Output(
                brand_id=brand.id,
                job_id=job.id,
                output_type="website",
                name=f"{topic.replace(' ', '-').lower()}-website.zip",
                description=f"Website for '{topic}' based on profile v{profile.version}",
                storage_path="",  # Will be set after storage
                file_size=len(zip_data),
                content_type="application/zip",
                metadata_json=json.dumps({
                    "topic": topic,
                    "pages": [p.get("slug") for p in pages],
                    "profile_version": profile.version,
                }),
            )
            db.add(output)
            db.flush()

            storage_path = storage.store_output(
                brand.id,
                output.id,
                output.name,
                io.BytesIO(zip_data),
                "application/zip",
            )
            output.storage_path = storage_path

            job.progress = 0.9
            job.logs = _append_log(job.logs, f"Stored output: {output.name}")
            db.commit()

            # Update job
            job.status = "completed"
            job.progress = 1.0
            job.output_id = output.id
            job.result_json = json.dumps({
                "output_id": output.id,
                "filename": output.name,
                "file_size": output.file_size,
            })
            job.logs = _append_log(job.logs, "Website generation complete")
            db.commit()

            logger.info(
                "Website generation complete",
                job_id=job_id,
                output_id=output.id,
            )

            return {
                "output_id": output.id,
                "filename": output.name,
            }

        except Exception as e:
            logger.error("Website generation failed", job_id=job_id, error=str(e))

            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")
                db.commit()

            raise


def generate_newsletter(job_id: str) -> dict:
    """
    Generate a newsletter based on brand profile.

    Args:
        job_id: The job ID to process

    Returns:
        dict with output_id
    """
    logger.info("Starting generate_newsletter task", job_id=job_id)

    with get_db_context() as db:
        try:
            # Get job
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            # Update status
            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting newsletter generation...")
            db.commit()

            # Get brand
            brand = db.query(Brand).filter(Brand.id == job.brand_id).first()
            if not brand:
                raise ValueError(f"Brand not found: {job.brand_id}")

            # Get profile
            profile = (
                db.query(BrandProfile)
                .filter(
                    BrandProfile.brand_id == brand.id,
                    BrandProfile.version == job.profile_version,
                )
                .first()
            )
            if not profile:
                raise ValueError(f"Profile version {job.profile_version} not found")

            profile_data = json.loads(profile.profile_json)

            job.progress = 0.2
            job.logs = _append_log(job.logs, f"Loaded profile v{profile.version}")
            db.commit()

            # Get job params
            params = json.loads(job.params_json) if job.params_json else {}
            topic = params.get("topic", "Newsletter")
            offer = params.get("offer")
            cta = params.get("cta", "Learn More")
            subject_line = params.get("subject_line")
            preview_text = params.get("preview_text")

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Generating newsletter for '{topic}'")
            db.commit()

            # Generate newsletter
            generator = NewsletterGenerator()
            zip_data = generator.generate(
                profile_data,
                topic,
                offer=offer,
                cta=cta,
                subject_line=subject_line,
                preview_text=preview_text,
            )

            job.progress = 0.7
            job.logs = _append_log(job.logs, "Newsletter generated")
            db.commit()

            # Store output
            storage = get_storage_service()

            output = Output(
                brand_id=brand.id,
                job_id=job.id,
                output_type="newsletter",
                name=f"{topic.replace(' ', '-').lower()}-newsletter.zip",
                description=f"Newsletter for '{topic}' based on profile v{profile.version}",
                storage_path="",
                file_size=len(zip_data),
                content_type="application/zip",
                metadata_json=json.dumps({
                    "topic": topic,
                    "offer": offer,
                    "cta": cta,
                    "profile_version": profile.version,
                }),
            )
            db.add(output)
            db.flush()

            storage_path = storage.store_output(
                brand.id,
                output.id,
                output.name,
                io.BytesIO(zip_data),
                "application/zip",
            )
            output.storage_path = storage_path

            job.progress = 0.9
            job.logs = _append_log(job.logs, f"Stored output: {output.name}")
            db.commit()

            # Update job
            job.status = "completed"
            job.progress = 1.0
            job.output_id = output.id
            job.result_json = json.dumps({
                "output_id": output.id,
                "filename": output.name,
                "file_size": output.file_size,
            })
            job.logs = _append_log(job.logs, "Newsletter generation complete")
            db.commit()

            logger.info(
                "Newsletter generation complete",
                job_id=job_id,
                output_id=output.id,
            )

            return {
                "output_id": output.id,
                "filename": output.name,
            }

        except Exception as e:
            logger.error("Newsletter generation failed", job_id=job_id, error=str(e))

            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")
                db.commit()

            raise


def _append_log(logs: str, message: str) -> str:
    """Append a message to the logs with timestamp."""
    timestamp = datetime.utcnow().isoformat()
    new_log = f"[{timestamp}] {message}"
    if logs:
        return f"{logs}\n{new_log}"
    return new_log
