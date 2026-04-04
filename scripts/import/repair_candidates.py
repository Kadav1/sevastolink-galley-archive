#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATES_DIR = REPO_ROOT / "data" / "imports" / "parsed" / "recipes-candidates"

FIELD_MAPS = {
    "complexity": {
        "easy": "Basic",
        "simple": "Basic",
        "basic": "Basic",
        "moderate": "Intermediate",
        "medium": "Intermediate",
        "intermediate": "Intermediate",
        "advanced": "Advanced",
        "project": "Project",
    },
    "dish_role": {
        # Invented meal-time roles → functional spec values
        "dinner": "Main",
        "lunch": "Main",
        "main course": "Main",
        "main_course": "Main",
        "main": "Main",
        "breakfast / brunch": "Brunch",
        "side dish": "Side",
        "side_dish": "Side",
        # Old compound value that was split in spec
        "sauce / condiment": "Sauce",
        "sauce/condiment": "Sauce",
        # Legacy pre-spec values
        "pantry staple": "Pantry Staple",
        "pantry_staple": "Pantry Staple",
        "street food": "Street Food",
        "street_food": "Street Food",
        "shared plate": "Shared Plate",
        "shared_plate": "Shared Plate",
    },
    "technique_family": {
        # Present-tense gerund forms → bare infinitive spec values
        "baking": "Bake",
        "roasting": "Roast",
        "grilling": "Grill",
        "frying": "Fry",
        "stir-frying": "Stir-Fry",
        "stir frying": "Stir-Fry",
        "deep frying": "Deep Fry",
        "deep-frying": "Deep Fry",
        "searing": "Sear",
        "simmering": "Simmer",
        "braising": "Braise",
        "stewing": "Stew",
        "poaching": "Poach",
        "steaming": "Steam",
        "boiling": "Boil",
        "smoking": "Smoke",
        "fermenting": "Ferment",
        "pickling": "Pickle",
        "curing": "Cure",
        "blending": "Blend",
        "emulsifying": "Emulsify",
        "marinating": "Marinate",
        "dehydrating": "Dehydrate",
        # Old compound values split in spec
        "cure / preserve": "Cure",
        "cure/preserve": "Cure",
        "raw / no-cook": "Raw",
        "raw/no-cook": "Raw",
        "no-cook": "Raw",
        # Misc
        "sauce_emulsion": "Emulsify",
        "emulsion": "Emulsify",
        "slow_cook": "Slow Cook",
        "slow cook": "Slow Cook",
        "pressure_cook": "Pressure Cook",
        "pressure cook": "Pressure Cook",
        "multi_stage": "Multi-Stage",
        "multi stage": "Multi-Stage",
    },
    "service_format": {
        "individual_servings": "Single Plate",
        "individual servings": "Single Plate",
        "hot plated": "Single Plate",
        "hot_plated": "Single Plate",
        "plate": "Single Plate",
        "single_plate": "Single Plate",
        "family_style": "Family Style",
        "family style": "Family Style",
        "meal_prep": "Meal Prep",
        "meal prep": "Meal Prep",
        "party_food": "Party Food",
        "party food": "Party Food",
        "sauce": "Sauce / Add-On",
        "sauce / add-on": "Sauce / Add-On",
        "side_component": "Side Component",
        "side component": "Side Component",
        "base_recipe": "Base Recipe",
        "base recipe": "Base Recipe",
        "kitchen_use": "Kitchen Use",
        "kitchen use": "Kitchen Use",
        "buffet / shared": "Buffet / Shared",
        "buffet/shared": "Buffet / Shared",
    },
    "primary_cuisine": {
        # Normalise casing / old broad-bucket values that predate spec
        "swedish": "Swedish",
        "scandinavian": "Nordic",
        "north african": None,      # too broad; drop and let user assign
        "middle eastern": "Levantine",
        "east asian": None,         # too broad; drop
        "south asian": "Indian",    # best-effort default
        "southeast asian": None,    # too broad; drop
        "central asian": None,      # too broad; drop
        "latin american": None,     # too broad; drop
        "west african": "West African",
        "sub-saharan african": None,
        "eastern european": "Eastern European",
        "central european": "German",
    },
    "secondary_cuisines": {
        "scandinavian": "Nordic",
        "north african": None,
        "middle eastern": "Levantine",
        "east asian": None,
        "south asian": "Indian",
        "southeast asian": None,
        "central asian": None,
        "latin american": None,
        "european": None,
        "western european": None,
        "eastern european": "Eastern European",
        "swedish": "Swedish",
    },
    "season": {
        "autumn, winter": "Autumn",
        "autumn/winter": "Autumn",
        "spring/summer": "Spring",
        "spring, summer": "Spring",
        "all-year": "All Year",
        "all year round": "All Year",
        "year-round": "All Year",
    },
}

