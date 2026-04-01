from __future__ import annotations

import re
from fractions import Fraction
from pathlib import Path
from typing import Any

from .constants import (
    COMPLEXITIES,
    DISH_ROLES,
    KNOWN_UNIT_TOKENS,
    METRIC_UNIT_MAP,
    PREPARATION_REPLACEMENTS,
    PRIMARY_CUISINES,
    SEASONS,
    SERVICE_FORMATS,
    SUSPICIOUS_ITEM_PREFIXES,
    TECHNIQUE_FAMILIES,
    TIME_CLASSES,
    VALUE_ALIASES,
    VOLUME_TO_ML,
    WEIGHT_TO_G,
)
from .models import CandidateExtrasPayload, CandidateUpdatePayload, IngredientRecord, StepRecord
from .references import unit_alias_map


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
    cleaned = cleaned.replace("kryddmatt", "kryddmått")
    cleaned = cleaned.replace("mck", "msk")
    cleaned = cleaned.replace("pieces", "piece")
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        return None
    return unit_alias_map().get(cleaned, cleaned)


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


def normalize_phrase_artifacts(text: str | None) -> str | None:
    if text is None:
        return None
    normalized = " ".join(str(text).split()).strip()
    if not normalized:
        return None
    for pattern, replacement in PREPARATION_REPLACEMENTS:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    return normalized


def metricize_ingredient(ingredient: dict[str, Any], warnings: list[str]) -> IngredientRecord:
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

    item_lower = item.casefold()
    if item_lower == "from relish or pickles":
        item = "pickle brine"
        note = f"{note}; from relish or pickles" if note else "from relish or pickles"
        warnings.append("Normalized malformed ingredient item 'from relish or pickles' to 'pickle brine'.")
    elif item_lower.endswith(" from relish or pickles") and "brine" in item_lower:
        item = re.sub(r"\s+from relish or pickles$", "", item, flags=re.IGNORECASE).strip()
        note = f"{note}; from relish or pickles" if note else "from relish or pickles"
        warnings.append("Trimmed source-text fragment from pickle brine ingredient item.")

    output = IngredientRecord(
        position=0,
        group_heading=None,
        quantity=None if quantity is None else str(quantity).strip() or None,
        unit=unit,
        item=item,
        preparation=note,
        optional=bool(ingredient.get("optional") or False),
        display_text=None,
    )

    if isinstance(output.quantity, str):
        output.quantity = output.quantity.replace("–", " to ").replace("-", " to ")
        output.quantity = re.sub(r"\s+", " ", output.quantity).strip()

    numeric_amount = parse_fractional_number(quantity)
    if numeric_amount is not None and unit:
        if unit in METRIC_UNIT_MAP:
            output.quantity = format_quantity(numeric_amount)
            output.unit = METRIC_UNIT_MAP[unit]
        elif unit in WEIGHT_TO_G:
            grams = numeric_amount * WEIGHT_TO_G[unit]
            if grams >= 1000:
                output.quantity = format_quantity(grams / 1000.0)
                output.unit = "kg"
            else:
                output.quantity = format_quantity(grams)
                output.unit = "g"
        elif unit in VOLUME_TO_ML:
            milliliters = numeric_amount * VOLUME_TO_ML[unit]
            output.quantity, output.unit = format_kitchen_metric_volume(milliliters)
        elif unit in {"pinch", "nypa", "small", "medium", "large", "clove", "cloves"}:
            output.quantity = format_quantity(numeric_amount)
            output.unit = unit
        elif unit == "piece":
            output.quantity = format_quantity(numeric_amount)
            output.unit = None
        else:
            warnings.append(f"No deterministic metric conversion rule for ingredient unit {unit!r}: {item}")
    elif unit in METRIC_UNIT_MAP:
        output.unit = METRIC_UNIT_MAP[unit]

    display_parts: list[str] = []
    if output.quantity:
        display_parts.append(output.quantity)
        if output.unit:
            display_parts.append(output.unit)
    display_parts.append(output.item)
    if output.preparation:
        display_parts.append(f"({output.preparation})")
    if output.optional:
        display_parts.append("[optional]")
    output.display_text = " ".join(display_parts) if display_parts else item
    return output


