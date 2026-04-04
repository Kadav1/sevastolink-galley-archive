# Phase 3: Testing & Documentation Review

## Test Coverage Findings

### Critical

**T-C1 — Path Traversal Untested** (`tests/test_media.py`)
`serve_media_file` constructs a file path from `asset.relative_path` with no containment guard, and no test exercises this with a malicious path. A DB row with `relative_path = "../../etc/passwd"` would serve arbitrary files silently.

Recommended test:
```python
async def test_serve_media_rejects_path_traversal(client):
    # Insert a media asset row with a crafted relative_path
    # Then GET /api/v1/media/{id}/file and assert 403
```

**T-C2 — FTS5 Injection Path Untested** (`tests/test_recipes.py`)
No test sends FTS5 special characters (`AND`, `OR`, `"`, `*`, `NEAR(`) in the `q` search parameter. Currently propagates as an unhandled 500.

```python
async def test_search_fts_special_chars_returns_400_not_500(client):
    for bad_q in ["AND", '"unclosed', "NEAR(chicken", "*"]:
        r = await c.get("/api/v1/recipes", params={"q": bad_q})
        assert r.status_code in (200, 400)  # not 500
        assert r.status_code != 500
```

### High

**T-H1 — Fixture Fragmentation: 10 of 13 Test Files Use Fixed-Path SQLite DBs**
Only `test_batch_intake.py` uses the shared `async_client` fixture from `conftest.py` (which uses `tmp_path` for a parallel-safe isolated DB). The other 10 files each roll their own fixed-path DB setup (`galley_test.sqlite`, `galley_recipes_test.sqlite`, etc.). This causes:
- Parallel pytest runs corrupt each other's DBs (`sqlite3.OperationalError: disk I/O error`)
- Boilerplate duplicated 10× in setup/teardown
- Each file's fixture is subtly different

All test files should migrate to the `async_client` fixture from `conftest.py`.

**T-H2 — Pantry AI Call Never Receives Recipe Ingredients**
`routes/pantry.py:50` hardcodes `"ingredients": []` in the archive context. The test mocks `suggest_pantry` at the route level, bypassing this — the mock always receives empty ingredients and passes. No test asserts `mock_fn.call_args` to verify ingredient content was forwarded.

```python
async def test_pantry_passes_ingredients_to_ai(client):
    # Create a recipe with known ingredients
    # Call pantry suggest
    # Assert mock was called with non-empty ingredient lists
    assert any(len(r["ingredients"]) > 0 for r in call_args["archive_recipes"])
```

**T-H3 — Verification State Trust Boundary Untested**
No test verifies that AI endpoints (`/suggest-metadata`, `/normalize`) cannot set or modify `verification_state`. This is a core architectural constraint (CLAUDE.md: "AI cannot set or modify verification state").

```python
async def test_suggest_metadata_cannot_modify_verification_state(client):
    # Create a Verified recipe
    # Call suggest-metadata with a mock that returns verification_state in payload
    # Assert recipe.verification_state is unchanged after apply
```

**T-H4 — Zero Frontend Test Coverage**
No Vitest unit tests, no Playwright E2E tests, no test script in `apps/web/package.json`. The entire React application — 8 pages, 20+ components, 5 custom hooks, 6 API modules — is untested. Critical paths like the intake approval flow, recipe edit, archive confirmation, and AI metadata apply have no automated coverage.

**T-H5 — `unarchive`, `set_favorite`, `ingredient_family` Filter, and `GET /ingredient-families` Untested**
`tests/test_recipes.py` tests `archive_recipe` but not `unarchive_recipe`. `set_favorite` / `unfavorite` have no tests. `GET /api/v1/recipes/ingredient-families` has no test. `ingredient_family` query parameter filter has no test.

### Medium

