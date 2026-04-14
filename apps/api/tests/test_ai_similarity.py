"""
Tests for POST /recipes/{id_or_slug}/similar.
"""
from unittest.mock import patch
import pytest
from httpx import AsyncClient


async def _create_recipe(ac: AsyncClient, title: str) -> str:
    r = await ac.post("/api/v1/recipes", json={
        "title": title,
        "dish_role": "Main",
        "primary_cuisine": "Italian",
        "ingredients": [{"position": 1, "item": "pasta", "quantity": "400g"}],
        "steps": [{"position": 1, "instruction": "Cook pasta."}],
    })
    return r.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_similar_returns_503_when_ai_disabled(async_client):
    slug = await _create_recipe(async_client, "Pasta Carbonara")
    r = await async_client.post(f"/api/v1/recipes/{slug}/similar", json={})
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_similar_returns_404_for_unknown_recipe(async_client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        r = await async_client.post("/api/v1/recipes/does-not-exist/similar", json={})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_similar_returns_503_when_lm_studio_unreachable(async_client):
    from src.ai.similarity_engine import SimilarityError, SimilarityErrorKind
    from src.config.settings import settings
    transport_err = SimilarityError(SimilarityErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.find_similar_recipes", return_value=(None, transport_err)):
        slug = await _create_recipe(async_client, "Pasta Carbonara")
        r = await async_client.post(f"/api/v1/recipes/{slug}/similar", json={})
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_similar_returns_ranked_results(async_client):
    from src.ai.similarity_engine import SimilarityResult
    from src.config.settings import settings
    mock_result = SimilarityResult(payload={
        "top_matches": [
            {
                "title": "Pasta Amatriciana",
                "similarity_score_band": "high",
                "primary_similarity_reason": "Same base technique and format.",
                "secondary_similarity_reasons": ["Both Italian pasta dishes"],
                "major_differences": ["Different sauce"],
            }
        ],
        "near_matches": [],
        "why_each_match_ranked": ["Pasta Amatriciana ranked high due to shared technique."],
        "major_difference_notes": [],
        "confidence_notes": ["Only 2 candidates provided — results may be limited."],
    })
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.find_similar_recipes", return_value=(mock_result, None)):
        slug = await _create_recipe(async_client, "Pasta Carbonara")
        await _create_recipe(async_client, "Pasta Amatriciana")
        r = await async_client.post(f"/api/v1/recipes/{slug}/similar", json={})
    assert r.status_code == 200
    d = r.json()["data"]
    assert len(d["top_matches"]) == 1
    assert d["top_matches"][0]["title"] == "Pasta Amatriciana"
    assert d["top_matches"][0]["similarity_score_band"] == "high"
