"""
Recipe normalization via LM Studio.

Builds the normalization prompt contract (v1.0.0), calls the LM Studio
client, validates the response against the contract schema, and maps the
result to a CandidateUpdate suitable for intake_service.update_candidate().

Error taxonomy (maps to prompt-contracts.md §14):
  transport_failure  — LM Studio unreachable / timeout / HTTP error
  parse_failure      — response is not JSON
  schema_failure     — required top-level keys missing or wrong result_type
  taxonomy_failure   — single-select field not in allowed vocabulary
  partial_success    — some fields missing but data block is otherwise usable
  empty_result       — data block present but all fields are null / empty
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from shared_prompts import get_contract, loader as _prompt_loader

from src.ai.base import AiError
from src.ai.lm_studio_client import LMStudioClient, LMStudioError, LMStudioErrorKind
from src.schemas.intake import CandidateUpdate
from src.schemas.recipe import IngredientIn, StepIn
from src.schemas.taxonomy import DISH_ROLES, PRIMARY_CUISINES, TECHNIQUE_FAMILIES

# ── Contract constants ─────────────────────────────────────────────────────────

CONTRACT_NAME = "recipe_normalization"
CONTRACT_VERSION = "1.0.0"

# ── Error model ────────────────────────────────────────────────────────────────

class NormalizationErrorKind(str, Enum):
    transport_failure = "transport_failure"
    parse_failure = "parse_failure"
    schema_failure = "schema_failure"
    taxonomy_failure = "taxonomy_failure"
    partial_success = "partial_success"
    empty_result = "empty_result"


@dataclass(frozen=True)
class NormalizationError(AiError):
    kind: NormalizationErrorKind
    message: str
    warnings: list[str] = field(default_factory=list)


@dataclass
class NormalizationResult:
    candidate_update: CandidateUpdate
    ambiguities: list[str]
    warnings: list[str]
    source_language: str | None = None


# ── Prompt / schema loading ───────────────────────────────────────────────────

_NORMALIZATION_CONTRACT = get_contract("normalization")
_SYSTEM_PROMPT = _prompt_loader.load_prompt_text(_NORMALIZATION_CONTRACT)
_OUTPUT_SCHEMA = _prompt_loader.load_schema(_NORMALIZATION_CONTRACT)
_RESPONSE_FORMAT = _prompt_loader.build_response_format(_NORMALIZATION_CONTRACT)


def build_normalization_prompt(raw_text: str, source_notes: str | None = None) -> list[dict[str, str]]:
    """Build the chat messages list for the normalization contract."""

    envelope = {
        "contract_name": CONTRACT_NAME,
        "contract_version": CONTRACT_VERSION,
        "raw_source_text": raw_text.strip(),
        "source_type": "paste_text",
        "source_url": None,
        "user_notes": source_notes,
        "allowed_taxonomy": {
            "dish_role": sorted(DISH_ROLES),
            "primary_cuisine": sorted(PRIMARY_CUISINES),
            "technique_family": sorted(TECHNIQUE_FAMILIES),
        },
    }

    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(envelope, ensure_ascii=True, indent=2)},
    ]


# ── Response parser and validator ─────────────────────────────────────────────

def _validate_taxonomy(
    value: Any, allowed: list[str], field_name: str, warnings: list[str]
) -> str | None:
    """Return the value if it's in allowed, null if None/empty, and add warning if unrecognised."""
    if value is None or value == "":
        return None
    if isinstance(value, str) and value in allowed:
        return value
    # Try case-insensitive match
    lower = value.lower() if isinstance(value, str) else ""
    for option in allowed:
        if option.lower() == lower:
            return option
    warnings.append(f"{field_name} value {value!r} not in allowed vocabulary — set to null")
    return None


def _parse_ingredients(raw: Any, warnings: list[str]) -> list[IngredientIn]:
    if not isinstance(raw, list):
        warnings.append("ingredients field is not an array — skipped")
        return []
    result: list[IngredientIn] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            warnings.append(f"ingredients[{i}] is not an object — skipped")
            continue
        item_text = item.get("item", "")
        if not isinstance(item_text, str) or not item_text.strip():
            warnings.append(f"ingredients[{i}] has empty item — skipped")
            continue
        result.append(
            IngredientIn(
                position=i + 1,
                item=item_text.strip(),
                quantity=item.get("quantity") or None,
                unit=item.get("unit") or None,
                preparation=item.get("preparation") or None,
                optional=bool(item.get("optional", False)),
            )
        )
    return result


