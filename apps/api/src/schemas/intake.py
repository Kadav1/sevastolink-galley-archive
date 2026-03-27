from typing import Literal
from pydantic import BaseModel

from src.schemas.recipe import (
    IngredientIn,
    RecipeSummaryOut,
    StepIn,
    VerificationState,
    SourceType,
)


# ── Intake job ────────────────────────────────────────────────────────────────

class IntakeJobCreate(BaseModel):
    intake_type: Literal["manual", "paste_text"]
    raw_source_text: str | None = None
    source_url: str | None = None
    source_notes: str | None = None


class IntakeJobOut(BaseModel):
    id: str
    intake_type: str
    status: str
    parse_status: str
    ai_status: str
    review_status: str
    raw_source_text: str | None
    source_url: str | None
    resulting_recipe_id: str | None
    candidate_id: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_orm(cls, job) -> "IntakeJobOut":
        candidate_id = job.candidate.id if job.candidate else None
        return cls(
            id=job.id,
            intake_type=job.intake_type,
            status=job.status,
            parse_status=job.parse_status,
            ai_status=job.ai_status,
            review_status=job.review_status,
            raw_source_text=job.raw_source_text,
            source_url=job.source_url,
            resulting_recipe_id=job.resulting_recipe_id,
            candidate_id=candidate_id,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )


# ── Candidate ─────────────────────────────────────────────────────────────────

class CandidateUpdate(BaseModel):
    title: str | None = None
    short_description: str | None = None
    dish_role: str | None = None
    primary_cuisine: str | None = None
    technique_family: str | None = None
    complexity: str | None = None
    time_class: str | None = None
    servings: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    notes: str | None = None
    service_notes: str | None = None
    source_credit: str | None = None
    ingredients: list[IngredientIn] | None = None
    steps: list[StepIn] | None = None


class CandidateIngredientOut(BaseModel):
    position: int
    group_heading: str | None
    quantity: str | None
    unit: str | None
    item: str | None
    preparation: str | None
    optional: bool


class CandidateStepOut(BaseModel):
    position: int
    instruction: str | None
    time_note: str | None
    equipment_note: str | None


class CandidateOut(BaseModel):
    id: str
    intake_job_id: str
    candidate_status: str
    title: str | None
    short_description: str | None
    dish_role: str | None
    primary_cuisine: str | None
    technique_family: str | None
    complexity: str | None
    time_class: str | None
    servings: str | None
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    notes: str | None
    service_notes: str | None
    source_credit: str | None
    ingredients: list[CandidateIngredientOut]
    steps: list[CandidateStepOut]
    created_at: str
    updated_at: str


# ── Approval ──────────────────────────────────────────────────────────────────

class ApproveIntakeIn(BaseModel):
    verification_state: VerificationState = VerificationState.unverified
    source_type: SourceType = SourceType.manual
    source_title: str | None = None
    source_author: str | None = None
    source_notes: str | None = None


class ApproveIntakeOut(BaseModel):
    recipe: RecipeSummaryOut
    intake_job_id: str
