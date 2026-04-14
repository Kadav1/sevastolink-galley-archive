import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.ai.lm_studio_client import LMStudioClient
from src.ai.metadata_suggester import MetadataErrorKind, suggest_metadata
from src.ai.rewriter import RewriteErrorKind, rewrite_recipe
from src.ai.similarity_engine import SimilarityErrorKind, find_similar_recipes
from src.config.settings import settings
from src.db.database import get_db
from src.schemas.ai_outputs import ArchiveRewriteOut, MetadataSuggestionOut, SimilarityIn, SimilarRecipesOut
from src.schemas.common import ApiResponse, ListMeta, ListResponse, error_detail
from src.schemas.ingredient_families import IngredientFamilyCount, IngredientFamiliesOut
from src.schemas.recipe import (
    RecipeArchiveResult,
    RecipeCreate,
    RecipeDetail,
    RecipeSummaryOut,
    RecipeUpdate,
    VerificationState,
)
from src.services import recipe_service

router = APIRouter(prefix="/recipes", tags=["recipes"])


def _detail(recipe) -> RecipeDetail:
    return RecipeDetail.from_orm_recipe(recipe)


def _summary(recipe) -> RecipeSummaryOut:
    return RecipeSummaryOut.from_orm_with_json(recipe)


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("/ingredient-families", response_model=ApiResponse[IngredientFamiliesOut])
async def list_ingredient_families(db: Session = Depends(get_db)):
    """Return ingredient family facet counts across the non-archived archive."""
    rows = recipe_service.ingredient_family_counts(db)
    return ApiResponse(
        data=IngredientFamiliesOut(
            families=[IngredientFamilyCount(**r) for r in rows],
            total=len(rows),
        )
    )