def _validate_payload_shape(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Response root is not an object."]

    for key in _OUTPUT_SCHEMA.get("required", []):
        if key not in payload:
            errors.append(f"Missing required field: {key}")

    if payload.get("output_language") != "en":
        errors.append("Field output_language must be 'en'.")

    if "ingredients" in payload and not isinstance(payload["ingredients"], list):
        errors.append("Field ingredients is not an array.")
    if "steps" in payload and not isinstance(payload["steps"], list):
        errors.append("Field steps is not an array.")
    if "uncertainty_notes" in payload and not isinstance(payload["uncertainty_notes"], list):
        errors.append("Field uncertainty_notes is not an array.")

    return errors


def _parse_steps(raw: Any, warnings: list[str]) -> list[StepIn]:
    if not isinstance(raw, list):
        warnings.append("steps field is not an array — skipped")
        return []
    result: list[StepIn] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            warnings.append(f"steps[{i}] is not an object — skipped")
            continue
        instruction = item.get("instruction", "")
        if not isinstance(instruction, str) or not instruction.strip():
            warnings.append(f"steps[{i}] has empty instruction — skipped")
            continue
        position = item.get("position", i + 1)
        if not isinstance(position, int) or position < 1:
            position = i + 1
        result.append(
            StepIn(
                position=position,
                instruction=instruction.strip(),
                time_note=item.get("time_note") or None,
                equipment_note=item.get("equipment_note") or None,
            )
        )
    return result


def _parse_response(
    content: str,
) -> tuple[NormalizationResult | None, NormalizationError | None]:
    """Parse and validate the model's raw string response."""
    warnings: list[str] = []

    # 1. Parse JSON
    try:
        body = json.loads(content)
    except json.JSONDecodeError as exc:
        return None, NormalizationError(
            NormalizationErrorKind.parse_failure,
            f"Response is not valid JSON: {exc}",
        )

    # 2. Top-level schema check
    validation_errors = _validate_payload_shape(body)
    if validation_errors:
        return None, NormalizationError(
            NormalizationErrorKind.schema_failure,
            "; ".join(validation_errors),
        )

    # 3. Extract and validate fields
    title = body.get("title")
    if not isinstance(title, str) or not title.strip():
        title = None

    ingredients = _parse_ingredients(body.get("ingredients", []), warnings)
    steps = _parse_steps(body.get("steps", []), warnings)

    def safe_int(val: Any, field: str) -> int | None:
        if val is None:
            return None
        try:
            result = int(val)
            if result < 0:
                warnings.append(f"{field} is negative — set to null")
                return None
            return result
        except (TypeError, ValueError):
            warnings.append(f"{field} is not an integer — set to null")
            return None

    prep_time = safe_int(body.get("prep_time_minutes"), "prep_time_minutes")
    cook_time = safe_int(body.get("cook_time_minutes"), "cook_time_minutes")

    servings_raw = body.get("servings")
    servings = str(servings_raw).strip() if servings_raw is not None and str(servings_raw).strip() else None

    dish_role = _validate_taxonomy(body.get("dish_role"), DISH_ROLES, "dish_role", warnings)
    primary_cuisine = _validate_taxonomy(
        body.get("primary_cuisine"), PRIMARY_CUISINES, "primary_cuisine", warnings
    )
    technique_family = _validate_taxonomy(
        body.get("technique_family"), TECHNIQUE_FAMILIES, "technique_family", warnings
    )

    notes = body.get("recipe_notes")
    if not isinstance(notes, str) or not notes.strip():
        notes = None

    source_credit = None

    uncertainty_notes = body.get("uncertainty_notes", [])
    ambiguities = [a for a in uncertainty_notes if isinstance(a, str) and a.strip()]

    source_language = body.get("source_language")
    if source_language is not None and not isinstance(source_language, str):
        warnings.append("source_language is not a string — set to null")
        source_language = None

    candidate_update = CandidateUpdate(
        title=title,
        short_description=body.get("short_description") if isinstance(body.get("short_description"), str) else None,
        prep_time_minutes=prep_time,
        cook_time_minutes=cook_time,
        servings=servings,
        dish_role=dish_role,
        primary_cuisine=primary_cuisine,
        technique_family=technique_family,
        complexity=body.get("complexity") if isinstance(body.get("complexity"), str) else None,
        time_class=body.get("time_class") if isinstance(body.get("time_class"), str) else None,
        notes=notes,
        service_notes=body.get("service_notes") if isinstance(body.get("service_notes"), str) else None,
        source_credit=source_credit,
        ingredients=ingredients if ingredients else None,
        steps=steps if steps else None,
    )

    # 4. Detect empty result
    all_null = (
        title is None
        and not ingredients
        and not steps
        and prep_time is None
        and cook_time is None
    )
    if all_null:
        return None, NormalizationError(
            NormalizationErrorKind.empty_result,
            "AI returned no usable content. Review source and continue manually.",
            warnings=warnings,
        )

    return NormalizationResult(
        candidate_update=candidate_update,
        ambiguities=ambiguities,
        warnings=warnings,
        source_language=source_language,
    ), None


# ── Public entry point ────────────────────────────────────────────────────────

def normalize_recipe(
    client: LMStudioClient,
    raw_text: str,
    source_notes: str | None = None,
    model: str = "",
) -> tuple[NormalizationResult | None, NormalizationError | None]:
    """
    Run the normalization contract against LM Studio.

    Returns (NormalizationResult, None) on success, or (None, NormalizationError).
    If LM Studio is unavailable, returns a transport_failure error — callers
    should surface this as a degraded-mode notice and allow manual entry.
    """
    messages = build_normalization_prompt(raw_text, source_notes)

    content, transport_err = client.chat_completion(
        messages,
        model=model,
        response_format=_RESPONSE_FORMAT,
    )
    if transport_err is not None:
        kind_map = {
            LMStudioErrorKind.unavailable: NormalizationErrorKind.transport_failure,
            LMStudioErrorKind.timeout: NormalizationErrorKind.transport_failure,
            LMStudioErrorKind.http_error: NormalizationErrorKind.transport_failure,
            LMStudioErrorKind.parse_error: NormalizationErrorKind.parse_failure,
            LMStudioErrorKind.no_content: NormalizationErrorKind.empty_result,
        }
        return None, NormalizationError(
            kind=kind_map.get(transport_err.kind, NormalizationErrorKind.transport_failure),
            message=str(transport_err),
        )

    return _parse_response(content)  # type: ignore[arg-type]
