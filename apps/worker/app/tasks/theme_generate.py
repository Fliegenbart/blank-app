"""Theme asset generation tasks."""
import io
import json
import traceback
from datetime import datetime
from typing import Optional
import structlog

from app.database import get_db_context
from app.storage import get_storage_service
from app.tasks.analyze import Job, Brand, BrandProfile

logger = structlog.get_logger()


def _append_log(logs: Optional[str], message: str) -> str:
    """Append a message to the logs with timestamp."""
    timestamp = datetime.utcnow().isoformat()
    new_log = f"[{timestamp}] {message}"
    if logs:
        return f"{logs}\n{new_log}"
    return new_log


def _get_theme_context(db, theme_id: str, profile_data: dict) -> dict:
    """Build theme context from theme data and brand profile."""
    from sqlalchemy.orm import Session

    # Import Theme model
    from sqlalchemy import Column, String, Text
    from sqlalchemy.ext.declarative import declarative_base

    # Query theme directly
    result = db.execute(
        "SELECT name, description, context_json FROM themes WHERE id = :id",
        {"id": theme_id}
    ).fetchone()

    if not result:
        return {"profile": profile_data, "theme": {}}

    theme_name, theme_description, context_json = result

    theme_context = {}
    if context_json:
        try:
            theme_context = json.loads(context_json)
        except json.JSONDecodeError:
            pass

    # Get theme documents
    docs_result = db.execute(
        "SELECT name, document_type, extracted_text FROM theme_documents WHERE theme_id = :id",
        {"id": theme_id}
    ).fetchall()

    documents = []
    for doc in docs_result:
        documents.append({
            "name": doc[0],
            "type": doc[1],
            "text": doc[2] or ""
        })

    return {
        "profile": profile_data,
        "theme": {
            "name": theme_name,
            "description": theme_description,
            "context": theme_context,
            "documents": documents
        }
    }


def _update_theme_asset(db, asset_id: str, status: str, **kwargs):
    """Update theme asset status and fields."""
    updates = {"status": status, "updated_at": datetime.utcnow()}
    updates.update(kwargs)

    set_clause = ", ".join([f"{k} = :{k}" for k in updates.keys()])
    db.execute(
        f"UPDATE theme_assets SET {set_clause} WHERE id = :asset_id",
        {"asset_id": asset_id, **updates}
    )


def _update_theme_job_progress(db, theme_job_id: str):
    """Update theme job progress based on completed assets."""
    if not theme_job_id:
        return

    # Get theme job
    result = db.execute(
        "SELECT total_assets FROM theme_jobs WHERE id = :id",
        {"id": theme_job_id}
    ).fetchone()

    if not result:
        return

    total_assets = result[0]

    # Count completed and failed assets
    completed = db.execute(
        """SELECT COUNT(*) FROM theme_assets ta
           JOIN jobs j ON ta.job_id = j.id
           WHERE j.params_json LIKE :pattern AND ta.status = 'completed'""",
        {"pattern": f'%"theme_job_id": "{theme_job_id}"%'}
    ).scalar() or 0

    failed = db.execute(
        """SELECT COUNT(*) FROM theme_assets ta
           JOIN jobs j ON ta.job_id = j.id
           WHERE j.params_json LIKE :pattern AND ta.status = 'failed'""",
        {"pattern": f'%"theme_job_id": "{theme_job_id}"%'}
    ).scalar() or 0

    progress = ((completed + failed) / total_assets * 100) if total_assets > 0 else 0
    status = "completed" if (completed + failed) >= total_assets else "running"

    db.execute(
        """UPDATE theme_jobs SET
           completed_assets = :completed,
           failed_assets = :failed,
           progress = :progress,
           status = :status,
           updated_at = :updated_at
           WHERE id = :id""",
        {
            "id": theme_job_id,
            "completed": completed,
            "failed": failed,
            "progress": progress,
            "status": status,
            "updated_at": datetime.utcnow()
        }
    )


