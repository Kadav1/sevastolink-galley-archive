"""
Tests for POST /intake-jobs/{job_id}/evaluate.
"""
from unittest.mock import patch
import pytest
from httpx import AsyncClient


async def _create_job_with_candidate(ac: AsyncClient) -> str:
    """Helper: create a paste_text job and set a candidate title."""
    create = await ac.post("/api/v1/intake-jobs", json={
        "intake_type": "paste_text",
        "raw_source_text": "Shakshuka\n\n2 eggs, 1 onion, canned tomatoes",
    })
    job_id = create.json()["data"]["id"]
    await ac.patch(f"/api/v1/intake-jobs/{job_id}/candidate", json={"title": "Shakshuka"})
    return job_id


@pytest.mark.asyncio
async def test_evaluate_returns_503_when_ai_disabled(async_client):
    job_id = await _create_job_with_candidate(async_client)
    r = await async_client.post(f"/api/v1/intake-jobs/{job_id}/evaluate")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_evaluate_returns_404_for_unknown_job(async_client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        r = await async_client.post("/api/v1/intake-jobs/DOESNOTEXIST/evaluate")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_evaluate_returns_503_when_lm_studio_unreachable(async_client):
    from src.ai.evaluator import EvaluationError, EvaluationErrorKind
    from src.config.settings import settings
    transport_err = EvaluationError(EvaluationErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.intake.evaluate_normalization", return_value=(None, transport_err)):
        job_id = await _create_job_with_candidate(async_client)
        r = await async_client.post(f"/api/v1/intake-jobs/{job_id}/evaluate")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_evaluate_returns_review_result(async_client):
    from src.ai.evaluator import EvaluationResult
    from src.config.settings import settings
    mock_result = EvaluationResult(
        fidelity_assessment="The candidate faithfully represents the source.",
        missing_information=[],
        likely_inventions_or_overreaches=[],
        ingredient_issues=[],
        step_issues=[],
        metadata_confidence="moderate",
        review_recommendation="safe_for_human_review",
        reviewer_notes=["Title matches source."],
    )
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.intake.evaluate_normalization", return_value=(mock_result, None)):
        job_id = await _create_job_with_candidate(async_client)
        r = await async_client.post(f"/api/v1/intake-jobs/{job_id}/evaluate")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["review_recommendation"] == "safe_for_human_review"
    assert d["fidelity_assessment"] == "The candidate faithfully represents the source."
    assert d["reviewer_notes"] == ["Title matches source."]