def dedupe_ingredients(ingredients: list[IngredientRecord], warnings: list[str]) -> list[IngredientRecord]:
    deduped: list[IngredientRecord] = []
    seen: dict[tuple[Any, ...], int] = {}

    for ingredient in ingredients:
        key = (
            ingredient.group_heading,
            ingredient.quantity,
            ingredient.unit,
            ingredient.item.strip().lower(),
            (ingredient.preparation or "").strip().lower(),
            bool(ingredient.optional),
        )
        if key in seen:
            warnings.append(f"Collapsed duplicate ingredient: {ingredient.display_text or ingredient.item}")
            continue
        seen[key] = len(deduped)
        deduped.append(ingredient)

    for position, ingredient in enumerate(deduped, start=1):
        ingredient.position = position
    return deduped


def add_unique_review_flag(review_flags: list[str], message: str) -> None:
    if message not in review_flags:
        review_flags.append(message)


def review_ingredient_quality(ingredients: list[IngredientRecord], *, warnings: list[str], review_flags: list[str]) -> None:
    relish_like_positions: list[int] = []
    shallot_positions: list[int] = []
    white_onion_positions: list[int] = []
    white_onion_powder_positions: list[int] = []

    for ingredient in ingredients:
        position = ingredient.position
        item = ingredient.item.strip()
        item_lower = item.lower()
        quantity = ingredient.quantity
        unit = ingredient.unit

        if unit and not quantity:
            warnings.append(f"Ingredient {position} has unit {unit!r} but no quantity: {item or '[empty item]'}")
            add_unique_review_flag(review_flags, f"Review ingredients: ingredient {position} has a unit but no quantity.")

        if any(item_lower.startswith(prefix) for prefix in SUSPICIOUS_ITEM_PREFIXES):
            warnings.append(f"Ingredient {position} item looks malformed: {item!r}")
            add_unique_review_flag(
                review_flags,
                f"Review ingredients: ingredient {position} item may contain source-text fragments instead of a clean ingredient name.",
            )

        if any(token in item_lower for token in ("relish", "pickle", "gherkin", "brine")):
            relish_like_positions.append(position)
        if "shallot" in item_lower:
            shallot_positions.append(position)
        if "white onion" in item_lower:
            white_onion_positions.append(position)
            if "powder" in item_lower:
                white_onion_powder_positions.append(position)

    if len(relish_like_positions) >= 2:
        warnings.append("Multiple relish/pickle/brine-related ingredients were produced; verify these lines were not split incorrectly.")
        add_unique_review_flag(
            review_flags,
            "Review ingredients: overlapping relish/pickle/brine ingredient lines may have been split incorrectly.",
        )
    if shallot_positions and white_onion_positions:
        warnings.append("Both shallot and white onion appear in the aromatics list; verify the model did not substitute one aromatic for another.")
        add_unique_review_flag(review_flags, "Review ingredients: shallot/white-onion identity may have drifted during normalization.")
    if white_onion_powder_positions:
        warnings.append("White onion powder appeared in the candidate; verify whether the source actually specified onion powder rather than white onion powder.")
        add_unique_review_flag(review_flags, "Review ingredients: onion-powder identity may have drifted during normalization.")


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


