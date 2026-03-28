"""
Tests for POST /recipes/{id_or_slug}/suggest-metadata.
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

TEST_DB_URL = "sqlite:///./data/db/galley_meta_test.sqlite"
TEST_DB_PATH = "./data/db/galley_meta_test.sqlite"


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
        "title": "Shakshuka",
        "ingredients": [{"position": 1, "item": "eggs", "quantity": "4"}],
        "steps": [{"position": 1, "instruction": "Simmer eggs in tomato sauce."}],
    })
    return r.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_suggest_metadata_returns_503_when_ai_disabled(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        slug = await _create_recipe(ac)
        r = await ac.post(f"/api/v1/recipes/{slug}/suggest-metadata")
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_suggest_metadata_returns_404_for_unknown_recipe(client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/recipes/does-not-exist/suggest-metadata")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_suggest_metadata_returns_503_when_lm_studio_unreachable(client):
    from src.ai.metadata_suggester import MetadataError, MetadataErrorKind
    from src.config.settings import settings
    transport_err = MetadataError(MetadataErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.suggest_metadata", return_value=(None, transport_err)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            slug = await _create_recipe(ac)
            r = await ac.post(f"/api/v1/recipes/{slug}/suggest-metadata")
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_suggest_metadata_returns_suggestions(client):
    from src.ai.metadata_suggester import MetadataResult
    from src.config.settings import settings
    mock_result = MetadataResult(payload={
        "dish_role": "Breakfast",
        "primary_cuisine": "Levantine",
        "secondary_cuisines": [],
        "technique_family": "Simmer",
        "ingredient_families": ["Eggs", "Tomatoes"],
        "complexity": "Easy",
        "time_class": "Quick",
        "service_format": None,
        "season": None,
        "mood_tags": [],
        "storage_profile": [],
        "dietary_flags": ["Vegetarian"],
        "sector": None,
        "class": None,
        "heat_window": None,
        "provision_tags": [],
        "short_description": "Eggs poached in spiced tomato sauce.",
        "confidence_notes": ["High confidence on dish_role and technique_family."],
        "uncertainty_notes": [],
    })
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.suggest_metadata", return_value=(mock_result, None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            slug = await _create_recipe(ac)
            r = await ac.post(f"/api/v1/recipes/{slug}/suggest-metadata")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["dish_role"] == "Breakfast"
    assert d["primary_cuisine"] == "Levantine"
    assert "Vegetarian" in d["dietary_flags"]
    assert d["short_description"] == "Eggs poached in spiced tomato sauce."
