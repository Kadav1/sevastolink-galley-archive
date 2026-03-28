"""
Tests for GET /settings and PATCH /settings.
"""
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app

TEST_DB_URL = "sqlite:///./data/db/galley_settings_test.sqlite"
TEST_DB_PATH = "./data/db/galley_settings_test.sqlite"


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
async def test_get_settings_returns_defaults(client):
    """GET /settings returns defaults when no rows are persisted."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/settings")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["default_verification_state"] == "Draft"
    assert d["library_default_sort"] == "updated_at_desc"
    assert "ai_enabled" in d


@pytest.mark.asyncio
async def test_patch_settings_persists_value(client):
    """PATCH /settings persists a new value and returns it."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.patch("/api/v1/settings", json={"default_verification_state": "Unverified"})
    assert r.status_code == 200
    assert r.json()["data"]["default_verification_state"] == "Unverified"


@pytest.mark.asyncio
async def test_patch_settings_persisted_survives_subsequent_get(client):
    """A patched value is returned by the next GET."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.patch("/api/v1/settings", json={"library_default_sort": "title_asc"})
        r = await ac.get("/api/v1/settings")
    assert r.status_code == 200
    assert r.json()["data"]["library_default_sort"] == "title_asc"


@pytest.mark.asyncio
async def test_patch_settings_with_invalid_value_returns_422(client):
    """Sending an unknown sort value is rejected by Pydantic validation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.patch("/api/v1/settings", json={"library_default_sort": "not_a_valid_sort"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_patch_empty_body_returns_current_values(client):
    """PATCH with no fields returns the current settings without error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.patch("/api/v1/settings", json={})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["default_verification_state"] == "Draft"
    assert d["library_default_sort"] == "updated_at_desc"
