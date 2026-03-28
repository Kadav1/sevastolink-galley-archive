"""
Intake endpoint tests — paste_text flow + normalize endpoint.
"""

import os
from unittest.mock import patch, MagicMock
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app

TEST_DB_URL = "sqlite:///./data/db/galley_intake_test.sqlite"
TEST_DB_PATH = "./data/db/galley_intake_test.sqlite"


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


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_paste_text_job(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/v1/intake-jobs", json={
            "intake_type": "paste_text",
            "raw_source_text": "Shakshuka\n\n2 tbsp olive oil\n1 onion, sliced",
            "source_notes": "From a saved note.",
        })
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["intake_type"] == "paste_text"
    assert d["status"] == "captured"
    assert d["candidate_id"] is not None


@pytest.mark.asyncio
async def test_create_paste_text_requires_raw_source(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/v1/intake-jobs", json={
            "intake_type": "paste_text",
        })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_get_intake_job(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create = await ac.post("/api/v1/intake-jobs", json={
            "intake_type": "paste_text",
            "raw_source_text": "Some recipe text",
        })
        job_id = create.json()["data"]["id"]
        r = await ac.get(f"/api/v1/intake-jobs/{job_id}")
    assert r.status_code == 200
    assert r.json()["data"]["id"] == job_id


@pytest.mark.asyncio
async def test_get_intake_job_not_found(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/intake-jobs/DOESNOTEXIST")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_candidate(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create = await ac.post("/api/v1/intake-jobs", json={
            "intake_type": "paste_text",
            "raw_source_text": "Shakshuka\n\noil, onion, eggs",
        })
        job_id = create.json()["data"]["id"]

        r = await ac.patch(f"/api/v1/intake-jobs/{job_id}/candidate", json={
            "title": "Shakshuka",
            "dish_role": "Breakfast",
            "primary_cuisine": "Levantine",
            "ingredients": [
                {"position": 1, "item": "olive oil", "quantity": "2 tbsp"},
                {"position": 2, "item": "onion", "quantity": "1"},
                {"position": 3, "item": "eggs", "quantity": "4"},
            ],
            "steps": [
                {"position": 1, "instruction": "Heat oil, soften onion."},
                {"position": 2, "instruction": "Add eggs and cook until set."},
            ],
        })
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["title"] == "Shakshuka"
    assert d["dish_role"] == "Breakfast"


