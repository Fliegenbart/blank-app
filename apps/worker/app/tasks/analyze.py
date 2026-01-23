import io
import json
import traceback
from datetime import datetime
import structlog

from sqlalchemy.orm import Session

from app.database import get_db_context
from app.storage import get_storage_service
from app.parsers import PPTXParser, PDFParser
from app.analyzers import BrandAnalyzer

logger = structlog.get_logger()


def analyze_upload(job_id: str) -> dict:
    """
    Analyze an uploaded document and create a brand profile.

    Args:
        job_id: The job ID to process

    Returns:
        dict with profile_id and version
    """
    logger.info("Starting analyze_upload task", job_id=job_id)

    with get_db_context() as db:
        try:
            # Import models here to avoid circular imports
            from app.models import Job, Upload, Brand, BrandProfile

            # Get job
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            # Update status
            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting analysis...")
            db.commit()

            # Get upload
            upload = db.query(Upload).filter(Upload.id == job.upload_id).first()
            if not upload:
                raise ValueError(f"Upload not found: {job.upload_id}")

            # Get brand
            brand = db.query(Brand).filter(Brand.id == job.brand_id).first()
            if not brand:
                raise ValueError(f"Brand not found: {job.brand_id}")

            # Get file from storage
            storage = get_storage_service()
            file_data = storage.get_file(upload.storage_path)
            if not file_data:
                raise ValueError(f"File not found in storage: {upload.storage_path}")

            job.progress = 0.2
            job.logs = _append_log(job.logs, f"Retrieved file: {upload.original_filename}")
            db.commit()

            # Parse document
            logger.info("Parsing document", file_type=upload.file_type)

            if upload.file_type in ("pptx", "ppt"):
                parser = PPTXParser()
            elif upload.file_type == "pdf":
                parser = PDFParser()
            else:
                raise ValueError(f"Unsupported file type: {upload.file_type}")

            parsed_doc = parser.parse(file_data)
            parsed_doc.filename = upload.original_filename

            job.progress = 0.4
            job.logs = _append_log(job.logs, f"Parsed {len(parsed_doc.pages)} pages")
            db.commit()

            # Store debug artifacts
            _store_debug_artifacts(job_id, parsed_doc, storage)

            job.progress = 0.5
            job.logs = _append_log(job.logs, "Stored debug artifacts")
            db.commit()

            # Analyze brand
            logger.info("Analyzing brand")
            analyzer = BrandAnalyzer()
            profile_data = analyzer.analyze(parsed_doc, brand.name)

            job.progress = 0.8
            job.logs = _append_log(job.logs, "Brand analysis complete")
            db.commit()

            # Generate summary
            summary_md = analyzer.generate_summary(profile_data)

            # Get next version number
            latest_profile = (
                db.query(BrandProfile)
                .filter(BrandProfile.brand_id == brand.id)
                .order_by(BrandProfile.version.desc())
                .first()
            )
            new_version = (latest_profile.version + 1) if latest_profile else 1

            # Create brand profile
            profile = BrandProfile(
                brand_id=brand.id,
                version=new_version,
                profile_json=json.dumps(profile_data),
                summary_md=summary_md,
                source_upload_id=upload.id,
                source_job_id=job.id,
            )
            db.add(profile)
            db.flush()

            # Update job
            job.status = "completed"
            job.progress = 1.0
            job.result_json = json.dumps({
                "profile_id": profile.id,
                "version": new_version,
            })
            job.logs = _append_log(job.logs, f"Created profile v{new_version}")

            # Update upload status
            upload.status = "processed"

            db.commit()

            logger.info(
                "Analysis complete",
                job_id=job_id,
                profile_id=profile.id,
                version=new_version,
            )

            return {
                "profile_id": profile.id,
                "version": new_version,
            }

        except Exception as e:
            logger.error("Analysis failed", job_id=job_id, error=str(e))

            # Update job with error
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")
                db.commit()

            raise


