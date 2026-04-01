"""
Tests for POST /recipes/{id_or_slug}/rewrite.
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

TEST_DB_URL = "sqlite:///./data/db/galley_rewrite_test.sqlite"
TEST_DB_PATH = "./data/db/galley_rewrite_test.sqlite"


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


async def _create_recipe(ac: AsyncClient) -> str:
    r = await ac.post("/api/v1/recipes", json={
        "title": "Pasta Bolognese",
        "ingredients": [
            {"position": 1, "item": "beef mince", "quantity": "500g"},
            {"position": 2, "item": "pasta", "quantity": "400g"},
        ],
        "steps": [{"position": 1, "instruction": "Brown the mince."}],
    })
    return r.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_rewrite_returns_503_when_ai_disabled(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        slug = await _create_recipe(ac)
        r = await ac.post(f"/api/v1/recipes/{slug}/rewrite")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_rewrite_returns_404_for_unknown_recipe(client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/recipes/does-not-exist/rewrite")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_rewrite_returns_503_when_lm_studio_unreachable(client):
    from src.ai.rewriter import RewriteError, RewriteErrorKind
    from src.config.settings import settings
    transport_err = RewriteError(RewriteErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.rewrite_recipe", return_value=(None, transport_err)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            slug = await _create_recipe(ac)
            r = await ac.post(f"/api/v1/recipes/{slug}/rewrite")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_rewrite_returns_rewritten_recipe(client):
    from src.ai.rewriter import RewriteResult
    from src.config.settings import settings
    mock_result = RewriteResult(payload={
        "title": "Pasta Bolognese",
        "short_description": "Classic Italian meat ragu on pasta.",
        "ingredients": [
            {"amount": "500", "unit": "g", "item": "beef mince", "note": None, "optional": False, "group": None},
            {"amount": "400", "unit": "g", "item": "pasta", "note": None, "optional": False, "group": None},
        ],
        "steps": [
            {"step_number": 1, "instruction": "Brown the beef mince in a wide pan over medium-high heat.",
             "time_note": "5 minutes", "heat_note": "medium-high", "equipment_note": "wide pan"},
        ],
        "recipe_notes": None,
        "service_notes": "Serve immediately with grated Parmesan.",
        "rewrite_notes": ["Clarified heat level in step 1."],
        "uncertainty_notes": [],
    })
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.rewrite_recipe", return_value=(mock_result, None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            slug = await _create_recipe(ac)
            r = await ac.post(f"/api/v1/recipes/{slug}/rewrite")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["title"] == "Pasta Bolognese"
    assert d["short_description"] == "Classic Italian meat ragu on pasta."
    assert len(d["ingredients"]) == 2
    assert len(d["steps"]) == 1
    assert d["steps"][0]["instruction"] == "Brown the beef mince in a wide pan over medium-high heat."
    assert d["rewrite_notes"] == ["Clarified heat level in step 1."]
