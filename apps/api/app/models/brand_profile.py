from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class BrandProfile(Base, TimestampMixin):
    """Brand profile model - versioned brand identity data."""

    __tablename__ = "brand_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand_id = Column(String(36), ForeignKey("brands.id"), nullable=False)
    version = Column(Integer, nullable=False)

    # Profile data
    profile_json = Column(Text, nullable=False)  # Full brand profile JSON
    summary_md = Column(Text, nullable=True)  # Markdown summary

    # Source tracking
    source_upload_id = Column(String(36), ForeignKey("uploads.id"), nullable=True)
    source_job_id = Column(String(36), ForeignKey("jobs.id"), nullable=True)

    # Relationships
    brand = relationship("Brand", back_populates="profiles")
    source_upload = relationship("Upload")
    source_job = relationship("Job")

    def __repr__(self):
        return f"<BrandProfile brand={self.brand_id} v{self.version}>"
