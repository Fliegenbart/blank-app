import os
import io
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
from functools import lru_cache
import structlog

from minio import Minio
from minio.error import S3Error

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class StorageBackend(ABC):
    """Abstract storage backend interface."""

    @abstractmethod
    def put_file(self, path: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        pass

    @abstractmethod
    def get_file(self, path: str) -> Optional[bytes]:
        pass

    @abstractmethod
    def delete_file(self, path: str) -> bool:
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        pass


class MinIOBackend(StorageBackend):
    """MinIO/S3 storage backend."""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            logger.error("Failed to create bucket", error=str(e))

    def put_file(self, path: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        try:
            data.seek(0, 2)
            size = data.tell()
            data.seek(0)
            self.client.put_object(self.bucket, path, data, size, content_type=content_type)
            return path
        except S3Error as e:
            logger.error("Failed to store file", path=path, error=str(e))
            raise

    def get_file(self, path: str) -> Optional[bytes]:
        try:
            response = self.client.get_object(self.bucket, path)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error:
            return None

    def delete_file(self, path: str) -> bool:
        try:
            self.client.remove_object(self.bucket, path)
            return True
        except S3Error:
            return False

    def file_exists(self, path: str) -> bool:
        try:
            self.client.stat_object(self.bucket, path)
            return True
        except S3Error:
            return False


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend."""

    def __init__(self):
        self.base_path = settings.LOCAL_STORAGE_PATH
        os.makedirs(self.base_path, exist_ok=True)

    def _get_full_path(self, path: str) -> str:
        return os.path.join(self.base_path, path)

    def put_file(self, path: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        full_path = self._get_full_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(data.read())
        return path

    def get_file(self, path: str) -> Optional[bytes]:
        full_path = self._get_full_path(path)
        try:
            with open(full_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def delete_file(self, path: str) -> bool:
        full_path = self._get_full_path(path)
        try:
            os.remove(full_path)
            return True
        except FileNotFoundError:
            return False

    def file_exists(self, path: str) -> bool:
        return os.path.exists(self._get_full_path(path))


class DatabaseStorageBackend(StorageBackend):
    """PostgreSQL database storage backend - stores files as BLOBs."""

    def put_file(self, path: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        """Store a file in database."""
        from app.database import SessionLocal
        from sqlalchemy import Column, String, Integer, LargeBinary, DateTime, func
        from sqlalchemy.orm import declarative_base
        import uuid

        Base = declarative_base()

        class FileBlob(Base):
            __tablename__ = "file_blobs"
            id = Column(String(36), primary_key=True)
            path = Column(String(500), nullable=False, unique=True, index=True)
            data = Column(LargeBinary, nullable=False)
            content_type = Column(String(100), nullable=False)
            size = Column(Integer, nullable=False)
            created_at = Column(DateTime, nullable=False, server_default=func.now())

        file_data = data.read()
        size = len(file_data)

        db = SessionLocal()
        try:
            existing = db.query(FileBlob).filter(FileBlob.path == path).first()
            if existing:
                existing.data = file_data
                existing.content_type = content_type
                existing.size = size
            else:
                blob = FileBlob(
                    id=str(uuid.uuid4()),
                    path=path,
                    data=file_data,
                    content_type=content_type,
                    size=size,
                )
                db.add(blob)
            db.commit()
            logger.info("Stored file in database", path=path, size=size)
            return path
        except Exception as e:
            db.rollback()
            logger.error("Failed to store file in database", path=path, error=str(e))
            raise
        finally:
            db.close()

    def get_file(self, path: str) -> Optional[bytes]:
        """Retrieve a file from database."""
        from app.database import SessionLocal
        from sqlalchemy import Column, String, Integer, LargeBinary, DateTime, func
        from sqlalchemy.orm import declarative_base

        Base = declarative_base()

        class FileBlob(Base):
            __tablename__ = "file_blobs"
            id = Column(String(36), primary_key=True)
            path = Column(String(500), nullable=False, unique=True, index=True)
            data = Column(LargeBinary, nullable=False)
            content_type = Column(String(100), nullable=False)
            size = Column(Integer, nullable=False)
            created_at = Column(DateTime, nullable=False, server_default=func.now())

        db = SessionLocal()
        try:
            blob = db.query(FileBlob).filter(FileBlob.path == path).first()
            if blob:
                return blob.data
            logger.error("File not found in database", path=path)
            return None
        finally:
            db.close()

    def delete_file(self, path: str) -> bool:
        """Delete a file from database."""
        from app.database import SessionLocal
        from sqlalchemy import Column, String, Integer, LargeBinary, DateTime, func
        from sqlalchemy.orm import declarative_base

        Base = declarative_base()

        class FileBlob(Base):
            __tablename__ = "file_blobs"
            id = Column(String(36), primary_key=True)
            path = Column(String(500), nullable=False, unique=True, index=True)
            data = Column(LargeBinary, nullable=False)
            content_type = Column(String(100), nullable=False)
            size = Column(Integer, nullable=False)
            created_at = Column(DateTime, nullable=False, server_default=func.now())

        db = SessionLocal()
        try:
            blob = db.query(FileBlob).filter(FileBlob.path == path).first()
            if blob:
                db.delete(blob)
                db.commit()
                logger.info("Deleted file from database", path=path)
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error("Failed to delete file from database", path=path, error=str(e))
            return False
        finally:
            db.close()

    def file_exists(self, path: str) -> bool:
        """Check if a file exists in database."""
        from app.database import SessionLocal
        from sqlalchemy import Column, String, Integer, LargeBinary, DateTime, func
        from sqlalchemy.orm import declarative_base

        Base = declarative_base()

        class FileBlob(Base):
            __tablename__ = "file_blobs"
            id = Column(String(36), primary_key=True)
            path = Column(String(500), nullable=False, unique=True, index=True)
            data = Column(LargeBinary, nullable=False)
            content_type = Column(String(100), nullable=False)
            size = Column(Integer, nullable=False)
            created_at = Column(DateTime, nullable=False, server_default=func.now())

        db = SessionLocal()
        try:
            return db.query(FileBlob).filter(FileBlob.path == path).first() is not None
        finally:
            db.close()


class StorageService:
    """High-level storage service."""

    def __init__(self, backend: StorageBackend):
        self.backend = backend

    def store_debug_artifact(self, job_id: str, filename: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        path = f"debug/{job_id}/{filename}"
        return self.backend.put_file(path, data, content_type)

    def store_output(self, brand_id: str, output_id: str, filename: str, data: BinaryIO, content_type: str) -> str:
        path = f"outputs/{brand_id}/{output_id}/{filename}"
        return self.backend.put_file(path, data, content_type)

    def store_profile_asset(self, brand_id: str, version: int, filename: str, data: BinaryIO, content_type: str) -> str:
        path = f"profiles/{brand_id}/v{version}/{filename}"
        return self.backend.put_file(path, data, content_type)

    def get_file(self, path: str) -> Optional[bytes]:
        return self.backend.get_file(path)


@lru_cache()
def get_storage_service() -> StorageService:
    """Get the storage service instance."""
    if settings.USE_LOCAL_STORAGE:
        backend = LocalStorageBackend()
    else:
        try:
            backend = MinIOBackend()
        except Exception as e:
            logger.warning("MinIO unavailable, using database storage", error=str(e))
            backend = DatabaseStorageBackend()
    return StorageService(backend)
