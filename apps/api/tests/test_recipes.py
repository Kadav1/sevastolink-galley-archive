"""
Recipe endpoint tests.
Uses a fresh in-memory SQLite DB for each test via override of get_db.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import Base, get_db
from src.db.init_db import init_db
from src.main import app

# ── Test DB fixture ───────────────────────────────────────────────────────────

TEST_DB_URL = "sqlite:///./data/db/galley_test.sqlite"


@pytest.fixture(scope="function")
def db_session():
    """Fresh schema for every test function."""
    from src.config.settings import settings
    import os

    test_path = "./data/db/galley_test.sqlite"
    # Remove leftover test DB
    if os.path.exists(test_path):
        os.remove(test_path)

    # Run migrations against test DB
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
    if os.path.exists(test_path):
        os.remove(test_path)


@pytest.fixture(scope="function")
def client(db_session):
    """HTTPX async client with test DB override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield  # we create client in each test
    app.dependency_overrides.clear()


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


async def _client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_recipes_empty(client):
    async with await _client() as c:
        r = await c.get("/api/v1/recipes")
    assert r.status_code == 200
    body = r.json()
    assert body["data"] == []
    assert body["meta"]["total"] == 0
    assert body["meta"]["limit"] == 50
    assert body["meta"]["offset"] == 0


@pytest.mark.asyncio
async def test_create_recipe(client):
    async with await _client() as c:
        r = await c.post("/api/v1/recipes", json=FULL_RECIPE)
    assert r.status_code == 201
    recipe = r.json()["data"]
    assert recipe["slug"] == "shakshuka"
    assert recipe["title"] == "Shakshuka"
    assert recipe["verification_state"] == "Verified"
    assert len(recipe["ingredients"]) == 1
    assert len(recipe["steps"]) == 1
    assert recipe["source"]["source_type"] == "Manual"


@pytest.mark.asyncio
async def test_get_recipe_by_slug(client):
    async with await _client() as c:
        await c.post("/api/v1/recipes", json=FULL_RECIPE)
        r = await c.get("/api/v1/recipes/shakshuka")
    assert r.status_code == 200
    assert r.json()["data"]["slug"] == "shakshuka"


@pytest.mark.asyncio
async def test_list_recipes_returns_created(client):
    async with await _client() as c:
        await c.post("/api/v1/recipes", json=FULL_RECIPE)
        r = await c.get("/api/v1/recipes")
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["total"] == 1
    assert body["data"][0]["slug"] == "shakshuka"


