"""
Normalization quality evaluation via LM Studio.

Takes the intake job's raw source text and the current structured candidate,
asks the model to assess faithfulness, completeness, and review readiness.
Does NOT modify anything — returns a review result only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from shared_prompts import get_contract, loader as _prompt_loader

from src.ai.base import AiError
from src.ai.lm_studio_client import LMStudioClient, LMStudioErrorKind


# ── Contract loading ──────────────────────────────────────────────────────────

_CONTRACT = get_contract("evaluation")
_SYSTEM_PROMPT = _prompt_loader.load_prompt_text(_CONTRACT)
_RESPONSE_FORMAT = _prompt_loader.build_response_format(_CONTRACT)

_REQUIRED_FIELDS = [
    "fidelity_assessment",
    "missing_information",
    "likely_inventions_or_overreaches",
    "ingredient_issues",
    "step_issues",
    "metadata_confidence",
    "review_recommendation",
    "reviewer_notes",
]


# ── Error model ───────────────────────────────────────────────────────────────

class EvaluationErrorKind(str, Enum):
    transport_failure = "transport_failure"
    parse_failure = "parse_failure"
    schema_failure = "schema_failure"


@dataclass(frozen=True)
class EvaluationError(AiError):
    kind: EvaluationErrorKind
    message: str


# ── Result model ──────────────────────────────────────────────────────────────

@dataclass
class EvaluationResult:
    fidelity_assessment: str
    missing_information: list[str]
    likely_inventions_or_overreaches: list[str]
    ingredient_issues: list[str]
    step_issues: list[str]
    metadata_confidence: str | None
    review_recommendation: str
    reviewer_notes: list[str]


# ── Internal helpers ──────────────────────────────────────────────────────────

def _validate_required(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["Response root is not an object."]
    return [f"Missing required field: {k}" for k in _REQUIRED_FIELDS if k not in body]


def _parse_response(content: str) -> tuple[EvaluationResult | None, EvaluationError | None]:
    try:
        body = json.loads(content)
    except json.JSONDecodeError as exc:
        return None, EvaluationError(EvaluationErrorKind.parse_failure, f"Not valid JSON: {exc}")

    errors = _validate_required(body)
    if errors:
        return None, EvaluationError(EvaluationErrorKind.schema_failure, "; ".join(errors))

    return EvaluationResult(
        fidelity_assessment=body["fidelity_assessment"],
        missing_information=body.get("missing_information") or [],
        likely_inventions_or_overreaches=body.get("likely_inventions_or_overreaches") or [],
        ingredient_issues=body.get("ingredient_issues") or [],
        step_issues=body.get("step_issues") or [],
        metadata_confidence=body.get("metadata_confidence"),
        review_recommendation=body["review_recommendation"],
        reviewer_notes=body.get("reviewer_notes") or [],
    ), None


# ── Public entry point ────────────────────────────────────────────────────────

def evaluate_normalization(
    client: LMStudioClient,
    raw_source_text: str,
    candidate: dict[str, Any],
    model: str = "",
) -> tuple[EvaluationResult | None, EvaluationError | None]:
    """
    Run the evaluation contract against LM Studio.

    `candidate` is a plain dict representation of the structured candidate
    (e.g. from CandidateOut.model_dump()).

    Returns (EvaluationResult, None) on success or (None, EvaluationError).
    """
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps({
            "raw_source_text": raw_source_text,
            "normalized_candidate_json": candidate,
        }, ensure_ascii=True)},
    ]
    content, transport_err = client.chat_completion(
        messages, model=model, response_format=_RESPONSE_FORMAT
    )
    if transport_err is not None:
        kind_map = {
            LMStudioErrorKind.unavailable: EvaluationErrorKind.transport_failure,
            LMStudioErrorKind.timeout: EvaluationErrorKind.transport_failure,
            LMStudioErrorKind.http_error: EvaluationErrorKind.transport_failure,
            LMStudioErrorKind.parse_error: EvaluationErrorKind.parse_failure,
            LMStudioErrorKind.no_content: EvaluationErrorKind.parse_failure,
        }
        return None, EvaluationError(
            kind=kind_map.get(transport_err.kind, EvaluationErrorKind.transport_failure),
            message=str(transport_err),
        )
    return _parse_response(content)  # type: ignore[arg-type]
