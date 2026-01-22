from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime


class JobCreate(BaseModel):
    """Schema for job creation."""

    job_type: str
    upload_id: Optional[str] = None
    profile_version: Optional[int] = None
    params: Optional[Dict[str, Any]] = None


class JobResponse(BaseModel):
    """Schema for job response."""

    id: str
    brand_id: str
    job_type: str
    status: str
    progress: float
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    logs: Optional[str] = None
    output_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
