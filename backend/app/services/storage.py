"""File/image upload handling (spec section 28: validate MIME type & size)."""
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

Path(settings.LOCAL_STORAGE_PATH).mkdir(parents=True, exist_ok=True)


async def save_upload(file: UploadFile, subdirectory: str = "complaints") -> str:
    if file.content_type not in settings.allowed_image_mime_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}",
        )

    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
        )

    extension = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}.get(file.content_type, "")
    filename = f"{uuid.uuid4()}{extension}"

    target_dir = Path(settings.LOCAL_STORAGE_PATH) / subdirectory
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    target_path.write_bytes(contents)

    return f"/uploads/{subdirectory}/{filename}"
