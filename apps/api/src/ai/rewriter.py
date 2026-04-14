"""
Archive-style recipe rewrite via LM Studio.

Takes an existing recipe and returns a cleaned, archive-ready version.
Does NOT modify the recipe in the database — returns a suggested rewrite only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from shared_prompts import get_contract, loader as _prompt_loader

from src.ai.base import AiError
from src.ai.lm_studio_client import LMStudioClient, LMStudioErrorKind


_CONTRACT = get_contract("rewrite")
_SYSTEM_PROMPT = _prompt_loader.load_prompt_text(_CONTRACT)
_RESPONSE_FORMAT = _prompt_loader.build_response_format(_CONTRACT)

_REQUIRED_FIELDS = [
    "title", "short_description", "ingredients", "steps",
    "recipe_notes", "service_notes", "rewrite_notes", "uncertainty_notes",
]


class RewriteErrorKind(str, Enum):
    transport_failure = "transport_failure"
    parse_failure = "parse_failure"
    schema_failure = "schema_failure"


@dataclass(frozen=True)
class RewriteError(AiError):
    kind: RewriteErrorKind
    message: str


@dataclass
class RewriteResult:
    payload: dict[str, Any]


def _validate_required(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["Response root is not an object."]
    return [f"Missing required field: {k}" for k in _REQUIRED_FIELDS if k not in body]


def _parse_response(content: str) -> tuple[RewriteResult | None, RewriteError | None]:
    try:
        body = json.loads(content)
    except json.JSONDecodeError as exc:
        return None, RewriteError(RewriteErrorKind.parse_failure, f"Not valid JSON: {exc}")
    errors = _validate_required(body)
    if errors:
        return None, RewriteError(RewriteErrorKind.schema_failure, "; ".join(errors))
    return RewriteResult(payload=body), None


def _build_recipe_envelope(recipe: dict[str, Any]) -> str:
    """Serialise the recipe fields the rewrite prompt expects."""
    ingredients = [
        {
            "quantity": i.get("quantity"),
            "unit": i.get("unit"),
            "item": i.get("item"),
            "preparation": i.get("preparation"),
            "optional": i.get("optional", False),
        }
        for i in (recipe.get("ingredients") or []) if isinstance(i, dict)
    ]
    steps = [
        {"instruction": s.get("instruction"), "time_note": s.get("time_note")}
        for s in (recipe.get("steps") or []) if isinstance(s, dict)
    ]
    envelope = {
        "title": recipe.get("title"),
        "ingredients": ingredients,
        "steps": steps,
        "notes": [n.get("content") for n in (recipe.get("notes") or []) if isinstance(n, dict)],
        "metadata": {
            k: recipe.get(k) for k in ("dish_role", "primary_cuisine", "technique_family")
        },
    }
    return json.dumps(envelope, ensure_ascii=True)


def rewrite_recipe(
    client: LMStudioClient,
    recipe: dict[str, Any],
    model: str = "",
) -> tuple[RewriteResult | None, RewriteError | None]:
    """
    Run the rewrite contract against LM Studio.

    `recipe` is a plain dict (e.g. from RecipeDetail.model_dump()).
    Returns (RewriteResult, None) on success or (None, RewriteError).
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
            LMStudioErrorKind.unavailable: RewriteErrorKind.transport_failure,
            LMStudioErrorKind.timeout: RewriteErrorKind.transport_failure,
            LMStudioErrorKind.http_error: RewriteErrorKind.transport_failure,
            LMStudioErrorKind.parse_error: RewriteErrorKind.parse_failure,
            LMStudioErrorKind.no_content: RewriteErrorKind.parse_failure,
        }
        return None, RewriteError(
            kind=kind_map.get(transport_err.kind, RewriteErrorKind.transport_failure),
            message=str(transport_err),
        )
    return _parse_response(content)  # type: ignore[arg-type]
