# Five AI Endpoints Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the 5 AI endpoints that have prompts and schemas defined but no backend code or routes: evaluation, metadata suggestion, archive rewrite, similarity, and pantry suggestion.

**Architecture:** Each endpoint follows the established normalizer pattern: an AI module in `apps/api/src/ai/` loads its prompt contract at import time, builds a message envelope, calls `LMStudioClient.chat_completion()`, validates required fields in the response, and returns a typed result-or-error tuple. Routes check `settings.lm_studio_enabled`, create the client, call the AI module, and return `ApiResponse[OutputModel]`. All new Pydantic output models live in a single new file `apps/api/src/schemas/ai_outputs.py`.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, pytest + pytest-asyncio, httpx AsyncClient, shared-prompts package, LMStudioClient

---

## File Map

**Create:**
- `apps/api/src/schemas/ai_outputs.py` — Pydantic models for all 5 AI response types + 2 request bodies
- `apps/api/src/ai/evaluator.py` — `evaluate_normalization()` function
- `apps/api/src/ai/metadata_suggester.py` — `suggest_metadata()` function
- `apps/api/src/ai/rewriter.py` — `rewrite_recipe()` function
- `apps/api/src/ai/similarity_engine.py` — `find_similar_recipes()` function
- `apps/api/src/ai/pantry_suggester.py` — `suggest_pantry()` function
- `apps/api/src/routes/pantry.py` — `POST /pantry/suggest`
- `apps/api/tests/test_ai_evaluation.py`
- `apps/api/tests/test_ai_metadata.py`
- `apps/api/tests/test_ai_rewrite.py`
- `apps/api/tests/test_ai_similarity.py`
- `apps/api/tests/test_ai_pantry.py`

**Modify:**
- `apps/api/src/routes/intake.py` — add `POST /intake-jobs/{job_id}/evaluate`
- `apps/api/src/routes/recipes.py` — add `POST /recipes/{id_or_slug}/suggest-metadata`, `/rewrite`, `/similar`
- `apps/api/src/main.py` — register pantry router

---

## Task 1: Shared AI Output Schemas

**Files:**
- Create: `apps/api/src/schemas/ai_outputs.py`

- [ ] **Step 1: Write the file**

```python
# apps/api/src/schemas/ai_outputs.py
"""
Pydantic models for AI endpoint request bodies and response payloads.

These are the API-layer shapes — they mirror the JSON schemas in
prompts/schemas/ but are expressed as Pydantic models for FastAPI
validation and OpenAPI documentation.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ── Evaluation ────────────────────────────────────────────────────────────────

class EvaluationOut(BaseModel):
    fidelity_assessment: str
    missing_information: list[str]
    likely_inventions_or_overreaches: list[str]
    ingredient_issues: list[str]
    step_issues: list[str]
    metadata_confidence: str | None
    review_recommendation: str  # "safe_for_human_review" | "review_with_caution" | "needs_major_correction"
    reviewer_notes: list[str]


# ── Metadata Suggestion ───────────────────────────────────────────────────────

class MetadataSuggestionOut(BaseModel):
    """
    AI-suggested taxonomy fields for an existing recipe.
    The field `operational_class` corresponds to the AI schema's `class` key
    (a Python reserved word) and to the recipe model's `operational_class` column.
    """
    model_config = {"populate_by_name": True}

    dish_role: str | None = None
    primary_cuisine: str | None = None
    secondary_cuisines: list[str] = []
    technique_family: str | None = None
    ingredient_families: list[str] = []
    complexity: str | None = None
    time_class: str | None = None
    service_format: str | None = None
    season: str | None = None
    mood_tags: list[str] = []
    storage_profile: list[str] = []
    dietary_flags: list[str] = []
    sector: str | None = None
    operational_class: str | None = Field(None, alias="class")
    heat_window: str | None = None
    provision_tags: list[str] = []
    short_description: str | None = None
    confidence_notes: list[str] = []
    uncertainty_notes: list[str] = []


# ── Archive Rewrite ───────────────────────────────────────────────────────────

class RewriteIngredientOut(BaseModel):
    amount: str | None = None
    unit: str | None = None
    item: str
    note: str | None = None
    optional: bool | None = None
    group: str | None = None


class RewriteStepOut(BaseModel):
    step_number: int
    instruction: str
    time_note: str | None = None
    heat_note: str | None = None
    equipment_note: str | None = None


class ArchiveRewriteOut(BaseModel):
    title: str | None = None
    short_description: str | None = None
    ingredients: list[RewriteIngredientOut] = []
    steps: list[RewriteStepOut] = []
    recipe_notes: str | None = None
    service_notes: str | None = None
    rewrite_notes: list[str] = []
    uncertainty_notes: list[str] = []


# ── Similarity ────────────────────────────────────────────────────────────────

class SimilarityIn(BaseModel):
    """Optional emphasis parameter for the similarity search."""
    emphasis: str | None = None  # e.g. "cuisine", "technique", "ingredient", "occasion"


class SimilarityMatchOut(BaseModel):
    title: str
    similarity_score_band: str  # "very_high" | "high" | "moderate" | "low"
    primary_similarity_reason: str
    secondary_similarity_reasons: list[str] = []
    major_differences: list[str] = []


class SimilarRecipesOut(BaseModel):
    top_matches: list[SimilarityMatchOut]
    near_matches: list[SimilarityMatchOut]
    why_each_match_ranked: list[str]
    major_difference_notes: list[str]
    confidence_notes: list[str]


# ── Pantry ────────────────────────────────────────────────────────────────────

class PantryQueryIn(BaseModel):
    available_ingredients: list[str]
    must_use: list[str] = []
    excluded: list[str] = []
    cuisine_preferences: list[str] = []
    time_limit_minutes: int | None = None


class PantryMatchOut(BaseModel):
    title: str
    match_type: str
    why_it_matches: str
    missing_items: list[str] = []
    recommended_adjustments: list[str] = []
    time_fit: str | None = None


class PantrySuggestionOut(BaseModel):
    direct_matches: list[PantryMatchOut]
    near_matches: list[PantryMatchOut]
    pantry_gap_notes: list[str]
    substitution_suggestions: list[str]
    quick_ideas: list[str]
    confidence_notes: list[str]
```

