"""
Media routes.

POST /intake-jobs/{job_id}/media          — attach source image/PDF to an intake job
POST /recipes/{id_or_slug}/media          — attach cover image/PDF to a recipe
GET  /media-assets/{asset_id}             — retrieve asset metadata
GET  /media-assets/{asset_id}/file        — serve the asset binary
"""
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.db.database import get_db
from src.schemas.common import ApiResponse, error_detail
from src.schemas.media_schema import MediaAssetOut
from src.services import media_service, recipe_service

router = APIRouter(tags=["media"])


@router.post(
    "/intake-jobs/{job_id}/media",
    response_model=ApiResponse[MediaAssetOut],
)
async def attach_intake_media(
    job_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Attach a source image or PDF to an intake job.

    Accepted types: image/jpeg, image/png, image/webp, application/pdf. Max 20 MB.
    Sets intake_jobs.source_media_asset_id to the new asset id.
    """
    asset = media_service.attach_to_intake_job(db, job_id, file)
    return ApiResponse(data=MediaAssetOut.model_validate(asset))


@router.post(
    "/recipes/{id_or_slug}/media",
    response_model=ApiResponse[MediaAssetOut],
)
async def attach_recipe_media(
    id_or_slug: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Attach a cover image or PDF to a canonical recipe.

    Accepted types: image/jpeg, image/png, image/webp, application/pdf. Max 20 MB.
    Sets recipes.cover_media_asset_id to the new asset id.
    """
    recipe = recipe_service.get_recipe(db, id_or_slug)
    if recipe is None:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Recipe not found."))
    asset = media_service.attach_to_recipe(db, recipe, file)
    return ApiResponse(data=MediaAssetOut.model_validate(asset))


@router.get(
    "/media-assets/{asset_id}",
    response_model=ApiResponse[MediaAssetOut],
)
async def get_media_asset(
    asset_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve metadata for a media asset by id."""
    asset = media_service.get_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Media asset not found."))
    return ApiResponse(data=MediaAssetOut.model_validate(asset))


@router.get("/media-assets/{asset_id}/file")
async def serve_media_file(
    asset_id: str,
    db: Session = Depends(get_db),
):
    """Serve the raw bytes of a stored media asset.

    Returns the file with its original MIME type.
    Use this URL as the src for <img> elements or PDF embeds.
    """
    asset = media_service.get_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Media asset not found."))
    file_path: Path = settings.media_dir / asset.relative_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Asset file not found on disk."))
    return FileResponse(
        path=str(file_path),
        media_type=asset.mime_type or "application/octet-stream",
        filename=asset.original_filename,
    )
