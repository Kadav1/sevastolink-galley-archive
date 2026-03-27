from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.ai.lm_studio_client import LMStudioClient
from src.ai.normalizer import NormalizationErrorKind, normalize_recipe
from src.config.settings import settings
from src.db.database import get_db
from src.schemas.common import ApiResponse
from src.schemas.intake import (
    ApproveIntakeIn,
    ApproveIntakeOut,
    CandidateIngredientOut,
    CandidateOut,
    CandidateStepOut,
    CandidateUpdate,
    IntakeJobCreate,
    IntakeJobOut,
)
from src.schemas.recipe import RecipeSummaryOut
from src.services import intake_service

router = APIRouter(prefix="/intake-jobs", tags=["intake"])


# ── Helpers ────────────────────────────────────────────────────────────────────

def _candidate_out(candidate) -> CandidateOut:
    return CandidateOut(
        id=candidate.id,
        intake_job_id=candidate.intake_job_id,
        candidate_status=candidate.candidate_status,
        title=candidate.title,
        short_description=candidate.short_description,
        dish_role=candidate.dish_role,
        primary_cuisine=candidate.primary_cuisine,
        technique_family=candidate.technique_family,
        complexity=candidate.complexity,
        time_class=candidate.time_class,
        servings=candidate.servings,
        prep_time_minutes=candidate.prep_time_minutes,
        cook_time_minutes=candidate.cook_time_minutes,
        notes=candidate.notes,
        service_notes=candidate.service_notes,
        source_credit=candidate.source_credit,
        ingredients=[
            CandidateIngredientOut(
                position=ing.position,
                group_heading=ing.group_heading,
                quantity=ing.quantity,
                unit=ing.unit,
                item=ing.item,
                preparation=ing.preparation,
                optional=bool(ing.optional),
            )
            for ing in (candidate.ingredients or [])
        ],
        steps=[
            CandidateStepOut(
                position=step.position,
                instruction=step.instruction,
                time_note=step.time_note,
                equipment_note=step.equipment_note,
            )
            for step in (candidate.steps or [])
        ],
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
    )


# ── Create ─────────────────────────────────────────────────────────────────────

@router.post("", response_model=ApiResponse[IntakeJobOut], status_code=status.HTTP_201_CREATED)
def create_intake_job(body: IntakeJobCreate, db: Session = Depends(get_db)):
    if body.intake_type == "paste_text" and not body.raw_source_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "validation_error", "message": "raw_source_text is required for paste_text intake."}},
        )
    job = intake_service.create_intake_job(db, body)
    db.commit()
    db.refresh(job)
    return ApiResponse(data=IntakeJobOut.from_orm(job))


# ── Get ────────────────────────────────────────────────────────────────────────

@router.get("/{job_id}", response_model=ApiResponse[IntakeJobOut])
def get_intake_job(job_id: str, db: Session = Depends(get_db)):
    job = intake_service.get_intake_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Intake job not found."}})
    return ApiResponse(data=IntakeJobOut.from_orm(job))


# ── Update candidate ──────────────────────────────────────────────────────────

@router.patch("/{job_id}/candidate", response_model=ApiResponse[CandidateOut])
def update_candidate(job_id: str, body: CandidateUpdate, db: Session = Depends(get_db)):
    candidate = intake_service.update_candidate(db, job_id, body)
    if candidate is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Intake job not found."}})
    db.commit()
    db.refresh(candidate)
    return ApiResponse(data=_candidate_out(candidate))


# ── Normalize (AI-assisted) ───────────────────────────────────────────────────

@router.post("/{job_id}/normalize", response_model=ApiResponse[CandidateOut])
def normalize_candidate(job_id: str, db: Session = Depends(get_db)):
    """
    Run AI normalization against the job's raw source text.

    Requires LM_STUDIO_ENABLED=true in settings.
    On AI failure the endpoint returns 503 with a machine-readable error code
    so the frontend can show a degraded-mode notice and allow manual entry.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail={"error": {"code": "ai_disabled", "message": "AI normalization is not enabled. Set LM_STUDIO_ENABLED=true to use this feature."}},
        )

    job = intake_service.get_intake_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Intake job not found."}})

    if not job.raw_source_text:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "no_source_text", "message": "Intake job has no raw source text to normalize."}},
        )

    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = normalize_recipe(
        client,
        raw_text=job.raw_source_text,
        source_notes=job.source_notes if hasattr(job, "source_notes") else None,
        model=settings.lm_studio_model,
    )

    if err is not None:
        # Map normalization error kinds to HTTP status + code
        if err.kind == NormalizationErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail={"error": {"code": "ai_unavailable", "message": "AI service is unavailable. You can continue manually."}},
            )
        raise HTTPException(
            status_code=502,
            detail={"error": {"code": f"ai_{err.kind.value}", "message": err.message}},
        )

    # Apply the AI-suggested fields to the candidate
    candidate = intake_service.update_candidate(db, job_id, result.candidate_update)
    if candidate is None:
        raise HTTPException(status_code=500, detail={"error": {"code": "internal_error", "message": "Failed to apply normalization result."}})

    db.commit()
    db.refresh(candidate)
    return ApiResponse(data=_candidate_out(candidate))


# ── Approve ────────────────────────────────────────────────────────────────────

@router.post("/{job_id}/approve", response_model=ApiResponse[ApproveIntakeOut], status_code=status.HTTP_201_CREATED)
def approve_intake_job(job_id: str, body: ApproveIntakeIn, db: Session = Depends(get_db)):
    job = intake_service.get_intake_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Intake job not found."}})
    if job.status == "approved":
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "conflict", "message": "Intake job has already been approved."}},
        )
    if not job.candidate or not job.candidate.title:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "candidate_incomplete", "message": "Candidate must have a title before approval."}},
        )

    recipe = intake_service.approve_intake_job(db, job_id, body)
    if not recipe:
        raise HTTPException(status_code=500, detail={"error": {"code": "internal_error", "message": "Approval failed."}})

    db.commit()
    db.refresh(recipe)
    return ApiResponse(data=ApproveIntakeOut(
        recipe=RecipeSummaryOut.from_orm_with_json(recipe),
        intake_job_id=job_id,
    ))
