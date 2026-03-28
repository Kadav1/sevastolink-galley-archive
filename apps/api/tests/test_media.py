"""
Tests for media endpoints:

  POST /intake-jobs/{job_id}/media   — attach source file to intake job
  POST /recipes/{id_or_slug}/media   — attach cover image to recipe
  GET  /media-assets/{asset_id}      — retrieve asset metadata
  GET  /media-assets/{asset_id}/file — serve asset binary
"""
import io
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app

TEST_DB_URL = "sqlite:///./data/db/galley_media_test.sqlite"
TEST_DB_PATH = "./data/db/galley_media_test.sqlite"

# Minimal valid PNG header bytes
_FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


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
def client(db_session, tmp_path):
    async def override_get_db():
        yield db_session

    from src.config.settings import settings
    orig_media_dir = settings.media_dir
    settings.media_dir = tmp_path

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    settings.media_dir = orig_media_dir


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _create_job(ac: AsyncClient) -> str:
    r = await ac.post("/api/v1/intake-jobs", json={
        "intake_type": "paste_text",
        "raw_source_text": "Test recipe source text",
    })
    assert r.status_code == 201
    return r.json()["data"]["id"]


async def _create_recipe(ac: AsyncClient, title: str = "Test Recipe") -> str:
    r = await ac.post("/api/v1/recipes", json={
        "title": title,
        "ingredients": [{"position": 1, "item": "flour"}],
        "steps": [{"position": 1, "instruction": "Mix."}],
    })
    assert r.status_code == 201
    return r.json()["data"]["slug"]


# ── Intake job media tests ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_attach_png_to_intake_job(client):
    """Uploading a PNG to an intake job returns a source_image asset."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        job_id = await _create_job(ac)
        r = await ac.post(
            f"/api/v1/intake-jobs/{job_id}/media",
            files={"file": ("photo.png", io.BytesIO(_FAKE_PNG), "image/png")},
        )
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["asset_kind"] == "source_image"
    assert d["mime_type"] == "image/png"
    assert d["original_filename"] == "photo.png"
    assert d["byte_size"] == len(_FAKE_PNG)
    assert "id" in d


@pytest.mark.asyncio
async def test_attach_pdf_to_intake_job(client):
    """Uploading a PDF produces asset_kind='source_pdf'."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        job_id = await _create_job(ac)
        r = await ac.post(
            f"/api/v1/intake-jobs/{job_id}/media",
            files={"file": ("recipe.pdf", io.BytesIO(b"%PDF-1.4 ..."), "application/pdf")},
        )
    assert r.status_code == 200
    assert r.json()["data"]["asset_kind"] == "source_pdf"


@pytest.mark.asyncio
async def test_attach_intake_media_links_job(client, db_session):
    """source_media_asset_id on the intake job is set after upload."""
    from src.models.intake import IntakeJob
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        job_id = await _create_job(ac)
        r = await ac.post(
            f"/api/v1/intake-jobs/{job_id}/media",
            files={"file": ("img.png", io.BytesIO(_FAKE_PNG), "image/png")},
        )
    asset_id = r.json()["data"]["id"]
    db_session.expire_all()
    job = db_session.get(IntakeJob, job_id)
    assert job is not None
    assert job.source_media_asset_id == asset_id


@pytest.mark.asyncio
async def test_attach_unsupported_mime_returns_422(client):
    """Non-image/non-pdf MIME type is rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        job_id = await _create_job(ac)
        r = await ac.post(
            f"/api/v1/intake-jobs/{job_id}/media",
            files={"file": ("doc.txt", io.BytesIO(b"hello"), "text/plain")},
        )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_attach_media_unknown_job_returns_404(client):
    """Uploading to a non-existent intake job returns 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/v1/intake-jobs/does-not-exist/media",
            files={"file": ("img.png", io.BytesIO(_FAKE_PNG), "image/png")},
        )
    assert r.status_code == 404


# ── Recipe media tests ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_attach_cover_image_to_recipe(client):
    """Uploading a cover image to a recipe returns a source_image asset."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        slug = await _create_recipe(ac)
        r = await ac.post(
            f"/api/v1/recipes/{slug}/media",
            files={"file": ("cover.png", io.BytesIO(_FAKE_PNG), "image/png")},
        )
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["asset_kind"] == "source_image"
    assert d["original_filename"] == "cover.png"


@pytest.mark.asyncio
async def test_attach_recipe_media_links_recipe(client, db_session):
    """cover_media_asset_id on the recipe is set after upload."""
    from src.models.recipe import Recipe
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        slug = await _create_recipe(ac, title="Covered Recipe")
        r = await ac.post(
            f"/api/v1/recipes/{slug}/media",
            files={"file": ("cover.png", io.BytesIO(_FAKE_PNG), "image/png")},
        )
    asset_id = r.json()["data"]["id"]
    db_session.expire_all()
    recipe = db_session.query(Recipe).filter(Recipe.slug == slug).first()
    assert recipe is not None
    assert recipe.cover_media_asset_id == asset_id


@pytest.mark.asyncio
async def test_attach_recipe_media_unknown_recipe_returns_404(client):
    """Uploading to a non-existent recipe returns 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/v1/recipes/no-such-recipe/media",
            files={"file": ("img.png", io.BytesIO(_FAKE_PNG), "image/png")},
        )
    assert r.status_code == 404


# ── Media asset retrieval tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_media_asset_metadata(client):
    """GET /media-assets/{id} returns the persisted metadata."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        job_id = await _create_job(ac)
        upload = await ac.post(
            f"/api/v1/intake-jobs/{job_id}/media",
            files={"file": ("img.png", io.BytesIO(_FAKE_PNG), "image/png")},
        )
        asset_id = upload.json()["data"]["id"]
        r = await ac.get(f"/api/v1/media-assets/{asset_id}")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["id"] == asset_id
    assert d["mime_type"] == "image/png"


@pytest.mark.asyncio
async def test_get_media_asset_unknown_returns_404(client):
    """GET /media-assets/{id} for unknown id returns 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/media-assets/does-not-exist")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_serve_media_file_returns_bytes(client):
    """GET /media-assets/{id}/file returns the raw file bytes."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        job_id = await _create_job(ac)
        upload = await ac.post(
            f"/api/v1/intake-jobs/{job_id}/media",
            files={"file": ("img.png", io.BytesIO(_FAKE_PNG), "image/png")},
        )
        asset_id = upload.json()["data"]["id"]
        r = await ac.get(f"/api/v1/media-assets/{asset_id}/file")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/png")
    assert r.content == _FAKE_PNG