def _store_debug_artifacts(job_id: str, parsed_doc, storage) -> None:
    """Store debug artifacts for the job."""
    # Store rendered pages
    for i, page in enumerate(parsed_doc.pages):
        if page.rendered_image:
            storage.store_debug_artifact(
                job_id,
                f"page_{i+1}.{page.rendered_image.format}",
                io.BytesIO(page.rendered_image.data),
                f"image/{page.rendered_image.format}",
            )

    # Store extracted text
    all_text = parsed_doc.get_all_text()
    if all_text:
        storage.store_debug_artifact(
            job_id,
            "extracted_text.txt",
            io.BytesIO(all_text.encode("utf-8")),
            "text/plain",
        )

    # Store theme data
    if parsed_doc.theme:
        theme_json = json.dumps({
            "color_scheme": parsed_doc.theme.color_scheme,
            "font_scheme": parsed_doc.theme.font_scheme,
            "accent_colors": parsed_doc.theme.accent_colors,
        }, indent=2)
        storage.store_debug_artifact(
            job_id,
            "theme.json",
            io.BytesIO(theme_json.encode("utf-8")),
            "application/json",
        )


def _append_log(logs: str, message: str) -> str:
    """Append a message to the logs with timestamp."""
    timestamp = datetime.utcnow().isoformat()
    new_log = f"[{timestamp}] {message}"
    if logs:
        return f"{logs}\n{new_log}"
    return new_log


# Models need to be imported for SQLAlchemy to work properly
# These are imported at the module level to ensure they're registered
def _import_models():
    """Import models to ensure they're registered with SQLAlchemy."""
    from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float, Boolean, DateTime
    from sqlalchemy.orm import relationship
    from sqlalchemy import func
    from app.database import Base

    class Job(Base):
        __tablename__ = "jobs"
        id = Column(String(36), primary_key=True)
        brand_id = Column(String(36), nullable=False)
        created_by = Column(String(36), nullable=False)
        job_type = Column(String(50), nullable=False)
        status = Column(String(50), nullable=False)
        progress = Column(Float, default=0.0)
        upload_id = Column(String(36), nullable=True)
        profile_version = Column(Integer, nullable=True)
        params_json = Column(Text, nullable=True)
        result_json = Column(Text, nullable=True)
        output_id = Column(String(36), nullable=True)
        logs = Column(Text, nullable=True)
        error_message = Column(Text, nullable=True)
        rq_job_id = Column(String(100), nullable=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    class Upload(Base):
        __tablename__ = "uploads"
        id = Column(String(36), primary_key=True)
        brand_id = Column(String(36), nullable=False)
        uploaded_by = Column(String(36), nullable=False)
        original_filename = Column(String(255), nullable=False)
        file_type = Column(String(50), nullable=False)
        file_size = Column(Integer, nullable=False)
        storage_path = Column(String(500), nullable=False)
        status = Column(String(50), default="uploaded")
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    class Brand(Base):
        __tablename__ = "brands"
        id = Column(String(36), primary_key=True)
        name = Column(String(255), nullable=False)
        slug = Column(String(255), nullable=False)
        description = Column(String(1000), nullable=True)
        organization_id = Column(String(36), nullable=False)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    class BrandProfile(Base):
        __tablename__ = "brand_profiles"
        id = Column(String(36), primary_key=True, default=lambda: __import__("uuid").uuid4().__str__())
        brand_id = Column(String(36), nullable=False)
        version = Column(Integer, nullable=False)
        profile_json = Column(Text, nullable=False)
        summary_md = Column(Text, nullable=True)
        source_upload_id = Column(String(36), nullable=True)
        source_job_id = Column(String(36), nullable=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    class Output(Base):
        __tablename__ = "outputs"
        id = Column(String(36), primary_key=True, default=lambda: __import__("uuid").uuid4().__str__())
        brand_id = Column(String(36), nullable=False)
        job_id = Column(String(36), nullable=True)
        output_type = Column(String(50), nullable=False)
        name = Column(String(255), nullable=False)
        description = Column(String(1000), nullable=True)
        storage_path = Column(String(500), nullable=False)
        file_size = Column(Integer, nullable=True)
        content_type = Column(String(100), nullable=True)
        metadata_json = Column(Text, nullable=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    return Job, Upload, Brand, BrandProfile, Output


# Create models module for worker
Job, Upload, Brand, BrandProfile, Output = _import_models()

# Add to app.models
import sys

class ModelsModule:
    Job = Job
    Upload = Upload
    Brand = Brand
    BrandProfile = BrandProfile
    Output = Output

sys.modules['app.models'] = ModelsModule()
