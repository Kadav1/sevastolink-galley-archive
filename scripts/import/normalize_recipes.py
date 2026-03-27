#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any
from urllib import error, request


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROMPT_PATH = REPO_ROOT / "prompts/runtime/normalization/recipe-normalization-v1.md"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json"
DEFAULT_TRANSLATION_PROMPT_PATH = REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md"
DEFAULT_TRANSLATION_SCHEMA_PATH = REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"

LANGUAGE_NAMES = {
    "en": "English",
    "sv": "Swedish",
}

SCHEMA_VERSION = "1.0.0"
ARTIFACT_TYPE = "intake_candidate_bundle"

DISH_ROLES = [
    "Breakfast",
    "Brunch",
    "Snack",
    "Starter",
    "Soup",
    "Salad",
    "Side",
    "Main",
    "Shared Plate",
    "Dessert",
    "Bread",
    "Dough",
    "Sauce",
    "Condiment",
    "Drink",
    "Preserve",
    "Pantry Staple",
    "Component",
    "Confectionery",
    "Street Food",
]

PRIMARY_CUISINES = [
    "Italian",
    "French",
    "Spanish",
    "Catalan",
    "Portuguese",
    "Greek",
    "Turkish",
    "British",
    "Irish",
    "Scottish",
    "Nordic",
    "Swedish",
    "Norwegian",
    "Danish",
    "Finnish",
    "German",
    "Austrian",
    "Swiss",
    "Dutch",
    "Belgian",
    "Eastern European",
    "Polish",
    "Hungarian",
    "Czech",
    "Romanian",
    "Russian",
    "Georgian",
    "Armenian",
    "Ukrainian",
    "Levantine",
    "Lebanese",
    "Syrian",
    "Palestinian",
    "Israeli",
    "Egyptian",
    "Moroccan",
    "Tunisian",
    "Algerian",
    "Libyan",
    "Persian",
    "Iraqi",
    "Yemeni",
    "Ethiopian",
    "Eritrean",
    "West African",
    "Nigerian",
    "Ghanaian",
    "Senegalese",
    "East African",
    "Kenyan",
    "South African",
    "Zimbabwean",
    "Indian",
    "North Indian",
    "South Indian",
    "Pakistani",
    "Bangladeshi",
    "Sri Lankan",
    "Nepali",
    "Thai",
    "Vietnamese",
    "Cambodian",
    "Laotian",
    "Filipino",
    "Indonesian",
    "Malaysian",
    "Singaporean",
    "Burmese",
    "Chinese",
    "Cantonese",
    "Sichuan",
    "Shanghainese",
    "Taiwanese",
    "Japanese",
    "Korean",
    "Mongolian",
    "Uzbek",
    "Kazakh",
    "Azerbaijani",
    "Caucasian",
    "Mexican",
    "Tex-Mex",
    "Oaxacan",
    "Central American",
    "Guatemalan",
    "Peruvian",
    "Colombian",
    "Venezuelan",
    "Brazilian",
    "Argentinian",
    "Chilean",
    "American",
    "American Southern",
    "American Midwest",
    "Cajun / Creole",
    "Caribbean",
    "Jamaican",
    "Cuban",
    "Fusion",
    "Global / Mixed",
]

TECHNIQUE_FAMILIES = [
    "Raw",
    "Assemble",
    "Marinate",
    "Cure",
    "Ferment",
    "Pickle",
    "Smoke",
    "Confit",
    "Poach",
    "Steam",
    "Boil",
    "Simmer",
    "Braise",
    "Stew",
    "Slow Cook",
    "Pressure Cook",
    "Sear",
    "Fry",
    "Stir-Fry",
    "Deep Fry",
    "Roast",
    "Bake",
    "Grill",
    "Emulsify",
    "Blend",
    "Dehydrate",
    "Multi-Stage",
]

COMPLEXITIES = ["Basic", "Intermediate", "Advanced", "Project"]
TIME_CLASSES = ["Under 15 min", "15–30 min", "30–60 min", "1–2 hr", "2–4 hr", "Half Day+", "Multi-Day"]
SERVICE_FORMATS = [
    "Single Plate",
    "Family Style",
    "Buffet / Shared",
    "Meal Prep",
    "Party Food",
    "Lunchbox",
    "Sauce / Add-On",
    "Side Component",
    "Base Recipe",
    "Kitchen Use",
]
SEASONS = ["Spring", "Summer", "Autumn", "Winter", "All Year"]

VALUE_ALIASES = {
    "dish_role": {
        "main": "Main",
        "main course": "Main",
        "main_course": "Main",
        "main-course": "Main",
        "starter course": "Starter",
        "side dish": "Side",
        "shared": "Shared Plate",
        "shared_plate": "Shared Plate",
        "sauce / condiment": "Sauce",
    },
    "technique_family": {
        "raw / no-cook": "Raw",
        "no cook": "Assemble",
        "no-cook": "Assemble",
        "sauce_emulsion": "Emulsify",
        "emulsion": "Emulsify",
        "pan fry": "Fry",
        "stir fry": "Stir-Fry",
        "deep-fry": "Deep Fry",
        "pressure-cook": "Pressure Cook",
        "slow-cook": "Slow Cook",
    },
    "service_format": {
        "hot plated": "Single Plate",
        "hot_plated": "Single Plate",
        "single_plate": "Single Plate",
        "family_style": "Family Style",
        "meal_prep": "Meal Prep",
    },
    "season": {
        "all_year": "All Year",
        "year-round": "All Year",
        "year round": "All Year",
    },
}

VOLUME_TO_ML = {
    "krm": 1.0,
    "kryddmått": 1.0,
    "tsp": 4.92892,
    "teaspoon": 4.92892,
    "teaspoons": 4.92892,
    "tsk": 4.92892,
    "tbsp": 14.7868,
    "tablespoon": 14.7868,
    "tablespoons": 14.7868,
    "msk": 14.7868,
    "fl oz": 29.5735,
    "fluid ounce": 29.5735,
    "fluid ounces": 29.5735,
    "cup": 236.588,
    "cups": 236.588,
    "pint": 473.176,
    "pints": 473.176,
    "quart": 946.353,
    "quarts": 946.353,
}

WEIGHT_TO_G = {
    "oz": 28.3495,
    "ounce": 28.3495,
    "ounces": 28.3495,
    "lb": 453.592,
    "lbs": 453.592,
    "pound": 453.592,
    "pounds": 453.592,
}

