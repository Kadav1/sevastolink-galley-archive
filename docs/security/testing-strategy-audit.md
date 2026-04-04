# Testing Strategy Audit — Sevastolink Galley Archive

**Date:** 2026-04-01
**Scope:** `apps/api/tests/` (96 test functions across 13 test files) + `apps/web/` frontend
**Auditor role:** Test automation engineer

---

## Executive Summary

The backend test suite has solid breadth across the happy-path API surface and acceptable AI-module error handling. The patterns are consistent and the test doubles are applied correctly at the module-import level (matching the mock-path rules in CLAUDE.md). However, several structural problems undermine the suite's reliability and security signal:

- **Fixture fragmentation**: 10 of 13 test files define their own `db_session` + `client` fixtures with a fixed SQLite path, creating a persistent parallel-corruption risk that the new `async_client` conftest fixture was designed to fix — but only 1 of 13 files uses it.
- **Zero frontend test coverage**: no test runner, no test framework, no test files.
- **Four prior-phase security gaps remain untested** (path traversal, FTS5 injection, CORS, batch exception leakage).
- **Pantry ingredient pass-through is structurally untestable** in the current mock layout — the mock bypasses the route's deliberate ingredient elision.
- **`get_recipe()` commits on every read** and no test asserts that mutation paths (archive, update, set_favorite) do not double-commit.

---

## 1. Fixture Quality and Isolation

### 1.1 Fixed-path SQLite — parallel corruption risk (High)

**Files:** `test_recipes.py` (L17), `test_intake.py` (L17), `test_media.py` (L20), `test_error_envelope.py` (L21), `test_ai_evaluation.py` (L15), `test_ai_metadata.py` (L15), `test_ai_pantry.py` (L15), `test_ai_rewrite.py` (L15), `test_ai_similarity.py` (L15), `test_settings.py` (L14)

Every one of these files declares a module-level constant such as:

```python
TEST_DB_URL = "sqlite:///./data/db/galley_intake_test.sqlite"
```

Ten separate SQLite paths are hardcoded to `./data/db/`. Running `pytest` with `-j2` (or any parallel runner) will cause `sqlite3.OperationalError: disk I/O error` because multiple workers compete on the same file — a risk explicitly documented in CLAUDE.md. The `conftest.py` `async_client` fixture solves this by using `tmp_path`, but it is only adopted by `test_batch_intake.py`. The remaining 10 files still use the legacy pattern.

**Recommendation:** Migrate all test files to the `async_client` conftest fixture. The migration is straightforward — replace the local `db_session` + `client` pair with `async_client: AsyncClient` and adjust any direct ORM assertions to use a separate `async_client`-compatible session.

### 1.2 `client` fixture yields `None`, not the HTTP client (Medium)

**File:** `test_recipes.py`, L47–55; `test_intake.py`, L43–49; repeated in 8 files.

The `client` fixture (function scope) overrides `get_db` and then `yield`s with no value — it yields `None`. Every test that receives `client` then ignores it and creates its own `AsyncClient` via a local `async with await _client() as c:` call. This means the DB override is active but the client fixture provides no value. If a test omits the `client` parameter (or a new contributor writes `async with await _client() as c:` without declaring `client`), the DB override will silently not be present and the test will use the production DB path or fail with a missing table error.

**Recommendation:** The `async_client` conftest pattern eliminates this entirely. For tests that legitimately need direct ORM access alongside HTTP calls, add a `db_session` parameter to `async_client` so both are available from the same isolated engine.

### 1.3 `db_session` is reused across HTTP calls in multi-step tests (Medium)

**File:** `test_media.py`, `test_intake.py`

The `client` fixture yields the same `db_session` object to both the test body (for ORM asserts) and the `get_db` override. SQLAlchemy session state is not thread-safe. In tests that issue multiple HTTP requests, each FastAPI handler refreshes/commits via the same session object that the test body holds open. This works in practice because tests are single-threaded, but a refresh inside a handler can invalidate the test body's ORM objects, causing subtle assertion failures that appear intermittent.

---

## 2. Test Coverage Gaps

### 2.1 Untested endpoints (Medium)

The following route handlers have no dedicated test:

