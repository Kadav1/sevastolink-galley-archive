"""
Tests for POST /pantry/suggest.
"""
from unittest.mock import patch, AsyncMock, MagicMock
import pytest


@pytest.mark.asyncio
async def test_pantry_returns_503_when_ai_disabled(async_client):
    r = await async_client.post("/api/v1/pantry/suggest", json={
        "available_ingredients": ["eggs", "onion", "tomatoes"],
    })
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_pantry_returns_422_for_empty_ingredients(async_client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        r = await async_client.post("/api/v1/pantry/suggest", json={
            "available_ingredients": [],
        })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_pantry_returns_503_when_lm_studio_unreachable(async_client):
    from src.ai.pantry_suggester import PantryError, PantryErrorKind
    from src.config.settings import settings
    transport_err = PantryError(PantryErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.pantry.suggest_pantry", return_value=(None, transport_err)):
        r = await async_client.post("/api/v1/pantry/suggest", json={
            "available_ingredients": ["eggs", "onion"],
        })
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_pantry_returns_suggestions(async_client):
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
        r = await async_client.post("/api/v1/pantry/suggest", json={
            "available_ingredients": ["eggs", "onion", "tomatoes"],
        })
    assert r.status_code == 200
    d = r.json()["data"]
    assert len(d["direct_matches"]) == 1
    assert d["direct_matches"][0]["title"] == "Shakshuka"
    assert d["quick_ideas"] == ["Scrambled eggs with onion and tomato"]


@pytest.mark.asyncio
async def test_pantry_forwards_recipe_ingredients_to_ai(async_client, db_session):
    """archive_dicts passed to suggest_pantry must include ingredient text, not empty lists."""
    from src.ai.pantry_suggester import PantryResult
    from src.config.settings import settings
    from src.services import recipe_service
    from src.schemas.recipe import RecipeCreate, IngredientIn

    # Create a recipe with an ingredient so ingredient_text is populated
    recipe = recipe_service.create_recipe(db_session, RecipeCreate(
        title="Tomato Soup",
        ingredients=[IngredientIn(position=1, item="tomatoes")],
    ))
    db_session.commit()

    mock_result = PantryResult(payload={
        "direct_matches": [], "near_matches": [], "pantry_gap_notes": [],
        "substitution_suggestions": [], "quick_ideas": [], "confidence_notes": [],
    })

    captured_kwargs: dict = {}

    def capture_call(*args, **kwargs):
        captured_kwargs.update(kwargs)
        return mock_result, None

    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.pantry.suggest_pantry", side_effect=capture_call):
        r = await async_client.post("/api/v1/pantry/suggest", json={
            "available_ingredients": ["tomatoes"],
        })

    assert r.status_code == 200
    archive_recipes = captured_kwargs.get("archive_recipes", [])
    # At least one recipe was forwarded to the AI
    assert len(archive_recipes) >= 1
    # The recipe's ingredient text was forwarded, not an empty list
    soup = next((rec for rec in archive_recipes if rec["title"] == "Tomato Soup"), None)
    assert soup is not None
    assert soup["ingredients"] != [], "ingredient_text must be forwarded to the AI, not an empty list"
    assert "tomatoes" in " ".join(soup["ingredients"]).lower()