@pytest.mark.asyncio
async def test_approve_intake_job(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create = await ac.post("/api/v1/intake-jobs", json={
            "intake_type": "paste_text",
            "raw_source_text": "Shakshuka\n\noil, onion, eggs",
        })
        job_id = create.json()["data"]["id"]

        await ac.patch(f"/api/v1/intake-jobs/{job_id}/candidate", json={
            "title": "Shakshuka",
            "dish_role": "Breakfast",
        })

        r = await ac.post(f"/api/v1/intake-jobs/{job_id}/approve", json={
            "verification_state": "Unverified",
            "source_type": "Manual",
            "source_notes": "Pasted from notes.",
        })
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["recipe"]["title"] == "Shakshuka"
    assert d["recipe"]["verification_state"] == "Unverified"
    assert d["intake_job_id"] == job_id


@pytest.mark.asyncio
async def test_approve_without_title_fails(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create = await ac.post("/api/v1/intake-jobs", json={
            "intake_type": "paste_text",
            "raw_source_text": "some pasted text",
        })
        job_id = create.json()["data"]["id"]
        # Do NOT update candidate with a title
        r = await ac.post(f"/api/v1/intake-jobs/{job_id}/approve", json={
            "verification_state": "Draft",
            "source_type": "Manual",
        })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_approve_twice_fails(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create = await ac.post("/api/v1/intake-jobs", json={
            "intake_type": "paste_text",
            "raw_source_text": "Ratatouille\n\ncourgette, tomato",
        })
        job_id = create.json()["data"]["id"]

        await ac.patch(f"/api/v1/intake-jobs/{job_id}/candidate", json={"title": "Ratatouille"})
        await ac.post(f"/api/v1/intake-jobs/{job_id}/approve", json={
            "verification_state": "Draft",
            "source_type": "Manual",
        })
        r = await ac.post(f"/api/v1/intake-jobs/{job_id}/approve", json={
            "verification_state": "Draft",
            "source_type": "Manual",
        })
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_approved_recipe_appears_in_library(client):
    """Approve an intake job and confirm the recipe is retrievable from /recipes."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create = await ac.post("/api/v1/intake-jobs", json={
            "intake_type": "paste_text",
            "raw_source_text": "Dal Tadka\n\nlentils, cumin, ghee",
        })
        job_id = create.json()["data"]["id"]

        await ac.patch(f"/api/v1/intake-jobs/{job_id}/candidate", json={
            "title": "Dal Tadka",
            "dish_role": "Dinner",
            "primary_cuisine": "South Asian",
        })
        await ac.post(f"/api/v1/intake-jobs/{job_id}/approve", json={
            "verification_state": "Unverified",
            "source_type": "Manual",
        })

        r = await ac.get("/api/v1/recipes")
    assert r.status_code == 200
    titles = [rec["title"] for rec in r.json()["data"]]
    assert "Dal Tadka" in titles


@pytest.mark.asyncio
async def test_manual_intake_job(client):
    """Manual intake type creates a job with empty raw_source_text."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/v1/intake-jobs", json={
            "intake_type": "manual",
        })
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["intake_type"] == "manual"
    assert d["raw_source_text"] is None


# ── Normalize endpoint tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_normalize_returns_503_when_ai_disabled(client):
    """Normalize endpoint returns 503 ai_disabled when LM_STUDIO_ENABLED=false."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create = await ac.post("/api/v1/intake-jobs", json={
            "intake_type": "paste_text",
            "raw_source_text": "Eggs Benedict\n\n4 eggs, 2 muffins",
        })
        job_id = create.json()["data"]["id"]
        r = await ac.post(f"/api/v1/intake-jobs/{job_id}/normalize")
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_normalize_returns_503_when_lm_studio_unreachable(client):
    """Normalize endpoint returns 503 ai_unavailable when LM Studio is off."""
    from src.ai.normalizer import NormalizationError, NormalizationErrorKind
    from src.config.settings import settings

    transport_err = NormalizationError(NormalizationErrorKind.transport_failure, "Connection refused")

    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.intake.normalize_recipe", return_value=(None, transport_err)):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            create = await ac.post("/api/v1/intake-jobs", json={
                "intake_type": "paste_text",
                "raw_source_text": "Eggs Benedict\n\n4 eggs, 2 muffins",
            })
            job_id = create.json()["data"]["id"]
            r = await ac.post(f"/api/v1/intake-jobs/{job_id}/normalize")

    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_normalize_applies_ai_result_to_candidate(client):
    """Normalize endpoint applies a successful AI result and returns updated CandidateOut."""
    from src.ai.normalizer import NormalizationResult, NormalizationError
    from src.schemas.intake import CandidateUpdate
    from src.schemas.recipe import IngredientIn, StepIn
    from src.config.settings import settings

    ai_candidate = CandidateUpdate(
        title="Eggs Benedict",
        dish_role="Breakfast",
        primary_cuisine="American",
        prep_time_minutes=10,
        cook_time_minutes=10,
        ingredients=[
            IngredientIn(position=1, item="eggs", quantity="4"),
            IngredientIn(position=2, item="English muffins", quantity="2"),
        ],
        steps=[
            StepIn(position=1, instruction="Poach the eggs."),
            StepIn(position=2, instruction="Toast the muffins."),
        ],
    )
    mock_result = NormalizationResult(
        candidate_update=ai_candidate,
        ambiguities=[],
        warnings=[],
    )

    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.intake.normalize_recipe", return_value=(mock_result, None)):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            create = await ac.post("/api/v1/intake-jobs", json={
                "intake_type": "paste_text",
                "raw_source_text": "Eggs Benedict\n\n4 eggs, 2 muffins",
            })
            job_id = create.json()["data"]["id"]
            r = await ac.post(f"/api/v1/intake-jobs/{job_id}/normalize")

    assert r.status_code == 200
    d = r.json()["data"]
    assert d["title"] == "Eggs Benedict"
    assert d["dish_role"] == "Breakfast"
    assert d["primary_cuisine"] == "American"
    assert d["prep_time_minutes"] == 10
    assert len(d["ingredients"]) == 2
    assert len(d["steps"]) == 2
    assert d["ingredients"][0]["item"] == "eggs"
    assert d["steps"][0]["instruction"] == "Poach the eggs."