METRIC_UNIT_MAP = {
    "gram": "g",
    "grams": "g",
    "g": "g",
    "kilogram": "kg",
    "kilograms": "kg",
    "kg": "kg",
    "milliliter": "ml",
    "milliliters": "ml",
    "ml": "ml",
    "deciliter": "dl",
    "deciliters": "dl",
    "dl": "dl",
    "decilitre": "dl",
    "decilitres": "dl",
    "liter": "l",
    "liters": "l",
    "l": "l",
    "krm": "ml",
    "kryddmått": "ml",
}


class NormalizationFailure(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize recipe text/markdown files with LM Studio and write intake-style candidate bundles."
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        type=Path,
        help="Directory containing .txt/.md recipe files",
    )
    parser.add_argument("output_dir", type=Path, help="Directory for emitted .candidate.json files")
    parser.add_argument(
        "--file",
        dest="input_file",
        type=Path,
        help="Process a single recipe file directly instead of scanning a folder.",
    )
    parser.add_argument("--model", required=True, help="Loaded LM Studio model identifier")
    parser.add_argument(
        "--translation-model",
        help="Optional LM Studio model identifier for a translation pass before normalization.",
    )
    parser.add_argument(
        "--translation-source-lang",
        default="sv",
        help="Source language code for the translation pass (default: sv).",
    )
    parser.add_argument(
        "--translation-target-lang",
        default="en",
        help="Target language code for the translation pass (default: en).",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:1234/v1",
        help="LM Studio OpenAI-compatible base URL (default: http://localhost:1234/v1)",
    )
    parser.add_argument(
        "--prompt-path",
        type=Path,
        default=DEFAULT_PROMPT_PATH,
        help=f"Path to runtime prompt markdown (default: {DEFAULT_PROMPT_PATH})",
    )
    parser.add_argument(
        "--schema-path",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help=f"Path to output JSON schema (default: {DEFAULT_SCHEMA_PATH})",
    )
    parser.add_argument(
        "--translation-prompt-path",
        type=Path,
        default=DEFAULT_TRANSLATION_PROMPT_PATH,
        help=f"Path to translation prompt markdown (default: {DEFAULT_TRANSLATION_PROMPT_PATH})",
    )
    parser.add_argument(
        "--translation-schema-path",
        type=Path,
        default=DEFAULT_TRANSLATION_SCHEMA_PATH,
        help=f"Path to translation JSON schema (default: {DEFAULT_TRANSLATION_SCHEMA_PATH})",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing .candidate.json files",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="LM Studio sampling temperature (default: 0.0)",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=240,
        help="Request timeout in seconds (default: 240)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all eligible recipe files in the folder. Default behavior processes only the first eligible file.",
    )
    return parser.parse_args()


def load_prompt_instructions(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```text\s*(.*?)```", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_response_format(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "recipe_normalization_output",
            "strict": True,
            "schema": schema,
        },
    }