| Endpoint | Route file | Notes |
|---|---|---|
| `POST /recipes/{slug}/favorite` | `recipes.py` L150 | Only `favorite=False` creation is tested, not the explicit toggle action |
| `POST /recipes/{slug}/unfavorite` | `recipes.py` L158 | Untested |
| `POST /recipes/{slug}/unarchive` | `recipes.py` L136 | Untested — archive is tested but unarchive is not |
| `GET /recipes/ingredient-families` | `recipes.py` L37 | Untested |
| Pagination (`limit`, `offset`) | `recipes.py` L64 | `limit` default is asserted in L97 of `test_recipes.py` but limit/offset paging is not exercised |
| Unknown `sort` value falls back to `updated_at_desc` | `recipe_service.py` L308 | `sort_map.get(sort, Recipe.updated_at.desc())` silent fallback is untested |
| `GET /intake-jobs` list endpoint | — | No list-jobs test (if this endpoint exists); only create + get-by-id is tested |
| `POST /intake-jobs/{id}/normalize` with `manual` intake type (no source text) | `intake.py` L169–173 | 422 `no_source_text` path is untested |
| `POST /intake-jobs/{id}/evaluate` with no candidate | `intake.py` L263–267 | 422 `no_candidate` path is untested |
| Normalize 502 fallback (non-transport AI error) | `intake.py` L191–193 | Only transport failure and success are tested; `parse_failure`/`schema_failure` → 502 path is not |

### 2.2 Verification state trust boundary — AI cannot set it (High)

**CLAUDE.md** states: "AI cannot set or modify verification state. This boundary must be enforced at the API layer." There is no test that sends a `verification_state` field through any AI-assisted endpoint and asserts it is ignored or rejected. The `suggest-metadata` endpoint returns `MetadataSuggestionOut` which does not include `verification_state`, but there is no test that explicitly verifies this is absent from the response, nor that a PATCH using AI suggestions cannot sneakily set the state.

**Recommended test:**
```python
async def test_suggest_metadata_does_not_include_verification_state(async_client):
    # Create recipe, mock AI returning a result with a "verification_state" field
    # injected into the payload, assert it is absent from MetadataSuggestionOut
    ...
    assert "verification_state" not in r.json()["data"]
```

### 2.3 `get_recipe()` commits on every read — mutation paths double-commit (Medium)

**Source:** `recipe_service.py` L185–197. `get_recipe()` sets `last_viewed_at` and calls `db.commit()` unconditionally. Every write operation (`update_recipe`, `archive_recipe`, `unarchive_recipe`, `set_favorite`, `delete_recipe`) calls `get_recipe()` internally, meaning every mutation does at minimum two commits. No test verifies:

1. That `last_viewed_at` is updated only on `GET /{slug}` calls, not on mutations.
2. That the double-commit on mutation paths does not cause observable side effects (e.g., incorrect `updated_at` timestamps on the response vs. the DB row, or FTS sync happening with a stale state).

**Recommended test:**
```python
async def test_last_viewed_at_updated_only_on_get(async_client):
    r1 = await async_client.post("/api/v1/recipes", json=MINIMAL_RECIPE)
    slug = r1.json()["data"]["slug"]
    before_patch = r1.json()["data"].get("last_viewed_at")
    # PATCH should not change last_viewed_at
    r2 = await async_client.patch(f"/api/v1/recipes/{slug}", json={"rating": 3})
    assert r2.json()["data"].get("last_viewed_at") == before_patch
    # GET should change last_viewed_at
    r3 = await async_client.get(f"/api/v1/recipes/{slug}")
    assert r3.json()["data"].get("last_viewed_at") != before_patch
```

### 2.4 Slug generation edge cases (Low)

`test_slug_collision` in `test_recipes.py` (L216) covers the counter-suffix path. Missing cases:

- Title with only special characters (falls back to `"recipe"` slug — `slugify.py` L12).
- Title with Unicode characters (Arabic, Cyrillic) — `re.sub(r"[^a-z0-9\s-]", "", s)` strips all non-ASCII silently.
- Very long title (no length cap exists in `slugify()`).

### 2.5 `ingredient_family` filter (Low)

