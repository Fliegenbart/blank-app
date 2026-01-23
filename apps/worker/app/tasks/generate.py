import io
import json
import traceback
from datetime import datetime
import structlog

from app.database import get_db_context
from app.storage import get_storage_service
from app.generators import WebsiteGenerator, NewsletterGenerator, LandingPageGenerator, SocialMediaGenerator, EmailGenerator
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


def _get_reference_structure(db, reference_id: str) -> dict:
    """Get reference structure from database."""
    from app.tasks.scrape import Reference

    if not reference_id:
        return None

    reference = db.query(Reference).filter(Reference.id == reference_id).first()
    if not reference or not reference.structure_json:
        return None

    try:
        return json.loads(reference.structure_json)
    except json.JSONDecodeError:
        return None


def generate_landing_page(job_id: str) -> dict:
    """
    Generate a landing page based on brand profile and optional reference.

    Args:
        job_id: The job ID to process

    Returns:
        dict with output_id
    """
    logger.info("Starting generate_landing_page task", job_id=job_id)

    with get_db_context() as db:
        try:
            # Get job
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            # Update status
            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting landing page generation...")
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
            topic = params.get("topic", "Landing Page")
            sections = params.get("sections")
            reference_id = params.get("reference_id")

            # Get reference structure if provided
            reference_structure = _get_reference_structure(db, reference_id)
            if reference_structure:
                job.logs = _append_log(job.logs, "Using reference structure")
                db.commit()

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Generating landing page for '{topic}'")
            db.commit()

            # Generate landing page
            generator = LandingPageGenerator()
            zip_data = generator.generate(profile_data, topic, reference_structure, sections)

            job.progress = 0.7
            job.logs = _append_log(job.logs, "Landing page generated")
            db.commit()

            # Store output
            storage = get_storage_service()

            output = Output(
                brand_id=brand.id,
                job_id=job.id,
                output_type="landing_page",
                name=f"{topic.replace(' ', '-').lower()}-landing-page.zip",
                description=f"Landing page for '{topic}' based on profile v{profile.version}",
                storage_path="",
                file_size=len(zip_data),
                content_type="application/zip",
                metadata_json=json.dumps({
                    "topic": topic,
                    "profile_version": profile.version,
                    "reference_id": reference_id,
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
            job.logs = _append_log(job.logs, "Landing page generation complete")
            db.commit()

            logger.info(
                "Landing page generation complete",
                job_id=job_id,
                output_id=output.id,
            )

            return {
                "output_id": output.id,
                "filename": output.name,
            }

        except Exception as e:
            logger.error("Landing page generation failed", job_id=job_id, error=str(e))

            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")
                db.commit()

            raise


def generate_social_media(job_id: str) -> dict:
    """
    Generate social media content based on brand profile and optional reference.

    Args:
        job_id: The job ID to process

    Returns:
        dict with output_id
    """
    logger.info("Starting generate_social_media task", job_id=job_id)

    with get_db_context() as db:
        try:
            # Get job
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            # Update status
            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting social media content generation...")
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
            topic = params.get("topic", "Social Media Post")
            platforms = params.get("platforms", ["twitter", "linkedin", "instagram"])
            reference_id = params.get("reference_id")

            # Get reference structure if provided
            reference_structure = _get_reference_structure(db, reference_id)
            if reference_structure:
                job.logs = _append_log(job.logs, "Using reference structure")
                db.commit()

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Generating content for {', '.join(platforms)}")
            db.commit()

            # Generate social media content
            generator = SocialMediaGenerator()
            zip_data = generator.generate(profile_data, topic, platforms, reference_structure)

            job.progress = 0.7
            job.logs = _append_log(job.logs, "Social media content generated")
            db.commit()

            # Store output
            storage = get_storage_service()

            output = Output(
                brand_id=brand.id,
                job_id=job.id,
                output_type="social_media",
                name=f"{topic.replace(' ', '-').lower()}-social-media.zip",
                description=f"Social media content for '{topic}' based on profile v{profile.version}",
                storage_path="",
                file_size=len(zip_data),
                content_type="application/zip",
                metadata_json=json.dumps({
                    "topic": topic,
                    "platforms": platforms,
                    "profile_version": profile.version,
                    "reference_id": reference_id,
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
            job.logs = _append_log(job.logs, "Social media content generation complete")
            db.commit()

            logger.info(
                "Social media generation complete",
                job_id=job_id,
                output_id=output.id,
            )

            return {
                "output_id": output.id,
                "filename": output.name,
            }

        except Exception as e:
            logger.error("Social media generation failed", job_id=job_id, error=str(e))

            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")
                db.commit()

            raise


def generate_email(job_id: str) -> dict:
    """
    Generate email content based on brand profile and optional reference.

    Args:
        job_id: The job ID to process

    Returns:
        dict with output_id
    """
    logger.info("Starting generate_email task", job_id=job_id)

    with get_db_context() as db:
        try:
            # Get job
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            # Update status
            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting email content generation...")
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
            topic = params.get("topic", "Email")
            email_type = params.get("email_type", "newsletter")
            reference_id = params.get("reference_id")

            # Get reference structure if provided
            reference_structure = _get_reference_structure(db, reference_id)
            if reference_structure:
                job.logs = _append_log(job.logs, "Using reference structure")
                db.commit()

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Generating {email_type} email for '{topic}'")
            db.commit()

            # Generate email content
            generator = EmailGenerator()
            zip_data = generator.generate(profile_data, topic, email_type, reference_structure)

            job.progress = 0.7
            job.logs = _append_log(job.logs, "Email content generated")
            db.commit()

            # Store output
            storage = get_storage_service()

            output = Output(
                brand_id=brand.id,
                job_id=job.id,
                output_type="email",
                name=f"{topic.replace(' ', '-').lower()}-{email_type}.zip",
                description=f"{email_type.title()} email for '{topic}' based on profile v{profile.version}",
                storage_path="",
                file_size=len(zip_data),
                content_type="application/zip",
                metadata_json=json.dumps({
                    "topic": topic,
                    "email_type": email_type,
                    "profile_version": profile.version,
                    "reference_id": reference_id,
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
            job.logs = _append_log(job.logs, "Email content generation complete")
            db.commit()

            logger.info(
                "Email generation complete",
                job_id=job_id,
                output_id=output.id,
            )

            return {
                "output_id": output.id,
                "filename": output.name,
            }

        except Exception as e:
            logger.error("Email generation failed", job_id=job_id, error=str(e))

            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")
                db.commit()

            raise
