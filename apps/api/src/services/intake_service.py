"""
Intake service — workflow logic for recipe archive intake.

Responsibilities:
- Create and track intake jobs (manual, paste_text)
- Manage structured candidates (create / update)
- Approve intake jobs: promote candidate → recipe
- Preserve raw source text (write-once on job)
"""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.models.intake import CandidateIngredient, CandidateStep, IntakeJob, StructuredCandidate
from src.models.recipe import Recipe, RecipeIngredient, RecipeNote, RecipeSource, RecipeStep
from src.schemas.intake import ApproveIntakeIn, CandidateUpdate, IntakeJobCreate
from src.utils.ids import new_ulid
from src.utils.slugify import unique_slug
from sqlalchemy import text

logger = logging.getLogger(__name__)

_UTC = timezone.utc


def _now() -> str:
    return datetime.now(_UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sync_fts(db: Session, recipe: Recipe) -> None:
    notes_text = " ".join(n.content for n in recipe.notes) if recipe.notes else ""
    db.execute(text("DELETE FROM recipe_search_fts WHERE recipe_id = :rid"), {"rid": recipe.id})
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


# ── Intake job ────────────────────────────────────────────────────────────────

def create_intake_job(db: Session, data: IntakeJobCreate) -> IntakeJob:
    job = IntakeJob(
        id=new_ulid(),
        intake_type=data.intake_type,
        status="captured",
        parse_status="not_started",
        ai_status="not_requested",
        review_status="not_started",
        raw_source_text=data.raw_source_text,
        source_url=data.source_url,
        source_notes=data.source_notes,
        created_at=_now(),
        updated_at=_now(),
    )
    db.add(job)

    # For paste_text jobs, create an empty candidate immediately so the client
    # can PATCH it without a separate creation step.
    candidate = StructuredCandidate(
        id=new_ulid(),
        intake_job_id=job.id,
        candidate_status="pending",
        created_at=_now(),
        updated_at=_now(),
    )
    db.add(candidate)
    db.flush()
    db.refresh(job)
    db.refresh(candidate)
    return job


def get_intake_job(db: Session, job_id: str) -> IntakeJob | None:
    return db.get(IntakeJob, job_id)


# ── Candidate ─────────────────────────────────────────────────────────────────

def update_candidate(db: Session, job_id: str, data: CandidateUpdate) -> StructuredCandidate | None:
    job = db.get(IntakeJob, job_id)
    if not job:
        return None

    candidate = job.candidate
    if not candidate:
        candidate = StructuredCandidate(
            id=new_ulid(),
            intake_job_id=job_id,
            candidate_status="pending",
            created_at=_now(),
            updated_at=_now(),
        )
        db.add(candidate)
        db.flush()

    # Apply scalar fields
    scalar_fields = [
        "title", "short_description", "dish_role", "primary_cuisine",
        "technique_family", "complexity", "time_class", "servings",
        "prep_time_minutes", "cook_time_minutes", "notes", "service_notes",
        "source_credit",
    ]
    for field in scalar_fields:
        val = getattr(data, field, None)
        if val is not None:
            setattr(candidate, field, val)

    # Replace ingredients if provided
    if data.ingredients is not None:
        for row in list(candidate.ingredients):
            db.delete(row)
        db.flush()
        for ing in data.ingredients:
            db.add(CandidateIngredient(
                id=new_ulid(),
                candidate_id=candidate.id,
                position=ing.position,
                group_heading=ing.group_heading,
                quantity=ing.quantity,
                unit=ing.unit,
                item=ing.item,
                preparation=ing.preparation,
                optional=1 if ing.optional else 0,
                display_text=ing.display_text,
            ))

    # Replace steps if provided
    if data.steps is not None:
        for row in list(candidate.steps):
            db.delete(row)
        db.flush()
        for step in data.steps:
            db.add(CandidateStep(
                id=new_ulid(),
                candidate_id=candidate.id,
                position=step.position,
                instruction=step.instruction,
                time_note=step.time_note,
                equipment_note=step.equipment_note,
            ))

    candidate.updated_at = _now()
    job.review_status = "in_progress"
    job.updated_at = _now()
    db.flush()
    db.refresh(candidate)
    return candidate


# ── Approve ───────────────────────────────────────────────────────────────────

def approve_intake_job(db: Session, job_id: str, data: ApproveIntakeIn) -> Recipe | None:
    """Promote a structured candidate to an approved recipe record."""
    job = db.get(IntakeJob, job_id)
    if not job:
        return None

    candidate = job.candidate
    if not candidate or not candidate.title:
        return None  # caller should return 422

    # Create source record — preserves raw source text from intake job
    source = RecipeSource(
        id=new_ulid(),
        source_type=data.source_type.value,
        source_title=data.source_title,
        source_author=data.source_author,
        source_url=job.source_url,
        source_notes=data.source_notes,
        raw_source_text=job.raw_source_text,  # write-once, preserved from intake
        created_at=_now(),
    )
    db.add(source)
    db.flush()

    # Build ingredient text for FTS
    ingredient_text = " ".join(
        i.item for i in candidate.ingredients if i.item
    )

    recipe = Recipe(
        id=new_ulid(),
        slug=unique_slug(db, candidate.title),
        title=candidate.title,
        short_description=candidate.short_description,
        dish_role=candidate.dish_role,
        primary_cuisine=candidate.primary_cuisine,
        technique_family=candidate.technique_family,
        complexity=candidate.complexity,
        time_class=candidate.time_class,
        service_format=candidate.service_format,
        season=candidate.season,
        secondary_cuisines=candidate.secondary_cuisines,
        ingredient_families=candidate.ingredient_families,
        mood_tags=candidate.mood_tags,
        storage_profile=candidate.storage_profile,
        dietary_flags=candidate.dietary_flags,
        provision_tags=candidate.provision_tags,
        sector=candidate.sector,
        operational_class=candidate.operational_class,
        heat_window=candidate.heat_window,
        servings=candidate.servings,
        prep_time_minutes=candidate.prep_time_minutes,
        cook_time_minutes=candidate.cook_time_minutes,
        rest_time_minutes=candidate.rest_time_minutes,
        verification_state=data.verification_state.value,
        favorite=0,
        archived=0,
        source_id=source.id,
        intake_job_id=job.id,
        ingredient_text=ingredient_text,
        created_at=_now(),
        updated_at=_now(),
    )
    db.add(recipe)
    db.flush()

    # Ingredients
    for ing in candidate.ingredients:
        db.add(RecipeIngredient(
            id=new_ulid(),
            recipe_id=recipe.id,
            position=ing.position,
            group_heading=ing.group_heading,
            quantity=ing.quantity,
            unit=ing.unit,
            item=ing.item or "",
            preparation=ing.preparation,
            optional=ing.optional,
            display_text=ing.display_text,
        ))

    # Steps
    for step in candidate.steps:
        db.add(RecipeStep(
            id=new_ulid(),
            recipe_id=recipe.id,
            position=step.position,
            instruction=step.instruction or "",
            time_note=step.time_note,
            equipment_note=step.equipment_note,
        ))

    # Notes from candidate
    notes_added = set()
    if candidate.notes:
        db.add(RecipeNote(
            id=new_ulid(),
            recipe_id=recipe.id,
            note_type="recipe",
            content=candidate.notes,
            created_at=_now(),
            updated_at=_now(),
        ))
        notes_added.add("recipe")
    if candidate.service_notes:
        db.add(RecipeNote(
            id=new_ulid(),
            recipe_id=recipe.id,
            note_type="service",
            content=candidate.service_notes,
            created_at=_now(),
            updated_at=_now(),
        ))
        notes_added.add("service")

    for note_type, json_blob in (
        ("storage", candidate.storage_profile),
        ("substitution", candidate.dietary_flags),
    ):
        try:
            values = json.loads(json_blob or "[]")
        except json.JSONDecodeError:
            values = []
        if values:
            db.add(RecipeNote(
                id=new_ulid(),
                recipe_id=recipe.id,
                note_type=note_type,
                content=", ".join(str(v) for v in values),
                created_at=_now(),
                updated_at=_now(),
            ))

    db.flush()
    db.refresh(recipe)

    # Sync FTS
    _sync_fts(db, recipe)

    # Mark intake job complete
    job.status = "approved"
    job.review_status = "completed"
    job.resulting_recipe_id = recipe.id
    job.completed_at = _now()
    job.updated_at = _now()

    candidate.candidate_status = "accepted"

    db.flush()
    return recipe