`list_recipes` has an `ingredient_family` filter that uses a raw SQL subquery with `json_each()` (L286–296 of `recipe_service.py`). No test in `test_recipes.py` exercises this filter. The `GET /recipes/ingredient-families` facet count endpoint is also completely untested.

---

## 3. Security Test Gaps

### 3.1 Path traversal on file serve (Critical)

**Source:** `media.py` L91 / `media_service.py` L64.

The `relative_path` stored in `media_assets` is built during upload as `f"{subdirectory}/{asset_id}{ext}"` (controlled path). However, the file-serve route at `GET /media-assets/{asset_id}/file` reads `asset.relative_path` from the DB and passes it directly to `settings.media_dir / asset.relative_path` without verifying the resolved path stays within `media_dir`. If a `relative_path` value like `../../etc/passwd` were ever stored in the DB (e.g., via a compromised DB migration, a future bug, or a crafted test), the `FileResponse` would serve arbitrary files.

More critically: `Path.__truediv__` on `Path("/data/media") / "../../etc/passwd"` resolves to `/etc/passwd` — Python's pathlib does not sanitise traversal sequences on the right-hand side. The current code offers no containment check.

**Recommended test (and the missing validation code it should exercise):**
```python
# In media_service.py, _save_file or serve_media_file should assert:
#   file_path.resolve().is_relative_to(settings.media_dir.resolve())

async def test_serve_media_file_traversal_blocked(async_client, db_session):
    # Directly insert a MediaAsset with a malicious relative_path
    from src.models.media import MediaAsset
    bad_asset = MediaAsset(
        id="test-bad",
        asset_kind="source_image",
        mime_type="image/png",
        relative_path="../../etc/passwd",
        checksum="x",
        byte_size=1,
    )
    db_session.add(bad_asset)
    db_session.commit()
    r = await async_client.get("/api/v1/media-assets/test-bad/file")
    # Must be 404 or 403, not 200 serving /etc/passwd
    assert r.status_code in (403, 404)
```

Until `is_relative_to()` is added to `serve_media_file`, this test will fail — which is the point.

### 3.2 FTS5 special character injection (High)

**Source:** `recipe_service.py` L242–249.

The FTS5 query is executed as:

```python
db.execute(
    text("SELECT recipe_id FROM recipe_search_fts WHERE recipe_search_fts MATCH :q ORDER BY rank"),
    {"q": q},
)
```

The `:q` binding prevents SQL injection, but FTS5's `MATCH` syntax has its own query language. Inputs like `shakshuka*`, `NOT shakshuka`, `"shakshuka" OR "bolognese"`, or the syntactically invalid `AND OR` will either silently succeed, return unexpected results, or raise a SQLite `OperationalError` that propagates as an unhandled 500. No test sends any FTS5 special characters. The 500-path is entirely untested.

**Recommended tests:**
```python
@pytest.mark.parametrize("q", [
    "shakshuka*",         # FTS5 prefix operator — should not 500
    '"eggs benedict"',    # phrase query — should match or return empty
    "AND OR",             # invalid FTS5 syntax — should return 400, not 500
    "sha* NOT oil",       # boolean operator
    "",                   # empty string — should not crash
])
async def test_fts_special_chars_do_not_500(async_client, q):
    r = await async_client.get("/api/v1/recipes", params={"q": q})
    assert r.status_code != 500
```

Note: the fix should wrap the FTS5 query in a try/except and translate `OperationalError` to a 400 `bad_query` error, then the test above can assert `r.status_code in (200, 400)`.

### 3.3 CORS policy is too narrow for declared use case (Medium)

**Source:** `main.py` L91–95.

The CORS policy hardcodes `allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]`. CLAUDE.md states the app is accessible "over the home network" and the example `LM_STUDIO_BASE_URL` uses `http://192.168.1.91:1234/v1`. A browser on the same network hitting the API from a different host (e.g., a tablet at `http://192.168.1.50:3000`) will be blocked by CORS preflight. No test verifies CORS headers at all — neither for the allowed origins nor for the rejection of disallowed ones.

