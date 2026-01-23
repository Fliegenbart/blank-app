from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class Organization(Base, TimestampMixin):
    """Organization model - top level container for brands."""

    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(1000), nullable=True)

    # Relationships
    brands = relationship("Brand", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization {self.name}>"
