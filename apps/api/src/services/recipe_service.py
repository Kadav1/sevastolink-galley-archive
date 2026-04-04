"""
Recipe service — all business logic for the recipe archive.

Responsibilities:
- CRUD for recipes + sub-resources
- Slug generation (unique)
- FTS5 index synchronisation
- Search (FTS + facet filter) with pagination
- Archive / unarchive / favorite / delete actions
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session, selectinload

from src.models.recipe import Recipe, RecipeIngredient, RecipeNote, RecipeSource, RecipeStep
from src.schemas.recipe import RecipeCreate, RecipeUpdate, VerificationState
from src.utils.ids import new_ulid
from src.utils.slugify import unique_slug

logger = logging.getLogger(__name__)

_UTC = timezone.utc


def _sanitize_fts_query(q: str) -> str:
    """Quote each token so FTS5 operators in user input are treated as literals.

    Strips embedded double-quotes from tokens before wrapping so that inputs
    like '"unclosed' don't produce malformed FTS5 syntax.
    """
    tokens = (token.replace('"', "") for token in q.strip().split() if token)
    return " ".join(f'"{t}"' for t in tokens if t)


def _now() -> str:
    return datetime.now(_UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_ingredient_text(ingredients: list[Any]) -> str:
    """Flat string of ingredient item names for FTS index."""
    return " ".join(
        i.item for i in ingredients if hasattr(i, "item") and i.item
    )


def _sync_fts(db: Session, recipe: Recipe) -> None:
    """Upsert recipe into the standalone FTS5 table."""
    notes_text = " ".join(n.content for n in recipe.notes) if recipe.notes else ""
    db.execute(
        text("DELETE FROM recipe_search_fts WHERE recipe_id = :rid"),
        {"rid": recipe.id},
    )
    db.execute(
        text(
            "INSERT INTO recipe_search_fts "
            "(recipe_id, title, short_description, notes, ingredient_text) "
            "VALUES (:rid, :title, :desc, :notes, :ingr)"
        ),
        {
            "rid": recipe.id,
            "title": recipe.title or "",
            "desc": recipe.short_description or "",
            "notes": notes_text,
            "ingr": recipe.ingredient_text or "",
        },
    )


def _save_ingredients(db: Session, recipe_id: str, ingredients: list) -> list[RecipeIngredient]:
    rows = []
    for ing in ingredients:
        row = RecipeIngredient(
            id=new_ulid(),
            recipe_id=recipe_id,
            position=ing.position,
            group_heading=ing.group_heading,
            quantity=ing.quantity,
            unit=ing.unit,
            item=ing.item,
            preparation=ing.preparation,
            optional=1 if ing.optional else 0,
            display_text=ing.display_text,
        )
        db.add(row)
        rows.append(row)
    return rows


def _save_steps(db: Session, recipe_id: str, steps: list) -> list[RecipeStep]:
    rows = []
    for step in steps:
        row = RecipeStep(
            id=new_ulid(),
            recipe_id=recipe_id,
            position=step.position,
            instruction=step.instruction,
            time_note=step.time_note,
            equipment_note=step.equipment_note,
        )
        db.add(row)
        rows.append(row)
    return rows


def _save_notes(db: Session, recipe_id: str, notes: list) -> list[RecipeNote]:
    rows = []
    for note in notes:
        row = RecipeNote(
            id=new_ulid(),
            recipe_id=recipe_id,
            note_type=note.note_type.value if hasattr(note.note_type, "value") else note.note_type,
            content=note.content,
            created_at=_now(),
            updated_at=_now(),
        )
        db.add(row)
        rows.append(row)
    return rows


def create_recipe(db: Session, data: RecipeCreate) -> Recipe:
    recipe_id = new_ulid()
    slug = unique_slug(db, data.title)
    now = _now()

    source: RecipeSource | None = None
    if data.source:
        source = RecipeSource(
            id=new_ulid(),
            source_type=data.source.source_type.value if hasattr(data.source.source_type, "value") else data.source.source_type,
            source_title=data.source.source_title,
            source_author=data.source.source_author,
            source_url=data.source.source_url,
            source_notes=data.source.source_notes,
            raw_source_text=data.source.raw_source_text,
            created_at=now,
        )
        db.add(source)
        db.flush()

    recipe = Recipe(
        id=recipe_id,
        slug=slug,
        title=data.title,
        short_description=data.short_description,
        dish_role=data.dish_role,
        primary_cuisine=data.primary_cuisine,
        secondary_cuisines=json.dumps(data.secondary_cuisines),
        technique_family=data.technique_family,
        complexity=data.complexity,
        time_class=data.time_class,
        service_format=data.service_format,
        season=data.season,
        ingredient_families=json.dumps(data.ingredient_families),
        mood_tags=json.dumps(data.mood_tags),
        storage_profile=json.dumps(data.storage_profile),
        dietary_flags=json.dumps(data.dietary_flags),
        provision_tags=json.dumps(data.provision_tags),
        sector=data.sector,
        operational_class=data.operational_class,
        heat_window=data.heat_window,
        servings=data.servings,
        prep_time_minutes=data.prep_time_minutes,
        cook_time_minutes=data.cook_time_minutes,
        rest_time_minutes=data.rest_time_minutes,
        verification_state=data.verification_state.value,
        favorite=1 if data.favorite else 0,
        archived=0,
        rating=data.rating,
        source_id=source.id if source else None,
        created_at=now,
        updated_at=now,
    )
    db.add(recipe)
    db.flush()

    ingredients = _save_ingredients(db, recipe_id, data.ingredients)
    _save_steps(db, recipe_id, data.steps)
    _save_notes(db, recipe_id, data.notes)

    recipe.ingredient_text = _build_ingredient_text(ingredients)

    db.flush()
    _sync_fts(db, recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def _get_recipe(db: Session, id_or_slug: str) -> Recipe | None:
    """Pure read — no side effects. Used internally by all service mutations."""
    from src.utils.ids import is_ulid
    if is_ulid(id_or_slug.upper()):
        return db.query(Recipe).filter(Recipe.id == id_or_slug.upper()).first()
    return db.query(Recipe).filter(Recipe.slug == id_or_slug).first()


def fetch_recipe(db: Session, id_or_slug: str) -> Recipe | None:
    """Pure read — no side effects. Use from any route that doesn't represent a user view."""
    return _get_recipe(db, id_or_slug)