**Recommended tests:**
```python
async def test_cors_allows_localhost(async_client):
    r = await async_client.options(
        "/api/v1/recipes",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" in r.headers
    assert r.headers["access-control-allow-origin"] == "http://localhost:3000"

async def test_cors_blocks_arbitrary_origin(async_client):
    r = await async_client.get(
        "/api/v1/recipes",
        headers={"Origin": "http://evil.example.com"},
    )
    assert r.headers.get("access-control-allow-origin") != "http://evil.example.com"
```

The CORS policy itself likely needs a settings-driven `ALLOWED_ORIGINS` list (defaulting to `localhost:3000`) to support the home-network use case.

### 3.4 Batch exception message leakage (Medium)

**Source:** `intake.py` L111–112.

```python
except Exception as exc:
    errors.append(BatchIntakeJobError(index=idx, message=str(exc)))
```

`str(exc)` on an unhandled `Exception` may expose internal Python stack details, SQLAlchemy internal error messages, or file system paths. `test_batch_intake.py::test_batch_create_partial_failure` (L32) verifies the `errors[0]["index"] == 1` field but does not assert that `errors[0]["message"]` is sanitised (i.e., does not contain an internal traceback or file path).

**Recommended test:**
```python
async def test_batch_error_message_is_sanitised(async_client):
    payload = {
        "jobs": [
            {"intake_type": "paste_text"},  # missing raw_source_text
        ]
    }
    resp = await async_client.post("/api/v1/intake-jobs/batch", json=payload)
    err_msg = resp.json()["data"]["errors"][0]["message"]
    # Must not contain Python internals
    assert "Traceback" not in err_msg
    assert "File /" not in err_msg
    assert "sqlalchemy" not in err_msg.lower()
    # Should be a short human-readable message
    assert len(err_msg) < 300
```

### 3.5 Settings write protection — `ai_enabled` must be read-only (Medium)

**Source:** `settings.py` (route) / `settings_service.py`.

CLAUDE.md states "`ai_enabled` in the settings response is read-only". The `SettingsUpdate` schema presumably excludes `ai_enabled`, but no test attempts to write it and asserts the attempt is rejected or ignored. A client sending `{"ai_enabled": true}` should not change `LM_STUDIO_ENABLED`.

**Recommended test:**
```python
async def test_patch_ai_enabled_is_ignored(async_client):
    r = await async_client.patch("/api/v1/settings", json={"ai_enabled": True})
    # Should either ignore the field (200 with ai_enabled unchanged) or reject with 422
    assert r.status_code in (200, 422)
    if r.status_code == 200:
        # The actual value must reflect the environment, not the request
        assert r.json()["data"]["ai_enabled"] == False  # tests run with AI disabled
```

---

## 4. Functional Correctness Gaps

### 4.1 Pantry route sends empty ingredient lists to the AI (High)

**Source:** `pantry.py` L44–51.

```python
archive_dicts = [
    {
        "title": r.title,
        "dish_role": r.dish_role,
        "primary_cuisine": r.primary_cuisine,
        "complexity": r.complexity,
        "ingredients": [],          # <-- hardcoded empty list
    }
    for r in archive_recipes_orm
]
```

The archive recipes are fetched from the DB (including ingredient data) but their `ingredients` field is always set to `[]`. The `pantry_suggester._recipe_for_pantry()` function (L66–76 of `pantry_suggester.py`) is capable of extracting ingredient items from a dict, but it never receives them. The AI gets no ingredient context for archive recipes, which directly degrades the quality of pantry suggestions.

The existing test `test_pantry_returns_suggestions` (L85) mocks `suggest_pantry` at the route boundary, so it cannot detect this bug. The mock replaces the entire function call, bypassing the argument-construction logic in `pantry.py`.

