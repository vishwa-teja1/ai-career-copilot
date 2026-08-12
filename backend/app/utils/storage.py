"""
Storage abstraction so services never care whether a file lands on local
disk (dev) or S3 (production) - controlled purely by STORAGE_BACKEND.
"""
import os
import uuid
from abc import ABC, abstractmethod

from app.core.config import get_settings

settings = get_settings()


class StorageBackend(ABC):
    @abstractmethod
    def save(self, file_bytes: bytes, original_filename: str, prefix: str) -> str:
        """Persist the file and return a storage key/path."""

    @abstractmethod
    def load(self, storage_path: str) -> bytes:
        """Retrieve file bytes by storage key/path."""


class LocalStorageBackend(StorageBackend):
    def save(self, file_bytes: bytes, original_filename: str, prefix: str) -> str:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        ext = os.path.splitext(original_filename)[1]
        key = f"{prefix}/{uuid.uuid4()}{ext}"
        full_path = os.path.join(settings.UPLOAD_DIR, key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(file_bytes)
        return full_path

    def load(self, storage_path: str) -> bytes:
        with open(storage_path, "rb") as f:
            return f.read()


class S3StorageBackend(StorageBackend):
    def __init__(self):
        import boto3  # imported lazily so local dev doesn't need boto3 installed

        self._client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self._bucket = settings.S3_BUCKET_NAME

    def save(self, file_bytes: bytes, original_filename: str, prefix: str) -> str:
        ext = os.path.splitext(original_filename)[1]
        key = f"{prefix}/{uuid.uuid4()}{ext}"
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=file_bytes,
            ServerSideEncryption="AES256",  # encrypt resumes at rest
        )
        return key

    def load(self, storage_path: str) -> bytes:
        obj = self._client.get_object(Bucket=self._bucket, Key=storage_path)
        return obj["Body"].read()


def get_storage_backend() -> StorageBackend:
    if settings.STORAGE_BACKEND == "s3":
        return S3StorageBackend()
    return LocalStorageBackend()