@router.get("", response_model=ListResponse[RecipeSummaryOut])
async def list_recipes(
    q: str | None = Query(None),
    verification_state: str | None = Query(None),
    favorite: bool | None = Query(None),
    archived: bool = Query(False),
    dish_role: str | None = Query(None),
    primary_cuisine: str | None = Query(None),
    technique_family: str | None = Query(None),
    complexity: str | None = Query(None),
    time_class: str | None = Query(None),
    sector: str | None = Query(None),
    operational_class: str | None = Query(None),
    heat_window: str | None = Query(None),
    ingredient_family: str | None = Query(None),
    sort: str = Query("updated_at_desc"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    recipes, total = recipe_service.list_recipes(
        db,
        q=q,
        verification_state=verification_state,
        favorite=favorite,
        archived=archived,
        dish_role=dish_role,
        primary_cuisine=primary_cuisine,
        technique_family=technique_family,
        complexity=complexity,
        time_class=time_class,
        sector=sector,
        operational_class=operational_class,
        heat_window=heat_window,
        ingredient_family=ingredient_family,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    return ListResponse(
        data=[_summary(r) for r in recipes],
        meta=ListMeta(total=total, limit=limit, offset=offset),
    )


# ── Create ────────────────────────────────────────────────────────────────────

@router.post("", response_model=ApiResponse[RecipeDetail], status_code=status.HTTP_201_CREATED)
async def create_recipe(data: RecipeCreate, db: Session = Depends(get_db)):
    recipe = recipe_service.create_recipe(db, data)
    db.commit()
    return ApiResponse(data=_detail(recipe))


# ── Get by ID or slug ─────────────────────────────────────────────────────────

@router.get("/{id_or_slug}", response_model=ApiResponse[RecipeDetail])
async def get_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    recipe = recipe_service.get_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    db.commit()
    return ApiResponse(data=_detail(recipe))


# ── Update ────────────────────────────────────────────────────────────────────

@router.patch("/{id_or_slug}", response_model=ApiResponse[RecipeDetail])
async def update_recipe(id_or_slug: str, data: RecipeUpdate, db: Session = Depends(get_db)):
    recipe = recipe_service.update_recipe(db, id_or_slug, data)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    db.commit()
    return ApiResponse(data=_detail(recipe))


# ── Archive / Unarchive ───────────────────────────────────────────────────────

@router.post("/{id_or_slug}/archive", response_model=ApiResponse[RecipeArchiveResult])
async def archive_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    recipe = recipe_service.archive_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    db.commit()
    return ApiResponse(data=RecipeArchiveResult(
        id=recipe.id,
        verification_state=recipe.verification_state,
        archived=bool(recipe.archived),
    ))


@router.post("/{id_or_slug}/unarchive", response_model=ApiResponse[RecipeArchiveResult])
async def unarchive_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    recipe = recipe_service.unarchive_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    db.commit()
    return ApiResponse(data=RecipeArchiveResult(
        id=recipe.id,
        verification_state=recipe.verification_state,
        archived=bool(recipe.archived),
    ))


# ── Favorite / Unfavorite ─────────────────────────────────────────────────────

@router.post("/{id_or_slug}/favorite", response_model=ApiResponse[RecipeSummaryOut])
async def favorite_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    recipe = recipe_service.set_favorite(db, id_or_slug, True)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    db.commit()
    return ApiResponse(data=_summary(recipe))


@router.post("/{id_or_slug}/unfavorite", response_model=ApiResponse[RecipeSummaryOut])
async def unfavorite_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    recipe = recipe_service.set_favorite(db, id_or_slug, False)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    db.commit()
    return ApiResponse(data=_summary(recipe))


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{id_or_slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    deleted = recipe_service.delete_recipe(db, id_or_slug)
    if not deleted:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    db.commit()


# ── Suggest Metadata (AI-assisted) ───────────────────────────────────────────

@router.post("/{id_or_slug}/suggest-metadata", response_model=ApiResponse[MetadataSuggestionOut])
async def suggest_recipe_metadata(id_or_slug: str, db: Session = Depends(get_db)):
    """
    Suggest taxonomy and classification fields for an existing recipe via AI.

    Returns suggested metadata for human review. Does NOT apply changes —
    use PATCH /recipes/{id_or_slug} to apply suggestions.
    Requires LM_STUDIO_ENABLED=true.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail=error_detail("ai_disabled", "AI metadata suggestion is not enabled. Set LM_STUDIO_ENABLED=true."),
        )
    recipe = recipe_service.fetch_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Recipe not found."))

    recipe_dict = _detail(recipe).model_dump()
    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = await asyncio.to_thread(
        suggest_metadata, client, recipe=recipe_dict, model=settings.lm_studio_model
    )

    if err is not None:
        if err.kind == MetadataErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail=error_detail("ai_unavailable", "AI service is unavailable."),
            )
        raise HTTPException(
            status_code=502,
            detail=error_detail(f"ai_{err.kind.value}", err.message),
        )

    return ApiResponse(data=MetadataSuggestionOut.model_validate(result.payload))


# ── Archive Rewrite (AI-assisted) ─────────────────────────────────────────────

@router.post("/{id_or_slug}/rewrite", response_model=ApiResponse[ArchiveRewriteOut])
async def rewrite_recipe_endpoint(id_or_slug: str, db: Session = Depends(get_db)):
    """
    Return an archive-style rewrite of a recipe via AI.

    Returns a suggested rewrite for human review. Does NOT apply changes —
    use PATCH /recipes/{id_or_slug} to apply the rewrite.
    Requires LM_STUDIO_ENABLED=true.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail=error_detail("ai_disabled", "AI rewrite is not enabled. Set LM_STUDIO_ENABLED=true."),
        )
    recipe = recipe_service.fetch_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Recipe not found."))

    recipe_dict = _detail(recipe).model_dump()
    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = await asyncio.to_thread(
        rewrite_recipe, client, recipe=recipe_dict, model=settings.lm_studio_model
    )

    if err is not None:
        if err.kind == RewriteErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail=error_detail("ai_unavailable", "AI service is unavailable."),
            )
        raise HTTPException(
            status_code=502,
            detail=error_detail(f"ai_{err.kind.value}", err.message),
        )

    return ApiResponse(data=ArchiveRewriteOut.model_validate(result.payload))


# ── Similar Recipes (AI-assisted) ─────────────────────────────────────────────

@router.post("/{id_or_slug}/similar", response_model=ApiResponse[SimilarRecipesOut])
async def similar_recipes(id_or_slug: str, body: SimilarityIn, db: Session = Depends(get_db)):
    """
    Return AI-ranked similar recipes from the archive.

    Fetches up to 20 other non-archived recipes and ranks them by culinary
    similarity to the source recipe. Pass `emphasis` in the body to focus on
    a specific similarity dimension (e.g. "cuisine", "technique", "ingredient").
    Requires LM_STUDIO_ENABLED=true.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail=error_detail("ai_disabled", "AI similarity is not enabled. Set LM_STUDIO_ENABLED=true."),
        )
    recipe = recipe_service.fetch_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Recipe not found."))

    candidates_orm, _ = recipe_service.list_recipes(
        db, archived=False, limit=21, offset=0, sort="updated_at_desc"
    )
    source_recipe_dict = _detail(recipe).model_dump()
    candidate_dicts = [
        _summary(r).model_dump() for r in candidates_orm if r.id != recipe.id
    ][:20]

    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = await asyncio.to_thread(
        find_similar_recipes,
        client,
        source_recipe=source_recipe_dict,
        candidates=candidate_dicts,
        emphasis=body.emphasis,
        model=settings.lm_studio_model,
    )

    if err is not None:
        if err.kind == SimilarityErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail=error_detail("ai_unavailable", "AI service is unavailable."),
            )
        raise HTTPException(
            status_code=502,
            detail=error_detail(f"ai_{err.kind.value}", err.message),
        )

    return ApiResponse(data=SimilarRecipesOut.model_validate(result.payload))