**Recommended test** (tests the actual call arguments, not just the response):
```python
from unittest.mock import patch, call

async def test_pantry_passes_ingredient_data_to_ai(async_client):
    # Create a recipe with known ingredients
    await async_client.post("/api/v1/recipes", json={
        "title": "Test Recipe",
        "ingredients": [
            {"position": 1, "item": "eggs", "quantity": "4"},
            {"position": 2, "item": "butter", "quantity": "50g"},
        ],
        "steps": [{"position": 1, "instruction": "Cook."}],
    })

    from src.config.settings import settings
    from src.ai.pantry_suggester import PantryResult
    mock_result = PantryResult(payload={
        "direct_matches": [], "near_matches": [], "pantry_gap_notes": [],
        "substitution_suggestions": [], "quick_ideas": [], "confidence_notes": [],
    })

    with patch.object(settings, "lm_studio_enabled", True), \
         patch("src.routes.pantry.suggest_pantry", return_value=(mock_result, None)) as mock_fn:
        await async_client.post("/api/v1/pantry/suggest", json={
            "available_ingredients": ["eggs", "butter"],
        })

    call_kwargs = mock_fn.call_args
    archive_recipes_arg = call_kwargs[1]["archive_recipes"]  # or positional index
    assert len(archive_recipes_arg) > 0
    first_recipe = archive_recipes_arg[0]
    # This will currently FAIL — ingredients is []
    assert first_recipe["ingredients"] != []
    assert "eggs" in first_recipe["ingredients"]
```

This test documents the bug and will pass once the fix is applied (reading `r.ingredients` instead of hardcoding `[]`).

### 4.2 `update_recipe` calls `get_recipe()` which commits before the update (Medium)

**Source:** `recipe_service.py` L315–375. `update_recipe` calls `get_recipe()` at L316, which sets `last_viewed_at` and commits. The update then proceeds on the same session. This means every PATCH results in two commits with different `last_viewed_at` values (the first from `get_recipe`, the second from `update_recipe`). The final DB state is correct, but the `last_viewed_at` field on a PATCHed record will reflect the time of the PATCH, not the time of the last genuine view — a semantic bug. No test asserts the `last_viewed_at` value after a PATCH.

---

## 5. Test Quality Issues

### 5.1 Tests are behaviour-oriented but over-rely on mocks at the wrong boundary (Medium)

All AI endpoint tests (5 files, 20 tests) mock `suggest_pantry`, `normalize_recipe`, etc. at the route level (`src.routes.<module>.<function>`). This is correct per CLAUDE.md and exercises the route error-handling logic. However, the AI modules themselves (`src/ai/*.py`) have zero unit tests. The internal parsing logic (`_parse_response`, `_validate_required`, `_recipe_for_pantry`) is only exercised if an integration test actually calls LM Studio, which never happens in CI.

A set of pure unit tests for the AI module parsing logic would be low-cost and high-value:

```python
# Example: tests/test_unit_pantry_parser.py
from src.ai.pantry_suggester import _parse_response, _validate_required

def test_parse_response_valid_json():
    valid = '{"direct_matches":[],"near_matches":[],"pantry_gap_notes":[],' \
            '"substitution_suggestions":[],"quick_ideas":[],"confidence_notes":[]}'
    result, err = _parse_response(valid)
    assert err is None
    assert result is not None

def test_parse_response_missing_field():
    partial = '{"direct_matches":[]}'
    result, err = _parse_response(partial)
    assert err is not None
    assert "near_matches" in err.message

def test_parse_response_invalid_json():
    result, err = _parse_response("not json {")
    assert err is not None
    assert err.kind.value == "parse_failure"
```

### 5.2 Error envelope tests use legacy fixture pattern (Low)

**File:** `test_error_envelope.py` L24–55.

This file defines its own `db_session` and `client` fixtures (using the fixed-path DB pattern) despite being the file most likely to be run in isolation to verify the error contract. It should be the first file migrated to `async_client`.

### 5.3 `test_get_recipe_by_slug` does not assert full response shape (Low)

**File:** `test_recipes.py` L117–121.

The test only asserts `slug == "shakshuka"`. It does not verify that `ingredients`, `steps`, `source`, or `verification_state` are present and correctly shaped. A regression in `RecipeDetail.from_orm_recipe()` could silently omit sub-resources.

### 5.4 `test_health_degraded_when_db_unreachable` mocks a private function (Low)

**File:** `test_health.py` L25.

```python
with patch("src.routes.health._db_ok", return_value=False):
```

`_db_ok` is a module-private helper. Testing through the private name is fragile; if it is renamed, the patch silently does nothing. Mock at the SQLAlchemy engine level or wrap `_db_ok` in a dependency for cleaner substitution.

