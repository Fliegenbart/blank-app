from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class OutputResponse(BaseModel):
    """Schema for output response."""

    id: str
    brand_id: str
    output_type: str
    name: str
    description: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    created_at: datetime
    download_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
