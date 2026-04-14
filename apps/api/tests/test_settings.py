"""
Tests for GET /settings and PATCH /settings.
"""
import pytest


@pytest.mark.asyncio
async def test_get_settings_returns_defaults(async_client):
    """GET /settings returns defaults when no rows are persisted."""
    r = await async_client.get("/api/v1/settings")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["default_verification_state"] == "Draft"
    assert d["library_default_sort"] == "updated_at_desc"
    assert "ai_enabled" in d


@pytest.mark.asyncio
async def test_patch_settings_persists_value(async_client):
    """PATCH /settings persists a new value and returns it."""
    r = await async_client.patch("/api/v1/settings", json={"default_verification_state": "Unverified"})
    assert r.status_code == 200
    assert r.json()["data"]["default_verification_state"] == "Unverified"


@pytest.mark.asyncio
async def test_patch_settings_persisted_survives_subsequent_get(async_client):
    """A patched value is returned by the next GET."""
    await async_client.patch("/api/v1/settings", json={"library_default_sort": "title_asc"})
    r = await async_client.get("/api/v1/settings")
    assert r.status_code == 200
    assert r.json()["data"]["library_default_sort"] == "title_asc"


@pytest.mark.asyncio
async def test_patch_settings_with_invalid_value_returns_422(async_client):
    """Sending an unknown sort value is rejected by Pydantic validation."""
    r = await async_client.patch("/api/v1/settings", json={"library_default_sort": "not_a_valid_sort"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_patch_empty_body_returns_current_values(async_client):
    """PATCH with no fields returns the current settings without error."""
    r = await async_client.patch("/api/v1/settings", json={})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["default_verification_state"] == "Draft"
    assert d["library_default_sort"] == "updated_at_desc"
