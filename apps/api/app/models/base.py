from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())
