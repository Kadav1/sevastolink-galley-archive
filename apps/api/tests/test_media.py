"""
Tests for media endpoints:

  POST /intake-jobs/{job_id}/media   — attach source file to intake job
  POST /recipes/{id_or_slug}/media   — attach cover image to recipe
  GET  /media-assets/{asset_id}      — retrieve asset metadata
  GET  /media-assets/{asset_id}/file — serve asset binary
"""
import io
import pytest
from httpx import AsyncClient

# Minimal valid PNG header bytes
_FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


@pytest.fixture
async def client(async_client, tmp_path):
    """Wraps async_client with a temporary media directory override."""
    from src.config.settings import settings
    orig_media_dir = settings.media_dir
    settings.media_dir = tmp_path
    yield async_client
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
    job_id = await _create_job(client)
    r = await client.post(
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
    job_id = await _create_job(client)
    r = await client.post(
        f"/api/v1/intake-jobs/{job_id}/media",
        files={"file": ("recipe.pdf", io.BytesIO(b"%PDF-1.4 ..."), "application/pdf")},
    )
    assert r.status_code == 200
    assert r.json()["data"]["asset_kind"] == "source_pdf"


@pytest.mark.asyncio
async def test_attach_intake_media_links_job(client, db_session):
    """source_media_asset_id on the intake job is set after upload."""
    from src.models.intake import IntakeJob
    job_id = await _create_job(client)
    r = await client.post(
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
    job_id = await _create_job(client)
    r = await client.post(
        f"/api/v1/intake-jobs/{job_id}/media",
        files={"file": ("doc.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_attach_media_unknown_job_returns_404(client):
    """Uploading to a non-existent intake job returns 404."""
    r = await client.post(
        "/api/v1/intake-jobs/does-not-exist/media",
        files={"file": ("img.png", io.BytesIO(_FAKE_PNG), "image/png")},
    )
    assert r.status_code == 404


# ── Recipe media tests ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_attach_cover_image_to_recipe(client):
    """Uploading a cover image to a recipe returns a source_image asset."""
    slug = await _create_recipe(client)
    r = await client.post(
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
    slug = await _create_recipe(client, title="Covered Recipe")
    r = await client.post(
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
    r = await client.post(
        "/api/v1/recipes/no-such-recipe/media",
        files={"file": ("img.png", io.BytesIO(_FAKE_PNG), "image/png")},
    )
    assert r.status_code == 404


# ── Media asset retrieval tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_media_asset_metadata(client):
    """GET /media-assets/{id} returns the persisted metadata."""
    job_id = await _create_job(client)
    upload = await client.post(
        f"/api/v1/intake-jobs/{job_id}/media",
        files={"file": ("img.png", io.BytesIO(_FAKE_PNG), "image/png")},
    )
    asset_id = upload.json()["data"]["id"]
    r = await client.get(f"/api/v1/media-assets/{asset_id}")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["id"] == asset_id
    assert d["mime_type"] == "image/png"


@pytest.mark.asyncio
async def test_get_media_asset_unknown_returns_404(client):
    """GET /media-assets/{id} for unknown id returns 404."""
    r = await client.get("/api/v1/media-assets/does-not-exist")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_serve_media_file_returns_bytes(client):
    """GET /media-assets/{id}/file returns the raw file bytes."""
    job_id = await _create_job(client)
    upload = await client.post(
        f"/api/v1/intake-jobs/{job_id}/media",
        files={"file": ("img.png", io.BytesIO(_FAKE_PNG), "image/png")},
    )
    asset_id = upload.json()["data"]["id"]
    r = await client.get(f"/api/v1/media-assets/{asset_id}/file")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/png")
    assert r.content == _FAKE_PNG


@pytest.mark.asyncio
async def test_serve_media_file_rejects_path_traversal(client, db_session):
    """A stored asset whose relative_path escapes media_dir must return 403."""
    import uuid
    from src.models.media import MediaAsset

    evil_asset = MediaAsset(
        id=str(uuid.uuid4()),
        asset_kind="source_image",
        original_filename="evil.png",
        mime_type="image/png",
        relative_path="../../outside_media_dir.txt",
        checksum="deadbeef",
        byte_size=100,
    )
    db_session.add(evil_asset)
    db_session.commit()

    r = await client.get(f"/api/v1/media-assets/{evil_asset.id}/file")
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_upload_over_20mb_returns_422(client):
    """A file exceeding 20 MB is rejected with 422 file_too_large."""
    oversized = b"\x89PNG\r\n\x1a\n" + b"\x00" * (20 * 1024 * 1024 + 1)
    job_id = await _create_job(client)
    r = await client.post(
        f"/api/v1/intake-jobs/{job_id}/media",
        files={"file": ("big.png", io.BytesIO(oversized), "image/png")},
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "file_too_large"


@pytest.mark.asyncio
async def test_attach_jpeg_to_intake_job(client):
    """JPEG uploads are accepted and produce asset_kind='source_image'."""
    _FAKE_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    job_id = await _create_job(client)
    r = await client.post(
        f"/api/v1/intake-jobs/{job_id}/media",
        files={"file": ("photo.jpg", io.BytesIO(_FAKE_JPEG), "image/jpeg")},
    )
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["asset_kind"] == "source_image"
    assert d["mime_type"] == "image/jpeg"


@pytest.mark.asyncio
async def test_attach_webp_to_intake_job(client):
    """WebP uploads are accepted and produce asset_kind='source_image'."""
    _FAKE_WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 50
    job_id = await _create_job(client)
    r = await client.post(
        f"/api/v1/intake-jobs/{job_id}/media",
        files={"file": ("photo.webp", io.BytesIO(_FAKE_WEBP), "image/webp")},
    )
    assert r.status_code == 200
    assert r.json()["data"]["asset_kind"] == "source_image"


@pytest.mark.asyncio
async def test_attach_empty_file_is_accepted(client):
    """A zero-byte file passes MIME and size checks (no minimum size guard)."""
    job_id = await _create_job(client)
    r = await client.post(
        f"/api/v1/intake-jobs/{job_id}/media",
        files={"file": ("empty.png", io.BytesIO(b""), "image/png")},
    )
    assert r.status_code == 200
    assert r.json()["data"]["byte_size"] == 0


@pytest.mark.asyncio
async def test_second_cover_upload_replaces_previous(client, db_session):
    """Uploading a second cover image overwrites cover_media_asset_id on the recipe."""
    from src.models.recipe import Recipe
    slug = await _create_recipe(client, title="Cover Replace Recipe")

    r1 = await client.post(
        f"/api/v1/recipes/{slug}/media",
        files={"file": ("first.png", io.BytesIO(_FAKE_PNG), "image/png")},
    )
    first_id = r1.json()["data"]["id"]

    r2 = await client.post(
        f"/api/v1/recipes/{slug}/media",
        files={"file": ("second.png", io.BytesIO(_FAKE_PNG), "image/png")},
    )
    second_id = r2.json()["data"]["id"]

    assert first_id != second_id
    db_session.expire_all()
    recipe = db_session.query(Recipe).filter(Recipe.slug == slug).first()
    assert recipe.cover_media_asset_id == second_id