**T-M1 — CORS Policy Untested**
No test sends a cross-origin request or verifies `Access-Control-Allow-Origin` headers. The LAN access use case (the product's primary deployment target) has no coverage.

**T-M2 — Batch Error Messages Not Sanitised in Tests** (`tests/test_batch_intake.py:test_batch_create_partial_failure`)
The test verifies `error["index"]` but not that `error["message"]` is sanitised (i.e., doesn't contain raw Python exception internals). `str(exc)` is currently serialised directly.

**T-M3 — `last_viewed_at` Side Effect Not Verified**
No test asserts that `last_viewed_at` is NOT updated when `update_recipe`, `archive_recipe`, or `delete_recipe` is called. The current bug (every mutation path double-commits `last_viewed_at`) is invisible in the test suite.

**T-M4 — AI Module `_parse_response` and `_validate_required` Have No Unit Tests**
All 6 AI modules have their parsing logic tested only end-to-end via mocked HTTP calls. There are no unit tests for `_parse_response()` or `_validate_required()` with malformed payloads (missing required fields, wrong types, extra fields, null values).

**T-M5 — Media Upload Size Limit Not Boundary-Tested**
`test_media.py` tests happy-path PNG and PDF uploads. No test sends a payload at exactly `MAX_BYTES`, one byte over, or zero bytes. The chunked-read fix (once applied) needs boundary tests.

**T-M6 — Slug Uniqueness Edge Cases Untested**
No tests for Unicode titles (e.g., "Crème Brûlée"), all-special-character titles (e.g., "!!!"), empty-after-slugify titles, or 50-item batch imports with duplicate titles.

### Low

**T-L1** — `client` fixture `yield`s `None` in 10 files — the `client` parameter in test functions is always `None`; tests create their own `AsyncClient` internally. The fixture is used only for its `app.dependency_overrides` side effect. This is confusing and was the source of a prior bug.
**T-L2** — `test_health.py` mocks `_db_ok` by patching `src.routes.health._db_ok` — private name, fragile if function is renamed.
**T-L3** — No test for the `GET /api/v1/settings` default values matching the spec (only patch tests exist).
**T-L4** — No test verifies the `BACKUP_INFO.txt` manifest format produced by `backup.sh`.
**T-L5** — No test for `repair_candidates.py` FIELD_MAPS transformations (the script has no automated test at all).

---

## Documentation Findings

### Critical

**D-C1 — CORS Blocks LAN Access, Undocumented Everywhere**
`main.py` restricts CORS to `localhost:3000` only. The product brief, technical architecture, local deployment doc, and nginx config all describe LAN access as a core use case. None mention the CORS constraint. A user following the deployment guide will get CORS-blocked API calls from any non-localhost device.

**D-C2 — `get_recipe()` Write Side Effect Undocumented**
`recipe_service.get_recipe()` silently calls `db.commit()` for `last_viewed_at` with no docstring. Any contributor who calls this function in a write path (or adds a new service function) will unknowingly introduce a pre-commit.

**D-C3 — Transaction Ownership Convention Split and Undocumented**
`recipe_service`, `media_service`, `settings_service` commit internally; `intake_service` uses flush-only and leaves commit to routes. The split is intentional but written nowhere. CLAUDE.md has no entry for this. New contributors must guess.

### High

**D-H1 — `api-spec.md` Documents ~10 Non-Existent Endpoints**
The following are documented with full contracts but have no route handlers:
- `POST /recipes/:id/mark-cooked`
- `GET /search/recipes`, `GET /search/facets`, `GET /search/ingredients`
- `GET /recipes/:id/related`
- `GET /intake-jobs` (list endpoint)
- `POST /intake-jobs/:id/abandon`
- All of `/media-assets`, `/ai-jobs`, `/backups`, `/system` route groups

**D-H2 — `GET /recipes` Filter Parameters Mismatch in `api-spec.md`**
- Spec documents `dietary_flag` and `ingredient` query params — neither is implemented
- Spec omits `ingredient_family` as an implemented filter parameter
- Spec omits `title_desc` as an implemented sort value
- Spec omits `operational_class` and `heat_window` as implemented filter parameters

**D-H3 — Pantry Limitation (Empty Ingredient Context) Undocumented**
`implemented-ai.md` describes pantry suggestion without noting that recipe ingredients are not included in the AI context — only taxonomy metadata is forwarded. Users will expect ingredient-level matching; they get taxonomy-level matching only.

**D-H4 — CLAUDE.md States `shared-taxonomy` Is "Not Yet Implemented"**
`CLAUDE.md` line under shared packages: "`packages/shared-taxonomy` is implemented and used by all AI modules" — actually, the taxonomy package is implemented and consumed by both the frontend (`FilterPanel`, `ManualEntryPage`) and backend (`schemas/taxonomy.py`). The CLAUDE.md gotchas section says "Shared packages live in `packages/` (shared-types, shared-taxonomy, shared-ui-tokens) — not yet implemented." This is stale.

### Medium

**D-M1 — `shared-prompts` Editable Install Not in Non-Docker Setup Docs**
The `sys.path` workaround in `main.py` requires a specific directory structure. The setup docs don't mention `pip install -e packages/shared-prompts` as an alternative (and cleaner) approach.

**D-M2 — No-Auth Architectural Decision Not Formally Recorded**
The deliberate choice to have no authentication is mentioned in passing in the product brief ("local-first, single-user") but never documented as an explicit architectural decision with its threat model, scope, and constraints (e.g., "safe on a trusted home LAN, not safe on a public network").

**D-M3 — `GET /api/v1/health/ai` Endpoint Undocumented in api-spec.md**
The AI health check endpoint (added in Session 43) is not in `api-spec.md`. The Settings page "Check connection" button depends on it.

**D-M4 — `ai_jobs` Internal Decision Not Cross-Referenced in `schema-spec.md`**
`implemented-ai.md §4.4` documents the `ai_jobs`-as-internal-infrastructure decision, but `schema-spec.md` still lists `ai_jobs` as a table without the "internal only" annotation.

### Low

**D-L1** — Some route handlers in `recipes.py` use inline `{"code": ..., "message": ...}` dicts instead of `error_detail()` — the pattern inconsistency is not noted in CLAUDE.md gotchas.
**D-L2** — The `backup.sh` / `restore.sh` scripts have good inline comments but no doc page in `docs/09_ops/` describing the backup strategy, retention policy, or restore procedure.
