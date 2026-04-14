"""
Recipe similarity ranking via LM Studio.

Takes a source recipe and a list of candidate recipes from the archive,
returns them ranked by culinary similarity.
Does NOT modify anything — returns a read-only result.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from shared_prompts import get_contract, loader as _prompt_loader

from src.ai.base import AiError
from src.ai.lm_studio_client import LMStudioClient, LMStudioErrorKind


_CONTRACT = get_contract("similarity")
_SYSTEM_PROMPT = _prompt_loader.load_prompt_text(_CONTRACT)
_RESPONSE_FORMAT = _prompt_loader.build_response_format(_CONTRACT)

_REQUIRED_FIELDS = [
    "top_matches", "near_matches", "why_each_match_ranked",
    "major_difference_notes", "confidence_notes",
]


class SimilarityErrorKind(str, Enum):
    transport_failure = "transport_failure"
    parse_failure = "parse_failure"
    schema_failure = "schema_failure"


@dataclass(frozen=True)
class SimilarityError(AiError):
    kind: SimilarityErrorKind
    message: str


@dataclass
class SimilarityResult:
    payload: dict[str, Any]


def _validate_required(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["Response root is not an object."]
    return [f"Missing required field: {k}" for k in _REQUIRED_FIELDS if k not in body]


def _parse_response(content: str) -> tuple[SimilarityResult | None, SimilarityError | None]:
    try:
        body = json.loads(content)
    except json.JSONDecodeError as exc:
        return None, SimilarityError(SimilarityErrorKind.parse_failure, f"Not valid JSON: {exc}")
    errors = _validate_required(body)
    if errors:
        return None, SimilarityError(SimilarityErrorKind.schema_failure, "; ".join(errors))
    return SimilarityResult(payload=body), None


def _recipe_summary(recipe: dict[str, Any]) -> dict[str, Any]:
    """Compact recipe representation for the similarity prompt."""
    return {
        "title": recipe.get("title"),
        "dish_role": recipe.get("dish_role"),
        "primary_cuisine": recipe.get("primary_cuisine"),
        "technique_family": recipe.get("technique_family"),
        "ingredient_families": recipe.get("ingredient_families") or [],
        "complexity": recipe.get("complexity"),
        "ingredients": [
            i.get("item") for i in (recipe.get("ingredients") or []) if isinstance(i, dict)
        ],
    }


def find_similar_recipes(
    client: LMStudioClient,
    source_recipe: dict[str, Any],
    candidates: list[dict[str, Any]],
    emphasis: str | None = None,
    model: str = "",
) -> tuple[SimilarityResult | None, SimilarityError | None]:
    """
    Run the similarity contract against LM Studio.

    `source_recipe` and each item in `candidates` are plain dicts.
    `candidates` should not include the source recipe.

    Returns (SimilarityResult, None) on success or (None, SimilarityError).
    """
    envelope: dict[str, Any] = {
        "source_recipe": _recipe_summary(source_recipe),
        "candidate_recipes": [_recipe_summary(c) for c in candidates],
    }
    if emphasis:
        envelope["similarity_emphasis"] = emphasis

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(envelope, ensure_ascii=True)},
    ]
    content, transport_err = client.chat_completion(
        messages, model=model, response_format=_RESPONSE_FORMAT
    )
    if transport_err is not None:
        kind_map = {
            LMStudioErrorKind.unavailable: SimilarityErrorKind.transport_failure,
            LMStudioErrorKind.timeout: SimilarityErrorKind.transport_failure,
            LMStudioErrorKind.http_error: SimilarityErrorKind.transport_failure,
            LMStudioErrorKind.parse_error: SimilarityErrorKind.parse_failure,
            LMStudioErrorKind.no_content: SimilarityErrorKind.parse_failure,
        }
        return None, SimilarityError(
            kind=kind_map.get(transport_err.kind, SimilarityErrorKind.transport_failure),
            message=str(transport_err),
        )
    return _parse_response(content)  # type: ignore[arg-type]
