from sqlalchemy import Column, String, Integer, LargeBinary, DateTime, func

from app.models.base import Base, generate_uuid


class FileBlob(Base):
    """FileBlob model - stores files in database."""

    __tablename__ = "file_blobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    path = Column(String(500), nullable=False, unique=True, index=True)
    data = Column(LargeBinary, nullable=False)
    content_type = Column(String(100), nullable=False, default="application/octet-stream")
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<FileBlob {self.path}>"
