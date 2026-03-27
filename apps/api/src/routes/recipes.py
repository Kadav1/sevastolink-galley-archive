from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas.common import ApiResponse, ListMeta, ListResponse
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

@router.get("", response_model=ListResponse[RecipeSummaryOut])
def list_recipes(
    q: str | None = Query(None),
    verification_state: str | None = Query(None),
    favorite: bool | None = Query(None),
    archived: bool = Query(False),
    dish_role: str | None = Query(None),
    primary_cuisine: str | None = Query(None),
    technique_family: str | None = Query(None),
    complexity: str | None = Query(None),
    time_class: str | None = Query(None),
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
def create_recipe(data: RecipeCreate, db: Session = Depends(get_db)):
    recipe = recipe_service.create_recipe(db, data)
    return ApiResponse(data=_detail(recipe))


# ── Get by ID or slug ─────────────────────────────────────────────────────────

@router.get("/{id_or_slug}", response_model=ApiResponse[RecipeDetail])
def get_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    recipe = recipe_service.get_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    return ApiResponse(data=_detail(recipe))


# ── Update ────────────────────────────────────────────────────────────────────

@router.patch("/{id_or_slug}", response_model=ApiResponse[RecipeDetail])
def update_recipe(id_or_slug: str, data: RecipeUpdate, db: Session = Depends(get_db)):
    recipe = recipe_service.update_recipe(db, id_or_slug, data)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    return ApiResponse(data=_detail(recipe))


# ── Archive / Unarchive ───────────────────────────────────────────────────────

@router.post("/{id_or_slug}/archive", response_model=ApiResponse[RecipeArchiveResult])
def archive_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    recipe = recipe_service.archive_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    return ApiResponse(data=RecipeArchiveResult(
        id=recipe.id,
        verification_state=recipe.verification_state,
        archived=bool(recipe.archived),
    ))


@router.post("/{id_or_slug}/unarchive", response_model=ApiResponse[RecipeArchiveResult])
def unarchive_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    recipe = recipe_service.unarchive_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    return ApiResponse(data=RecipeArchiveResult(
        id=recipe.id,
        verification_state=recipe.verification_state,
        archived=bool(recipe.archived),
    ))


# ── Favorite / Unfavorite ─────────────────────────────────────────────────────

@router.post("/{id_or_slug}/favorite", response_model=ApiResponse[RecipeSummaryOut])
def favorite_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    recipe = recipe_service.set_favorite(db, id_or_slug, True)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    return ApiResponse(data=_summary(recipe))


@router.post("/{id_or_slug}/unfavorite", response_model=ApiResponse[RecipeSummaryOut])
def unfavorite_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    recipe = recipe_service.set_favorite(db, id_or_slug, False)
    if not recipe:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
    return ApiResponse(data=_summary(recipe))


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{id_or_slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(id_or_slug: str, db: Session = Depends(get_db)):
    deleted = recipe_service.delete_recipe(db, id_or_slug)
    if not deleted:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Recipe not found."})
