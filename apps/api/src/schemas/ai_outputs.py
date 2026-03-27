# apps/api/src/schemas/ai_outputs.py
"""
Pydantic models for AI endpoint request bodies and response payloads.

These are the API-layer shapes — they mirror the JSON schemas in
prompts/schemas/ but are expressed as Pydantic models for FastAPI
validation and OpenAPI documentation.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ── Evaluation ────────────────────────────────────────────────────────────────

class EvaluationOut(BaseModel):
    fidelity_assessment: str
    missing_information: list[str]
    likely_inventions_or_overreaches: list[str]
    ingredient_issues: list[str]
    step_issues: list[str]
    metadata_confidence: str | None
    review_recommendation: str  # "safe_for_human_review" | "review_with_caution" | "needs_major_correction"
    reviewer_notes: list[str]


# ── Metadata Suggestion ───────────────────────────────────────────────────────

class MetadataSuggestionOut(BaseModel):
    """
    AI-suggested taxonomy fields for an existing recipe.
    The field `operational_class` corresponds to the AI schema's `class` key
    (a Python reserved word) and to the recipe model's `operational_class` column.
    """
    model_config = {"populate_by_name": True}

    dish_role: str | None = None
    primary_cuisine: str | None = None
    secondary_cuisines: list[str] = []
    technique_family: str | None = None
    ingredient_families: list[str] = []
    complexity: str | None = None
    time_class: str | None = None
    service_format: str | None = None
    season: str | None = None
    mood_tags: list[str] = []
    storage_profile: list[str] = []
    dietary_flags: list[str] = []
    sector: str | None = None
    operational_class: str | None = Field(None, alias="class")
    heat_window: str | None = None
    provision_tags: list[str] = []
    short_description: str | None = None
    confidence_notes: list[str] = []
    uncertainty_notes: list[str] = []


# ── Archive Rewrite ───────────────────────────────────────────────────────────

class RewriteIngredientOut(BaseModel):
    amount: str | None = None
    unit: str | None = None
    item: str
    note: str | None = None
    optional: bool | None = None
    group: str | None = None


class RewriteStepOut(BaseModel):
    step_number: int
    instruction: str
    time_note: str | None = None
    heat_note: str | None = None
    equipment_note: str | None = None


class ArchiveRewriteOut(BaseModel):
    title: str | None = None
    short_description: str | None = None
    ingredients: list[RewriteIngredientOut] = []
    steps: list[RewriteStepOut] = []
    recipe_notes: str | None = None
    service_notes: str | None = None
    rewrite_notes: list[str] = []
    uncertainty_notes: list[str] = []


# ── Similarity ────────────────────────────────────────────────────────────────

class SimilarityIn(BaseModel):
    """Optional emphasis parameter for the similarity search."""
    emphasis: str | None = None  # e.g. "cuisine", "technique", "ingredient", "occasion"


class SimilarityMatchOut(BaseModel):
    title: str
    similarity_score_band: str  # "very_high" | "high" | "moderate" | "low"
    primary_similarity_reason: str
    secondary_similarity_reasons: list[str] = []
    major_differences: list[str] = []


class SimilarRecipesOut(BaseModel):
    top_matches: list[SimilarityMatchOut]
    near_matches: list[SimilarityMatchOut]
    why_each_match_ranked: list[str]
    major_difference_notes: list[str]
    confidence_notes: list[str]


# ── Pantry ────────────────────────────────────────────────────────────────────

class PantryQueryIn(BaseModel):
    available_ingredients: list[str]
    must_use: list[str] = []
    excluded: list[str] = []
    cuisine_preferences: list[str] = []
    time_limit_minutes: int | None = None


class PantryMatchOut(BaseModel):
    title: str
    match_type: str
    why_it_matches: str
    missing_items: list[str] = []
    recommended_adjustments: list[str] = []
    time_fit: str | None = None


class PantrySuggestionOut(BaseModel):
    direct_matches: list[PantryMatchOut]
    near_matches: list[PantryMatchOut]
    pantry_gap_notes: list[str]
    substitution_suggestions: list[str]
    quick_ideas: list[str]
    confidence_notes: list[str]
