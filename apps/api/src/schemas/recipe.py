import json
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, field_validator, model_validator


# ── Enums ────────────────────────────────────────────────────────────────────

class VerificationState(str, Enum):
    draft = "Draft"
    unverified = "Unverified"
    verified = "Verified"
    archived = "Archived"


class IntakeStatus(str, Enum):
    captured = "captured"
    extracting = "extracting"
    structured = "structured"
    in_review = "in_review"
    approved = "approved"
    failed = "failed"
    abandoned = "abandoned"


class NoteType(str, Enum):
    recipe = "recipe"
    service = "service"
    storage = "storage"
    substitution = "substitution"
    source = "source"


class SourceType(str, Enum):
    manual = "Manual"
    book = "Book"
    website = "Website"
    family = "Family Recipe"
    screenshot = "Screenshot"
    pdf = "PDF"
    image_scan = "Image / Scan"
    ai_normalized = "AI-Normalized"
    composite = "Composite / Merged"


# ── Sub-resource inputs ───────────────────────────────────────────────────────

class IngredientIn(BaseModel):
    position: int
    group_heading: str | None = None
    quantity: str | None = None
    unit: str | None = None
    item: str
    preparation: str | None = None
    optional: bool = False
    display_text: str | None = None


class StepIn(BaseModel):
    position: int
    instruction: str
    time_note: str | None = None
    equipment_note: str | None = None


class NoteIn(BaseModel):
    note_type: NoteType
    content: str


class SourceIn(BaseModel):
    source_type: SourceType = SourceType.manual
    source_title: str | None = None
    source_author: str | None = None
    source_url: str | None = None
    source_notes: str | None = None
    raw_source_text: str | None = None


# ── Sub-resource outputs ──────────────────────────────────────────────────────

class IngredientOut(BaseModel):
    id: str
    position: int
    group_heading: str | None = None
    quantity: str | None = None
    unit: str | None = None
    item: str
    preparation: str | None = None
    optional: bool = False
    display_text: str | None = None

    model_config = {"from_attributes": True}


class StepOut(BaseModel):
    id: str
    position: int
    instruction: str
    time_note: str | None = None
    equipment_note: str | None = None

    model_config = {"from_attributes": True}


class NoteOut(BaseModel):
    id: str
    note_type: str
    content: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class SourceOut(BaseModel):
    id: str
    source_type: str
    source_title: str | None = None
    source_author: str | None = None
    source_url: str | None = None
    source_notes: str | None = None
    raw_source_text: str | None = None
    created_at: str

    model_config = {"from_attributes": True}


# ── Recipe Create ─────────────────────────────────────────────────────────────

class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    short_description: str | None = None

    # Taxonomy
    dish_role: str | None = None
    primary_cuisine: str | None = None
    secondary_cuisines: list[str] = []
    technique_family: str | None = None
    complexity: str | None = None
    time_class: str | None = None
    service_format: str | None = None
    season: str | None = None
    ingredient_families: list[str] = []
    mood_tags: list[str] = []
    storage_profile: list[str] = []
    dietary_flags: list[str] = []
    provision_tags: list[str] = []

    # Sevastolink overlay
    sector: str | None = None
    operational_class: str | None = None
    heat_window: str | None = None

    # Timing
    servings: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    rest_time_minutes: int | None = None

    # State
    verification_state: VerificationState = VerificationState.draft
    favorite: bool = False
    rating: int | None = Field(None, ge=1, le=5)

    # Sub-resources
    ingredients: list[IngredientIn] = []
    steps: list[StepIn] = []
    notes: list[NoteIn] = []
    source: SourceIn | None = None


# ── Recipe Update ─────────────────────────────────────────────────────────────

class RecipeUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    short_description: str | None = None

    dish_role: str | None = None
    primary_cuisine: str | None = None
    secondary_cuisines: list[str] | None = None
    technique_family: str | None = None
    complexity: str | None = None
    time_class: str | None = None
    service_format: str | None = None
    season: str | None = None
    ingredient_families: list[str] | None = None
    mood_tags: list[str] | None = None
    storage_profile: list[str] | None = None
    dietary_flags: list[str] | None = None
    provision_tags: list[str] | None = None
    sector: str | None = None
    operational_class: str | None = None
    heat_window: str | None = None
    servings: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    rest_time_minutes: int | None = None
    verification_state: VerificationState | None = None
    favorite: bool | None = None
    rating: int | None = Field(None, ge=1, le=5)

    # When provided, these replace all existing rows
    ingredients: list[IngredientIn] | None = None
    steps: list[StepIn] | None = None
    notes: list[NoteIn] | None = None


# ── Recipe Summary (list response) ───────────────────────────────────────────

