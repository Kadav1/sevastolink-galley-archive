import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.ai.evaluator import EvaluationErrorKind, EvaluationResult, evaluate_normalization
from src.ai.lm_studio_client import LMStudioClient
from src.ai.normalizer import NormalizationErrorKind, normalize_recipe
from src.config.settings import settings
from src.db.database import get_db
from src.schemas.common import ApiResponse, error_detail
from src.schemas.ai_outputs import EvaluationOut
from src.schemas.intake import (
    ApproveIntakeIn,
    ApproveIntakeOut,
    BatchIntakeIn,
    BatchIntakeJobError,
    BatchIntakeOut,
    CandidateOut,
    CandidateUpdate,
    IntakeJobCreate,
    IntakeJobOut,
)
from src.schemas.recipe import RecipeSummaryOut
from src.services import intake_service

router = APIRouter(prefix="/intake-jobs", tags=["intake"])


def _candidate_out(candidate) -> CandidateOut:
    return CandidateOut.model_validate(candidate, from_attributes=True)


# ── Create ─────────────────────────────────────────────────────────────────────

@router.post("", response_model=ApiResponse[IntakeJobOut], status_code=status.HTTP_201_CREATED)
async def create_intake_job(body: IntakeJobCreate, db: Session = Depends(get_db)):
    if body.intake_type == "paste_text" and not body.raw_source_text:
        raise HTTPException(
            status_code=422,
            detail=error_detail("validation_error", "raw_source_text is required for paste_text intake."),
        )
    job = intake_service.create_intake_job(db, body)
    db.commit()
    db.refresh(job)
    return ApiResponse(data=IntakeJobOut.from_orm(job))


# ── Batch create ──────────────────────────────────────────────────────────────

@router.post("/batch", response_model=ApiResponse[BatchIntakeOut], status_code=status.HTTP_201_CREATED)
async def batch_create_intake_jobs(body: BatchIntakeIn, db: Session = Depends(get_db)):
    """Create multiple intake jobs in a single request (max 50).

    Each job is attempted independently. Failures are collected and returned
    alongside successes — the batch does not abort on a per-item failure.
    """
    created: list[IntakeJobOut] = []
    errors: list[BatchIntakeJobError] = []

    for idx, job_create in enumerate(body.jobs):
        try:
            sp = db.begin_nested()
            if job_create.intake_type == "paste_text" and not job_create.raw_source_text:
                raise ValueError("raw_source_text is required for paste_text intake.")
            job = intake_service.create_intake_job(db, job_create)
            db.flush()
            db.refresh(job)
            sp.commit()
            created.append(IntakeJobOut.from_orm(job))
        except Exception as exc:
            sp.rollback()
            errors.append(BatchIntakeJobError(index=idx, message=str(exc)))

    db.commit()

    result = BatchIntakeOut(
        created=created,
        errors=errors,
        total=len(body.jobs),
        succeeded=len(created),
        failed=len(errors),
    )
    return ApiResponse(data=result)


# ── Get ────────────────────────────────────────────────────────────────────────

@router.get("/{job_id}", response_model=ApiResponse[IntakeJobOut])
async def get_intake_job(job_id: str, db: Session = Depends(get_db)):
    job = intake_service.get_intake_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Intake job not found."))
    return ApiResponse(data=IntakeJobOut.from_orm(job))


# ── Update candidate ──────────────────────────────────────────────────────────

@router.patch("/{job_id}/candidate", response_model=ApiResponse[CandidateOut])
async def update_candidate(job_id: str, body: CandidateUpdate, db: Session = Depends(get_db)):
    candidate = intake_service.update_candidate(db, job_id, body)
    if candidate is None:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Intake job not found."))
    db.commit()
    db.refresh(candidate)
    return ApiResponse(data=_candidate_out(candidate))


# ── Normalize (AI-assisted) ───────────────────────────────────────────────────

