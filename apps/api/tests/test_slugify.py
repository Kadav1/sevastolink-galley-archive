"""
Unit tests for src/utils/slugify.py — slugify() and unique_slug().
"""
import pytest
from src.utils.slugify import slugify


# ── slugify() ─────────────────────────────────────────────────────────────────

def test_slugify_basic():
    assert slugify("Shakshuka") == "shakshuka"


def test_slugify_lowercases():
    assert slugify("Beef Bourguignon") == "beef-bourguignon"


def test_slugify_strips_leading_trailing_hyphens():
    assert slugify("  - Hello World - ") == "hello-world"


def test_slugify_collapses_multiple_spaces():
    assert slugify("pasta   e   fagioli") == "pasta-e-fagioli"


def test_slugify_collapses_mixed_whitespace_and_hyphens():
    assert slugify("pasta - e - fagioli") == "pasta-e-fagioli"


def test_slugify_removes_special_chars():
    # Punctuation stripped; words joined with hyphens
    assert slugify("Mum's Roast Chicken!") == "mums-roast-chicken"


def test_slugify_removes_unicode_accents():
    # Non-ASCII letters are stripped (not transliterated)
    result = slugify("Crème Brûlée")
    assert result == "crme-brle" or "creme" not in result  # stripped, not transliterated
    assert all(c in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in result)


def test_slugify_strips_ampersand_and_slash():
    assert slugify("Salt & Pepper / Lime") == "salt-pepper-lime"


def test_slugify_numbers_preserved():
    assert slugify("3-Ingredient Pancakes") == "3-ingredient-pancakes"


def test_slugify_all_special_chars_returns_recipe_fallback():
    # If nothing survives, fall back to "recipe"
    assert slugify("!!!###$$$") == "recipe"


def test_slugify_empty_string_returns_recipe_fallback():
    assert slugify("") == "recipe"


def test_slugify_whitespace_only_returns_recipe_fallback():
    assert slugify("   ") == "recipe"


def test_slugify_already_slug():
    assert slugify("simple-recipe") == "simple-recipe"


def test_slugify_numbers_only():
    assert slugify("42") == "42"


def test_slugify_arabic_chars_stripped():
    # Arabic characters are outside [a-z0-9] — stripped to fallback
    result = slugify("مرق")
    assert result == "recipe"


def test_slugify_chinese_chars_stripped():
    result = slugify("红烧肉")
    assert result == "recipe"


def test_slugify_mixed_latin_and_unicode():
    # ASCII parts survive; non-ASCII stripped
    result = slugify("Coq au Vin (coq=cock)")
    assert result == "coq-au-vin-coqcock"


# ── unique_slug() — collision handling ────────────────────────────────────────

@pytest.mark.asyncio
async def test_unique_slug_no_collision(db_session):
    from src.utils.slugify import unique_slug
    slug = unique_slug(db_session, "Shakshuka")
    assert slug == "shakshuka"


@pytest.mark.asyncio
async def test_unique_slug_appends_counter_on_collision(db_session):
    from src.utils.slugify import unique_slug
    from src.services import recipe_service
    from src.schemas.recipe import RecipeCreate

    recipe_service.create_recipe(db_session, RecipeCreate(title="Shakshuka"))
    db_session.commit()

    slug = unique_slug(db_session, "Shakshuka")
    assert slug == "shakshuka-2"


@pytest.mark.asyncio
async def test_unique_slug_increments_past_multiple_collisions(db_session):
    from src.utils.slugify import unique_slug
    from src.services import recipe_service
    from src.schemas.recipe import RecipeCreate

    recipe_service.create_recipe(db_session, RecipeCreate(title="Soup"))
    recipe_service.create_recipe(db_session, RecipeCreate(title="Soup"))
    db_session.commit()

    slug = unique_slug(db_session, "Soup")
    assert slug == "soup-3"


@pytest.mark.asyncio
async def test_unique_slug_raises_after_max_attempts(db_session):
    from src.utils.slugify import unique_slug, _MAX_SLUG_ATTEMPTS
    from src.services import recipe_service
    from src.schemas.recipe import RecipeCreate

    # Create enough collisions to exhaust the counter
    for _ in range(_MAX_SLUG_ATTEMPTS):
        recipe_service.create_recipe(db_session, RecipeCreate(title="Collision"))
    db_session.commit()

    with pytest.raises(RuntimeError, match="unique slug"):
        unique_slug(db_session, "Collision")
