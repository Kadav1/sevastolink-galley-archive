"""
Recipe endpoint tests.
"""

import pytest

# ── Helpers ───────────────────────────────────────────────────────────────────

MINIMAL_RECIPE = {
    "title": "Shakshuka",
    "verification_state": "Verified",
    "ingredients": [
        {"position": 1, "item": "eggs", "quantity": "4", "display_text": "4 eggs"}
    ],
    "steps": [
        {"position": 1, "instruction": "Heat oil. Add tomatoes. Crack in eggs."}
    ],
}

FULL_RECIPE = {
    **MINIMAL_RECIPE,
    "short_description": "Eggs in spiced tomato sauce.",
    "dish_role": "Breakfast",
    "primary_cuisine": "Levantine",
    "technique_family": "Simmer",
    "complexity": "Basic",
    "time_class": "15–30 min",
    "source": {"source_type": "Manual", "source_notes": "House version."},
}


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_recipes_empty(async_client):
    r = await async_client.get("/api/v1/recipes")
    assert r.status_code == 200
    body = r.json()
    assert body["data"] == []
    assert body["meta"]["total"] == 0
    assert body["meta"]["limit"] == 50
    assert body["meta"]["offset"] == 0


@pytest.mark.asyncio
async def test_create_recipe(async_client):
    r = await async_client.post("/api/v1/recipes", json=FULL_RECIPE)
    assert r.status_code == 201
    recipe = r.json()["data"]
    assert recipe["slug"] == "shakshuka"
    assert recipe["title"] == "Shakshuka"
    assert recipe["verification_state"] == "Verified"
    assert len(recipe["ingredients"]) == 1
    assert len(recipe["steps"]) == 1
    assert recipe["source"]["source_type"] == "Manual"


@pytest.mark.asyncio
async def test_get_recipe_by_slug(async_client):
    await async_client.post("/api/v1/recipes", json=FULL_RECIPE)
    r = await async_client.get("/api/v1/recipes/shakshuka")
    assert r.status_code == 200
    assert r.json()["data"]["slug"] == "shakshuka"


@pytest.mark.asyncio
async def test_list_recipes_returns_created(async_client):
    await async_client.post("/api/v1/recipes", json=FULL_RECIPE)
    r = await async_client.get("/api/v1/recipes")
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["total"] == 1
    assert body["data"][0]["slug"] == "shakshuka"


