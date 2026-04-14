"""
Error envelope contract tests.

Verifies that all error responses use the unified envelope:
    {"error": {"code": "...", "message": "..."}}

Tests use real endpoints with known-bad inputs so the coverage
reflects the actual wire contract.
"""
import pytest


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
async def test_recipe_not_found_shape(async_client):
    r = await async_client.get("/api/v1/recipes/does-not-exist")
    assert r.status_code == 404
    assert_error_envelope(r.json(), "not_found")


@pytest.mark.asyncio
async def test_intake_job_not_found_shape(async_client):
    r = await async_client.get("/api/v1/intake-jobs/does-not-exist")
    assert r.status_code == 404
    assert_error_envelope(r.json(), "not_found")


@pytest.mark.asyncio
async def test_media_asset_not_found_shape(async_client):
    r = await async_client.get("/api/v1/media-assets/does-not-exist")
    assert r.status_code == 404
    assert_error_envelope(r.json(), "not_found")


# ── 422 validation error ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pydantic_validation_error_shape(async_client):
    # Missing required field — triggers RequestValidationError
    r = await async_client.post("/api/v1/intake-jobs", json={})
    assert r.status_code == 422
    assert_error_envelope(r.json(), "validation_error")


@pytest.mark.asyncio
async def test_paste_text_missing_source_shape(async_client):
    r = await async_client.post("/api/v1/intake-jobs", json={"intake_type": "paste_text"})
    assert r.status_code == 422
    assert_error_envelope(r.json(), "validation_error")


# ── 503 AI disabled ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_normalize_ai_disabled_shape(async_client):
    # Create a job first, then attempt normalize (AI is disabled in tests)
    create = await async_client.post(
        "/api/v1/intake-jobs",
        json={"intake_type": "paste_text", "raw_source_text": "some text"},
    )
    assert create.status_code == 201
    job_id = create.json()["data"]["id"]

    r = await async_client.post(f"/api/v1/intake-jobs/{job_id}/normalize")
    assert r.status_code == 503
    assert_error_envelope(r.json(), "ai_disabled")


@pytest.mark.asyncio
async def test_pantry_suggest_ai_disabled_shape(async_client):
    r = await async_client.post(
        "/api/v1/pantry/suggest",
        json={"available_ingredients": ["eggs", "butter"]},
    )
    assert r.status_code == 503
    assert_error_envelope(r.json(), "ai_disabled")


# ── No legacy "detail" wrapper on any error ───────────────────────────────────

@pytest.mark.asyncio
async def test_no_detail_wrapper_on_404(async_client):
    r = await async_client.get("/api/v1/recipes/nonexistent")
    body = r.json()
    assert "detail" not in body
    assert "error" in body


@pytest.mark.asyncio
async def test_no_detail_wrapper_on_422(async_client):
    r = await async_client.post("/api/v1/intake-jobs", json={})
    body = r.json()
    assert "detail" not in body
    assert "error" in body