TIME_CLASS_ORDER = [
    (15, "Under 15 min"),
    (30, "15–30 min"),
    (60, "30–60 min"),
    (120, "1–2 hr"),
    (240, "2–4 hr"),
]

INGREDIENT_UNITS_TO_ITEMS = {"salt", "pepper", "olive oil", "oil"}
VALID_UNITS = {
    "g", "kg", "mg",
    "ml", "cl", "dl", "l",
    "tsp", "tbsp", "tsp.", "tbsp.", "krm", "tsk", "msk",
    "cup", "cups",
    "pinch", "dash",
    "piece", "pieces", "pc", "pcs",
    "package", "packages", "packet", "packets",
    "can", "cans", "jar", "jars",
    "slice", "slices",
}
PREPARATION_PREFIX_UNITS = {
    "chopped",
    "finely chopped",
    "roughly chopped",
    "grated",
    "finely grated",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair deterministic issues in recipe candidate bundles.")
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=DEFAULT_CANDIDATES_DIR,
        help=f"Directory containing .candidate.json files (default: {DEFAULT_CANDIDATES_DIR})",
    )
    return parser.parse_args()


def canonical_key(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().casefold()


def infer_time_class(total_time_minutes: Any) -> str | None:
    if total_time_minutes is None:
        return None
    try:
        minutes = int(float(total_time_minutes))
    except (TypeError, ValueError):
        return None
    for threshold, label in TIME_CLASS_ORDER:
        if minutes <= threshold:
            return label
    if minutes <= 12 * 60:
        return "Half Day+"
    return "Multi-Day"


def clean_preparation(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1].strip()
    return text or None


def clean_quantity(quantity: Any) -> tuple[str | None, bool]:
    if quantity is None:
        return None, False
    text = str(quantity).strip()
    if not text:
        return None, False
    lowered = text.casefold()
    optional = "valfritt" in lowered or "optional" in lowered
    text = re.sub(r"\bvalfritt\b", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\boptional\b", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\s+", " ", text).strip()
    return (text or None), optional


def build_display_text(ingredient: dict[str, Any]) -> str:
    parts: list[str] = []
    quantity = ingredient.get("quantity")
    unit = ingredient.get("unit")
    item = ingredient.get("item")
    preparation = ingredient.get("preparation")
    optional = bool(ingredient.get("optional"))

    if quantity:
        parts.append(str(quantity))
    if unit:
        parts.append(str(unit))
    if item:
        parts.append(str(item))
    if preparation:
        parts.append(f"({preparation})")
    if optional:
        parts.append("[optional]")
    return " ".join(parts).strip()


def normalize_ingredient(ingredient: dict[str, Any]) -> dict[str, Any]:
    item = (ingredient.get("item") or "").strip()
    unit = (ingredient.get("unit") or "").strip()
    quantity, inferred_optional = clean_quantity(ingredient.get("quantity"))
    preparation = clean_preparation(ingredient.get("preparation"))
    optional = bool(ingredient.get("optional")) or inferred_optional

    if item and unit and canonical_key(item) == canonical_key(unit):
        unit = ""

    if canonical_key(unit) in INGREDIENT_UNITS_TO_ITEMS:
        if not item or canonical_key(item) == canonical_key(unit):
            item = unit
            unit = ""

    if canonical_key(unit) in PREPARATION_PREFIX_UNITS:
        if item:
            item = f"{unit} {item}"
        else:
            item = unit
        unit = ""

    if quantity:
        match = re.match(
            r"^(?P<qty>[0-9]+(?:[.,][0-9]+)?|[¼½¾⅓⅔⅛⅜⅝⅞]|\d+\s*/\s*\d+)\s+"
            r"(?P<unit>tsp|tbsp|ml|g|kg)\s+(?P<item>.+)$",
            quantity,
            flags=re.IGNORECASE,
        )
        if match and not unit:
            quantity = match.group("qty").replace(",", ".")
            unit = match.group("unit")
            if not item:
                item = match.group("item").strip()
        elif unit and quantity.casefold().endswith(f" {unit.casefold()}"):
            quantity = quantity[: -(len(unit) + 1)].strip() or None

    if unit and canonical_key(unit) not in VALID_UNITS:
        if item:
            if canonical_key(unit) not in canonical_key(item):
                item = f"{unit} {item}"
        else:
            item = unit
        unit = ""

    ingredient["quantity"] = quantity
    ingredient["unit"] = unit or None
    ingredient["item"] = item or None
    ingredient["preparation"] = preparation
    ingredient["optional"] = optional
    ingredient["display_text"] = build_display_text(ingredient)
    return ingredient


def normalize_scalar(value: Any, mapping_name: str) -> Any:
    mapping = FIELD_MAPS[mapping_name]
    if value is None:
        return None
    normalized = mapping.get(canonical_key(value))
    if normalized is not None or canonical_key(value) in mapping:
        return normalized
    return value


def normalize_secondary_cuisines(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        mapped = normalize_scalar(value, "secondary_cuisines")
        if mapped is None:
            continue
        key = canonical_key(mapped)
        if key and key not in seen:
            seen.add(key)
            normalized.append(str(mapped))
    return normalized


def should_drop_message(message: str) -> bool:
    prefixes = (
        "Review complexity:",
        "Review time_class:",
        "Review dish_role:",
        "Review technique_family:",
        "Review service_format:",
        "Review secondary_cuisines:",
        "Review primary_cuisine:",
        "Review season:",
        "Review ingredients: ingredient ",
    )
    warning_prefixes = (
        "complexity value ",
        "time_class value ",
        "dish_role normalized from ",
        "technique_family value ",
        "service_format value ",
        "secondary_cuisines value ",
        "primary_cuisine value ",
        "season value ",
        "No deterministic metric conversion rule for ingredient unit ",
        "Recovered malformed range unit ",
        "Ingredient ",
    )
    return message.startswith(prefixes) or message.startswith(warning_prefixes)


def repair_bundle(path: Path) -> bool:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    update = bundle["candidate"]["candidate_update"]
    extras = bundle["candidate"]["candidate_extras"]

    repaired_complexity = normalize_scalar(update.get("complexity"), "complexity")
    if repaired_complexity != update.get("complexity"):
        update["complexity"] = repaired_complexity
        changed = True

    repaired_dish_role = normalize_scalar(update.get("dish_role"), "dish_role")
    if repaired_dish_role != update.get("dish_role"):
        update["dish_role"] = repaired_dish_role
        changed = True

    repaired_technique_family = normalize_scalar(update.get("technique_family"), "technique_family")
    if repaired_technique_family != update.get("technique_family"):
        update["technique_family"] = repaired_technique_family
        changed = True

    repaired_primary_cuisine = normalize_scalar(update.get("primary_cuisine"), "primary_cuisine")
    if repaired_primary_cuisine != update.get("primary_cuisine"):
        update["primary_cuisine"] = repaired_primary_cuisine
        changed = True

    repaired_service_format = normalize_scalar(extras.get("service_format"), "service_format")
    if repaired_service_format != extras.get("service_format"):
        extras["service_format"] = repaired_service_format
        changed = True

    repaired_secondary_cuisines = normalize_secondary_cuisines(extras.get("secondary_cuisines"))
    if repaired_secondary_cuisines != extras.get("secondary_cuisines", []):
        extras["secondary_cuisines"] = repaired_secondary_cuisines
        changed = True

    inferred_time_class = infer_time_class(extras.get("total_time_minutes"))
    if inferred_time_class and update.get("time_class") != inferred_time_class:
        update["time_class"] = inferred_time_class
        changed = True

    repaired_season = normalize_scalar(extras.get("season"), "season")
    if repaired_season != extras.get("season"):
        extras["season"] = repaired_season
        changed = True

    ingredients = update.get("ingredients", [])
    repaired_ingredients: list[dict[str, Any]] = []
    for ingredient in ingredients:
        before = json.dumps(ingredient, sort_keys=True, ensure_ascii=False)
        repaired = normalize_ingredient(dict(ingredient))
        after = json.dumps(repaired, sort_keys=True, ensure_ascii=False)
        if before != after:
            changed = True
        repaired_ingredients.append(repaired)
    update["ingredients"] = repaired_ingredients

    if bundle.get("review_flags"):
        new_flags = [flag for flag in bundle["review_flags"] if not should_drop_message(flag)]
        if new_flags != bundle["review_flags"]:
            bundle["review_flags"] = new_flags
            changed = True

    if bundle.get("warnings"):
        new_warnings = [warning for warning in bundle["warnings"] if not should_drop_message(warning)]
        if new_warnings != bundle["warnings"]:
            bundle["warnings"] = new_warnings
            changed = True

    if changed:
        path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    args = parse_args()
    directory = args.directory
    changed_count = 0
    file_count = 0
    for path in sorted(directory.glob("*.candidate.json")):
        file_count += 1
        if repair_bundle(path):
            changed_count += 1
    print(f"Checked {file_count} candidate bundle(s); repaired {changed_count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
