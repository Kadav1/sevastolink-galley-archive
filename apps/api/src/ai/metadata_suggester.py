"""
Metadata enrichment suggestions via LM Studio.

Takes an existing recipe and suggests taxonomy and classification fields.
Does NOT modify the recipe — returns suggestions only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from shared_prompts import get_contract, loader as _prompt_loader

from src.ai.lm_studio_client import LMStudioClient, LMStudioErrorKind


_CONTRACT = get_contract("metadata")
_SYSTEM_PROMPT = _prompt_loader.load_prompt_text(_CONTRACT)
_RESPONSE_FORMAT = _prompt_loader.build_response_format(_CONTRACT)

_REQUIRED_FIELDS = [
    "dish_role", "primary_cuisine", "secondary_cuisines", "technique_family",
    "ingredient_families", "complexity", "time_class", "service_format",
    "season", "mood_tags", "storage_profile", "dietary_flags", "sector",
    "class", "heat_window", "provision_tags", "short_description",
    "confidence_notes", "uncertainty_notes",
]


class MetadataErrorKind(str, Enum):
    transport_failure = "transport_failure"
    parse_failure = "parse_failure"
    schema_failure = "schema_failure"


@dataclass
class MetadataError:
    kind: MetadataErrorKind
    message: str

    def __str__(self) -> str:
        return f"MetadataError({self.kind.value}): {self.message}"


@dataclass
class MetadataResult:
    """Holds the raw validated payload dict from the AI."""
    payload: dict[str, Any]


def _validate_required(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["Response root is not an object."]
    return [f"Missing required field: {k}" for k in _REQUIRED_FIELDS if k not in body]


def _parse_response(content: str) -> tuple[MetadataResult | None, MetadataError | None]:
    try:
        body = json.loads(content)
    except json.JSONDecodeError as exc:
        return None, MetadataError(MetadataErrorKind.parse_failure, f"Not valid JSON: {exc}")
    errors = _validate_required(body)
    if errors:
        return None, MetadataError(MetadataErrorKind.schema_failure, "; ".join(errors))
    return MetadataResult(payload=body), None


def _build_recipe_envelope(recipe: dict[str, Any]) -> str:
    """Serialise relevant recipe fields for the metadata prompt."""
    ingredients = [
        i.get("item", "") for i in (recipe.get("ingredients") or [])
        if isinstance(i, dict)
    ]
    steps = [
        s.get("instruction", "") for s in (recipe.get("steps") or [])
        if isinstance(s, dict)
    ]
    envelope = {
        "title": recipe.get("title"),
        "short_description": recipe.get("short_description"),
        "ingredients": ingredients,
        "steps": steps,
        "notes": [n.get("content") for n in (recipe.get("notes") or []) if isinstance(n, dict)],
        "existing_metadata": {
            k: recipe.get(k) for k in (
                "dish_role", "primary_cuisine", "technique_family",
                "complexity", "time_class", "dietary_flags",
            )
        },
    }
    return json.dumps(envelope, ensure_ascii=True)


def suggest_metadata(
    client: LMStudioClient,
    recipe: dict[str, Any],
    model: str = "",
) -> tuple[MetadataResult | None, MetadataError | None]:
    """
    Run the metadata contract against LM Studio.

    `recipe` is a plain dict (e.g. from RecipeDetail.model_dump()).
    Returns (MetadataResult, None) on success or (None, MetadataError).
    """
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_recipe_envelope(recipe)},
    ]
    content, transport_err = client.chat_completion(
        messages, model=model, response_format=_RESPONSE_FORMAT
    )
    if transport_err is not None:
        kind_map = {
            LMStudioErrorKind.unavailable: MetadataErrorKind.transport_failure,
            LMStudioErrorKind.timeout: MetadataErrorKind.transport_failure,
            LMStudioErrorKind.http_error: MetadataErrorKind.transport_failure,
            LMStudioErrorKind.parse_error: MetadataErrorKind.parse_failure,
            LMStudioErrorKind.no_content: MetadataErrorKind.parse_failure,
        }
        return None, MetadataError(
            kind=kind_map.get(transport_err.kind, MetadataErrorKind.transport_failure),
            message=str(transport_err),
        )
    return _parse_response(content)  # type: ignore[arg-type]
