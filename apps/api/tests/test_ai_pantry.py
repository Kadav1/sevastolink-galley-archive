"""
Tests for POST /pantry/suggest.
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

TEST_DB_URL = "sqlite:///./data/db/galley_pantry_test.sqlite"
TEST_DB_PATH = "./data/db/galley_pantry_test.sqlite"


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


@pytest.mark.asyncio
async def test_pantry_returns_503_when_ai_disabled(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/v1/pantry/suggest", json={
            "available_ingredients": ["eggs", "onion", "tomatoes"],
        })
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_pantry_returns_422_for_empty_ingredients(client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/pantry/suggest", json={
                "available_ingredients": [],
            })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_pantry_returns_503_when_lm_studio_unreachable(client):
    from src.ai.pantry_suggester import PantryError, PantryErrorKind
    from src.config.settings import settings
    transport_err = PantryError(PantryErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.pantry.suggest_pantry", return_value=(None, transport_err)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/pantry/suggest", json={
                "available_ingredients": ["eggs", "onion"],
            })
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_pantry_returns_suggestions(client):
    from src.ai.pantry_suggester import PantryResult
    from src.config.settings import settings
    mock_result = PantryResult(payload={
        "direct_matches": [
            {
                "title": "Shakshuka",
                "match_type": "direct",
                "why_it_matches": "All main ingredients available.",
                "missing_items": [],
                "recommended_adjustments": [],
                "time_fit": "Quick",
            }
        ],
        "near_matches": [],
        "pantry_gap_notes": [],
        "substitution_suggestions": [],
        "quick_ideas": ["Scrambled eggs with onion and tomato"],
        "confidence_notes": ["High confidence on direct match."],
    })
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.pantry.suggest_pantry", return_value=(mock_result, None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/pantry/suggest", json={
                "available_ingredients": ["eggs", "onion", "tomatoes"],
            })
    assert r.status_code == 200
    d = r.json()["data"]
    assert len(d["direct_matches"]) == 1
    assert d["direct_matches"][0]["title"] == "Shakshuka"
    assert d["quick_ideas"] == ["Scrambled eggs with onion and tomato"]
