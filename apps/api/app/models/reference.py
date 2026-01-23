from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin, generate_uuid


class ReferenceStatus(str, enum.Enum):
    """Reference processing status."""
    PENDING = "pending"
    SCRAPING = "scraping"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class Reference(Base, TimestampMixin):
    """Reference model - website references for asset generation."""

    __tablename__ = "references"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand_id = Column(String(36), ForeignKey("brands.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Reference info
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    # URLs (stored as JSON array)
    urls_json = Column(Text, nullable=False)

    # Status
    status = Column(String(20), nullable=False, default=ReferenceStatus.PENDING.value)
    error_message = Column(Text, nullable=True)

    # Scraped data (stored as JSON)
    scraped_data_json = Column(Text, nullable=True)

    # Analyzed structure (stored as JSON)
    structure_json = Column(Text, nullable=True)

    # Storage path for screenshots
    screenshots_path = Column(String(500), nullable=True)

    # Stats
    page_count = Column(Integer, nullable=True)
    total_word_count = Column(Integer, nullable=True)

    # Relationships
    brand = relationship("Brand", back_populates="references")
    user = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Reference {self.name} brand={self.brand_id}>"
