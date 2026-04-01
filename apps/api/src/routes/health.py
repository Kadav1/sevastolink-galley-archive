import sqlite3

from pydantic import BaseModel

from fastapi import APIRouter

from src.ai.lm_studio_client import LMStudioClient
from src.config.settings import settings
from src.schemas.common import ApiResponse

router = APIRouter()

ai_router = APIRouter()


def _db_ok() -> bool:
    """Ping the SQLite database. Returns True if reachable."""
    try:
        conn = sqlite3.connect(str(settings.db_path), timeout=2)
        conn.execute("SELECT 1")
        conn.close()
        return True
    except Exception:
        return False


@router.get("/health")
async def health() -> dict:
    db_reachable = _db_ok()
    return {
        "status": "ok" if db_reachable else "degraded",
        "service": "galley-api",
        "db": "ok" if db_reachable else "unreachable",
    }


class AiHealthOut(BaseModel):
    ai_enabled: bool
    reachable: bool | None
    model: str | None
    error: str | None


@ai_router.get("/health/ai", response_model=ApiResponse[AiHealthOut])
async def health_ai() -> ApiResponse[AiHealthOut]:
    """
    GET /api/v1/health/ai

    Returns the current AI connection status.
    - ai_enabled=false: LM_STUDIO_ENABLED is off; reachable and model are null.
    - ai_enabled=true, reachable=true: LM Studio is reachable at the configured URL.
    - ai_enabled=true, reachable=false: LM Studio is not reachable; error contains details.
    """
    if not settings.lm_studio_enabled:
        return ApiResponse(data=AiHealthOut(
            ai_enabled=False,
            reachable=None,
            model=None,
            error=None,
        ))

    client = LMStudioClient(settings.lm_studio_base_url)
    ok, err = client.check_availability()

    return ApiResponse(data=AiHealthOut(
        ai_enabled=True,
        reachable=ok,
        model=(settings.lm_studio_model or None) if ok else None,
        error=err.message if err else None,
    ))