@pytest.mark.asyncio
async def test_list_recipes_fts_search(client):
    async with await _client() as c:
        await c.post("/api/v1/recipes", json=FULL_RECIPE)
        r_match = await c.get("/api/v1/recipes", params={"q": "shakshuka"})
        r_nomatch = await c.get("/api/v1/recipes", params={"q": "bolognese"})
    assert r_match.json()["meta"]["total"] == 1
    assert r_nomatch.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_recipes_filter_verification_state(client):
    async with await _client() as c:
        await c.post("/api/v1/recipes", json=FULL_RECIPE)
        r_verified = await c.get("/api/v1/recipes", params={"verification_state": "Verified"})
        r_draft = await c.get("/api/v1/recipes", params={"verification_state": "Draft"})
    assert r_verified.json()["meta"]["total"] == 1
    assert r_draft.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_recipes_filter_favorite(client):
    async with await _client() as c:
        await c.post("/api/v1/recipes", json={**FULL_RECIPE, "favorite": False})
        r_fav = await c.get("/api/v1/recipes", params={"favorite": "true"})
        r_all = await c.get("/api/v1/recipes")
    assert r_fav.json()["meta"]["total"] == 0
    assert r_all.json()["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_update_recipe(client):
    async with await _client() as c:
        await c.post("/api/v1/recipes", json=FULL_RECIPE)
        r = await c.patch("/api/v1/recipes/shakshuka", json={"complexity": "Intermediate", "rating": 4})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["complexity"] == "Intermediate"
    assert data["rating"] == 4


@pytest.mark.asyncio
async def test_archive_recipe(client):
    async with await _client() as c:
        await c.post("/api/v1/recipes", json=FULL_RECIPE)
        r = await c.post("/api/v1/recipes/shakshuka/archive")
    assert r.status_code == 200
    result = r.json()["data"]
    assert result["archived"] is True
    assert result["verification_state"] == "Archived"


@pytest.mark.asyncio
async def test_archived_excluded_from_default_list(client):
    async with await _client() as c:
        await c.post("/api/v1/recipes", json=FULL_RECIPE)
        await c.post("/api/v1/recipes/shakshuka/archive")
        r_default = await c.get("/api/v1/recipes")
        r_with_archived = await c.get("/api/v1/recipes", params={"archived": "true"})
    assert r_default.json()["meta"]["total"] == 0
    assert r_with_archived.json()["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_delete_recipe(client):
    async with await _client() as c:
        await c.post("/api/v1/recipes", json=FULL_RECIPE)
        r_del = await c.delete("/api/v1/recipes/shakshuka")
        r_get = await c.get("/api/v1/recipes/shakshuka")
    assert r_del.status_code == 204
    assert r_get.status_code == 404


@pytest.mark.asyncio
async def test_get_recipe_not_found(client):
    async with await _client() as c:
        r = await c.get("/api/v1/recipes/nonexistent-recipe")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_slug_collision(client):
    """Two recipes with the same title get unique slugs."""
    async with await _client() as c:
        r1 = await c.post("/api/v1/recipes", json=MINIMAL_RECIPE)
        r2 = await c.post("/api/v1/recipes", json=MINIMAL_RECIPE)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["data"]["slug"] != r2.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_list_recipes_summary_includes_ingredient_count(client):
    """RecipeSummaryOut must include ingredient_count."""
    recipe = {**MINIMAL_RECIPE, "ingredients": [
        {"position": 1, "item": "eggs", "quantity": "4"},
        {"position": 2, "item": "olive oil", "quantity": "2 tbsp"},
        {"position": 3, "item": "tomatoes", "quantity": "400 g"},
    ]}
    async with await _client() as c:
        await c.post("/api/v1/recipes", json=recipe)
        r = await c.get("/api/v1/recipes")
    assert r.status_code == 200
    summary = r.json()["data"][0]
    assert "ingredient_count" in summary
    assert summary["ingredient_count"] == 3


@pytest.mark.asyncio
async def test_list_recipes_filter_sector(client):
    """sector filter returns only matching recipes."""
    async with await _client() as c:
        await c.post("/api/v1/recipes", json={**FULL_RECIPE, "sector": "Galley"})
        await c.post("/api/v1/recipes", json={**MINIMAL_RECIPE, "title": "Other Recipe"})
        r_galley = await c.get("/api/v1/recipes", params={"sector": "Galley"})
        r_other = await c.get("/api/v1/recipes", params={"sector": "Shoreside"})
    assert r_galley.json()["meta"]["total"] == 1
    assert r_other.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_recipes_filter_operational_class(client):
    """operational_class filter returns only matching recipes."""
    async with await _client() as c:
        await c.post("/api/v1/recipes", json={**FULL_RECIPE, "operational_class": "Passage"})
        r_match = await c.get("/api/v1/recipes", params={"operational_class": "Passage"})
        r_no = await c.get("/api/v1/recipes", params={"operational_class": "Harbor"})
    assert r_match.json()["meta"]["total"] == 1
    assert r_no.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_recipes_filter_heat_window(client):
    """heat_window filter returns only matching recipes."""
    async with await _client() as c:
        await c.post("/api/v1/recipes", json={**FULL_RECIPE, "heat_window": "No Heat"})
        r_match = await c.get("/api/v1/recipes", params={"heat_window": "No Heat"})
        r_no = await c.get("/api/v1/recipes", params={"heat_window": "Open Flame"})
    assert r_match.json()["meta"]["total"] == 1
    assert r_no.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_recipes_sort_title_desc(client):
    """sort=title_desc returns recipes in reverse alphabetical order."""
    async with await _client() as c:
        await c.post("/api/v1/recipes", json={**MINIMAL_RECIPE, "title": "Anchovy Toast"})
        await c.post("/api/v1/recipes", json={**MINIMAL_RECIPE, "title": "Zucchini Fritters"})
        r = await c.get("/api/v1/recipes", params={"sort": "title_desc"})
    titles = [item["title"] for item in r.json()["data"]]
    assert titles == sorted(titles, reverse=True)
