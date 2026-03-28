"""
Settings routes.

GET  /settings  — read current settings (persisted prefs + read-only runtime signal)
PATCH /settings — update one or more persisted product preferences
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.settings import settings as app_settings
from src.db.database import get_db
from src.schemas.common import ApiResponse
from src.schemas.settings_schema import SettingsOut, SettingsUpdate
from src.services import settings_service

router = APIRouter(prefix="/settings", tags=["settings"])


def _build_out(db: Session) -> SettingsOut:
    persisted = settings_service.get_all(db)
    return SettingsOut(
        default_verification_state=persisted["default_verification_state"],  # type: ignore[arg-type]
        library_default_sort=persisted["library_default_sort"],  # type: ignore[arg-type]
        ai_enabled=app_settings.lm_studio_enabled,
    )


@router.get("", response_model=ApiResponse[SettingsOut])
async def get_settings(db: Session = Depends(get_db)):
    """Return current product settings."""
    return ApiResponse(data=_build_out(db))


@router.patch("", response_model=ApiResponse[SettingsOut])
async def update_settings(body: SettingsUpdate, db: Session = Depends(get_db)):
    """Update one or more persisted product preferences."""
    updates: dict[str, str] = {}
    if body.default_verification_state is not None:
        updates[settings_service.KEY_DEFAULT_VERIFICATION_STATE] = body.default_verification_state
    if body.library_default_sort is not None:
        updates[settings_service.KEY_LIBRARY_DEFAULT_SORT] = body.library_default_sort

    if updates:
        settings_service.update(db, updates)

    return ApiResponse(data=_build_out(db))
