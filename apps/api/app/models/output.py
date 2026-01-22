from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class Output(Base, TimestampMixin):
    """Output model - generated content."""

    __tablename__ = "outputs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand_id = Column(String(36), ForeignKey("brands.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=True)

    # Output info
    output_type = Column(String(50), nullable=False)  # website, newsletter
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    # Storage
    storage_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)

    # Metadata
    metadata_json = Column(Text, nullable=True)

    # Relationships
    brand = relationship("Brand", back_populates="outputs")

    def __repr__(self):
        return f"<Output {self.name} type={self.output_type}>"