def iter_recipe_files(input_dir: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in ("**/*.txt", "**/*.md"):
        files.extend(input_dir.glob(pattern))
    return sorted(path for path in files if path.is_file() and is_recipe_source_file(path))


def is_recipe_source_file(path: Path) -> bool:
    lowered_name = path.name.lower()
    if lowered_name in {"readme.md", "readme.txt"}:
        return False
    if lowered_name.startswith("."):
        return False
    if any(part.startswith(".") or part.startswith("_") for part in path.parts):
        return False
    return True


def resolve_input_files(args: argparse.Namespace) -> list[Path]:
    input_file: Path | None = args.input_file
    input_dir: Path | None = args.input_dir

    if input_file is not None and input_dir is not None:
        raise NormalizationFailure("Provide either an input directory or --file, not both.")
    if input_file is None and input_dir is None:
        raise NormalizationFailure("Provide an input directory or use --file.")

    if input_file is not None:
        if not input_file.exists() or not input_file.is_file():
            raise NormalizationFailure(f"Input file does not exist or is not a file: {input_file}")
        if not is_recipe_source_file(input_file):
            raise NormalizationFailure(f"Input file is not treated as a recipe source: {input_file}")
        return [input_file]

    assert input_dir is not None
    if not input_dir.exists() or not input_dir.is_dir():
        raise NormalizationFailure(f"Input directory does not exist or is not a directory: {input_dir}")

    files = iter_recipe_files(input_dir)
    if not files:
        raise NormalizationFailure(f"No .txt or .md files found in {input_dir}")
    if not args.all:
        if len(files) > 1:
            print(
                f"[INFO] Found {len(files)} eligible recipe files; processing only the first by default: {files[0]}",
                file=sys.stderr,
            )
            print("[INFO] Use --all to process the full folder.", file=sys.stderr)
        files = files[:1]
    return files


def parse_fractional_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None

    cleaned = value.strip().replace("\u2044", "/")
    if not cleaned:
        return None

    mixed = re.fullmatch(r"(\d+)\s+(\d+)/(\d+)", cleaned)
    if mixed:
        whole = float(mixed.group(1))
        frac = Fraction(int(mixed.group(2)), int(mixed.group(3)))
        return whole + float(frac)

    frac = re.fullmatch(r"(\d+)/(\d+)", cleaned)
    if frac:
        return float(Fraction(int(frac.group(1)), int(frac.group(2))))

    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_unit(unit: str | None) -> str | None:
    if unit is None:
        return None
    cleaned = (
        unit.strip()
        .replace("а", "a")
        .replace("с", "c")
        .replace("е", "e")
        .replace("к", "k")
        .replace("м", "m")
        .replace("о", "o")
        .replace("р", "p")
        .replace("х", "x")
        .lower()
    )
    cleaned = cleaned.replace("nypa", "pinch")
    cleaned = cleaned.replace("kryddmatt", "kryddmått")
    cleaned = cleaned.replace("kryddmått", "krm")
    cleaned = cleaned.replace("matsked", "msk").replace("matskedar", "msk")
    cleaned = cleaned.replace("tesked", "tsk").replace("teskedar", "tsk")
    cleaned = cleaned.replace("mck", "msk")
    cleaned = cleaned.replace("pieces", "piece")
    cleaned = cleaned.replace("tablespoons", "tbsp").replace("tablespoon", "tbsp")
    cleaned = cleaned.replace("teaspoons", "tsp").replace("teaspoon", "tsp")
    cleaned = cleaned.replace("pounds", "lb").replace("pound", "lb")
    cleaned = cleaned.replace("ounces", "oz").replace("ounce", "oz")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or None


KNOWN_UNIT_TOKENS = {
    "g",
    "gram",
    "grams",
    "kg",
    "mg",
    "ml",
    "cl",
    "dl",
    "l",
    "tsp",
    "tbsp",
    "msk",
    "tsk",
    "cup",
    "cups",
    "oz",
    "lb",
    "piece",
    "pinch",
    "small",
    "medium",
    "large",
    "clove",
    "cloves",
}


def split_amount_and_embedded_unit(value: Any) -> tuple[Any, str | None, str | None]:
    if not isinstance(value, str):
        return value, None, None

    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return None, None, None

    match = re.fullmatch(
        r"(?P<amount>\d+(?:[.,]\d+)?\s*(?:-|–|to)\s*\d+(?:[.,]\d+)?|\d+\s+\d+/\d+|\d+/\d+|\d+(?:[.,]\d+)?)\s+(?P<unit>[^\d].*)",
        cleaned,
    )
    if not match:
        return value, None, None

    amount = match.group("amount").replace(",", ".")
    tail = match.group("unit").strip()
    tokens = tail.split()

    candidates: list[tuple[str, str | None]] = []
    if len(tokens) >= 2:
        candidates.append((" ".join(tokens[:2]), " ".join(tokens[2:]) or None))
    candidates.append((tokens[0], " ".join(tokens[1:]) or None))

    for unit_candidate, remainder in candidates:
        normalized = normalize_unit(unit_candidate)
        if normalized in KNOWN_UNIT_TOKENS:
            return amount, normalized, remainder

    normalized_tail = normalize_unit(tail)
    return amount, normalized_tail, None


def format_quantity(value: float) -> str:
    if value >= 100:
        rounded = round(value)
        return str(int(rounded))
    if value >= 10:
        return f"{value:.1f}".rstrip("0").rstrip(".")
    return f"{value:.2f}".rstrip("0").rstrip(".")


def round_to_step(value: float, step: float) -> float:
    return round(value / step) * step


def format_kitchen_metric_volume(milliliters: float) -> tuple[str, str]:
    if milliliters < 10:
        rounded_ml = max(0.5, round_to_step(milliliters, 0.5))
        return format_quantity(rounded_ml), "ml"
    if milliliters < 100:
        step = 5.0 if milliliters < 50 else 10.0
        rounded_ml = max(step, round_to_step(milliliters, step))
        return format_quantity(rounded_ml), "ml"
    if milliliters < 1000:
        rounded_dl = round_to_step(milliliters / 100.0, 0.1)
        return format_quantity(rounded_dl), "dl"
    rounded_l = round_to_step(milliliters / 1000.0, 0.1)
    return format_quantity(rounded_l), "l"


def fahrenheit_to_celsius(value: float) -> int:
    return round((value - 32.0) * 5.0 / 9.0)


def convert_fahrenheit_in_text(text: str | None) -> str | None:
    if not text:
        return text

    def repl(match: re.Match[str]) -> str:
        fahrenheit = float(match.group(1))
        celsius = fahrenheit_to_celsius(fahrenheit)
        return f"{celsius} C"

    return re.sub(r"\b(\d{2,3})\s*°?\s*F\b", repl, text, flags=re.IGNORECASE)


PREPARATION_REPLACEMENTS = (
    (r"\bfin chopped\b", "finely chopped"),
    (r"\bfinely chop\b", "finely chopped"),
    (r"\bgrated coarse\b", "coarsely grated"),
    (r",\s*grated coarse\b", ", coarsely grated"),
    (r",\s*grated coarsely\b", ", coarsely grated"),
    (r"\bgrated finely\b", "finely grated"),
    (r",\s*grated finely\b", ", finely grated"),
    (r"\bground freshly\b", "freshly ground"),
)


def normalize_phrase_artifacts(text: str | None) -> str | None:
    if text is None:
        return None
    normalized = " ".join(str(text).split()).strip()
    if not normalized:
        return None
    for pattern, replacement in PREPARATION_REPLACEMENTS:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    return normalized


def metricize_ingredient(
    ingredient: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    item = ingredient.get("item") or ""
    note = ingredient.get("note")
    quantity = ingredient.get("amount")
    embedded_quantity, embedded_unit, embedded_item_tail = split_amount_and_embedded_unit(quantity)
    if embedded_unit is not None:
        quantity = embedded_quantity
    unit = normalize_unit(ingredient.get("unit")) or embedded_unit
    raw_unit = ingredient.get("unit")
    if isinstance(raw_unit, str):
        malformed_range_unit = re.fullmatch(
            r"(?:to|–|-)\s*(\d+(?:[.,]\d+)?)\s+(.+)",
            " ".join(raw_unit.strip().split()),
            flags=re.IGNORECASE,
        )
        if malformed_range_unit:
            upper_bound = malformed_range_unit.group(1).replace(",", ".")
            normalized_remainder = normalize_unit(malformed_range_unit.group(2))
            if normalized_remainder:
                base_quantity = None if quantity is None else str(quantity).strip() or None
                if base_quantity:
                    quantity = f"{base_quantity} to {upper_bound}"
                unit = normalized_remainder
                warnings.append(
                    f"Recovered malformed range unit {raw_unit!r} into quantity range {quantity!r}."
                )
    if embedded_item_tail:
        if item:
            if embedded_item_tail.casefold() != item.casefold():
                item = f"{embedded_item_tail} {item}".strip()
        else:
            item = embedded_item_tail

    item = normalize_phrase_artifacts(item) or ""
    note = normalize_phrase_artifacts(note)

    # Clean recurring model phrasing drift in ingredient names.
    item_lower = item.casefold()
    if item_lower == "from relish or pickles":
        item = "pickle brine"
        if note:
            if "relish" not in note.casefold() and "pickle" not in note.casefold():
                note = f"{note}; from relish or pickles"
        else:
            note = "from relish or pickles"
        warnings.append("Normalized malformed ingredient item 'from relish or pickles' to 'pickle brine'.")
    elif item_lower.endswith(" from relish or pickles") and "brine" in item_lower:
        item = re.sub(r"\s+from relish or pickles$", "", item, flags=re.IGNORECASE).strip()
        if note:
            if "relish" not in note.casefold() and "pickle" not in note.casefold():
                note = f"{note}; from relish or pickles"
        else:
            note = "from relish or pickles"
        warnings.append("Trimmed source-text fragment from pickle brine ingredient item.")

    output = {
        "position": 0,
        "group_heading": None,
        "quantity": None if quantity is None else str(quantity).strip() or None,
        "unit": unit,
        "item": item,
        "preparation": note,
        "optional": bool(ingredient.get("optional") or False),
        "display_text": None,
    }

    if isinstance(output["quantity"], str):
        output["quantity"] = output["quantity"].replace("–", " to ").replace("-", " to ")
        output["quantity"] = re.sub(r"\s+", " ", output["quantity"]).strip()

    numeric_amount = parse_fractional_number(quantity)
    if numeric_amount is not None and unit:
        if unit in METRIC_UNIT_MAP:
            output["quantity"] = format_quantity(numeric_amount)
            output["unit"] = METRIC_UNIT_MAP[unit]
        elif unit in WEIGHT_TO_G:
            grams = numeric_amount * WEIGHT_TO_G[unit]
            if grams >= 1000:
                output["quantity"] = format_quantity(grams / 1000.0)
                output["unit"] = "kg"
            else:
                output["quantity"] = format_quantity(grams)
                output["unit"] = "g"
        elif unit in VOLUME_TO_ML:
            milliliters = numeric_amount * VOLUME_TO_ML[unit]
            output["quantity"], output["unit"] = format_kitchen_metric_volume(milliliters)
        elif unit in {"pinch", "nypa", "small", "medium", "large", "clove", "cloves"}:
            output["quantity"] = format_quantity(numeric_amount)
            output["unit"] = unit
        elif unit == "piece":
            output["quantity"] = format_quantity(numeric_amount)
            output["unit"] = None
        else:
            warnings.append(
                f"No deterministic metric conversion rule for ingredient unit {unit!r}: {item}"
            )
    elif unit in METRIC_UNIT_MAP:
        output["unit"] = METRIC_UNIT_MAP[unit]

    display_parts: list[str] = []
    if output["quantity"]:
        display_parts.append(output["quantity"])
        if output["unit"]:
            display_parts.append(output["unit"])
    display_parts.append(output["item"])
    if output["preparation"]:
        display_parts.append(f"({output['preparation']})")
    if output["optional"]:
        display_parts.append("[optional]")
    output["display_text"] = " ".join(display_parts) if display_parts else item

    return output


def dedupe_ingredients(
    ingredients: list[dict[str, Any]],
    warnings: list[str],
) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: dict[tuple[Any, ...], int] = {}

    for ingredient in ingredients:
        key = (
            ingredient.get("group_heading"),
            ingredient.get("quantity"),
            ingredient.get("unit"),
            (ingredient.get("item") or "").strip().lower(),
            (ingredient.get("preparation") or "").strip().lower(),
            bool(ingredient.get("optional")),
        )
        existing_index = seen.get(key)
        if existing_index is not None:
            warnings.append(
                f"Collapsed duplicate ingredient: {ingredient.get('display_text') or ingredient.get('item')}"
            )
            continue
        seen[key] = len(deduped)
        deduped.append(ingredient)

    for position, ingredient in enumerate(deduped, start=1):
        ingredient["position"] = position

    return deduped


SUSPICIOUS_ITEM_PREFIXES = (
    "from ",
    "with ",
    "for ",
    "to ",
    "optional ",
)


def add_unique_review_flag(review_flags: list[str], message: str) -> None:
    if message not in review_flags:
        review_flags.append(message)


def review_ingredient_quality(
    ingredients: list[dict[str, Any]],
    *,
    warnings: list[str],
    review_flags: list[str],
) -> None:
    relish_like_positions: list[int] = []
    shallot_positions: list[int] = []
    white_onion_positions: list[int] = []
    white_onion_powder_positions: list[int] = []

    for ingredient in ingredients:
        position = ingredient.get("position")
        item = str(ingredient.get("item") or "").strip()
        item_lower = item.lower()
        quantity = ingredient.get("quantity")
        unit = ingredient.get("unit")

        if unit and not quantity:
            warnings.append(
                f"Ingredient {position} has unit {unit!r} but no quantity: {item or '[empty item]'}"
            )
            add_unique_review_flag(
                review_flags,
                f"Review ingredients: ingredient {position} has a unit but no quantity.",
            )

        if any(item_lower.startswith(prefix) for prefix in SUSPICIOUS_ITEM_PREFIXES):
            warnings.append(
                f"Ingredient {position} item looks malformed: {item!r}"
            )
            add_unique_review_flag(
                review_flags,
                f"Review ingredients: ingredient {position} item may contain source-text fragments instead of a clean ingredient name.",
            )

        if any(token in item_lower for token in ("relish", "pickle", "gherkin", "brine")):
            relish_like_positions.append(int(position or 0))

        if "shallot" in item_lower:
            shallot_positions.append(int(position or 0))
        if "white onion" in item_lower:
            white_onion_positions.append(int(position or 0))
            if "powder" in item_lower:
                white_onion_powder_positions.append(int(position or 0))

    if len([pos for pos in relish_like_positions if pos > 0]) >= 2:
        warnings.append(
            "Multiple relish/pickle/brine-related ingredients were produced; verify these lines were not split incorrectly."
        )
        add_unique_review_flag(
            review_flags,
            "Review ingredients: overlapping relish/pickle/brine ingredient lines may have been split incorrectly.",
        )

    if shallot_positions and white_onion_positions:
        warnings.append(
            "Both shallot and white onion appear in the aromatics list; verify the model did not substitute one aromatic for another."
        )
        add_unique_review_flag(
            review_flags,
            "Review ingredients: shallot/white-onion identity may have drifted during normalization.",
        )

    if white_onion_powder_positions:
        warnings.append(
            "White onion powder appeared in the candidate; verify whether the source actually specified onion powder rather than white onion powder."
        )
        add_unique_review_flag(
            review_flags,
            "Review ingredients: onion-powder identity may have drifted during normalization.",
        )


def canonicalize_single_select(
    value: Any,
    *,
    field_name: str,
    allowed: list[str],
    warnings: list[str],
    review_flags: list[str],
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        warnings.append(f"{field_name} is not a string — set to null")
        review_flags.append(f"Review {field_name}: model returned a non-string value.")
        return None

    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned in allowed:
        return cleaned

    lowered = cleaned.lower()
    for option in allowed:
        if option.lower() == lowered:
            return option

    alias = VALUE_ALIASES.get(field_name, {}).get(lowered)
    if alias and alias in allowed:
        warnings.append(f"{field_name} normalized from {value!r} to {alias!r}")
        review_flags.append(f"Review {field_name}: normalized AI value {value!r} to canonical value {alias!r}.")
        return alias

    warnings.append(f"{field_name} value {value!r} not in allowed vocabulary — set to null")
    review_flags.append(f"Review {field_name}: AI value {value!r} was outside the allowed vocabulary and was cleared.")
    return None


def canonicalize_multi_select(
    values: Any,
    *,
    field_name: str,
    allowed: list[str],
    warnings: list[str],
    review_flags: list[str],
) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        warnings.append(f"{field_name} is not an array — set to empty")
        review_flags.append(f"Review {field_name}: model returned a non-array value.")
        return []

    normalized: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        canonical = canonicalize_single_select(
            raw_value,
            field_name=field_name,
            allowed=allowed,
            warnings=warnings,
            review_flags=review_flags,
        )
        if canonical and canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)
    return normalized


def normalize_uncertainty_notes(
    values: Any,
    *,
    warnings: list[str],
    review_flags: list[str],
    max_items: int = 12,
) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        warnings.append("uncertainty_notes is not an array — set to empty")
        review_flags.append("Review uncertainty_notes: model returned a non-array value.")
        return []

    cleaned_notes: list[str] = []
    seen: set[str] = set()
    skipped_generic = 0

    for raw_value in values:
        if not isinstance(raw_value, str):
            continue
        note = " ".join(raw_value.split()).strip()
        if not note:
            continue
        lowered = note.lower()
        if lowered.startswith("uncertainty in exact "):
            skipped_generic += 1
            continue
        if lowered in seen:
            continue
        seen.add(lowered)
        cleaned_notes.append(note)

    if skipped_generic:
        warnings.append(f"Removed {skipped_generic} generic uncertainty note(s).")
        review_flags.append("Review uncertainty_notes: repetitive generic uncertainty lines were removed.")

    if len(cleaned_notes) > max_items:
        dropped = len(cleaned_notes) - max_items
        cleaned_notes = cleaned_notes[:max_items]
        warnings.append(f"Capped uncertainty_notes to {max_items} entries; dropped {dropped} extra note(s).")
        review_flags.append(f"Review uncertainty_notes: capped to {max_items} entries after cleanup.")

    return cleaned_notes


def validate_normalization_payload(payload: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Response root is not an object."]

    required = schema.get("required", [])
    for key in required:
        if key not in payload:
            errors.append(f"Missing required field: {key}")

    if errors:
        return errors

    if payload.get("output_language") != "en":
        errors.append("Field output_language must be 'en'.")

    array_fields = (
        "secondary_cuisines",
        "ingredient_families",
        "mood_tags",
        "storage_profile",
        "dietary_flags",
        "provision_tags",
        "ingredients",
        "steps",
        "uncertainty_notes",
    )
    for key in array_fields:
        if key in payload and not isinstance(payload[key], list):
            errors.append(f"Field {key} is not an array.")

    for idx, ingredient in enumerate(payload.get("ingredients", []), start=1):
        if not isinstance(ingredient, dict):
            errors.append(f"Ingredient {idx} is not an object.")
            continue
        for key in ("amount", "unit", "item", "note", "optional", "group"):
            if key not in ingredient:
                errors.append(f"Ingredient {idx} missing field: {key}")
        if "item" in ingredient and not isinstance(ingredient.get("item"), str):
            errors.append(f"Ingredient {idx} field item is not a string.")

    for idx, step in enumerate(payload.get("steps", []), start=1):
        if not isinstance(step, dict):
            errors.append(f"Step {idx} is not an object.")
            continue
        for key in ("step_number", "instruction", "time_note", "heat_note", "equipment_note"):
            if key not in step:
                errors.append(f"Step {idx} missing field: {key}")
        if "step_number" in step and not isinstance(step.get("step_number"), int):
            errors.append(f"Step {idx} step_number is not an integer.")
        if "instruction" in step and not isinstance(step.get("instruction"), str):
            errors.append(f"Step {idx} instruction is not a string.")

    return errors


def validate_translation_payload(payload: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Translation response root is not an object."]

    required = schema.get("required", [])
    for key in required:
        if key not in payload:
            errors.append(f"Missing required translation field: {key}")

    if errors:
        return errors

    if payload.get("output_language") != "en":
        errors.append("Translation field output_language must be 'en'.")

    translated_text = payload.get("translated_text")
    if not isinstance(translated_text, str) or not translated_text.strip():
        errors.append("Translation field translated_text must be a non-empty string.")

    source_language = payload.get("source_language")
    if not isinstance(source_language, str) or not source_language.strip():
        errors.append("Translation field source_language must be a non-empty string.")

    return errors


def build_user_prompt(filename: str, raw_source_text: str, source_type: str, source_url: str | None) -> str:
    envelope = {
        "raw_source_text": raw_source_text,
        "source_type": source_type,
        "source_url": source_url,
        "user_notes": None,
        "filename": filename,
    }
    return json.dumps(envelope, ensure_ascii=True, indent=2)


def build_translation_user_prompt(filename: str, raw_source_text: str, source_type: str, source_url: str | None) -> str:
    envelope = {
        "raw_source_text": raw_source_text,
        "source_type": source_type,
        "source_url": source_url,
        "filename": filename,
    }
    return json.dumps(envelope, ensure_ascii=True, indent=2)


def build_plain_translation_prompt(
    *,
    source_text: str,
    source_lang_code: str,
    target_lang_code: str,
) -> str:
    return "\n".join(
        [
            f"Translate the following {source_lang_code} recipe text into {target_lang_code}.",
            "Output only the translation.",
            "Preserve quantities, units, temperatures, timings, headings, and line breaks where practical.",
            "",
            source_text,
        ]
    )


def build_translategemma_content_item(
    *,
    source_text: str,
    source_lang_code: str,
    target_lang_code: str,
) -> dict[str, Any]:
    return {
        "type": "text",
        "source_lang_code": source_lang_code,
        "target_lang_code": target_lang_code,
        "text": source_text,
        "image": None,
    }


def get_language_name(language_code: str) -> str:
    return LANGUAGE_NAMES.get(language_code.replace("_", "-").casefold(), language_code)


def build_translategemma_completion_prompt(
    *,
    source_text: str,
    source_lang_code: str,
    target_lang_code: str,
) -> str:
    source_lang = get_language_name(source_lang_code)
    target_lang = get_language_name(target_lang_code)
    return (
        "<bos><start_of_turn>user\n"
        f"You are a professional {source_lang} ({source_lang_code}) to "
        f"{target_lang} ({target_lang_code}) translator. Your goal is to accurately "
        f"convey the meaning and nuances of the original {source_lang} text while "
        f"adhering to {target_lang} grammar, vocabulary, and cultural sensitivities.\n"
        f"Produce only the {target_lang} translation, without any additional "
        f"explanations or commentary. Please translate the following {source_lang} "
        f"text into {target_lang}:\n\n\n"
        f"{source_text.strip()}\n"
        "<end_of_turn>\n"
        "<start_of_turn>model\n"
    )


def lmstudio_post_json(
    *,
    url: str,
    payload: dict[str, Any],
    timeout_seconds: int,
) -> dict[str, Any]:
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            raw_response = response.read().decode("utf-8")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise NormalizationFailure(f"LM Studio HTTP error {exc.code}: {body}") from exc
    except error.URLError as exc:
        raise NormalizationFailure(
            f"Could not connect to LM Studio at {url}: {exc}"
        ) from exc

    try:
        return json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise NormalizationFailure(
            f"Unexpected LM Studio response shape: {raw_response[:500]}"
        ) from exc


def lmstudio_chat_raw_content(
    *,
    base_url: str,
    payload: dict[str, Any],
    timeout_seconds: int,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    parsed = lmstudio_post_json(
        url=url,
        payload=payload,
        timeout_seconds=timeout_seconds,
    )

    try:
        message = parsed["choices"][0]["message"]
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            content = message.get("reasoning_content")
    except (KeyError, IndexError, TypeError) as exc:
        raise NormalizationFailure(f"Unexpected LM Studio response shape: {parsed}") from exc

    if not isinstance(content, str) or not content.strip():
        raise NormalizationFailure("LM Studio returned empty content.")

    return content


def lmstudio_completion_raw_text(
    *,
    base_url: str,
    payload: dict[str, Any],
    timeout_seconds: int,
) -> str:
    url = base_url.rstrip("/") + "/completions"
    parsed = lmstudio_post_json(
        url=url,
        payload=payload,
        timeout_seconds=timeout_seconds,
    )

    try:
        text = parsed["choices"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise NormalizationFailure(f"Unexpected LM Studio completion response shape: {parsed}") from exc

    if not isinstance(text, str) or not text.strip():
        raise NormalizationFailure("LM Studio returned empty completion text.")

    return text


def lmstudio_chat_completion(
    *,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    response_format: dict[str, Any],
    temperature: float,
    timeout_seconds: int,
) -> tuple[dict[str, Any], str]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": response_format,
        "temperature": temperature,
        "stream": False,
    }
    try:
        content = lmstudio_chat_raw_content(
            base_url=base_url,
            payload=payload,
            timeout_seconds=timeout_seconds,
        )
    except NormalizationFailure as exc:
        if "conversations must start with a user prompt" not in str(exc).casefold():
            raise
        merged_prompt = "\n\n".join(
            [
                "Follow these instructions exactly.",
                system_prompt.strip(),
                "User input:",
                user_prompt,
            ]
        )
        fallback_payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": merged_prompt},
            ],
            "response_format": response_format,
            "temperature": temperature,
            "stream": False,
        }
        content = lmstudio_chat_raw_content(
            base_url=base_url,
            payload=fallback_payload,
            timeout_seconds=timeout_seconds,
        )

    try:
        return json.loads(content), content
    except json.JSONDecodeError as exc:
        raise NormalizationFailure(
            f"LM Studio returned non-JSON content: {content[:500]}"
        ) from exc


def lmstudio_translation_completion(
    *,
    base_url: str,
    model: str,
    source_text: str,
    source_lang_code: str,
    target_lang_code: str,
    system_prompt: str | None,
    response_format: dict[str, Any] | None,
    temperature: float,
    timeout_seconds: int,
) -> tuple[dict[str, Any], str]:
    if "translategemma" in model.casefold():
        completion_prompt = build_translategemma_completion_prompt(
            source_text=source_text,
            source_lang_code=source_lang_code,
            target_lang_code=target_lang_code,
        )
        completion_payload = {
            "model": model,
            "prompt": completion_prompt,
            "temperature": temperature,
            "stream": False,
        }
        content_item = build_translategemma_content_item(
            source_text=source_text,
            source_lang_code=source_lang_code,
            target_lang_code=target_lang_code,
        )
        custom_payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [content_item],
                }
            ],
            "temperature": temperature,
            "stream": False,
        }
        try:
            content = lmstudio_completion_raw_text(
                base_url=base_url,
                payload=completion_payload,
                timeout_seconds=timeout_seconds,
            )
        except NormalizationFailure as exc:
            try:
                content = lmstudio_chat_raw_content(
                    base_url=base_url,
                    payload=custom_payload,
                    timeout_seconds=timeout_seconds,
                )
            except NormalizationFailure:
                # Some LM Studio profiles for TranslateGemma use a normal Gemma-style
                # chat template rather than the model-specific structured user content.
                # Retry once with a plain user prompt in that case.
                prompt = build_plain_translation_prompt(
                    source_text=source_text,
                    source_lang_code=source_lang_code,
                    target_lang_code=target_lang_code,
                )
                plain_payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "temperature": temperature,
                    "stream": False,
                }
                if "jinja template" not in str(exc).lower():
                    raise exc
                content = lmstudio_chat_raw_content(
                    base_url=base_url,
                    payload=plain_payload,
                    timeout_seconds=timeout_seconds,
                )
        translated_text = content.strip()
        return {
            "source_language": source_lang_code,
            "output_language": target_lang_code,
            "translated_text": translated_text,
        }, translated_text

    if system_prompt is None or response_format is None:
        raise NormalizationFailure("Translation prompt/schema are required for JSON-based translation models.")

    user_prompt = build_translation_user_prompt(
        filename="source.txt",
        raw_source_text=source_text,
        source_type="text_file",
        source_url=None,
    )
    return lmstudio_chat_completion(
        base_url=base_url,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_format=response_format,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
    )


