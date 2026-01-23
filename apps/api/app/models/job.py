from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin, generate_uuid


class JobStatus(str, enum.Enum):
    """Job status enum."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, enum.Enum):
    """Job type enum."""

    ANALYZE = "analyze"
    GENERATE_WEBSITE = "generate_website"
    GENERATE_NEWSLETTER = "generate_newsletter"
    SCRAPE_REFERENCE = "scrape_reference"
    GENERATE_LANDING_PAGE = "generate_landing_page"
    GENERATE_SOCIAL_MEDIA = "generate_social_media"
    GENERATE_EMAIL = "generate_email"


class Job(Base, TimestampMixin):
    """Job model - represents an async job."""

    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand_id = Column(String(36), ForeignKey("brands.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Job info
    job_type = Column(String(50), nullable=False)
    status = Column(String(50), default=JobStatus.PENDING.value, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0

    # References
    upload_id = Column(String(36), ForeignKey("uploads.id"), nullable=True)
    profile_version = Column(Integer, nullable=True)  # for generate jobs

    # Params (JSON string)
    params_json = Column(Text, nullable=True)

    # Results
    result_json = Column(Text, nullable=True)
    output_id = Column(String(36), ForeignKey("outputs.id"), nullable=True)

    # Logging
    logs = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # RQ job reference
    rq_job_id = Column(String(100), nullable=True)

    # Relationships
    brand = relationship("Brand", back_populates="jobs")
    user = relationship("User")
    upload = relationship("Upload")
    output = relationship("Output", foreign_keys=[output_id])

    def __repr__(self):
        return f"<Job {self.id} type={self.job_type} status={self.status}>"
