"""
Tests for POST /recipes/{id_or_slug}/suggest-metadata.
"""
from unittest.mock import patch
import pytest
from httpx import AsyncClient


async def _create_recipe(ac: AsyncClient) -> str:
    r = await ac.post("/api/v1/recipes", json={
        "title": "Shakshuka",
        "ingredients": [{"position": 1, "item": "eggs", "quantity": "4"}],
        "steps": [{"position": 1, "instruction": "Simmer eggs in tomato sauce."}],
    })
    return r.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_suggest_metadata_returns_503_when_ai_disabled(async_client):
    slug = await _create_recipe(async_client)
    r = await async_client.post(f"/api/v1/recipes/{slug}/suggest-metadata")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_suggest_metadata_returns_404_for_unknown_recipe(async_client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        r = await async_client.post("/api/v1/recipes/does-not-exist/suggest-metadata")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_suggest_metadata_returns_503_when_lm_studio_unreachable(async_client):
    from src.ai.metadata_suggester import MetadataError, MetadataErrorKind
    from src.config.settings import settings
    transport_err = MetadataError(MetadataErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.suggest_metadata", return_value=(None, transport_err)):
        slug = await _create_recipe(async_client)
        r = await async_client.post(f"/api/v1/recipes/{slug}/suggest-metadata")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_suggest_metadata_returns_suggestions(async_client):
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
        slug = await _create_recipe(async_client)
        r = await async_client.post(f"/api/v1/recipes/{slug}/suggest-metadata")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["dish_role"] == "Breakfast"
    assert d["primary_cuisine"] == "Levantine"
    assert "Vegetarian" in d["dietary_flags"]
    assert d["short_description"] == "Eggs poached in spiced tomato sauce."


@pytest.mark.asyncio
async def test_suggest_metadata_response_excludes_verification_state(async_client):
    """AI suggest-metadata must never include verification_state in its response payload.

    The boundary is enforced at the schema level (MetadataSuggestionOut has no such field),
    so the response data dict must not contain the key — regardless of what the model returns.
    """
    from src.ai.metadata_suggester import MetadataResult
    from src.config.settings import settings
    mock_result = MetadataResult(payload={
        "dish_role": "Main",
        "primary_cuisine": "Mediterranean",
        "secondary_cuisines": [],
        "technique_family": None,
        "ingredient_families": [],
        "complexity": None,
        "time_class": None,
        "service_format": None,
        "season": None,
        "mood_tags": [],
        "storage_profile": [],
        "dietary_flags": [],
        "sector": None,
        "class": None,
        "heat_window": None,
        "provision_tags": [],
        "short_description": None,
        "confidence_notes": [],
        "uncertainty_notes": [],
    })
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.suggest_metadata", return_value=(mock_result, None)):
        slug = await _create_recipe(async_client)
        r = await async_client.post(f"/api/v1/recipes/{slug}/suggest-metadata")
    assert r.status_code == 200
    assert "verification_state" not in r.json()["data"], (
        "AI suggestion response must not expose verification_state"
    )