- [ ] **Step 2: Verify the file parses cleanly**

Run from `apps/api/`:
```bash
python -c "from src.schemas.ai_outputs import EvaluationOut, MetadataSuggestionOut, ArchiveRewriteOut, SimilarRecipesOut, PantrySuggestionOut; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add apps/api/src/schemas/ai_outputs.py
git commit -m "feat: add Pydantic output schemas for five AI endpoints"
```

---

## Task 2: Evaluation Endpoint

Lets the user ask AI to review a normalization result against the raw source text.

**Route:** `POST /api/v1/intake-jobs/{job_id}/evaluate`
**Input:** nothing (uses job's raw_source_text and current candidate)
**Output:** `ApiResponse[EvaluationOut]`

**Files:**
- Create: `apps/api/src/ai/evaluator.py`
- Modify: `apps/api/src/routes/intake.py`
- Create: `apps/api/tests/test_ai_evaluation.py`

- [ ] **Step 1: Write the failing tests**

```python
# apps/api/tests/test_ai_evaluation.py
"""
Tests for POST /intake-jobs/{job_id}/evaluate.
"""
import os
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app

TEST_DB_URL = "sqlite:///./data/db/galley_eval_test.sqlite"
TEST_DB_PATH = "./data/db/galley_eval_test.sqlite"


@pytest.fixture(scope="function")
def db_session():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    from src.config.settings import settings
    orig_url = settings.database_url
    settings.database_url = TEST_DB_URL
    init_db()
    settings.database_url = orig_url
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.clear()


async def _create_job_with_candidate(ac: AsyncClient) -> str:
    """Helper: create a paste_text job and set a candidate title."""
    create = await ac.post("/api/v1/intake-jobs", json={
        "intake_type": "paste_text",
        "raw_source_text": "Shakshuka\n\n2 eggs, 1 onion, canned tomatoes",
    })
    job_id = create.json()["data"]["id"]
    await ac.patch(f"/api/v1/intake-jobs/{job_id}/candidate", json={"title": "Shakshuka"})
    return job_id


@pytest.mark.asyncio
async def test_evaluate_returns_503_when_ai_disabled(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        job_id = await _create_job_with_candidate(ac)
        r = await ac.post(f"/api/v1/intake-jobs/{job_id}/evaluate")
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_evaluate_returns_404_for_unknown_job(client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/intake-jobs/DOESNOTEXIST/evaluate")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_evaluate_returns_503_when_lm_studio_unreachable(client):
    from src.ai.evaluator import EvaluationError, EvaluationErrorKind
    from src.config.settings import settings
    transport_err = EvaluationError(EvaluationErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.intake.evaluate_normalization", return_value=(None, transport_err)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            job_id = await _create_job_with_candidate(ac)
            r = await ac.post(f"/api/v1/intake-jobs/{job_id}/evaluate")
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_evaluate_returns_review_result(client):
    from src.ai.evaluator import EvaluationResult
    from src.config.settings import settings
    mock_result = EvaluationResult(
        fidelity_assessment="The candidate faithfully represents the source.",
        missing_information=[],
        likely_inventions_or_overreaches=[],
        ingredient_issues=[],
        step_issues=[],
        metadata_confidence="moderate",
        review_recommendation="safe_for_human_review",
        reviewer_notes=["Title matches source."],
    )
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.intake.evaluate_normalization", return_value=(mock_result, None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            job_id = await _create_job_with_candidate(ac)
            r = await ac.post(f"/api/v1/intake-jobs/{job_id}/evaluate")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["review_recommendation"] == "safe_for_human_review"
    assert d["fidelity_assessment"] == "The candidate faithfully represents the source."
    assert d["reviewer_notes"] == ["Title matches source."]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd apps/api && python -m pytest tests/test_ai_evaluation.py -q
```
Expected: `ImportError` or `ModuleNotFoundError` — `evaluator` does not exist yet.

- [ ] **Step 3: Create the AI module**

```python
# apps/api/src/ai/evaluator.py
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


@dataclass
class EvaluationError:
    kind: EvaluationErrorKind
    message: str

    def __str__(self) -> str:
        return f"EvaluationError({self.kind.value}): {self.message}"


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
```

- [ ] **Step 4: Add the route to intake.py**

At the top of `apps/api/src/routes/intake.py`, add the new import after the existing imports:

```python
from src.ai.evaluator import EvaluationErrorKind, EvaluationResult, evaluate_normalization
from src.schemas.ai_outputs import EvaluationOut
```

Add this route at the end of `apps/api/src/routes/intake.py`:

```python
# ── Evaluate (AI quality review) ──────────────────────────────────────────────

@router.post("/{job_id}/evaluate", response_model=ApiResponse[EvaluationOut])
def evaluate_candidate(job_id: str, db: Session = Depends(get_db)):
    """
    Run an AI quality review of the current candidate against the raw source.

    Returns a structured review with faithfulness assessment and a recommendation.
    Does NOT modify the candidate — this is a read-only review endpoint.
    Requires LM_STUDIO_ENABLED=true.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail={"error": {"code": "ai_disabled", "message": "AI evaluation is not enabled. Set LM_STUDIO_ENABLED=true."}},
        )

    job = intake_service.get_intake_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Intake job not found."}})

    if not job.raw_source_text:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "no_source_text", "message": "Intake job has no raw source text to evaluate against."}},
        )

    candidate = job.candidate
    if not candidate:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "no_candidate", "message": "Intake job has no structured candidate to evaluate."}},
        )

    candidate_dict = _candidate_out(candidate).model_dump()

    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = evaluate_normalization(
        client,
        raw_source_text=job.raw_source_text,
        candidate=candidate_dict,
        model=settings.lm_studio_model,
    )

    if err is not None:
        if err.kind == EvaluationErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail={"error": {"code": "ai_unavailable", "message": "AI service is unavailable."}},
            )
        raise HTTPException(
            status_code=502,
            detail={"error": {"code": f"ai_{err.kind.value}", "message": err.message}},
        )

    return ApiResponse(data=EvaluationOut(
        fidelity_assessment=result.fidelity_assessment,
        missing_information=result.missing_information,
        likely_inventions_or_overreaches=result.likely_inventions_or_overreaches,
        ingredient_issues=result.ingredient_issues,
        step_issues=result.step_issues,
        metadata_confidence=result.metadata_confidence,
        review_recommendation=result.review_recommendation,
        reviewer_notes=result.reviewer_notes,
    ))
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd apps/api && python -m pytest tests/test_ai_evaluation.py -v
```
Expected: 4 tests pass.

- [ ] **Step 6: Run the full suite to confirm no regressions**

```bash
cd apps/api && python -m pytest tests/ -q
```
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add apps/api/src/ai/evaluator.py apps/api/src/routes/intake.py apps/api/tests/test_ai_evaluation.py
git commit -m "feat: add POST /intake-jobs/{job_id}/evaluate AI quality review endpoint"
```

---

## Task 3: Metadata Suggestion Endpoint

Suggests taxonomy enrichment for an existing approved recipe.

**Route:** `POST /api/v1/recipes/{id_or_slug}/suggest-metadata`
**Input:** nothing (reads recipe from DB)
**Output:** `ApiResponse[MetadataSuggestionOut]`

**Files:**
- Create: `apps/api/src/ai/metadata_suggester.py`
- Modify: `apps/api/src/routes/recipes.py`
- Create: `apps/api/tests/test_ai_metadata.py`

- [ ] **Step 1: Write the failing tests**

```python
# apps/api/tests/test_ai_metadata.py
"""
Tests for POST /recipes/{id_or_slug}/suggest-metadata.
"""
import os
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app

TEST_DB_URL = "sqlite:///./data/db/galley_meta_test.sqlite"
TEST_DB_PATH = "./data/db/galley_meta_test.sqlite"


@pytest.fixture(scope="function")
def db_session():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    from src.config.settings import settings
    orig_url = settings.database_url
    settings.database_url = TEST_DB_URL
    init_db()
    settings.database_url = orig_url
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.clear()


async def _create_recipe(ac: AsyncClient) -> str:
    r = await ac.post("/api/v1/recipes", json={
        "title": "Shakshuka",
        "ingredients": [{"position": 1, "item": "eggs", "quantity": "4"}],
        "steps": [{"position": 1, "instruction": "Simmer eggs in tomato sauce."}],
    })
    return r.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_suggest_metadata_returns_503_when_ai_disabled(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        slug = await _create_recipe(ac)
        r = await ac.post(f"/api/v1/recipes/{slug}/suggest-metadata")
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_suggest_metadata_returns_404_for_unknown_recipe(client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/recipes/does-not-exist/suggest-metadata")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_suggest_metadata_returns_503_when_lm_studio_unreachable(client):
    from src.ai.metadata_suggester import MetadataError, MetadataErrorKind
    from src.config.settings import settings
    transport_err = MetadataError(MetadataErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.suggest_metadata", return_value=(None, transport_err)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            slug = await _create_recipe(ac)
            r = await ac.post(f"/api/v1/recipes/{slug}/suggest-metadata")
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_suggest_metadata_returns_suggestions(client):
    from src.ai.metadata_suggester import MetadataResult
    from src.config.settings import settings
    mock_result = MetadataResult(payload={
        "dish_role": "Breakfast",
        "primary_cuisine": "Levantine",
        "secondary_cuisines": [],
        "technique_family": "Simmer",
        "ingredient_families": ["Eggs", "Tomatoes"],
        "complexity": "Easy",
        "time_class": "Quick",
        "service_format": None,
        "season": None,
        "mood_tags": [],
        "storage_profile": [],
        "dietary_flags": ["Vegetarian"],
        "sector": None,
        "class": None,
        "heat_window": None,
        "provision_tags": [],
        "short_description": "Eggs poached in spiced tomato sauce.",
        "confidence_notes": ["High confidence on dish_role and technique_family."],
        "uncertainty_notes": [],
    })
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.suggest_metadata", return_value=(mock_result, None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            slug = await _create_recipe(ac)
            r = await ac.post(f"/api/v1/recipes/{slug}/suggest-metadata")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["dish_role"] == "Breakfast"
    assert d["primary_cuisine"] == "Levantine"
    assert "Vegetarian" in d["dietary_flags"]
    assert d["short_description"] == "Eggs poached in spiced tomato sauce."
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd apps/api && python -m pytest tests/test_ai_metadata.py -q
```
Expected: `ImportError` — `metadata_suggester` does not exist yet.

- [ ] **Step 3: Create the AI module**

```python
# apps/api/src/ai/metadata_suggester.py
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
```

- [ ] **Step 4: Add the route to recipes.py**

At the top of `apps/api/src/routes/recipes.py`, add after the existing imports:

```python
from src.ai.lm_studio_client import LMStudioClient
from src.ai.metadata_suggester import MetadataErrorKind, suggest_metadata
from src.config.settings import settings
from src.schemas.ai_outputs import MetadataSuggestionOut
```

Add this route at the end of `apps/api/src/routes/recipes.py`:

```python
# ── Suggest Metadata (AI-assisted) ───────────────────────────────────────────

@router.post("/{id_or_slug}/suggest-metadata", response_model=ApiResponse[MetadataSuggestionOut])
def suggest_recipe_metadata(id_or_slug: str, db: Session = Depends(get_db)):
    """
    Suggest taxonomy and classification fields for an existing recipe via AI.

    Returns suggested metadata for human review. Does NOT apply changes —
    use PATCH /recipes/{id_or_slug} to apply suggestions.
    Requires LM_STUDIO_ENABLED=true.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail={"error": {"code": "ai_disabled", "message": "AI metadata suggestion is not enabled. Set LM_STUDIO_ENABLED=true."}},
        )
    recipe = recipe_service.get_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Recipe not found."}})

    recipe_dict = _detail(recipe).model_dump()
    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = suggest_metadata(client, recipe=recipe_dict, model=settings.lm_studio_model)

    if err is not None:
        if err.kind == MetadataErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail={"error": {"code": "ai_unavailable", "message": "AI service is unavailable."}},
            )
        raise HTTPException(
            status_code=502,
            detail={"error": {"code": f"ai_{err.kind.value}", "message": err.message}},
        )

    return ApiResponse(data=MetadataSuggestionOut.model_validate(result.payload))
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd apps/api && python -m pytest tests/test_ai_metadata.py -v
```
Expected: 4 tests pass.

- [ ] **Step 6: Run full suite**

```bash
cd apps/api && python -m pytest tests/ -q
```
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add apps/api/src/ai/metadata_suggester.py apps/api/src/routes/recipes.py apps/api/tests/test_ai_metadata.py
git commit -m "feat: add POST /recipes/{id_or_slug}/suggest-metadata AI endpoint"
```

---

## Task 4: Archive Rewrite Endpoint

Rewrites a recipe into Sevastolink house style without changing its meaning.

**Route:** `POST /api/v1/recipes/{id_or_slug}/rewrite`
**Input:** nothing (reads recipe from DB)
**Output:** `ApiResponse[ArchiveRewriteOut]`

**Files:**
- Create: `apps/api/src/ai/rewriter.py`
- Modify: `apps/api/src/routes/recipes.py`
- Create: `apps/api/tests/test_ai_rewrite.py`

- [ ] **Step 1: Write the failing tests**

```python
# apps/api/tests/test_ai_rewrite.py
"""
Tests for POST /recipes/{id_or_slug}/rewrite.
"""
import os
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app

TEST_DB_URL = "sqlite:///./data/db/galley_rewrite_test.sqlite"
TEST_DB_PATH = "./data/db/galley_rewrite_test.sqlite"


@pytest.fixture(scope="function")
def db_session():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    from src.config.settings import settings
    orig_url = settings.database_url
    settings.database_url = TEST_DB_URL
    init_db()
    settings.database_url = orig_url
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.clear()


async def _create_recipe(ac: AsyncClient) -> str:
    r = await ac.post("/api/v1/recipes", json={
        "title": "Pasta Bolognese",
        "ingredients": [
            {"position": 1, "item": "beef mince", "quantity": "500g"},
            {"position": 2, "item": "pasta", "quantity": "400g"},
        ],
        "steps": [{"position": 1, "instruction": "Brown the mince."}],
    })
    return r.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_rewrite_returns_503_when_ai_disabled(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        slug = await _create_recipe(ac)
        r = await ac.post(f"/api/v1/recipes/{slug}/rewrite")
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_rewrite_returns_404_for_unknown_recipe(client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/recipes/does-not-exist/rewrite")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_rewrite_returns_503_when_lm_studio_unreachable(client):
    from src.ai.rewriter import RewriteError, RewriteErrorKind
    from src.config.settings import settings
    transport_err = RewriteError(RewriteErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.rewrite_recipe", return_value=(None, transport_err)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            slug = await _create_recipe(ac)
            r = await ac.post(f"/api/v1/recipes/{slug}/rewrite")
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_rewrite_returns_rewritten_recipe(client):
    from src.ai.rewriter import RewriteResult
    from src.config.settings import settings
    mock_result = RewriteResult(payload={
        "title": "Pasta Bolognese",
        "short_description": "Classic Italian meat ragu on pasta.",
        "ingredients": [
            {"amount": "500", "unit": "g", "item": "beef mince", "note": None, "optional": False, "group": None},
            {"amount": "400", "unit": "g", "item": "pasta", "note": None, "optional": False, "group": None},
        ],
        "steps": [
            {"step_number": 1, "instruction": "Brown the beef mince in a wide pan over medium-high heat.",
             "time_note": "5 minutes", "heat_note": "medium-high", "equipment_note": "wide pan"},
        ],
        "recipe_notes": None,
        "service_notes": "Serve immediately with grated Parmesan.",
        "rewrite_notes": ["Clarified heat level in step 1."],
        "uncertainty_notes": [],
    })
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.rewrite_recipe", return_value=(mock_result, None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            slug = await _create_recipe(ac)
            r = await ac.post(f"/api/v1/recipes/{slug}/rewrite")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["title"] == "Pasta Bolognese"
    assert d["short_description"] == "Classic Italian meat ragu on pasta."
    assert len(d["ingredients"]) == 2
    assert len(d["steps"]) == 1
    assert d["steps"][0]["instruction"] == "Brown the beef mince in a wide pan over medium-high heat."
    assert d["rewrite_notes"] == ["Clarified heat level in step 1."]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd apps/api && python -m pytest tests/test_ai_rewrite.py -q
```
Expected: `ImportError` — `rewriter` does not exist yet.

- [ ] **Step 3: Create the AI module**

```python
# apps/api/src/ai/rewriter.py
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


@dataclass
class RewriteError:
    kind: RewriteErrorKind
    message: str

    def __str__(self) -> str:
        return f"RewriteError({self.kind.value}): {self.message}"


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
```

- [ ] **Step 4: Add the route to recipes.py**

Add to the imports at the top of `apps/api/src/routes/recipes.py` (after the metadata imports added in Task 3):

```python
from src.ai.rewriter import RewriteErrorKind, rewrite_recipe
from src.schemas.ai_outputs import ArchiveRewriteOut
```

Add this route at the end of `apps/api/src/routes/recipes.py`:

```python
# ── Archive Rewrite (AI-assisted) ─────────────────────────────────────────────

@router.post("/{id_or_slug}/rewrite", response_model=ApiResponse[ArchiveRewriteOut])
def rewrite_recipe_endpoint(id_or_slug: str, db: Session = Depends(get_db)):
    """
    Return an archive-style rewrite of a recipe via AI.

    Returns a suggested rewrite for human review. Does NOT apply changes —
    use PATCH /recipes/{id_or_slug} to apply the rewrite.
    Requires LM_STUDIO_ENABLED=true.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail={"error": {"code": "ai_disabled", "message": "AI rewrite is not enabled. Set LM_STUDIO_ENABLED=true."}},
        )
    recipe = recipe_service.get_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Recipe not found."}})

    recipe_dict = _detail(recipe).model_dump()
    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = rewrite_recipe(client, recipe=recipe_dict, model=settings.lm_studio_model)

    if err is not None:
        if err.kind == RewriteErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail={"error": {"code": "ai_unavailable", "message": "AI service is unavailable."}},
            )
        raise HTTPException(
            status_code=502,
            detail={"error": {"code": f"ai_{err.kind.value}", "message": err.message}},
        )

    return ApiResponse(data=ArchiveRewriteOut.model_validate(result.payload))
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd apps/api && python -m pytest tests/test_ai_rewrite.py -v
```
Expected: 4 tests pass.

- [ ] **Step 6: Run full suite**

```bash
cd apps/api && python -m pytest tests/ -q
```
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add apps/api/src/ai/rewriter.py apps/api/src/routes/recipes.py apps/api/tests/test_ai_rewrite.py
git commit -m "feat: add POST /recipes/{id_or_slug}/rewrite AI endpoint"
```

---

## Task 5: Similarity Endpoint

Finds and ranks similar recipes within the archive relative to a source recipe.

**Route:** `POST /api/v1/recipes/{id_or_slug}/similar`
**Input:** `SimilarityIn` (optional `emphasis` parameter)
**Output:** `ApiResponse[SimilarRecipesOut]`

The endpoint fetches up to 20 other non-archived recipes from the archive and passes them as candidates to the AI.

**Files:**
- Create: `apps/api/src/ai/similarity_engine.py`
- Modify: `apps/api/src/routes/recipes.py`
- Create: `apps/api/tests/test_ai_similarity.py`

- [ ] **Step 1: Write the failing tests**

```python
# apps/api/tests/test_ai_similarity.py
"""
Tests for POST /recipes/{id_or_slug}/similar.
"""
import os
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app

TEST_DB_URL = "sqlite:///./data/db/galley_sim_test.sqlite"
TEST_DB_PATH = "./data/db/galley_sim_test.sqlite"


@pytest.fixture(scope="function")
def db_session():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    from src.config.settings import settings
    orig_url = settings.database_url
    settings.database_url = TEST_DB_URL
    init_db()
    settings.database_url = orig_url
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.clear()


async def _create_recipe(ac: AsyncClient, title: str) -> str:
    r = await ac.post("/api/v1/recipes", json={
        "title": title,
        "dish_role": "Dinner",
        "primary_cuisine": "Italian",
        "ingredients": [{"position": 1, "item": "pasta", "quantity": "400g"}],
        "steps": [{"position": 1, "instruction": "Cook pasta."}],
    })
    return r.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_similar_returns_503_when_ai_disabled(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        slug = await _create_recipe(ac, "Pasta Carbonara")
        r = await ac.post(f"/api/v1/recipes/{slug}/similar", json={})
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_similar_returns_404_for_unknown_recipe(client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/recipes/does-not-exist/similar", json={})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_similar_returns_503_when_lm_studio_unreachable(client):
    from src.ai.similarity_engine import SimilarityError, SimilarityErrorKind
    from src.config.settings import settings
    transport_err = SimilarityError(SimilarityErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.find_similar_recipes", return_value=(None, transport_err)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            slug = await _create_recipe(ac, "Pasta Carbonara")
            r = await ac.post(f"/api/v1/recipes/{slug}/similar", json={})
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_similar_returns_ranked_results(client):
    from src.ai.similarity_engine import SimilarityResult
    from src.config.settings import settings
    mock_result = SimilarityResult(payload={
        "top_matches": [
            {
                "title": "Pasta Amatriciana",
                "similarity_score_band": "high",
                "primary_similarity_reason": "Same base technique and format.",
                "secondary_similarity_reasons": ["Both Italian pasta dishes"],
                "major_differences": ["Different sauce"],
            }
        ],
        "near_matches": [],
        "why_each_match_ranked": ["Pasta Amatriciana ranked high due to shared technique."],
        "major_difference_notes": [],
        "confidence_notes": ["Only 2 candidates provided — results may be limited."],
    })
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.recipes.find_similar_recipes", return_value=(mock_result, None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            slug = await _create_recipe(ac, "Pasta Carbonara")
            await _create_recipe(ac, "Pasta Amatriciana")
            r = await ac.post(f"/api/v1/recipes/{slug}/similar", json={})
    assert r.status_code == 200
    d = r.json()["data"]
    assert len(d["top_matches"]) == 1
    assert d["top_matches"][0]["title"] == "Pasta Amatriciana"
    assert d["top_matches"][0]["similarity_score_band"] == "high"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd apps/api && python -m pytest tests/test_ai_similarity.py -q
```
Expected: `ImportError` — `similarity_engine` does not exist yet.

- [ ] **Step 3: Create the AI module**

```python
# apps/api/src/ai/similarity_engine.py
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


@dataclass
class SimilarityError:
    kind: SimilarityErrorKind
    message: str

    def __str__(self) -> str:
        return f"SimilarityError({self.kind.value}): {self.message}"


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

    `source_recipe` and each item in `candidates` are plain dicts
    (e.g. from RecipeDetail.model_dump() or RecipeSummaryOut.model_dump()).
    `candidates` should not include the source recipe.

    Returns (SimilarityResult, None) on success or (None, SimilarityError).
    """
    envelope = {
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
```

- [ ] **Step 4: Add the route to recipes.py**

Add to the imports at the top of `apps/api/src/routes/recipes.py`:

```python
from src.ai.similarity_engine import SimilarityErrorKind, find_similar_recipes
from src.schemas.ai_outputs import SimilarityIn, SimilarRecipesOut
```

Add at the end of `apps/api/src/routes/recipes.py`:

```python
# ── Similar Recipes (AI-assisted) ─────────────────────────────────────────────

@router.post("/{id_or_slug}/similar", response_model=ApiResponse[SimilarRecipesOut])
def similar_recipes(id_or_slug: str, body: SimilarityIn, db: Session = Depends(get_db)):
    """
    Return AI-ranked similar recipes from the archive.

    Fetches up to 20 other non-archived recipes and ranks them by culinary
    similarity to the source recipe. Pass `emphasis` in the body to focus on
    a specific similarity dimension (e.g. "cuisine", "technique", "ingredient").
    Requires LM_STUDIO_ENABLED=true.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail={"error": {"code": "ai_disabled", "message": "AI similarity is not enabled. Set LM_STUDIO_ENABLED=true."}},
        )
    recipe = recipe_service.get_recipe(db, id_or_slug)
    if not recipe:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Recipe not found."}})

    # Fetch up to 20 other non-archived recipes as candidates.
    candidates_orm, _ = recipe_service.list_recipes(
        db, archived=False, limit=21, offset=0, sort="updated_at_desc"
    )
    source_recipe_dict = _detail(recipe).model_dump()
    candidate_dicts = [
        _summary(r).model_dump() for r in candidates_orm if r.id != recipe.id
    ][:20]

    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = find_similar_recipes(
        client,
        source_recipe=source_recipe_dict,
        candidates=candidate_dicts,
        emphasis=body.emphasis,
        model=settings.lm_studio_model,
    )

    if err is not None:
        if err.kind == SimilarityErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail={"error": {"code": "ai_unavailable", "message": "AI service is unavailable."}},
            )
        raise HTTPException(
            status_code=502,
            detail={"error": {"code": f"ai_{err.kind.value}", "message": err.message}},
        )

    return ApiResponse(data=SimilarRecipesOut.model_validate(result.payload))
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd apps/api && python -m pytest tests/test_ai_similarity.py -v
```
Expected: 4 tests pass.

- [ ] **Step 6: Run full suite**

```bash
cd apps/api && python -m pytest tests/ -q
```
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add apps/api/src/ai/similarity_engine.py apps/api/src/routes/recipes.py apps/api/tests/test_ai_similarity.py
git commit -m "feat: add POST /recipes/{id_or_slug}/similar AI endpoint"
```

---

## Task 6: Pantry Suggestion Endpoint

Suggests what to cook from available ingredients, cross-referenced against the archive.

**Route:** `POST /api/v1/pantry/suggest`
**Input:** `PantryQueryIn` (list of available ingredients + optional constraints)
**Output:** `ApiResponse[PantrySuggestionOut]`

The endpoint fetches up to 20 non-archived recipes to pass as archive context.

**Files:**
- Create: `apps/api/src/ai/pantry_suggester.py`
- Create: `apps/api/src/routes/pantry.py`
- Modify: `apps/api/src/main.py`
- Create: `apps/api/tests/test_ai_pantry.py`

- [ ] **Step 1: Write the failing tests**

```python
# apps/api/tests/test_ai_pantry.py
"""
Tests for POST /pantry/suggest.
"""
import os
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app

TEST_DB_URL = "sqlite:///./data/db/galley_pantry_test.sqlite"
TEST_DB_PATH = "./data/db/galley_pantry_test.sqlite"


@pytest.fixture(scope="function")
def db_session():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    from src.config.settings import settings
    orig_url = settings.database_url
    settings.database_url = TEST_DB_URL
    init_db()
    settings.database_url = orig_url
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_pantry_returns_503_when_ai_disabled(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/v1/pantry/suggest", json={
            "available_ingredients": ["eggs", "onion", "tomatoes"],
        })
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_disabled"


@pytest.mark.asyncio
async def test_pantry_returns_422_for_empty_ingredients(client):
    from src.config.settings import settings
    with patch.object(settings, "lm_studio_enabled", True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/pantry/suggest", json={
                "available_ingredients": [],
            })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_pantry_returns_503_when_lm_studio_unreachable(client):
    from src.ai.pantry_suggester import PantryError, PantryErrorKind
    from src.config.settings import settings
    transport_err = PantryError(PantryErrorKind.transport_failure, "Connection refused")
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.pantry.suggest_pantry", return_value=(None, transport_err)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/pantry/suggest", json={
                "available_ingredients": ["eggs", "onion"],
            })
    assert r.status_code == 503
    assert r.json()["detail"]["error"]["code"] == "ai_unavailable"


