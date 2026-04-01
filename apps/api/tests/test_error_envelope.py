"""
Error envelope contract tests.

Verifies that all error responses use the unified envelope:
    {"error": {"code": "...", "message": "..."}}

Tests use real endpoints with known-bad inputs so the coverage
reflects the actual wire contract.
"""
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app

TEST_DB_URL = "sqlite:///./data/db/galley_error_envelope_test.sqlite"
TEST_DB_PATH = "./data/db/galley_error_envelope_test.sqlite"


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


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


# ── Shape contract helpers ─────────────────────────────────────────────────────

def assert_error_envelope(body: dict, expected_code: str | None = None) -> None:
    """Assert the unified error envelope shape."""
    assert "error" in body, f"Expected 'error' key, got: {list(body.keys())}"
    assert "detail" not in body, f"Unexpected FastAPI 'detail' wrapper present"
    error = body["error"]
    assert "code" in error, f"'error' dict missing 'code': {error}"
    assert "message" in error, f"'error' dict missing 'message': {error}"
    if expected_code is not None:
        assert error["code"] == expected_code, f"Expected code={expected_code!r}, got={error['code']!r}"


# ── 404 not found ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_recipe_not_found_shape(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/recipes/does-not-exist")
    assert r.status_code == 404
    assert_error_envelope(r.json(), "not_found")


@pytest.mark.asyncio
async def test_intake_job_not_found_shape(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/intake-jobs/does-not-exist")
    assert r.status_code == 404
    assert_error_envelope(r.json(), "not_found")


@pytest.mark.asyncio
async def test_media_asset_not_found_shape(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/media-assets/does-not-exist")
    assert r.status_code == 404
    assert_error_envelope(r.json(), "not_found")


# ── 422 validation error ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pydantic_validation_error_shape(client):
    # Missing required field — triggers RequestValidationError
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/v1/intake-jobs", json={})
    assert r.status_code == 422
    assert_error_envelope(r.json(), "validation_error")


@pytest.mark.asyncio
async def test_paste_text_missing_source_shape(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/v1/intake-jobs", json={"intake_type": "paste_text"})
    assert r.status_code == 422
    assert_error_envelope(r.json(), "validation_error")


# ── 503 AI disabled ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_normalize_ai_disabled_shape(client):
    # Create a job first, then attempt normalize (AI is disabled in tests)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create = await ac.post(
            "/api/v1/intake-jobs",
            json={"intake_type": "paste_text", "raw_source_text": "some text"},
        )
        assert create.status_code == 201
        job_id = create.json()["data"]["id"]

        r = await ac.post(f"/api/v1/intake-jobs/{job_id}/normalize")
    assert r.status_code == 503
    assert_error_envelope(r.json(), "ai_disabled")


@pytest.mark.asyncio
async def test_pantry_suggest_ai_disabled_shape(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/v1/pantry/suggest",
            json={"available_ingredients": ["eggs", "butter"]},
        )
    assert r.status_code == 503
    assert_error_envelope(r.json(), "ai_disabled")


# ── No legacy "detail" wrapper on any error ───────────────────────────────────

@pytest.mark.asyncio
async def test_no_detail_wrapper_on_404(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/recipes/nonexistent")
    body = r.json()
    assert "detail" not in body
    assert "error" in body


@pytest.mark.asyncio
async def test_no_detail_wrapper_on_422(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/v1/intake-jobs", json={})
    body = r.json()
    assert "detail" not in body
    assert "error" in body
