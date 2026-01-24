from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.brand import BrandRole


class BrandCreate(BaseModel):
    """Schema for brand creation."""

    name: str
    slug: str
    description: Optional[str] = None
    organization_id: Optional[str] = None  # Will create org if not provided


class BrandUpdate(BaseModel):
    """Schema for brand update."""

    name: Optional[str] = None
    description: Optional[str] = None


class BrandMemberResponse(BaseModel):
    """Schema for brand member response."""

    id: str
    user_id: str
    email: str
    full_name: Optional[str]
    role: BrandRole
    created_at: datetime

    class Config:
        from_attributes = True


class BrandResponse(BaseModel):
    """Schema for brand response."""

    id: str
    name: str
    slug: str
    description: Optional[str]
    organization_id: str
    created_at: datetime
    updated_at: datetime
    members: Optional[List[BrandMemberResponse]] = None

    class Config:
        from_attributes = True


class BrandMemberCreate(BaseModel):
    """Schema for adding a member to a brand."""

    user_email: str
    role: BrandRole = BrandRole.VIEWER


class BrandMemberUpdate(BaseModel):
    """Schema for updating a brand member."""

    role: BrandRole