@pytest.mark.asyncio
async def test_list_recipes_fts_search(async_client):
    await async_client.post("/api/v1/recipes", json=FULL_RECIPE)
    r_match = await async_client.get("/api/v1/recipes", params={"q": "shakshuka"})
    r_nomatch = await async_client.get("/api/v1/recipes", params={"q": "bolognese"})
    assert r_match.json()["meta"]["total"] == 1
    assert r_nomatch.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_recipes_filter_verification_state(async_client):
    await async_client.post("/api/v1/recipes", json=FULL_RECIPE)
    r_verified = await async_client.get("/api/v1/recipes", params={"verification_state": "Verified"})
    r_draft = await async_client.get("/api/v1/recipes", params={"verification_state": "Draft"})
    assert r_verified.json()["meta"]["total"] == 1
    assert r_draft.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_recipes_filter_favorite(async_client):
    await async_client.post("/api/v1/recipes", json={**FULL_RECIPE, "favorite": False})
    r_fav = await async_client.get("/api/v1/recipes", params={"favorite": "true"})
    r_all = await async_client.get("/api/v1/recipes")
    assert r_fav.json()["meta"]["total"] == 0
    assert r_all.json()["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_update_recipe(async_client):
    await async_client.post("/api/v1/recipes", json=FULL_RECIPE)
    r = await async_client.patch("/api/v1/recipes/shakshuka", json={"complexity": "Intermediate", "rating": 4})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["complexity"] == "Intermediate"
    assert data["rating"] == 4


@pytest.mark.asyncio
async def test_archive_recipe(async_client):
    await async_client.post("/api/v1/recipes", json=FULL_RECIPE)
    r = await async_client.post("/api/v1/recipes/shakshuka/archive")
    assert r.status_code == 200
    result = r.json()["data"]
    assert result["archived"] is True
    assert result["verification_state"] == "Archived"


@pytest.mark.asyncio
async def test_archived_excluded_from_default_list(async_client):
    await async_client.post("/api/v1/recipes", json=FULL_RECIPE)
    await async_client.post("/api/v1/recipes/shakshuka/archive")
    r_default = await async_client.get("/api/v1/recipes")
    r_with_archived = await async_client.get("/api/v1/recipes", params={"archived": "true"})
    assert r_default.json()["meta"]["total"] == 0
    assert r_with_archived.json()["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_delete_recipe(async_client):
    await async_client.post("/api/v1/recipes", json=FULL_RECIPE)
    r_del = await async_client.delete("/api/v1/recipes/shakshuka")
    r_get = await async_client.get("/api/v1/recipes/shakshuka")
    assert r_del.status_code == 204
    assert r_get.status_code == 404


@pytest.mark.asyncio
async def test_get_recipe_not_found(async_client):
    r = await async_client.get("/api/v1/recipes/nonexistent-recipe")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_slug_collision(async_client):
    """Two recipes with the same title get unique slugs."""
    r1 = await async_client.post("/api/v1/recipes", json=MINIMAL_RECIPE)
    r2 = await async_client.post("/api/v1/recipes", json=MINIMAL_RECIPE)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["data"]["slug"] != r2.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_list_recipes_summary_includes_ingredient_count(async_client):
    """RecipeSummaryOut must include ingredient_count."""
    recipe = {**MINIMAL_RECIPE, "ingredients": [
        {"position": 1, "item": "eggs", "quantity": "4"},
        {"position": 2, "item": "olive oil", "quantity": "2 tbsp"},
        {"position": 3, "item": "tomatoes", "quantity": "400 g"},
    ]}
    await async_client.post("/api/v1/recipes", json=recipe)
    r = await async_client.get("/api/v1/recipes")
    assert r.status_code == 200
    summary = r.json()["data"][0]
    assert "ingredient_count" in summary
    assert summary["ingredient_count"] == 3


@pytest.mark.asyncio
async def test_list_recipes_filter_sector(async_client):
    """sector filter returns only matching recipes."""
    await async_client.post("/api/v1/recipes", json={**FULL_RECIPE, "sector": "Galley"})
    await async_client.post("/api/v1/recipes", json={**MINIMAL_RECIPE, "title": "Other Recipe"})
    r_galley = await async_client.get("/api/v1/recipes", params={"sector": "Galley"})
    r_other = await async_client.get("/api/v1/recipes", params={"sector": "Shoreside"})
    assert r_galley.json()["meta"]["total"] == 1
    assert r_other.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_recipes_filter_operational_class(async_client):
    """operational_class filter returns only matching recipes."""
    await async_client.post("/api/v1/recipes", json={**FULL_RECIPE, "operational_class": "Field Meal"})
    r_match = await async_client.get("/api/v1/recipes", params={"operational_class": "Field Meal"})
    r_no = await async_client.get("/api/v1/recipes", params={"operational_class": "Experimental"})
    assert r_match.json()["meta"]["total"] == 1
    assert r_no.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_recipes_filter_heat_window(async_client):
    """heat_window filter returns only matching recipes."""
    await async_client.post("/api/v1/recipes", json={**FULL_RECIPE, "heat_window": "No Heat"})
    r_match = await async_client.get("/api/v1/recipes", params={"heat_window": "No Heat"})
    r_no = await async_client.get("/api/v1/recipes", params={"heat_window": "Open Flame"})
    assert r_match.json()["meta"]["total"] == 1
    assert r_no.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_recipes_sort_title_desc(async_client):
    """sort=title_desc returns recipes in reverse alphabetical order."""
    await async_client.post("/api/v1/recipes", json={**MINIMAL_RECIPE, "title": "Anchovy Toast"})
    await async_client.post("/api/v1/recipes", json={**MINIMAL_RECIPE, "title": "Zucchini Fritters"})
    r = await async_client.get("/api/v1/recipes", params={"sort": "title_desc"})
    titles = [item["title"] for item in r.json()["data"]]
    assert titles == sorted(titles, reverse=True)


@pytest.mark.asyncio
async def test_mutation_does_not_touch_last_viewed_at(db_session):
    """update_recipe and archive_recipe must not set last_viewed_at — only GET should."""
    from src.models.recipe import Recipe
    from src.schemas.recipe import RecipeCreate, RecipeUpdate
    from src.services import recipe_service

    data = RecipeCreate(**{**MINIMAL_RECIPE, "verification_state": "Unverified"})
    recipe = recipe_service.create_recipe(db_session, data)
    assert recipe.last_viewed_at is None, "last_viewed_at should be None after create"

    recipe_service.update_recipe(db_session, recipe.slug, RecipeUpdate(title="Shakshuka Updated"))
    db_session.expire_all()
    updated = db_session.get(Recipe, recipe.id)
    assert updated.last_viewed_at is None, "update_recipe must not touch last_viewed_at"

    recipe_service.archive_recipe(db_session, recipe.slug)
    db_session.expire_all()
    archived = db_session.get(Recipe, recipe.id)
    assert archived.last_viewed_at is None, "archive_recipe must not touch last_viewed_at"


@pytest.mark.asyncio
async def test_search_with_fts5_operators_returns_200(async_client):
    """Search queries containing FTS5 operators must not raise a 500."""
    # These inputs contain raw FTS5 syntax that would cause sqlite3.OperationalError
    # if passed directly to MATCH. Each must return 200, not 500.
    for bad_query in ['AND', '"unclosed', 'NEAR(', 'test AND']:
        r = await async_client.get("/api/v1/recipes", params={"q": bad_query})
        assert r.status_code == 200, f"Expected 200 for q={bad_query!r}, got {r.status_code}"
