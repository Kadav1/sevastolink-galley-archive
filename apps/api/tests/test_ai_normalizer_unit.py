"""
Unit tests for normalizer internal parsing helpers.

These test _parse_response, _validate_payload_shape, _validate_taxonomy,
_parse_ingredients, and _parse_steps directly — no HTTP client needed.
"""
import json
import pytest

from src.ai.normalizer import (
    NormalizationErrorKind,
    _parse_ingredients,
    _parse_response,
    _parse_steps,
    _validate_payload_shape,
    _validate_taxonomy,
)


# ── Minimal valid payload fixture ─────────────────────────────────────────────

def _minimal_payload(**overrides) -> dict:
    base = {
        "source_language": "en",
        "output_language": "en",
        "title": "Test Recipe",
        "short_description": None,
        "dish_role": None,
        "primary_cuisine": None,
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
        "servings": None,
        "prep_time_minutes": None,
        "cook_time_minutes": None,
        "total_time_minutes": None,
        "yield_text": None,
        "ingredients": [{"item": "eggs", "quantity": "2", "unit": None, "preparation": None, "optional": False}],
        "steps": [{"position": 1, "instruction": "Boil the eggs."}],
        "recipe_notes": None,
        "service_notes": None,
        "source_type": "paste_text",
        "source_url": None,
        "raw_source_text": "Boil eggs.",
        "uncertainty_notes": [],
        "confidence_summary": "High",
    }
    base.update(overrides)
    return base


# ── _validate_payload_shape ────────────────────────────────────────────────────

def test_validate_payload_shape_valid():
    errors = _validate_payload_shape(_minimal_payload())
    assert errors == []


def test_validate_payload_shape_not_dict():
    errors = _validate_payload_shape("not a dict")
    assert len(errors) == 1
    assert "not an object" in errors[0]


def test_validate_payload_shape_missing_required_field():
    payload = _minimal_payload()
    del payload["output_language"]
    errors = _validate_payload_shape(payload)
    assert any("output_language" in e for e in errors)


def test_validate_payload_shape_wrong_output_language():
    errors = _validate_payload_shape(_minimal_payload(output_language="fr"))
    assert any("output_language" in e for e in errors)


def test_validate_payload_shape_ingredients_not_array():
    errors = _validate_payload_shape(_minimal_payload(ingredients="not a list"))
    assert any("ingredients" in e for e in errors)


def test_validate_payload_shape_steps_not_array():
    errors = _validate_payload_shape(_minimal_payload(steps={"key": "val"}))
    assert any("steps" in e for e in errors)


def test_validate_payload_shape_uncertainty_notes_not_array():
    errors = _validate_payload_shape(_minimal_payload(uncertainty_notes="bad"))
    assert any("uncertainty_notes" in e for e in errors)


# ── _validate_taxonomy ─────────────────────────────────────────────────────────

def test_validate_taxonomy_exact_match():
    result = _validate_taxonomy("Breakfast", ["Breakfast", "Lunch"], "dish_role", [])
    assert result == "Breakfast"


def test_validate_taxonomy_case_insensitive_match():
    warnings: list[str] = []
    result = _validate_taxonomy("breakfast", ["Breakfast", "Lunch"], "dish_role", warnings)
    assert result == "Breakfast"
    assert warnings == []


def test_validate_taxonomy_none_returns_none():
    result = _validate_taxonomy(None, ["Breakfast"], "dish_role", [])
    assert result is None


def test_validate_taxonomy_empty_string_returns_none():
    result = _validate_taxonomy("", ["Breakfast"], "dish_role", [])
    assert result is None


def test_validate_taxonomy_unknown_value_returns_none_with_warning():
    warnings: list[str] = []
    result = _validate_taxonomy("Brunch", ["Breakfast", "Lunch"], "dish_role", warnings)
    assert result is None
    assert len(warnings) == 1
    assert "dish_role" in warnings[0]
    assert "Brunch" in warnings[0]


# ── _parse_ingredients ────────────────────────────────────────────────────────

def test_parse_ingredients_valid():
    raw = [{"item": "eggs", "quantity": "2", "unit": None, "preparation": None, "optional": False}]
    result = _parse_ingredients(raw, [])
    assert len(result) == 1
    assert result[0].item == "eggs"
    assert result[0].position == 1