def generate_flyer(job_id: str) -> dict:
    """Generate a flyer based on brand profile and theme context."""
    logger.info("Starting generate_flyer task", job_id=job_id)

    with get_db_context() as db:
        try:
            # Get job
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting flyer generation...")
            db.commit()

            # Get params
            params = json.loads(job.params_json) if job.params_json else {}
            theme_id = params.get("theme_id")
            theme_job_id = params.get("theme_job_id")
            asset_id = params.get("asset_id")

            # Get brand and profile
            brand = db.query(Brand).filter(Brand.id == job.brand_id).first()
            if not brand:
                raise ValueError(f"Brand not found: {job.brand_id}")

            profile = db.query(BrandProfile).filter(
                BrandProfile.brand_id == brand.id,
                BrandProfile.version == job.profile_version,
            ).first()
            if not profile:
                raise ValueError(f"Profile version {job.profile_version} not found")

            profile_data = json.loads(profile.profile_json)

            job.progress = 0.2
            job.logs = _append_log(job.logs, f"Loaded profile v{profile.version}")
            db.commit()

            # Get theme context
            context = _get_theme_context(db, theme_id, profile_data)

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Generating flyer for theme: {context['theme'].get('name', 'Unknown')}")
            db.commit()

            # Update asset status
            _update_theme_asset(db, asset_id, "generating")
            db.commit()

            # Generate flyer
            from app.generators.flyer_generator import FlyerGenerator
            generator = FlyerGenerator()
            zip_data = generator.generate(context)

            job.progress = 0.7
            job.logs = _append_log(job.logs, "Flyer generated")
            db.commit()

            # Store output
            storage = get_storage_service()
            theme_name = context['theme'].get('name', 'theme').lower().replace(' ', '-')
            filename = f"{theme_name}-flyer.zip"
            storage_path = f"themes/{theme_id}/assets/{asset_id}/{filename}"
            storage.store(storage_path, zip_data, "application/zip")

            job.progress = 0.9
            job.logs = _append_log(job.logs, f"Stored: {storage_path}")
            db.commit()

            # Update asset
            _update_theme_asset(
                db, asset_id,
                status="completed",
                storage_path=storage_path,
                file_size=len(zip_data),
                content_type="application/zip"
            )

            # Update theme job progress
            _update_theme_job_progress(db, theme_job_id)

            # Complete job
            job.status = "completed"
            job.progress = 1.0
            job.result_json = json.dumps({"asset_id": asset_id, "storage_path": storage_path})
            job.logs = _append_log(job.logs, "Flyer generation complete")
            db.commit()

            logger.info("Flyer generation complete", job_id=job_id, asset_id=asset_id)
            return {"asset_id": asset_id}

        except Exception as e:
            logger.error("Flyer generation failed", job_id=job_id, error=str(e))

            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                params = json.loads(job.params_json) if job.params_json else {}
                asset_id = params.get("asset_id")
                theme_job_id = params.get("theme_job_id")

                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")

                if asset_id:
                    _update_theme_asset(db, asset_id, "failed", error_message=str(e))

                if theme_job_id:
                    _update_theme_job_progress(db, theme_job_id)

                db.commit()

            raise


def generate_brochure(job_id: str) -> dict:
    """Generate a brochure based on brand profile and theme context."""
    logger.info("Starting generate_brochure task", job_id=job_id)

    with get_db_context() as db:
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting brochure generation...")
            db.commit()

            params = json.loads(job.params_json) if job.params_json else {}
            theme_id = params.get("theme_id")
            theme_job_id = params.get("theme_job_id")
            asset_id = params.get("asset_id")

            brand = db.query(Brand).filter(Brand.id == job.brand_id).first()
            profile = db.query(BrandProfile).filter(
                BrandProfile.brand_id == brand.id,
                BrandProfile.version == job.profile_version,
            ).first()
            profile_data = json.loads(profile.profile_json)

            job.progress = 0.2
            db.commit()

            context = _get_theme_context(db, theme_id, profile_data)

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Generating brochure for: {context['theme'].get('name', 'Unknown')}")
            db.commit()

            _update_theme_asset(db, asset_id, "generating")
            db.commit()

            from app.generators.brochure_generator import BrochureGenerator
            generator = BrochureGenerator()
            zip_data = generator.generate(context)

            job.progress = 0.7
            db.commit()

            storage = get_storage_service()
            theme_name = context['theme'].get('name', 'theme').lower().replace(' ', '-')
            filename = f"{theme_name}-brochure.zip"
            storage_path = f"themes/{theme_id}/assets/{asset_id}/{filename}"
            storage.store(storage_path, zip_data, "application/zip")

            _update_theme_asset(db, asset_id, "completed",
                storage_path=storage_path, file_size=len(zip_data), content_type="application/zip")
            _update_theme_job_progress(db, theme_job_id)

            job.status = "completed"
            job.progress = 1.0
            job.result_json = json.dumps({"asset_id": asset_id})
            job.logs = _append_log(job.logs, "Brochure generation complete")
            db.commit()

            return {"asset_id": asset_id}

        except Exception as e:
            logger.error("Brochure generation failed", job_id=job_id, error=str(e))
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                params = json.loads(job.params_json) if job.params_json else {}
                job.status = "failed"
                job.error_message = str(e)
                if params.get("asset_id"):
                    _update_theme_asset(db, params["asset_id"], "failed", error_message=str(e))
                if params.get("theme_job_id"):
                    _update_theme_job_progress(db, params["theme_job_id"])
                db.commit()
            raise