class RecipeSummaryOut(BaseModel):
    id: str
    slug: str
    title: str
    short_description: str | None = None
    dish_role: str | None = None
    primary_cuisine: str | None = None
    technique_family: str | None = None
    complexity: str | None = None
    time_class: str | None = None
    sector: str | None = None
    operational_class: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    total_time_minutes: int | None = None
    servings: str | None = None
    verification_state: VerificationState = VerificationState.draft
    favorite: bool = False
    rating: int | None = None
    created_at: str
    updated_at: str
    ingredient_count: int = 0
    cover_media_asset_id: str | None = None
    last_cooked_at: str | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_json(cls, recipe: Any) -> "RecipeSummaryOut":
        """Build from ORM object, computing derived fields."""
        fields = cls.model_fields.keys()
        data = {
            c.key: getattr(recipe, c.key)
            for c in recipe.__table__.columns
            if c.key in fields
        }
        data["favorite"] = bool(data.get("favorite", 0))
        data["total_time_minutes"] = (
            (recipe.prep_time_minutes or 0) + (recipe.cook_time_minutes or 0)
        ) or None
        data["ingredient_count"] = len(recipe.ingredients)
        return cls.model_validate(data)


# ── Recipe Detail (single response) ──────────────────────────────────────────

class RecipeDetail(BaseModel):
    id: str
    slug: str
    title: str
    short_description: str | None = None

    dish_role: str | None = None
    primary_cuisine: str | None = None
    secondary_cuisines: list[str] = []
    technique_family: str | None = None
    complexity: str | None = None
    time_class: str | None = None
    service_format: str | None = None
    season: str | None = None
    ingredient_families: list[str] = []
    mood_tags: list[str] = []
    storage_profile: list[str] = []
    dietary_flags: list[str] = []
    provision_tags: list[str] = []

    sector: str | None = None
    operational_class: str | None = None
    heat_window: str | None = None

    servings: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    total_time_minutes: int | None = None
    rest_time_minutes: int | None = None

    verification_state: VerificationState = VerificationState.draft
    favorite: bool = False
    archived: bool = False
    rating: int | None = None

    ingredients: list[IngredientOut] = []
    steps: list[StepOut] = []
    notes: list[NoteOut] = []
    source: SourceOut | None = None

    cover_media_asset_id: str | None = None
    intake_job_id: str | None = None
    created_at: str
    updated_at: str
    last_cooked_at: str | None = None
    last_viewed_at: str | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_recipe(cls, recipe: Any) -> "RecipeDetail":
        """Build full detail from ORM Recipe, deserialising JSON array columns."""
        def parse_json_list(val: Any) -> list:
            if val is None:
                return []
            if isinstance(val, list):
                return val
            try:
                result = json.loads(val)
                return result if isinstance(result, list) else []
            except (json.JSONDecodeError, TypeError):
                return []

        return cls(
            id=recipe.id,
            slug=recipe.slug,
            title=recipe.title,
            short_description=recipe.short_description,
            dish_role=recipe.dish_role,
            primary_cuisine=recipe.primary_cuisine,
            secondary_cuisines=parse_json_list(recipe.secondary_cuisines),
            technique_family=recipe.technique_family,
            complexity=recipe.complexity,
            time_class=recipe.time_class,
            service_format=recipe.service_format,
            season=recipe.season,
            ingredient_families=parse_json_list(recipe.ingredient_families),
            mood_tags=parse_json_list(recipe.mood_tags),
            storage_profile=parse_json_list(recipe.storage_profile),
            dietary_flags=parse_json_list(recipe.dietary_flags),
            provision_tags=parse_json_list(recipe.provision_tags),
            sector=recipe.sector,
            operational_class=recipe.operational_class,
            heat_window=recipe.heat_window,
            servings=recipe.servings,
            prep_time_minutes=recipe.prep_time_minutes,
            cook_time_minutes=recipe.cook_time_minutes,
            total_time_minutes=(recipe.prep_time_minutes or 0) + (recipe.cook_time_minutes or 0) or None,
            rest_time_minutes=recipe.rest_time_minutes,
            verification_state=recipe.verification_state,
            favorite=bool(recipe.favorite),
            archived=bool(recipe.archived),
            rating=recipe.rating,
            ingredients=[IngredientOut.model_validate(i, from_attributes=True) for i in recipe.ingredients],
            steps=[StepOut.model_validate(s, from_attributes=True) for s in recipe.steps],
            notes=[NoteOut.model_validate(n, from_attributes=True) for n in recipe.notes],
            source=SourceOut.model_validate(recipe.source, from_attributes=True) if recipe.source else None,
            cover_media_asset_id=recipe.cover_media_asset_id,
            intake_job_id=recipe.intake_job_id,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
            last_cooked_at=recipe.last_cooked_at,
            last_viewed_at=recipe.last_viewed_at,
        )


class RecipeArchiveResult(BaseModel):
    id: str
    verification_state: VerificationState
    archived: bool


# ── Misc response ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    service: str


# Legacy alias kept for existing health route
RecipeSummary = RecipeSummaryOut