def test_parse_ingredients_positions_are_sequential():
    raw = [{"item": "eggs"}, {"item": "tomatoes"}, {"item": "onion"}]
    result = _parse_ingredients(raw, [])
    assert [r.position for r in result] == [1, 2, 3]


def test_parse_ingredients_not_list_returns_empty_with_warning():
    warnings: list[str] = []
    result = _parse_ingredients("not a list", warnings)
    assert result == []
    assert len(warnings) == 1


def test_parse_ingredients_skips_non_dict_items():
    warnings: list[str] = []
    raw = [{"item": "eggs"}, "bad", {"item": "tomatoes"}]
    result = _parse_ingredients(raw, warnings)
    assert len(result) == 2
    assert len(warnings) == 1
    assert "ingredients[1]" in warnings[0]


def test_parse_ingredients_skips_empty_item():
    warnings: list[str] = []
    raw = [{"item": ""}, {"item": "eggs"}]
    result = _parse_ingredients(raw, warnings)
    assert len(result) == 1
    assert result[0].item == "eggs"
    assert len(warnings) == 1


def test_parse_ingredients_optional_defaults_false():
    raw = [{"item": "eggs"}]
    result = _parse_ingredients(raw, [])
    assert result[0].optional is False


# ── _parse_steps ──────────────────────────────────────────────────────────────

def test_parse_steps_valid():
    raw = [{"position": 1, "instruction": "Boil water."}]
    result = _parse_steps(raw, [])
    assert len(result) == 1
    assert result[0].instruction == "Boil water."
    assert result[0].position == 1


def test_parse_steps_not_list_returns_empty_with_warning():
    warnings: list[str] = []
    result = _parse_steps(None, warnings)
    assert result == []
    assert len(warnings) == 1


def test_parse_steps_skips_empty_instruction():
    warnings: list[str] = []
    raw = [{"position": 1, "instruction": "   "}, {"position": 2, "instruction": "Stir."}]
    result = _parse_steps(raw, warnings)
    assert len(result) == 1
    assert result[0].instruction == "Stir."
    assert len(warnings) == 1


def test_parse_steps_bad_position_falls_back_to_index():
    raw = [{"position": -1, "instruction": "Stir."}, {"position": 0, "instruction": "Serve."}]
    result = _parse_steps(raw, [])
    assert result[0].position == 1
    assert result[1].position == 2


# ── _parse_response ────────────────────────────────────────────────────────────

def test_parse_response_valid_returns_result():
    content = json.dumps(_minimal_payload())
    result, err = _parse_response(content)
    assert err is None
    assert result is not None
    assert result.candidate_update.title == "Test Recipe"


def test_parse_response_invalid_json_returns_parse_error():
    result, err = _parse_response("{ not json }")
    assert result is None
    assert err is not None
    assert err.kind == NormalizationErrorKind.parse_failure


def test_parse_response_missing_required_field_returns_schema_error():
    payload = _minimal_payload()
    del payload["output_language"]
    result, err = _parse_response(json.dumps(payload))
    assert result is None
    assert err is not None
    assert err.kind == NormalizationErrorKind.schema_failure


def test_parse_response_negative_prep_time_becomes_null():
    content = json.dumps(_minimal_payload(prep_time_minutes=-5))
    result, err = _parse_response(content)
    assert err is None
    assert result.candidate_update.prep_time_minutes is None
    assert any("prep_time_minutes" in w for w in result.warnings)


def test_parse_response_non_integer_cook_time_becomes_null():
    content = json.dumps(_minimal_payload(cook_time_minutes="quick"))
    result, err = _parse_response(content)
    assert err is None
    assert result.candidate_update.cook_time_minutes is None
    assert any("cook_time_minutes" in w for w in result.warnings)


def test_parse_response_unknown_taxonomy_value_nulled_with_warning():
    content = json.dumps(_minimal_payload(dish_role="NotARealRole"))
    result, err = _parse_response(content)
    assert err is None
    assert result.candidate_update.dish_role is None
    assert any("dish_role" in w for w in result.warnings)


def test_parse_response_servings_coerced_to_string():
    content = json.dumps(_minimal_payload(servings=4))
    result, err = _parse_response(content)
    assert err is None
    assert result.candidate_update.servings == "4"


def test_parse_response_uncertainty_notes_forwarded_as_ambiguities():
    content = json.dumps(_minimal_payload(uncertainty_notes=["Could be vegetarian."]))
    result, err = _parse_response(content)
    assert err is None
    assert "Could be vegetarian." in result.ambiguities