def build_candidate_bundle(
    *,
    source_path: Path,
    relative_source_path: Path,
    source_text: str,
    normalized_input_text: str,
    source_type: str,
    source_url: str | None,
    model: str,
    prompt_path: Path,
    schema_path: Path,
    raw_payload: dict[str, Any],
    raw_payload_json: str,
    translation_payload: dict[str, Any] | None,
    translation_payload_json: str | None,
    translation_model: str | None,
    translation_prompt_path: Path | None,
    translation_schema_path: Path | None,
) -> dict[str, Any]:
    warnings: list[str] = []
    review_flags: list[str] = []

    normalized_ingredients: list[dict[str, Any]] = []
    for ingredient in raw_payload.get("ingredients", []):
        normalized = metricize_ingredient(ingredient, warnings)
        normalized_ingredients.append(normalized)
    ingredients = dedupe_ingredients(normalized_ingredients, warnings)
    review_ingredient_quality(
        ingredients,
        warnings=warnings,
        review_flags=review_flags,
    )

    steps: list[dict[str, Any]] = []
    for position, step in enumerate(raw_payload.get("steps", []), start=1):
        instruction = convert_fahrenheit_in_text(step.get("instruction"))
        time_note = step.get("time_note")
        equipment_note_parts = []
        if step.get("equipment_note"):
            equipment_note_parts.append(str(step["equipment_note"]).strip())
        if step.get("heat_note"):
            equipment_note_parts.append(f"Heat: {convert_fahrenheit_in_text(step['heat_note'])}")
        equipment_note = " | ".join(part for part in equipment_note_parts if part) or None

        steps.append(
            {
                "position": position,
                "instruction": instruction,
                "time_note": convert_fahrenheit_in_text(time_note),
                "equipment_note": equipment_note,
            }
        )

    title = raw_payload.get("title")
    short_description = raw_payload.get("short_description")
    dish_role = canonicalize_single_select(
        raw_payload.get("dish_role"),
        field_name="dish_role",
        allowed=DISH_ROLES,
        warnings=warnings,
        review_flags=review_flags,
    )
    primary_cuisine = canonicalize_single_select(
        raw_payload.get("primary_cuisine"),
        field_name="primary_cuisine",
        allowed=PRIMARY_CUISINES,
        warnings=warnings,
        review_flags=review_flags,
    )
    technique_family = canonicalize_single_select(
        raw_payload.get("technique_family"),
        field_name="technique_family",
        allowed=TECHNIQUE_FAMILIES,
        warnings=warnings,
        review_flags=review_flags,
    )
    complexity = canonicalize_single_select(
        raw_payload.get("complexity"),
        field_name="complexity",
        allowed=COMPLEXITIES,
        warnings=warnings,
        review_flags=review_flags,
    )
    time_class = canonicalize_single_select(
        raw_payload.get("time_class"),
        field_name="time_class",
        allowed=TIME_CLASSES,
        warnings=warnings,
        review_flags=review_flags,
    )
    service_format = canonicalize_single_select(
        raw_payload.get("service_format"),
        field_name="service_format",
        allowed=SERVICE_FORMATS,
        warnings=warnings,
        review_flags=review_flags,
    )
    season = canonicalize_single_select(
        raw_payload.get("season"),
        field_name="season",
        allowed=SEASONS,
        warnings=warnings,
        review_flags=review_flags,
    )
    secondary_cuisines = canonicalize_multi_select(
        raw_payload.get("secondary_cuisines", []),
        field_name="secondary_cuisines",
        allowed=PRIMARY_CUISINES,
        warnings=warnings,
        review_flags=review_flags,
    )
    uncertainty_notes = normalize_uncertainty_notes(
        raw_payload.get("uncertainty_notes", []),
        warnings=warnings,
        review_flags=review_flags,
    )

    candidate_update = {
        "title": title,
        "short_description": short_description,
        "dish_role": dish_role,
        "primary_cuisine": primary_cuisine,
        "technique_family": technique_family,
        "complexity": complexity,
        "time_class": time_class,
        "servings": None if raw_payload.get("servings") is None else str(raw_payload.get("servings")),
        "prep_time_minutes": raw_payload.get("prep_time_minutes"),
        "cook_time_minutes": raw_payload.get("cook_time_minutes"),
        "notes": raw_payload.get("recipe_notes"),
        "service_notes": raw_payload.get("service_notes"),
        "source_credit": None,
        "ingredients": ingredients,
        "steps": steps,
    }

    candidate_extras = {
        "secondary_cuisines": secondary_cuisines,
        "ingredient_families": raw_payload.get("ingredient_families", []),
        "service_format": service_format,
        "season": season,
        "mood_tags": raw_payload.get("mood_tags", []),
        "storage_profile": raw_payload.get("storage_profile", []),
        "dietary_flags": raw_payload.get("dietary_flags", []),
        "provision_tags": raw_payload.get("provision_tags", []),
        "sector": raw_payload.get("sector"),
        "operational_class": raw_payload.get("class"),
        "heat_window": raw_payload.get("heat_window"),
        "total_time_minutes": raw_payload.get("total_time_minutes"),
        "yield_text": raw_payload.get("yield_text"),
        "uncertainty_notes": uncertainty_notes,
        "confidence_summary": raw_payload.get("confidence_summary"),
    }

    bundle = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "source": {
            "source_type": source_type,
            "source_language": (
                translation_payload.get("source_language")
                if translation_payload is not None
                else raw_payload.get("source_language")
            ),
            "output_language": raw_payload.get("output_language"),
            "source_url": source_url,
            "source_file": str(source_path),
            "relative_source_path": str(relative_source_path),
            "raw_source_text": source_text,
            "normalized_input_text": normalized_input_text,
        },
        "candidate": {
            "candidate_status": "pending",
            "approval_required": True,
            "candidate_update": candidate_update,
            "candidate_extras": candidate_extras,
        },
        "ai_metadata": {
            "provider": "lm_studio",
            "model": model,
            "prompt_path": str(prompt_path.relative_to(REPO_ROOT)),
            "schema_path": str(schema_path.relative_to(REPO_ROOT)),
            "generated_at_unix": int(time.time()),
            "ai_payload_json": raw_payload_json,
        },
        "review_flags": review_flags,
        "warnings": warnings,
    }

    if translation_payload is not None and translation_payload_json is not None and translation_model is not None:
        bundle["ai_metadata"]["translation_model"] = translation_model
        bundle["ai_metadata"]["translation_payload_json"] = translation_payload_json
        if translation_prompt_path is not None:
            bundle["ai_metadata"]["translation_prompt_path"] = str(translation_prompt_path.relative_to(REPO_ROOT))
        if translation_schema_path is not None:
            bundle["ai_metadata"]["translation_schema_path"] = str(translation_schema_path.relative_to(REPO_ROOT))

    return bundle


