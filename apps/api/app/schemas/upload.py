from pydantic import BaseModel
from datetime import datetime


class UploadResponse(BaseModel):
    """Schema for upload response."""

    id: str
    brand_id: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
