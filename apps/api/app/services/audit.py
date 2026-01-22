import json
from typing import Optional, Any, Dict
import structlog

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

logger = structlog.get_logger()


class AuditService:
    """Service for audit logging."""

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        brand_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            brand_id=brand_id,
            details_json=json.dumps(details) if details else None,
        )
        self.db.add(audit_log)
        self.db.commit()

        logger.info(
            "Audit log created",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            brand_id=brand_id,
        )

        return audit_log

    def log_job_created(self, job_id: str, job_type: str, user_id: str, brand_id: str):
        """Log job creation."""
        return self.log(
            action="job.created",
            resource_type="job",
            resource_id=job_id,
            user_id=user_id,
            brand_id=brand_id,
            details={"job_type": job_type},
        )

    def log_profile_created(self, profile_id: str, version: int, user_id: str, brand_id: str):
        """Log brand profile creation."""
        return self.log(
            action="profile.created",
            resource_type="brand_profile",
            resource_id=profile_id,
            user_id=user_id,
            brand_id=brand_id,
            details={"version": version},
        )

    def log_output_created(self, output_id: str, output_type: str, user_id: str, brand_id: str):
        """Log output creation."""
        return self.log(
            action="output.created",
            resource_type="output",
            resource_id=output_id,
            user_id=user_id,
            brand_id=brand_id,
            details={"output_type": output_type},
        )

    def log_upload_created(self, upload_id: str, filename: str, user_id: str, brand_id: str):
        """Log upload creation."""
        return self.log(
            action="upload.created",
            resource_type="upload",
            resource_id=upload_id,
            user_id=user_id,
            brand_id=brand_id,
            details={"filename": filename},
        )