def generate_teaser_script(job_id: str) -> dict:
    """Generate a teaser script based on brand profile and theme context."""
    logger.info("Starting generate_teaser_script task", job_id=job_id)

    with get_db_context() as db:
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            job.status = "running"
            job.progress = 0.1
            db.commit()

            params = json.loads(job.params_json) if job.params_json else {}
            theme_id = params.get("theme_id")
            theme_job_id = params.get("theme_job_id")
            asset_id = params.get("asset_id")

            brand = db.query(Brand).filter(Brand.id == job.brand_id).first()
            profile = db.query(BrandProfile).filter(
                BrandProfile.brand_id == brand.id,
                BrandProfile.version == job.profile_version,
            ).first()
            profile_data = json.loads(profile.profile_json)

            context = _get_theme_context(db, theme_id, profile_data)

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Generating teaser script for: {context['theme'].get('name', 'Unknown')}")
            db.commit()

            _update_theme_asset(db, asset_id, "generating")
            db.commit()

            from app.generators.teaser_script_generator import TeaserScriptGenerator
            generator = TeaserScriptGenerator()
            zip_data = generator.generate(context)

            job.progress = 0.7
            db.commit()

            storage = get_storage_service()
            theme_name = context['theme'].get('name', 'theme').lower().replace(' ', '-')
            storage_path = f"themes/{theme_id}/assets/{asset_id}/{theme_name}-teaser-script.zip"
            storage.store(storage_path, zip_data, "application/zip")

            _update_theme_asset(db, asset_id, "completed",
                storage_path=storage_path, file_size=len(zip_data), content_type="application/zip")
            _update_theme_job_progress(db, theme_job_id)

            job.status = "completed"
            job.progress = 1.0
            job.result_json = json.dumps({"asset_id": asset_id})
            job.logs = _append_log(job.logs, "Teaser script generation complete")
            db.commit()

            return {"asset_id": asset_id}

        except Exception as e:
            logger.error("Teaser script generation failed", job_id=job_id, error=str(e))
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                params = json.loads(job.params_json) if job.params_json else {}
                job.status = "failed"
                job.error_message = str(e)
                if params.get("asset_id"):
                    _update_theme_asset(db, params["asset_id"], "failed", error_message=str(e))
                if params.get("theme_job_id"):
                    _update_theme_job_progress(db, params["theme_job_id"])
                db.commit()
            raise


