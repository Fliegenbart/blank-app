from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin, generate_uuid


class BrandRole(str, enum.Enum):
    """Roles for brand members."""

    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class Brand(Base, TimestampMixin):
    """Brand model - represents a brand within an organization."""

    __tablename__ = "brands"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="brands")
    members = relationship("BrandMember", back_populates="brand", cascade="all, delete-orphan")
    uploads = relationship("Upload", back_populates="brand", cascade="all, delete-orphan")
    profiles = relationship("BrandProfile", back_populates="brand", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="brand", cascade="all, delete-orphan")
    outputs = relationship("Output", back_populates="brand", cascade="all, delete-orphan")
    references = relationship("Reference", back_populates="brand", cascade="all, delete-orphan")
    themes = relationship("Theme", back_populates="brand", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Brand {self.name}>"


class BrandMember(Base, TimestampMixin):
    """Brand member - links users to brands with roles."""

    __tablename__ = "brand_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    brand_id = Column(String(36), ForeignKey("brands.id"), nullable=False)
    role = Column(SQLEnum(BrandRole), nullable=False, default=BrandRole.VIEWER)

    # Relationships
    user = relationship("User", back_populates="brand_memberships")
    brand = relationship("Brand", back_populates="members")

    def __repr__(self):
        return f"<BrandMember user={self.user_id} brand={self.brand_id} role={self.role}>"