@router.post("/{job_id}/normalize", response_model=ApiResponse[CandidateOut])
async def normalize_candidate(job_id: str, db: Session = Depends(get_db)):
    """
    Run AI normalization against the job's raw source text.

    Requires LM_STUDIO_ENABLED=true in settings.
    On AI failure the endpoint returns 503 with a machine-readable error code
    so the frontend can show a degraded-mode notice and allow manual entry.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail=error_detail("ai_disabled", "AI normalization is not enabled. Set LM_STUDIO_ENABLED=true to use this feature."),
        )

    job = intake_service.get_intake_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Intake job not found."))

    if not job.raw_source_text:
        raise HTTPException(
            status_code=422,
            detail=error_detail("no_source_text", "Intake job has no raw source text to normalize."),
        )

    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = await asyncio.to_thread(
        normalize_recipe,
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
                detail=error_detail("ai_unavailable", "AI service is unavailable. You can continue manually."),
            )
        raise HTTPException(
            status_code=502,
            detail=error_detail(f"ai_{err.kind.value}", err.message),
        )

    # Apply the AI-suggested fields to the candidate
    candidate = intake_service.update_candidate(db, job_id, result.candidate_update)
    if candidate is None:
        raise HTTPException(status_code=500, detail=error_detail("internal_error", "Failed to apply normalization result."))

    db.commit()
    db.refresh(candidate)
    return ApiResponse(data=_candidate_out(candidate))


# ── Approve ────────────────────────────────────────────────────────────────────

@router.post("/{job_id}/approve", response_model=ApiResponse[ApproveIntakeOut], status_code=status.HTTP_201_CREATED)
async def approve_intake_job(job_id: str, body: ApproveIntakeIn, db: Session = Depends(get_db)):
    job = intake_service.get_intake_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Intake job not found."))
    if job.status == "approved":
        raise HTTPException(
            status_code=409,
            detail=error_detail("conflict", "Intake job has already been approved."),
        )
    if not job.candidate or not job.candidate.title:
        raise HTTPException(
            status_code=422,
            detail=error_detail("candidate_incomplete", "Candidate must have a title before approval."),
        )

    recipe = intake_service.approve_intake_job(db, job_id, body)
    if not recipe:
        raise HTTPException(status_code=500, detail=error_detail("internal_error", "Approval failed."))

    db.commit()
    db.refresh(recipe)
    return ApiResponse(data=ApproveIntakeOut(
        recipe=RecipeSummaryOut.from_orm_with_json(recipe),
        intake_job_id=job_id,
    ))


# ── Evaluate (AI quality review) ──────────────────────────────────────────────

@router.post("/{job_id}/evaluate", response_model=ApiResponse[EvaluationOut])
async def evaluate_candidate(job_id: str, db: Session = Depends(get_db)):
    """
    Run an AI quality review of the current candidate against the raw source.

    Returns a structured review with faithfulness assessment and a recommendation.
    Does NOT modify the candidate — this is a read-only review endpoint.
    Requires LM_STUDIO_ENABLED=true.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail=error_detail("ai_disabled", "AI evaluation is not enabled. Set LM_STUDIO_ENABLED=true."),
        )

    job = intake_service.get_intake_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=error_detail("not_found", "Intake job not found."))

    if not job.raw_source_text:
        raise HTTPException(
            status_code=422,
            detail=error_detail("no_source_text", "Intake job has no raw source text to evaluate against."),
        )

    candidate = job.candidate
    if not candidate:
        raise HTTPException(
            status_code=422,
            detail=error_detail("no_candidate", "Intake job has no structured candidate to evaluate."),
        )

    candidate_dict = _candidate_out(candidate).model_dump()

    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = await asyncio.to_thread(
        evaluate_normalization,
        client,
        raw_source_text=job.raw_source_text,
        candidate=candidate_dict,
        model=settings.lm_studio_model,
    )

    if err is not None:
        if err.kind == EvaluationErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail=error_detail("ai_unavailable", "AI service is unavailable."),
            )
        raise HTTPException(
            status_code=502,
            detail=error_detail(f"ai_{err.kind.value}", err.message),
        )

    return ApiResponse(data=EvaluationOut(
        fidelity_assessment=result.fidelity_assessment,
        missing_information=result.missing_information,
        likely_inventions_or_overreaches=result.likely_inventions_or_overreaches,
        ingredient_issues=result.ingredient_issues,
        step_issues=result.step_issues,
        metadata_confidence=result.metadata_confidence,
        review_recommendation=result.review_recommendation,
        reviewer_notes=result.reviewer_notes,
    ))