def build_candidate_payloads(
    raw_payload: dict[str, Any],
    *,
    initial_warnings: list[str] | None = None,
    initial_review_flags: list[str] | None = None,
) -> tuple[CandidateUpdatePayload, CandidateExtrasPayload, list[str], list[str]]:
    warnings: list[str] = list(initial_warnings or [])
    review_flags: list[str] = list(initial_review_flags or [])

    normalized_ingredients = [metricize_ingredient(ingredient, warnings) for ingredient in raw_payload.get("ingredients", [])]
    ingredients = dedupe_ingredients(normalized_ingredients, warnings)
    review_ingredient_quality(ingredients, warnings=warnings, review_flags=review_flags)

    steps = []
    for position, step in enumerate(raw_payload.get("steps", []), start=1):
        equipment_note_parts = []
        if step.get("equipment_note"):
            equipment_note_parts.append(str(step["equipment_note"]).strip())
        if step.get("heat_note"):
            equipment_note_parts.append(f"Heat: {convert_fahrenheit_in_text(step['heat_note'])}")
        equipment_note = " | ".join(part for part in equipment_note_parts if part) or None
        steps.append(
            StepRecord(
                position=position,
                instruction=convert_fahrenheit_in_text(step.get("instruction")) or "",
                time_note=convert_fahrenheit_in_text(step.get("time_note")),
                equipment_note=equipment_note,
            )
        )

    candidate_update = CandidateUpdatePayload(
        title=raw_payload.get("title"),
        short_description=raw_payload.get("short_description"),
        dish_role=canonicalize_single_select(raw_payload.get("dish_role"), field_name="dish_role", allowed=DISH_ROLES, warnings=warnings, review_flags=review_flags),
        primary_cuisine=canonicalize_single_select(raw_payload.get("primary_cuisine"), field_name="primary_cuisine", allowed=PRIMARY_CUISINES, warnings=warnings, review_flags=review_flags),
        technique_family=canonicalize_single_select(raw_payload.get("technique_family"), field_name="technique_family", allowed=TECHNIQUE_FAMILIES, warnings=warnings, review_flags=review_flags),
        complexity=canonicalize_single_select(raw_payload.get("complexity"), field_name="complexity", allowed=COMPLEXITIES, warnings=warnings, review_flags=review_flags),
        time_class=canonicalize_single_select(raw_payload.get("time_class"), field_name="time_class", allowed=TIME_CLASSES, warnings=warnings, review_flags=review_flags),
        servings=None if raw_payload.get("servings") is None else str(raw_payload.get("servings")),
        prep_time_minutes=raw_payload.get("prep_time_minutes"),
        cook_time_minutes=raw_payload.get("cook_time_minutes"),
        notes=raw_payload.get("recipe_notes"),
        service_notes=raw_payload.get("service_notes"),
        source_credit=None,
        ingredients=ingredients,
        steps=steps,
    )

    candidate_extras = CandidateExtrasPayload(
        secondary_cuisines=canonicalize_multi_select(raw_payload.get("secondary_cuisines", []), field_name="secondary_cuisines", allowed=PRIMARY_CUISINES, warnings=warnings, review_flags=review_flags),
        ingredient_families=raw_payload.get("ingredient_families", []),
        service_format=canonicalize_single_select(raw_payload.get("service_format"), field_name="service_format", allowed=SERVICE_FORMATS, warnings=warnings, review_flags=review_flags),
        season=canonicalize_single_select(raw_payload.get("season"), field_name="season", allowed=SEASONS, warnings=warnings, review_flags=review_flags),
        mood_tags=raw_payload.get("mood_tags", []),
        storage_profile=raw_payload.get("storage_profile", []),
        dietary_flags=raw_payload.get("dietary_flags", []),
        provision_tags=raw_payload.get("provision_tags", []),
        sector=raw_payload.get("sector"),
        operational_class=raw_payload.get("class"),
        heat_window=raw_payload.get("heat_window"),
        total_time_minutes=raw_payload.get("total_time_minutes"),
        yield_text=raw_payload.get("yield_text"),
        uncertainty_notes=normalize_uncertainty_notes(raw_payload.get("uncertainty_notes", []), warnings=warnings, review_flags=review_flags),
        confidence_summary=raw_payload.get("confidence_summary"),
    )

    return candidate_update, candidate_extras, warnings, review_flags


def serialize_path_for_bundle(path: Path) -> str:
    from .constants import REPO_ROOT

    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())
