"""
Tests for POST /intake-jobs/{job_id}/evaluate.
"""
import os
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app

TEST_DB_URL = "sqlite:///./data/db/galley_eval_test.sqlite"
TEST_DB_PATH = "./data/db/galley_eval_test.sqlite"


@pytest.fixture(scope="function")
def db_session():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    from src.config.settings import settings
    orig_url = settings.database_url
    settings.database_url = TEST_DB_URL
    init_db()
    settings.database_url = orig_url
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


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
async def test_evaluate_returns_503_when_ai_disabled(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        job_id = await _create_job_with_candidate(ac)
        r = await ac.post(f"/api/v1/intake-jobs/{job_id}/evaluate")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_evaluate_returns_404_for_unknown_job(client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/intake-jobs/DOESNOTEXIST/evaluate")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_evaluate_returns_503_when_lm_studio_unreachable(client):
    from src.ai.evaluator import EvaluationError, EvaluationErrorKind
    from src.config.settings import settings
    transport_err = EvaluationError(EvaluationErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.intake.evaluate_normalization", return_value=(None, transport_err)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            job_id = await _create_job_with_candidate(ac)
            r = await ac.post(f"/api/v1/intake-jobs/{job_id}/evaluate")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_evaluate_returns_review_result(client):
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
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            job_id = await _create_job_with_candidate(ac)
            r = await ac.post(f"/api/v1/intake-jobs/{job_id}/evaluate")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["review_recommendation"] == "safe_for_human_review"
    assert d["fidelity_assessment"] == "The candidate faithfully represents the source."
    assert d["reviewer_notes"] == ["Title matches source."]
