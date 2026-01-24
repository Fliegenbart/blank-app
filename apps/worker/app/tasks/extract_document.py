"""Theme document extraction task."""
import json
import traceback
from datetime import datetime
import structlog
from sqlalchemy import text

from app.database import get_db_context
from app.storage import get_storage_service
from app.parsers import PDFParser, PPTXParser
from app.tasks.analyze import Job

logger = structlog.get_logger()


def _append_log(logs, message: str) -> str:
    timestamp = datetime.utcnow().isoformat()
    entry = f"[{timestamp}] {message}"
    return f"{logs}\n{entry}" if logs else entry


def extract_theme_document(job_id: str) -> dict:
    """Extract text from a theme document and store it."""
    logger.info("Starting extract_theme_document task", job_id=job_id)

    with get_db_context() as db:
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")

            job.status = "running"
            job.progress = 0.1
            job.logs = _append_log(job.logs, "Starting document extraction...")
            db.commit()

            params = json.loads(job.params_json) if job.params_json else {}
            document_id = params.get("theme_document_id")
            if not document_id:
                raise ValueError("theme_document_id missing in job params")

            result = db.execute(
                text("SELECT storage_path, file_type FROM theme_documents WHERE id = :id"),
                {"id": document_id},
            ).fetchone()

            if not result:
                raise ValueError(f"Theme document not found: {document_id}")

            storage_path, file_type = result

            storage = get_storage_service()
            file_data = storage.get_file(storage_path)
            if not file_data:
                raise ValueError(f"File not found in storage: {storage_path}")

            job.progress = 0.3
            job.logs = _append_log(job.logs, "Loaded document from storage")
            db.commit()

            if file_type in ("pptx", "ppt"):
                parser = PPTXParser()
            elif file_type == "pdf":
                parser = PDFParser()
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            parsed_doc = parser.parse(file_data)
            extracted_text = parsed_doc.get_all_text()

            job.progress = 0.7
            job.logs = _append_log(job.logs, "Extracted text from document")
            db.commit()

            db.execute(
                text(
                    """
                    UPDATE theme_documents
                    SET extracted_text = :text, status = :status, updated_at = :updated
                    WHERE id = :id
                    """
                ),
                {
                    "text": extracted_text,
                    "status": "completed",
                    "updated": datetime.utcnow(),
                    "id": document_id,
                },
            )

            job.status = "completed"
            job.progress = 1.0
            job.result_json = json.dumps({"theme_document_id": document_id})
            job.logs = _append_log(job.logs, "Document extraction complete")
            db.commit()

            return {"theme_document_id": document_id}

        except Exception as e:
            logger.error("Document extraction failed", job_id=job_id, error=str(e))

            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.logs = _append_log(job.logs, f"Error: {str(e)}\n{traceback.format_exc()}")
                db.commit()

            if "document_id" in locals():
                db.execute(
                    text(
                        """
                        UPDATE theme_documents
                        SET status = :status, updated_at = :updated
                        WHERE id = :id
                        """
                    ),
                    {"status": "failed", "updated": datetime.utcnow(), "id": document_id},
                )
                db.commit()

            raise
