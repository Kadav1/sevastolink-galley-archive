"""
Pantry suggestion endpoint.

POST /pantry/suggest — AI-powered cooking suggestions based on available ingredients.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.ai.lm_studio_client import LMStudioClient
from src.ai.pantry_suggester import PantryErrorKind, suggest_pantry
from src.config.settings import settings
from src.db.database import get_db
from src.schemas.ai_outputs import PantryQueryIn, PantrySuggestionOut
from src.schemas.common import ApiResponse, error_detail
from src.services import recipe_service

router = APIRouter(prefix="/pantry", tags=["pantry"])


@router.post("/suggest", response_model=ApiResponse[PantrySuggestionOut], status_code=status.HTTP_200_OK)
async def pantry_suggest(body: PantryQueryIn, db: Session = Depends(get_db)):
    """
    Suggest recipes based on available ingredients.

    Fetches up to 20 non-archived archive recipes as context for the AI.
    The AI returns direct matches, near matches, and quick ideas.
    Requires LM_STUDIO_ENABLED=true.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail=error_detail("ai_disabled", "AI pantry suggestion is not enabled. Set LM_STUDIO_ENABLED=true."),
        )

    if not body.available_ingredients:
        raise HTTPException(
            status_code=422,
            detail=error_detail("validation_error", "available_ingredients must not be empty."),
        )

    archive_recipes_orm, _ = recipe_service.list_recipes(
        db, archived=False, limit=20, offset=0, sort="updated_at_desc"
    )
    archive_dicts = [
        {
            "title": r.title,
            "dish_role": r.dish_role,
            "primary_cuisine": r.primary_cuisine,
            "complexity": r.complexity,
            "ingredients": [],
        }
        for r in archive_recipes_orm
    ]

    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = suggest_pantry(
        client,
        available_ingredients=body.available_ingredients,
        archive_recipes=archive_dicts,
        must_use=body.must_use or None,
        excluded=body.excluded or None,
        cuisine_preferences=body.cuisine_preferences or None,
        time_limit_minutes=body.time_limit_minutes,
        model=settings.lm_studio_model,
    )

    if err is not None:
        if err.kind == PantryErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail=error_detail("ai_unavailable", "AI service is unavailable."),
            )
        raise HTTPException(
            status_code=502,
            detail=error_detail(f"ai_{err.kind.value}", err.message),
        )

    return ApiResponse(data=PantrySuggestionOut.model_validate(result.payload))