def get_recipe(db: Session, id_or_slug: str) -> Recipe | None:
    """Read a recipe and record the view timestamp. Call only from GET route handlers."""
    recipe = _get_recipe(db, id_or_slug)
    if recipe:
        recipe.last_viewed_at = _now()
        db.commit()
        db.refresh(recipe)
    return recipe


def ingredient_family_counts(db: Session) -> list[dict]:
    """Return ingredient families with recipe counts, sorted by count desc.

    Uses json_each() to expand the ingredient_families JSON array on each recipe.
    Only counts non-archived recipes.
    """
    rows = db.execute(
        text(
            "SELECT jf.value AS family, COUNT(*) AS count "
            "FROM recipes, json_each(recipes.ingredient_families) AS jf "
            "WHERE recipes.archived = 0 "
            "  AND recipes.ingredient_families IS NOT NULL "
            "  AND recipes.ingredient_families != 'null' "
            "GROUP BY jf.value "
            "ORDER BY count DESC, jf.value ASC"
        )
    ).fetchall()
    return [{"family": row[0], "count": row[1]} for row in rows]


def list_recipes(
    db: Session,
    q: str | None = None,
    verification_state: str | None = None,
    favorite: bool | None = None,
    archived: bool = False,
    dish_role: str | None = None,
    primary_cuisine: str | None = None,
    technique_family: str | None = None,
    complexity: str | None = None,
    time_class: str | None = None,
    sector: str | None = None,
    operational_class: str | None = None,
    heat_window: str | None = None,
    ingredient_family: str | None = None,
    sort: str = "updated_at_desc",
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Recipe], int]:

    if q:
        # FTS search: get matching recipe IDs
        fts_rows = db.execute(
            text(
                "SELECT recipe_id FROM recipe_search_fts "
                "WHERE recipe_search_fts MATCH :q "
                "ORDER BY rank"
            ),
            {"q": _sanitize_fts_query(q)},
        ).fetchall()
        matching_ids = [row[0] for row in fts_rows]
        if not matching_ids:
            return [], 0
        query = db.query(Recipe).filter(Recipe.id.in_(matching_ids))
    else:
        query = db.query(Recipe)

    # Eager-load ingredients so ingredient_count is available without N+1 queries
    query = query.options(selectinload(Recipe.ingredients))

    # Exclude archived by default
    if not archived:
        query = query.filter(Recipe.archived == 0)

    # Facet filters
    if verification_state:
        query = query.filter(Recipe.verification_state == verification_state)
    if favorite is True:
        query = query.filter(Recipe.favorite == 1)
    if dish_role:
        query = query.filter(Recipe.dish_role == dish_role)
    if primary_cuisine:
        query = query.filter(Recipe.primary_cuisine == primary_cuisine)
    if technique_family:
        query = query.filter(Recipe.technique_family == technique_family)
    if complexity:
        query = query.filter(Recipe.complexity == complexity)
    if time_class:
        query = query.filter(Recipe.time_class == time_class)
    if sector:
        query = query.filter(Recipe.sector == sector)
    if operational_class:
        query = query.filter(Recipe.operational_class == operational_class)
    if heat_window:
        query = query.filter(Recipe.heat_window == heat_window)
    if ingredient_family:
        query = query.filter(
            Recipe.id.in_(
                db.execute(
                    text(
                        "SELECT recipe_id FROM recipes, json_each(recipes.ingredient_families) AS jf "
                        "WHERE jf.value = :fam"
                    ),
                    {"fam": ingredient_family},
                ).scalars().all()
            )
        )

    total = query.count()

    # Sorting
    sort_map = {
        "updated_at_desc": Recipe.updated_at.desc(),
        "created_at_desc": Recipe.created_at.desc(),
        "title_asc": Recipe.title.asc(),
        "title_desc": Recipe.title.desc(),
        "last_cooked_at_desc": Recipe.last_cooked_at.desc(),
    }
    order_col = sort_map.get(sort, Recipe.updated_at.desc())
    query = query.order_by(order_col)

    recipes = query.offset(offset).limit(limit).all()
    return recipes, total


