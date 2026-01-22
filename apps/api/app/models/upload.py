from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class Upload(Base, TimestampMixin):
    """Upload model - represents an uploaded file."""

    __tablename__ = "uploads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand_id = Column(String(36), ForeignKey("brands.id"), nullable=False)
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    # File info
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, pptx
    file_size = Column(Integer, nullable=False)  # bytes
    storage_path = Column(String(500), nullable=False)  # path in storage

    # Status
    status = Column(String(50), default="uploaded", nullable=False)  # uploaded, processing, processed, failed

    # Relationships
    brand = relationship("Brand", back_populates="uploads")
    user = relationship("User")

    def __repr__(self):
        return f"<Upload {self.original_filename}>"