def generate_presentation(job_id: str) -> dict:
    """Generate a presentation based on brand profile and theme context."""
    logger.info("Starting generate_presentation task", job_id=job_id)

    with get_db_context() as db:
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            job.status = "running"
            job.progress = 0.1
            db.commit()

            params = json.loads(job.params_json) if job.params_json else {}
            theme_id = params.get("theme_id")
            theme_job_id = params.get("theme_job_id")
            asset_id = params.get("asset_id")

            brand = db.query(Brand).filter(Brand.id == job.brand_id).first()
            profile = db.query(BrandProfile).filter(
                BrandProfile.brand_id == brand.id,
                BrandProfile.version == job.profile_version,
            ).first()
            profile_data = json.loads(profile.profile_json)

            context = _get_theme_context(db, theme_id, profile_data)

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Generating presentation for: {context['theme'].get('name', 'Unknown')}")
            db.commit()

            _update_theme_asset(db, asset_id, "generating")
            db.commit()

            from app.generators.presentation_generator import PresentationGenerator
            generator = PresentationGenerator()
            pptx_data = generator.generate(context)

            job.progress = 0.7
            db.commit()

            storage = get_storage_service()
            theme_name = context['theme'].get('name', 'theme').lower().replace(' ', '-')
            storage_path = f"themes/{theme_id}/assets/{asset_id}/{theme_name}-presentation.pptx"
            storage.store(storage_path, pptx_data, "application/vnd.openxmlformats-officedocument.presentationml.presentation")

            _update_theme_asset(db, asset_id, "completed",
                storage_path=storage_path, file_size=len(pptx_data),
                content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
            _update_theme_job_progress(db, theme_job_id)

            job.status = "completed"
            job.progress = 1.0
            job.result_json = json.dumps({"asset_id": asset_id})
            job.logs = _append_log(job.logs, "Presentation generation complete")
            db.commit()

            return {"asset_id": asset_id}

        except Exception as e:
            logger.error("Presentation generation failed", job_id=job_id, error=str(e))
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                params = json.loads(job.params_json) if job.params_json else {}
                job.status = "failed"
                job.error_message = str(e)
                if params.get("asset_id"):
                    _update_theme_asset(db, params["asset_id"], "failed", error_message=str(e))
                if params.get("theme_job_id"):
                    _update_theme_job_progress(db, params["theme_job_id"])
                db.commit()
            raise


def generate_banner_ads(job_id: str) -> dict:
    """Generate banner ads based on brand profile and theme context."""
    logger.info("Starting generate_banner_ads task", job_id=job_id)

    with get_db_context() as db:
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            job.status = "running"
            job.progress = 0.1
            db.commit()

            params = json.loads(job.params_json) if job.params_json else {}
            theme_id = params.get("theme_id")
            theme_job_id = params.get("theme_job_id")
            asset_id = params.get("asset_id")

            brand = db.query(Brand).filter(Brand.id == job.brand_id).first()
            profile = db.query(BrandProfile).filter(
                BrandProfile.brand_id == brand.id,
                BrandProfile.version == job.profile_version,
            ).first()
            profile_data = json.loads(profile.profile_json)

            context = _get_theme_context(db, theme_id, profile_data)

            job.progress = 0.3
            job.logs = _append_log(job.logs, f"Generating banner ads for: {context['theme'].get('name', 'Unknown')}")
            db.commit()

            _update_theme_asset(db, asset_id, "generating")
            db.commit()

            from app.generators.banner_generator import BannerGenerator
            generator = BannerGenerator()
            zip_data = generator.generate(context)

            job.progress = 0.7
            db.commit()

            storage = get_storage_service()
            theme_name = context['theme'].get('name', 'theme').lower().replace(' ', '-')
            storage_path = f"themes/{theme_id}/assets/{asset_id}/{theme_name}-banners.zip"
            storage.store(storage_path, zip_data, "application/zip")

            _update_theme_asset(db, asset_id, "completed",
                storage_path=storage_path, file_size=len(zip_data), content_type="application/zip")
            _update_theme_job_progress(db, theme_job_id)

            job.status = "completed"
            job.progress = 1.0
            job.result_json = json.dumps({"asset_id": asset_id})
            job.logs = _append_log(job.logs, "Banner ads generation complete")
            db.commit()

            return {"asset_id": asset_id}

        except Exception as e:
            logger.error("Banner ads generation failed", job_id=job_id, error=str(e))
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                params = json.loads(job.params_json) if job.params_json else {}
                job.status = "failed"
                job.error_message = str(e)
                if params.get("asset_id"):
                    _update_theme_asset(db, params["asset_id"], "failed", error_message=str(e))
                if params.get("theme_job_id"):
                    _update_theme_job_progress(db, params["theme_job_id"])
                db.commit()
            raise
