import os
import io
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
from functools import lru_cache
import structlog

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class StorageBackend(ABC):
    """Abstract storage backend interface."""

    @abstractmethod
    def put_file(self, path: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        """Store a file and return the storage path."""
        pass

    @abstractmethod
    def get_file(self, path: str) -> Optional[bytes]:
        """Retrieve a file by path."""
        pass

    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """Delete a file by path."""
        pass

    @abstractmethod
    def get_presigned_url(self, path: str, expires: int = 3600) -> Optional[str]:
        """Get a presigned URL for file access."""
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
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
        """Ensure the bucket exists."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("Created MinIO bucket", bucket=self.bucket)
        except S3Error as e:
            logger.error("Failed to create bucket", error=str(e))

    def put_file(self, path: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        """Store a file in MinIO."""
        try:
            # Get file size
            data.seek(0, 2)
            size = data.tell()
            data.seek(0)

            self.client.put_object(
                self.bucket,
                path,
                data,
                size,
                content_type=content_type,
            )
            logger.info("Stored file in MinIO", path=path, size=size)
            return path
        except S3Error as e:
            logger.error("Failed to store file", path=path, error=str(e))
            raise

    def get_file(self, path: str) -> Optional[bytes]:
        """Retrieve a file from MinIO."""
        try:
            response = self.client.get_object(self.bucket, path)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error("Failed to get file", path=path, error=str(e))
            return None

    def delete_file(self, path: str) -> bool:
        """Delete a file from MinIO."""
        try:
            self.client.remove_object(self.bucket, path)
            logger.info("Deleted file from MinIO", path=path)
            return True
        except S3Error as e:
            logger.error("Failed to delete file", path=path, error=str(e))
            return False

    def get_presigned_url(self, path: str, expires: int = 3600) -> Optional[str]:
        """Get a presigned URL for file access."""
        try:
            from datetime import timedelta
            url = self.client.presigned_get_object(
                self.bucket,
                path,
                expires=timedelta(seconds=expires),
            )
            return url
        except S3Error as e:
            logger.error("Failed to generate presigned URL", path=path, error=str(e))
            return None

    def file_exists(self, path: str) -> bool:
        """Check if a file exists in MinIO."""
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
        """Get full filesystem path."""
        return os.path.join(self.base_path, path)

    def put_file(self, path: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        """Store a file locally."""
        full_path = self._get_full_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(data.read())

        logger.info("Stored file locally", path=path)
        return path

    def get_file(self, path: str) -> Optional[bytes]:
        """Retrieve a file from local storage."""
        full_path = self._get_full_path(path)
        try:
            with open(full_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            logger.error("File not found", path=path)
            return None

    def delete_file(self, path: str) -> bool:
        """Delete a file from local storage."""
        full_path = self._get_full_path(path)
        try:
            os.remove(full_path)
            logger.info("Deleted file locally", path=path)
            return True
        except FileNotFoundError:
            return False

    def get_presigned_url(self, path: str, expires: int = 3600) -> Optional[str]:
        """Local storage doesn't support presigned URLs."""
        return None

    def file_exists(self, path: str) -> bool:
        """Check if a file exists locally."""
        return os.path.exists(self._get_full_path(path))


class DatabaseStorageBackend(StorageBackend):
    """PostgreSQL database storage backend - stores files as BLOBs."""

    def put_file(self, path: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        """Store a file in database."""
        from app.core.database import SessionLocal
        from app.models.file_blob import FileBlob

        file_data = data.read()
        size = len(file_data)

        db = SessionLocal()
        try:
            # Check if file already exists
            existing = db.query(FileBlob).filter(FileBlob.path == path).first()
            if existing:
                existing.data = file_data
                existing.content_type = content_type
                existing.size = size
            else:
                blob = FileBlob(
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
        from app.core.database import SessionLocal
        from app.models.file_blob import FileBlob

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
        from app.core.database import SessionLocal
        from app.models.file_blob import FileBlob

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

    def get_presigned_url(self, path: str, expires: int = 3600) -> Optional[str]:
        """Database storage doesn't support presigned URLs."""
        return None

    def file_exists(self, path: str) -> bool:
        """Check if a file exists in database."""
        from app.core.database import SessionLocal
        from app.models.file_blob import FileBlob

        db = SessionLocal()
        try:
            return db.query(FileBlob).filter(FileBlob.path == path).first() is not None
        finally:
            db.close()


class StorageService:
    """High-level storage service with backend abstraction."""

    def __init__(self, backend: StorageBackend):
        self.backend = backend

    def store_upload(self, brand_id: str, upload_id: str, filename: str, data: BinaryIO, content_type: str) -> str:
        """Store an uploaded file."""
        path = f"uploads/{brand_id}/{upload_id}/{filename}"
        return self.backend.put_file(path, data, content_type)

    def store_debug_artifact(self, job_id: str, filename: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        """Store a debug artifact for a job."""
        path = f"debug/{job_id}/{filename}"
        return self.backend.put_file(path, data, content_type)

    def store_output(self, brand_id: str, output_id: str, filename: str, data: BinaryIO, content_type: str) -> str:
        """Store a generated output."""
        path = f"outputs/{brand_id}/{output_id}/{filename}"
        return self.backend.put_file(path, data, content_type)

    def store_profile_asset(self, brand_id: str, version: int, filename: str, data: BinaryIO, content_type: str) -> str:
        """Store a brand profile asset."""
        path = f"profiles/{brand_id}/v{version}/{filename}"
        return self.backend.put_file(path, data, content_type)

    def get_file(self, path: str) -> Optional[bytes]:
        """Get a file by path."""
        return self.backend.get_file(path)

    def delete_file(self, path: str) -> bool:
        """Delete a file by path."""
        return self.backend.delete_file(path)

    def get_download_url(self, path: str, expires: int = 3600) -> Optional[str]:
        """Get a download URL for a file."""
        return self.backend.get_presigned_url(path, expires)

    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        return self.backend.file_exists(path)

    def store(self, path: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Store raw bytes at a given path."""
        return self.backend.put_file(path, io.BytesIO(data), content_type)

    def get(self, path: str) -> Optional[bytes]:
        """Get file content by path (alias for get_file)."""
        return self.backend.get_file(path)

    def delete(self, path: str) -> bool:
        """Delete a file by path (alias for delete_file)."""
        return self.backend.delete_file(path)


@lru_cache()
def get_storage_service() -> StorageService:
    """Get the storage service instance."""
    if settings.USE_LOCAL_STORAGE:
        backend = LocalStorageBackend()
    else:
        try:
            backend = MinIOBackend()
        except Exception as e:
            logger.warning("MinIO unavailable, falling back to database storage", error=str(e))
            backend = DatabaseStorageBackend()

    return StorageService(backend)
