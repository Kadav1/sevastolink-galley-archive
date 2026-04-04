"""
Media service.

Handles source-file attachment for intake jobs.
Saves uploaded files to the local media directory, records metadata
in media_assets, and links the asset to the intake job.
"""
import hashlib
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.schemas.common import error_detail
from src.models.intake import IntakeJob
from src.models.media import MediaAsset
from src.models.recipe import Recipe

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_BYTES = 20 * 1024 * 1024  # 20 MB

_MIME_EXT: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}

_MIME_KIND: dict[str, str] = {
    "image/jpeg": "source_image",
    "image/png": "source_image",
    "image/webp": "source_image",
    "application/pdf": "source_pdf",
}


def get_by_id(db: Session, asset_id: str) -> MediaAsset | None:
    """Return a MediaAsset by id, or None if not found."""
    return db.get(MediaAsset, asset_id)


def _save_file(file: UploadFile, subdirectory: str) -> tuple[str, str, str, int]:
    """
    Validate, read, and persist an uploaded file.

    Returns (asset_id, relative_path, checksum, byte_size).
    Raises HTTPException on invalid MIME type or oversized file.
    """
    mime = file.content_type or ""
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=422,
            detail=error_detail("unsupported_media_type", f"Unsupported file type '{mime}'. Allowed: image/jpeg, image/png, image/webp, application/pdf."),
        )

    chunks: list[bytes] = []
    total = 0
    chunk_size = 64 * 1024  # 64 KB
    while True:
        chunk = file.file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_BYTES:
            raise HTTPException(status_code=422, detail=error_detail("file_too_large", "File exceeds the 20 MB limit."))
        chunks.append(chunk)
    data = b"".join(chunks)

    asset_id = str(uuid.uuid4())
    ext = _MIME_EXT[mime]
    relative_path = f"{subdirectory}/{asset_id}{ext}"
    dest: Path = settings.media_dir / relative_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)

    return asset_id, relative_path, hashlib.sha256(data).hexdigest(), len(data)


def _create_asset(db: Session, file: UploadFile, subdirectory: str) -> MediaAsset:
    """Create, persist, and return a new MediaAsset."""
    mime = file.content_type or ""
    asset_id, relative_path, checksum, byte_size = _save_file(file, subdirectory)
    asset = MediaAsset(
        id=asset_id,
        asset_kind=_MIME_KIND[mime],
        original_filename=file.filename,
        mime_type=mime,
        relative_path=relative_path,
        checksum=checksum,
        byte_size=byte_size,
    )
    db.add(asset)
    return asset


def attach_to_intake_job(db: Session, job_id: str, file: UploadFile) -> MediaAsset:
    """Save an uploaded file, create a MediaAsset record, and link it to the job."""
    job = db.get(IntakeJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Intake job not found."))
    asset = _create_asset(db, file, "intake")
    job.source_media_asset_id = asset.id
    db.commit()
    db.refresh(asset)
    return asset


def attach_to_recipe(db: Session, recipe: Recipe, file: UploadFile) -> MediaAsset:
    """Save an uploaded file, create a MediaAsset record, and set it as the recipe cover."""
    asset = _create_asset(db, file, "recipes")
    recipe.cover_media_asset_id = asset.id
    db.commit()
    db.refresh(asset)
    return asset