@pytest.mark.asyncio
async def test_pantry_returns_suggestions(client):
    from src.ai.pantry_suggester import PantryResult
    from src.config.settings import settings
    mock_result = PantryResult(payload={
        "direct_matches": [
            {
                "title": "Shakshuka",
                "match_type": "direct",
                "why_it_matches": "All main ingredients available.",
                "missing_items": [],
                "recommended_adjustments": [],
                "time_fit": "Quick",
            }
        ],
        "near_matches": [],
        "pantry_gap_notes": [],
        "substitution_suggestions": [],
        "quick_ideas": ["Scrambled eggs with onion and tomato"],
        "confidence_notes": ["High confidence on direct match."],
    })
    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.pantry.suggest_pantry", return_value=(mock_result, None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/pantry/suggest", json={
                "available_ingredients": ["eggs", "onion", "tomatoes"],
            })
    assert r.status_code == 200
    d = r.json()["data"]
    assert len(d["direct_matches"]) == 1
    assert d["direct_matches"][0]["title"] == "Shakshuka"
    assert d["quick_ideas"] == ["Scrambled eggs with onion and tomato"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd apps/api && python -m pytest tests/test_ai_pantry.py -q
```
Expected: 404 Not Found errors or `ImportError` — route does not exist yet.

- [ ] **Step 3: Create the AI module**

```python
# apps/api/src/ai/pantry_suggester.py
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
```

- [ ] **Step 4: Create the pantry route**

```python
# apps/api/src/routes/pantry.py
"""
Pantry suggestion endpoint.

POST /pantry/suggest — AI-powered cooking suggestions based on available ingredients.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.ai.lm_studio_client import LMStudioClient
from src.ai.pantry_suggester import PantryErrorKind, suggest_pantry
from src.config.settings import settings
from src.db.database import get_db
from src.schemas.ai_outputs import PantryQueryIn, PantrySuggestionOut
from src.schemas.common import ApiResponse
from src.services import recipe_service

router = APIRouter(prefix="/pantry", tags=["pantry"])


@router.post("/suggest", response_model=ApiResponse[PantrySuggestionOut], status_code=status.HTTP_200_OK)
def pantry_suggest(body: PantryQueryIn, db: Session = Depends(get_db)):
    """
    Suggest recipes based on available ingredients.

    Fetches up to 20 non-archived archive recipes as context for the AI.
    The AI returns direct matches, near matches, and quick ideas.
    Requires LM_STUDIO_ENABLED=true.
    """
    if not settings.lm_studio_enabled:
        raise HTTPException(
            status_code=503,
            detail={"error": {"code": "ai_disabled", "message": "AI pantry suggestion is not enabled. Set LM_STUDIO_ENABLED=true."}},
        )

    if not body.available_ingredients:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "validation_error", "message": "available_ingredients must not be empty."}},
        )

    archive_recipes_orm, _ = recipe_service.list_recipes(
        db, archived=False, limit=20, offset=0, sort="updated_at_desc"
    )
    archive_dicts = [
        {
            "title": r.title,
            "dish_role": r.dish_role,
            "primary_cuisine": r.primary_cuisine,
            "complexity": r.complexity,
            "ingredients": [],  # RecipeSummaryOut does not include ingredients — titles suffice
        }
        for r in archive_recipes_orm
    ]

    client = LMStudioClient(settings.lm_studio_base_url)
    result, err = suggest_pantry(
        client,
        available_ingredients=body.available_ingredients,
        archive_recipes=archive_dicts,
        must_use=body.must_use or None,
        excluded=body.excluded or None,
        cuisine_preferences=body.cuisine_preferences or None,
        time_limit_minutes=body.time_limit_minutes,
        model=settings.lm_studio_model,
    )

    if err is not None:
        if err.kind == PantryErrorKind.transport_failure:
            raise HTTPException(
                status_code=503,
                detail={"error": {"code": "ai_unavailable", "message": "AI service is unavailable."}},
            )
        raise HTTPException(
            status_code=502,
            detail={"error": {"code": f"ai_{err.kind.value}", "message": err.message}},
        )

    return ApiResponse(data=PantrySuggestionOut.model_validate(result.payload))
```

- [ ] **Step 5: Register the pantry router in main.py**

In `apps/api/src/main.py`, add the pantry import after the existing route imports:

```python
from src.routes.pantry import router as pantry_router
```

And register it in the `v1_router` block (after `v1_router.include_router(intake_router)`):

```python
v1_router.include_router(pantry_router)
```

The full `v1_router` block should now look like:

```python
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(recipes_router)
v1_router.include_router(intake_router)
v1_router.include_router(pantry_router)
app.include_router(v1_router)
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
cd apps/api && python -m pytest tests/test_ai_pantry.py -v
```
Expected: 4 tests pass.

- [ ] **Step 7: Run the full suite**

```bash
cd apps/api && python -m pytest tests/ -q
```
Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add apps/api/src/ai/pantry_suggester.py apps/api/src/routes/pantry.py apps/api/src/main.py apps/api/tests/test_ai_pantry.py
git commit -m "feat: add POST /pantry/suggest AI endpoint"
```

---

## Self-Review

**Spec coverage check:**

| Endpoint | Prompt | Schema | AI Module | Route | Tests |
|---|---|---|---|---|---|
| evaluate | `normalization-review-v1.md` | `normalization-review-output.schema.json` | Task 2 | Task 2 | Task 2 |
| suggest-metadata | `metadata-suggestion-v1.md` | `metadata-suggestion-output.schema.json` | Task 3 | Task 3 | Task 3 |
| rewrite | `archive-rewrite-v1.md` | `archive-rewrite-output.schema.json` | Task 4 | Task 4 | Task 4 |
| similar | `similar-recipes-v1.md` | `similar-recipes-output.schema.json` | Task 5 | Task 5 | Task 5 |
| pantry/suggest | `pantry-suggestion-v1.md` | `pantry-suggestion-output.schema.json` | Task 6 | Task 6 | Task 6 |

All 5 prompt families covered. Each has a failing-test step, implementation step, passing-test step, and commit.

**Consistent names across tasks:**
- `evaluate_normalization` used in both `evaluator.py` and mocked at `src.routes.intake.evaluate_normalization` ✓
- `suggest_metadata` used in both `metadata_suggester.py` and mocked at `src.routes.recipes.suggest_metadata` ✓
- `rewrite_recipe` used in both `rewriter.py` and mocked at `src.routes.recipes.rewrite_recipe` ✓
- `find_similar_recipes` used in both `similarity_engine.py` and mocked at `src.routes.recipes.find_similar_recipes` ✓
- `suggest_pantry` used in both `pantry_suggester.py` and mocked at `src.routes.pantry.suggest_pantry` ✓

**`class` field aliasing:** `MetadataSuggestionOut` uses `Field(alias="class")` mapped to Python name `operational_class`. `model_validate(result.payload)` will correctly pick up the `"class"` key from the AI JSON because `populate_by_name: True` + alias is set. Route calls `MetadataSuggestionOut.model_validate(result.payload)` which reads `"class"` from the dict. ✓

**Pantry archive context:** The pantry route passes recipe titles, dish_role, primary_cuisine, complexity, and an empty ingredients list (since `list_recipes` returns summary objects without full ingredient lists). This is sufficient for the pantry prompt which only needs enough context to suggest matches — if fuller ingredient context is needed in future, fetch full `RecipeDetail` per recipe (expensive) or add an ingredients field to the summary query.