def update_recipe(db: Session, id_or_slug: str, data: RecipeUpdate) -> Recipe | None:
    recipe = _get_recipe(db, id_or_slug)
    if not recipe:
        return None

    now = _now()
    scalar_fields = [
        "title", "short_description", "dish_role", "primary_cuisine",
        "technique_family", "complexity", "time_class", "service_format", "season",
        "sector", "operational_class", "heat_window", "servings",
        "prep_time_minutes", "cook_time_minutes", "rest_time_minutes", "rating",
    ]
    json_fields = [
        "secondary_cuisines", "ingredient_families", "mood_tags",
        "storage_profile", "dietary_flags", "provision_tags",
    ]

    update_data = data.model_dump(exclude_unset=True)

    for field in scalar_fields:
        if field in update_data:
            setattr(recipe, field, update_data[field])

    for field in json_fields:
        if field in update_data:
            setattr(recipe, field, json.dumps(update_data[field]))

    if "verification_state" in update_data:
        vs = update_data["verification_state"]
        recipe.verification_state = vs.value if hasattr(vs, "value") else vs

    if "favorite" in update_data:
        recipe.favorite = 1 if update_data["favorite"] else 0

    # Array replace for sub-resources
    if data.ingredients is not None:
        for row in recipe.ingredients:
            db.delete(row)
        db.flush()
        new_ings = _save_ingredients(db, recipe.id, data.ingredients)
        recipe.ingredient_text = _build_ingredient_text(new_ings)

    if data.steps is not None:
        for row in recipe.steps:
            db.delete(row)
        db.flush()
        _save_steps(db, recipe.id, data.steps)

    if data.notes is not None:
        for row in recipe.notes:
            db.delete(row)
        db.flush()
        _save_notes(db, recipe.id, data.notes)

    recipe.updated_at = now
    db.flush()
    db.refresh(recipe)
    _sync_fts(db, recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def archive_recipe(db: Session, id_or_slug: str) -> Recipe | None:
    recipe = _get_recipe(db, id_or_slug)
    if not recipe:
        return None
    recipe.verification_state = VerificationState.archived.value
    recipe.archived = 1
    recipe.updated_at = _now()
    db.commit()
    db.refresh(recipe)
    return recipe


def unarchive_recipe(db: Session, id_or_slug: str) -> Recipe | None:
    recipe = _get_recipe(db, id_or_slug)
    if not recipe:
        return None
    recipe.verification_state = VerificationState.unverified.value
    recipe.archived = 0
    recipe.updated_at = _now()
    db.commit()
    db.refresh(recipe)
    return recipe


def set_favorite(db: Session, id_or_slug: str, value: bool) -> Recipe | None:
    recipe = _get_recipe(db, id_or_slug)
    if not recipe:
        return None
    recipe.favorite = 1 if value else 0
    recipe.updated_at = _now()
    db.commit()
    db.refresh(recipe)
    return recipe


def delete_recipe(db: Session, id_or_slug: str) -> bool:
    recipe = _get_recipe(db, id_or_slug)
    if not recipe:
        return False
    db.execute(
        text("DELETE FROM recipe_search_fts WHERE recipe_id = :rid"),
        {"rid": recipe.id},
    )
    db.delete(recipe)
    db.commit()
    return True