def process_file(
    *,
    input_root: Path,
    source_path: Path,
    output_dir: Path,
    base_url: str,
    model: str,
    translation_model: str | None,
    translation_source_lang: str,
    translation_target_lang: str,
    prompt_path: Path,
    schema_path: Path,
    translation_prompt_path: Path | None,
    translation_schema_path: Path | None,
    system_prompt: str,
    schema: dict[str, Any],
    translation_system_prompt: str | None,
    translation_schema: dict[str, Any] | None,
    overwrite: bool,
    temperature: float,
    timeout_seconds: int,
) -> Path:
    source_text = source_path.read_text(encoding="utf-8", errors="replace").strip()
    if not source_text:
        raise NormalizationFailure(f"File is empty: {source_path}")

    source_type = "markdown_file" if source_path.suffix.lower() == ".md" else "text_file"
    relative_source_path = source_path.relative_to(input_root)
    normalized_input_text = source_text
    translation_payload: dict[str, Any] | None = None
    translation_payload_json: str | None = None

    if translation_model is not None:
        if translation_system_prompt is None or translation_schema is None:
            raise NormalizationFailure("Translation model was provided without translation prompt/schema being loaded.")

        translation_user_prompt = build_translation_user_prompt(
            filename=source_path.name,
            raw_source_text=source_text,
            source_type=source_type,
            source_url=None,
        )
        translation_payload, translation_payload_json = lmstudio_translation_completion(
            base_url=base_url,
            model=translation_model,
            source_text=source_text,
            source_lang_code=translation_source_lang,
            target_lang_code=translation_target_lang,
            system_prompt=translation_system_prompt,
            response_format=None if translation_schema is None else schema_response_format(translation_schema),
            temperature=temperature,
            timeout_seconds=timeout_seconds,
        )
        translation_errors = validate_translation_payload(translation_payload, translation_schema)
        if translation_errors:
            raise NormalizationFailure("; ".join(translation_errors))
        normalized_input_text = translation_payload["translated_text"].strip()
        if not normalized_input_text:
            raise NormalizationFailure("Translation model returned an empty translated_text.")

    user_prompt = build_user_prompt(
        filename=source_path.name,
        raw_source_text=normalized_input_text,
        source_type=source_type,
        source_url=None,
    )

    payload, raw_payload_json = lmstudio_chat_completion(
        base_url=base_url,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_format=schema_response_format(schema),
        temperature=temperature,
        timeout_seconds=timeout_seconds,
    )

    validation_errors = validate_normalization_payload(payload, schema)
    if validation_errors:
        raise NormalizationFailure("; ".join(validation_errors))

    artifact = build_candidate_bundle(
        source_path=source_path,
        relative_source_path=relative_source_path,
        source_text=source_text,
        normalized_input_text=normalized_input_text,
        source_type=source_type,
        source_url=None,
        model=model,
        prompt_path=prompt_path,
        schema_path=schema_path,
        raw_payload=payload,
        raw_payload_json=raw_payload_json,
        translation_payload=translation_payload,
        translation_payload_json=translation_payload_json,
        translation_model=translation_model,
        translation_prompt_path=translation_prompt_path,
        translation_schema_path=translation_schema_path,
    )

    output_path = output_dir / relative_source_path.with_suffix(".candidate.json")
    if output_path.exists() and not overwrite:
        raise NormalizationFailure(f"Refusing to overwrite existing file: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=True), encoding="utf-8")
    return output_path


def main() -> int:
    args = parse_args()

    if not args.prompt_path.exists():
        print(f"Prompt file not found: {args.prompt_path}", file=sys.stderr)
        return 2

    if not args.schema_path.exists():
        print(f"Schema file not found: {args.schema_path}", file=sys.stderr)
        return 2

    if args.translation_model is not None and not args.translation_prompt_path.exists():
        print(f"Translation prompt file not found: {args.translation_prompt_path}", file=sys.stderr)
        return 2

    if args.translation_model is not None and not args.translation_schema_path.exists():
        print(f"Translation schema file not found: {args.translation_schema_path}", file=sys.stderr)
        return 2

    try:
        files = resolve_input_files(args)
    except NormalizationFailure as exc:
        print(str(exc), file=sys.stderr)
        return 2

    input_root = args.input_file.parent if args.input_file is not None else args.input_dir

    system_prompt = load_prompt_instructions(args.prompt_path)
    schema = load_schema(args.schema_path)
    translation_system_prompt = None
    translation_schema = None
    if args.translation_model is not None:
        translation_system_prompt = load_prompt_instructions(args.translation_prompt_path)
        translation_schema = load_schema(args.translation_schema_path)

    failures = 0
    for source_path in files:
        try:
            output_path = process_file(
                input_root=input_root,
                source_path=source_path,
                output_dir=args.output_dir,
                base_url=args.base_url,
                model=args.model,
                translation_model=args.translation_model,
                translation_source_lang=args.translation_source_lang,
                translation_target_lang=args.translation_target_lang,
                prompt_path=args.prompt_path,
                schema_path=args.schema_path,
                translation_prompt_path=args.translation_prompt_path if args.translation_model is not None else None,
                translation_schema_path=args.translation_schema_path if args.translation_model is not None else None,
                system_prompt=system_prompt,
                schema=schema,
                translation_system_prompt=translation_system_prompt,
                translation_schema=translation_schema,
                overwrite=args.overwrite,
                temperature=args.temperature,
                timeout_seconds=args.timeout_seconds,
            )
            print(f"[OK] {source_path} -> {output_path}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"[FAIL] {source_path}: {exc}", file=sys.stderr)

    if failures:
        print(f"\nCompleted with {failures} failure(s).", file=sys.stderr)
        return 1

    print("\nCompleted successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
