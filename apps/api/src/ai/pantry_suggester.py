"""
Pantry-based cooking suggestions via LM Studio.

Takes a list of available ingredients and optional archive recipe context,
returns direct matches, near matches, and quick ideas.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from shared_prompts import get_contract, loader as _prompt_loader

from src.ai.lm_studio_client import LMStudioClient, LMStudioErrorKind


_CONTRACT = get_contract("pantry")
_SYSTEM_PROMPT = _prompt_loader.load_prompt_text(_CONTRACT)
_RESPONSE_FORMAT = _prompt_loader.build_response_format(_CONTRACT)

_REQUIRED_FIELDS = [
    "direct_matches", "near_matches", "pantry_gap_notes",
    "substitution_suggestions", "quick_ideas", "confidence_notes",
]


class PantryErrorKind(str, Enum):
    transport_failure = "transport_failure"
    parse_failure = "parse_failure"
    schema_failure = "schema_failure"


@dataclass
class PantryError:
    kind: PantryErrorKind
    message: str

    def __str__(self) -> str:
        return f"PantryError({self.kind.value}): {self.message}"


@dataclass
class PantryResult:
    payload: dict[str, Any]


def _validate_required(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["Response root is not an object."]
    return [f"Missing required field: {k}" for k in _REQUIRED_FIELDS if k not in body]


def _parse_response(content: str) -> tuple[PantryResult | None, PantryError | None]:
    try:
        body = json.loads(content)
    except json.JSONDecodeError as exc:
        return None, PantryError(PantryErrorKind.parse_failure, f"Not valid JSON: {exc}")
    errors = _validate_required(body)
    if errors:
        return None, PantryError(PantryErrorKind.schema_failure, "; ".join(errors))
    return PantryResult(payload=body), None


def _recipe_for_pantry(recipe: dict[str, Any]) -> dict[str, Any]:
    """Compact representation for pantry prompt context."""
    return {
        "title": recipe.get("title"),
        "dish_role": recipe.get("dish_role"),
        "primary_cuisine": recipe.get("primary_cuisine"),
        "complexity": recipe.get("complexity"),
        "ingredients": [
            i.get("item") for i in (recipe.get("ingredients") or []) if isinstance(i, dict)
        ],
    }


def suggest_pantry(
    client: LMStudioClient,
    available_ingredients: list[str],
    archive_recipes: list[dict[str, Any]],
    must_use: list[str] | None = None,
    excluded: list[str] | None = None,
    cuisine_preferences: list[str] | None = None,
    time_limit_minutes: int | None = None,
    model: str = "",
) -> tuple[PantryResult | None, PantryError | None]:
    """
    Run the pantry contract against LM Studio.

    `archive_recipes` is a list of plain dicts from the archive (used as context).
    Returns (PantryResult, None) on success or (None, PantryError).
    """
    envelope: dict[str, Any] = {
        "available_ingredients": available_ingredients,
        "candidate_recipes": [_recipe_for_pantry(r) for r in archive_recipes],
    }
    if must_use:
        envelope["must_use_ingredients"] = must_use
    if excluded:
        envelope["excluded_ingredients"] = excluded
    if cuisine_preferences:
        envelope["cuisine_preferences"] = cuisine_preferences
    if time_limit_minutes is not None:
        envelope["time_limit_minutes"] = time_limit_minutes

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(envelope, ensure_ascii=True)},
    ]
    content, transport_err = client.chat_completion(
        messages, model=model, response_format=_RESPONSE_FORMAT
    )
    if transport_err is not None:
        kind_map = {
            LMStudioErrorKind.unavailable: PantryErrorKind.transport_failure,
            LMStudioErrorKind.timeout: PantryErrorKind.transport_failure,
            LMStudioErrorKind.http_error: PantryErrorKind.transport_failure,
            LMStudioErrorKind.parse_error: PantryErrorKind.parse_failure,
            LMStudioErrorKind.no_content: PantryErrorKind.parse_failure,
        }
        return None, PantryError(
            kind=kind_map.get(transport_err.kind, PantryErrorKind.transport_failure),
            message=str(transport_err),
        )
    return _parse_response(content)  # type: ignore[arg-type]