---

## 6. Test Pyramid Assessment

| Layer | Count | Notes |
|---|---|---|
| Unit (pure function, no DB, no HTTP) | ~11 | `test_prompt_registry.py` only; no unit tests for `slugify`, `ids`, `pantry_suggester._parse_response`, etc. |
| Integration (HTTP + real DB) | ~85 | Dominant tier — good breadth but limited depth |
| E2E / contract | 0 | No Playwright/Cypress tests; no contract tests against the OpenAPI schema |

The pyramid is inverted at the bottom: the unit layer is thin. Moving AI parsing logic into unit-testable functions and adding a small suite of pure unit tests would increase confidence in the parsing layer without adding DB or HTTP overhead.

---

## 7. Frontend Test Coverage

**Coverage: zero.**

`apps/web/package.json` has no test script, no test framework dependency (Vitest, Jest, Playwright, Cypress), and no test files exist under `apps/web/src/`. TypeScript type-checking (`npm run type-check`) is the only automated quality gate.

Given the UI implements non-trivial logic — the `useFavorite` hook's cache invalidation, `useSettings` preference loading, the Kitchen Mode scale factor, the intake hub state machine — the absence of any frontend tests is a significant gap.

**Priority additions:**

| Priority | Area | Recommended tool |
|---|---|---|
| High | `useFavorite` / `useSettings` hooks (cache invalidation, error states) | Vitest + React Testing Library |
| High | Intake hub form validation (paste_text requires raw_source) | Vitest + React Testing Library |
| Medium | `scaleStepText()` in `lib/scaling.ts` — pure function, easily unit-tested | Vitest |
| Medium | `slugify` equivalence (frontend slug generation must match backend) | Vitest |
| Low | Library page filter behaviour (multi-select, URL state) | Playwright |
| Low | Kitchen Mode accessible font scaling at viewport extremes | Playwright |

Minimum viable setup: add `vitest` + `@testing-library/react` + `@testing-library/user-event` as dev dependencies, configure `vite.config.ts` with `test: { environment: "jsdom" }`, and add `"test": "vitest run"` to package scripts.

---

## 8. Prioritised Findings Summary

| # | Severity | Finding | File(s) |
|---|---|---|---|
| 1 | Critical | Path traversal on `GET /media-assets/{id}/file` — no `is_relative_to()` check, no test | `media.py` L91, `media_service.py` L64 |
| 2 | High | FTS5 special character injection → unhandled 500 — zero tests for special chars | `recipe_service.py` L242 |
| 3 | High | Pantry route hardcodes `"ingredients": []` — bug invisible to current mocks | `pantry.py` L50 |
| 4 | High | Verification state AI boundary has no enforcement test | `recipes.py` L176–209 |
| 5 | High | 10 of 13 test files use fixed-path SQLite — parallel corruption risk | All legacy test files |
| 6 | Medium | CORS policy excludes home-network origins; no CORS headers tested | `main.py` L91 |
| 7 | Medium | Batch exception leakage — `str(exc)` not sanitised; test doesn't assert message content | `intake.py` L112, `test_batch_intake.py` L46 |
| 8 | Medium | `get_recipe()` commits on read — `last_viewed_at` polluted on all mutations, untested | `recipe_service.py` L194 |
| 9 | Medium | `ai_enabled` write protection untested | `settings.py` |
| 10 | Medium | Unarchive, unfavorite, favorite toggle, ingredient-families endpoints untested | `recipes.py` L136–162, L37 |
| 11 | Medium | AI module parsing logic (`_parse_response`, `_validate_required`) has no unit tests | `src/ai/*.py` |
| 12 | Medium | Zero frontend test coverage — no framework configured | `apps/web/` |
| 13 | Low | `client` fixture yields `None` — structural smell, easy to misuse | All legacy test files |
| 14 | Low | FTS5 prefix and boolean query behaviour untested | `recipe_service.py` L242 |
| 15 | Low | Slug edge cases (Unicode, all-special-chars, very long) untested | `slugify.py` |
| 16 | Low | `_db_ok` private function mocked by name — fragile patch target | `test_health.py` L25 |
