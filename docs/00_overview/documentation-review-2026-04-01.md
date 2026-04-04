# Documentation Review — Sevastolink Galley Archive

**Date:** 2026-04-01
**Reviewer:** Claude Code (claude-sonnet-4-6)
**Scope:** CLAUDE.md, all docs/ specification files, README.md, ops docs, inline code comments, cross-referenced against apps/api/src/ implementation

---

## Executive Summary

The documentation structure is well above average for a solo project. There is a clear and consistently followed pattern of paired `spec` + `implemented-*` documents that honestly separates target-state guidance from current runtime behavior. The README is genuinely useful and accurate. Ops documentation is complete and operational.

The findings below are real gaps, not cosmetic issues. The six highest-severity items (three Critical, three High) all directly affect contributors working on the codebase: two involve undocumented behavior that can surprise a contributor mid-session, three involve the API spec diverging from runtime implementation, and one is the CORS/LAN contradiction that affects actual home-network users.

---

## 1. CORS Blocks the Stated Core Requirement

**Severity: Critical**
**Affects:** `apps/api/src/main.py`, `docs/01_product/product-brief.md`, `docs/06_architecture/technical-architecture.md`, README.md, CLAUDE.md

**Finding:**

The product spec states home-network accessibility as a core goal (§3.6, §5.6, §7.5) and the README documents it under "For Self-Hosters." The architecture doc (§12) acknowledges LAN access as a valid configuration path. Yet the CORS middleware in `main.py` only allows `http://localhost:3000` and `http://127.0.0.1:3000`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    ...
)
```

A device accessing the archive over the LAN via nginx at `http://192.168.1.x:8080` will have its API calls blocked by the browser with a CORS error. The nginx setup correctly proxies requests to the backend, but the backend's CORS policy then rejects them because the `Origin` header contains the LAN IP, not `localhost`.

The deployment docs correctly explain how nginx enables LAN access, but do not mention this CORS constraint anywhere. A user following the documented nginx LAN setup will encounter silent failures.

**Recommendation:**

Document this in CLAUDE.md under Known Gotchas with the current behavior and the proper fix (allow all private-network origins, or read allowed origins from an environment variable). Separately, add a note to `docs/09_ops/local-deployment.md` in the "Home-network access" section and to the README LM Studio/networking sections. The fix is outside documentation scope but the constraint must be disclosed.

---

## 2. `get_recipe()` Side Effect Is Undocumented

**Severity: Critical**
**Affects:** `apps/api/src/services/recipe_service.py`, CLAUDE.md, inline docstring

**Finding:**

`get_recipe()` in `recipe_service.py` is a read function by name and signature, but it unconditionally calls `db.commit()` on every successful lookup:

```python
def get_recipe(db: Session, id_or_slug: str) -> Recipe | None:
    ...
    if recipe:
        recipe.last_viewed_at = _now()
        db.commit()
        db.refresh(recipe)
    return recipe
```

This has two undocumented consequences:

1. Any caller that has staged unflushed writes before calling `get_recipe()` will have those writes committed prematurely.
2. Tests that mock `get_recipe` or set up pre-conditions relying on uncommitted state can produce unexpected behavior.

There is no docstring on the function. The CLAUDE.md Known Gotchas section lists the `last_viewed_at` tracking as a finding but marks it as undocumented — it has not been addressed in the codebase or docs.

**Recommendation:**

Add a docstring to `get_recipe()` in `recipe_service.py` explicitly stating: "This function writes `last_viewed_at` and commits the session as a side effect of every read. Do not call it while the session has unflushed staged writes intended for a separate transaction." Add a corresponding Known Gotcha entry to CLAUDE.md.

---

## 3. Transaction Ownership Convention Is Unwritten

**Severity: Critical**
**Affects:** All service files, CLAUDE.md, `docs/06_architecture/technical-architecture.md`

**Finding:**

The codebase uses two different transaction ownership patterns with no documented convention:

- **Services commit:** `recipe_service.py` — `create_recipe`, `update_recipe`, `archive_recipe`, `unarchive_recipe`, `set_favorite`, `delete_recipe`, and `get_recipe` all call `db.commit()` internally.
- **Routes commit:** `intake.py` routes — `create_intake_job`, `update_candidate`, `normalize_candidate`, and `approve_intake_job` all call `db.commit()` in the route handler after the service call returns.
- **Services flush only:** `intake_service.py` service functions never call `db.commit()` — they use `db.flush()` and leave commit to the caller.

This split pattern is not documented anywhere. A new contributor adding a service function must guess which convention applies. The `recipe_service` and `intake_service` files follow opposite conventions, making the inconsistency invisible unless both are read.

`media_service.py` commits internally (matching recipe_service), while `settings_service.py` also commits internally. So the actual pattern is: recipe, media, and settings services commit; intake service flushes and defers commit to the route.

**Recommendation:**

Document the intended convention explicitly in CLAUDE.md under Known Gotchas. Recommended wording: explain that `recipe_service`, `media_service`, and `settings_service` own their commits internally; `intake_service` uses flush-only and the route layer commits. Note that this split is intentional (intake operations span multiple steps that routes orchestrate), and link to the relevant service files as examples.

---

## 4. API Spec Documents Endpoints That Do Not Exist

**Severity: High**
**Affects:** `docs/07_api/api-spec.md`

**Finding:**

The api-spec.md documents multiple endpoints as part of the spec that have no corresponding route handlers in the current implementation. The "current-state gap note" at the top of the file acknowledges this in general terms, but does not identify which specific endpoints are unimplemented. Contributors reading the spec to understand what the API does will encounter documented contracts for endpoints that return 404.

Unimplemented endpoints documented in the spec without implementation:

- `POST /recipes/:id/mark-cooked` (§7.9) — no handler in `recipes.py`; `mark-cooked` does not appear in the route file at all
- `GET /search/recipes` (§8.1) — no `/search` router exists; this endpoint is merged into `GET /recipes` in the actual implementation
- `GET /search/facets` (§8.2) — not implemented; facets are available via `GET /recipes/ingredient-families` only (a narrower endpoint)
- `GET /search/ingredients` (§8.3) — not implemented
- `GET /recipes/:id/related` (§8.4) — not implemented
- `GET /intake-jobs` list endpoint (§9.3) — no list handler in `intake.py`; only `GET /intake-jobs/:id` exists
- `POST /intake-jobs/:id/abandon` (§9.1 workflow diagram) — not implemented
- All of §10 (`/media-assets`), §11 (`/ai-jobs`), §12 (`/settings` — partially), §13 (`/backups`), §14 (`/system`) — documented but not implemented or only partially implemented

The existing `implemented-api.md` file is mentioned in the current-state gap note as the corrective reference, but its path is not directly linked and it is unclear whether it exists and is current.

**Recommendation:**

Add a table at the top of `api-spec.md` (or in the gap note) explicitly listing every endpoint group with a status column: `implemented`, `partial`, or `not yet implemented`. This makes the gap immediately visible without requiring a contributor to cross-reference the route files. Alternatively, mark each endpoint header in the spec with a status badge.

---

## 5. `GET /recipes` Filter Parameters Diverge from Spec

**Severity: High**
**Affects:** `docs/07_api/api-spec.md` §7.1, `apps/api/src/routes/recipes.py`

**Finding:**

The api-spec §7.1 documents `dietary_flag` and `ingredient` as valid query parameters for `GET /recipes`. Neither is implemented in the route handler or the `list_recipes` service function.

The spec also documents `title_asc` as a sort option in the sort parameter table, while the actual implementation in `recipe_service.py` supports both `title_asc` and `title_desc`. The spec omits `title_desc`.

Conversely, the implementation supports `ingredient_family` (singular, JSON array member matching) while the spec uses a different framing. This is not a problem but the mismatch in parameter naming should be explicit.

**Recommendation:**

Update api-spec.md §7.1 to: remove `dietary_flag` and `ingredient` from the documented query parameters (or mark them as not yet implemented), add `title_desc` to the sort options table, and verify the `ingredient_family` parameter name matches the spec exactly.

---

## 6. Pantry Empty Ingredients Limitation Is Undocumented

**Severity: High**
**Affects:** `apps/api/src/routes/pantry.py`, `docs/05_ai/implemented-ai.md`, CLAUDE.md

**Finding:**

The pantry suggestion endpoint fetches up to 20 archive recipes for AI context, but the archive context passed to the AI contains empty ingredient lists:

```python
archive_dicts = [
    {
        "title": r.title,
        "dish_role": r.dish_role,
        "primary_cuisine": r.primary_cuisine,
        "complexity": r.complexity,
        "ingredients": [],   # always empty
    }
    for r in archive_recipes_orm
]
```

The ORM query uses `list_recipes()` which does not eager-load ingredients. As a result, the AI receives recipe titles and taxonomy but no actual ingredient information for matching. The `implemented-ai.md` §3.6 describes pantry suggestion as implemented and working, with no mention of this constraint. A user expecting "I have chicken and lemon, what can I make from my archive?" to leverage actual ingredient data will get suggestions based on title and classification only.

CLAUDE.md lists this as a prior finding but it has not been documented in the user-facing or implementation documentation.

**Recommendation:**

Add a Known Limitation note to `docs/05_ai/implemented-ai.md` §3.6 stating that the current pantry archive context includes recipe metadata but not ingredient lists, and that ingredient matching is therefore based on taxonomy fields only. Add the same finding to CLAUDE.md Known Gotchas with a note about the fix (eager-load ingredients or use a separate query to include them in the context dict).

---

## 7. `sys.path` Manipulation: Fix Path Not Documented

**Severity: Medium**
**Affects:** `apps/api/src/main.py`, `docs/09_ops/local-deployment.md`, CLAUDE.md

**Finding:**

`main.py` contains a `sys.path` injection at module load to make `packages/shared-prompts` importable without a formal pip install:

```python
_SHARED_PROMPTS_SRC = str(Path(__file__).resolve().parents[3] / "packages" / "shared-prompts" / "src")
if _SHARED_PROMPTS_SRC not in sys.path:
    sys.path.insert(0, _SHARED_PROMPTS_SRC)
```

The comment explains why but not how to eliminate it. The deployment doc (`local-deployment.md`) mentions `pip install -e ".[dev]"` for the non-Docker path but does not mention that `shared-prompts` has its own package that requires a separate editable install. If a contributor installs `apps/api` as an editable package and removes the `sys.path` line, imports will break until `packages/shared-prompts` is also installed.

CLAUDE.md mentions this under Known Gotchas as a workaround but notes that "the proper fix (editable install) is not in setup docs."

**Recommendation:**

Add to `docs/09_ops/local-deployment.md` in the "Running without Docker" section: state that `packages/shared-prompts` must be installed separately with `pip install -e packages/shared-prompts` when running the API outside Docker, and that the `sys.path` workaround in `main.py` handles this automatically in the Docker path where the repo root is volume-mounted.

---

## 8. No-Auth Decision Is Not Formally Documented

**Severity: Medium**
**Affects:** `docs/06_architecture/technical-architecture.md`, `docs/01_product/product-brief.md`

**Finding:**

The product is deliberately unauthenticated. The architecture doc §15 (Security model) states that multi-user identity and enterprise auth are non-goals, and the product brief §4.5 states it is not a cloud product. However, no document explicitly records the no-authentication decision as a deliberate choice and explains the reasoning.

A contributor encountering the bare API without authentication might reasonably conclude it is incomplete rather than intentional. The LAN exposure via nginx further compounds this: someone standing up the stack on a home network with other users has no documented guidance on whether this is safe and intentional.

The product-brief Decisions section (§10) lists 10 decisions, none of which explicitly address authentication or access control.

**Recommendation:**

Add a decision record to `docs/01_product/product-brief.md` §Decisions: "No user authentication is implemented. The product is designed for single-household use on a trusted home network. All operations are permitted to any device that can reach the service. This is intentional and not a security gap for the intended deployment context." Add the same framing to `docs/06_architecture/technical-architecture.md` §15.

---

## 9. Health Endpoint Response Shape Undocumented, Actual Shape Richer Than Spec Implies

**Severity: Medium**
**Affects:** `docs/07_api/api-spec.md`, `apps/api/src/routes/health.py`

**Finding:**

The api-spec does not document the health endpoint at all (it is mentioned in the gap note as "implemented today" but has no dedicated section). The actual implementation returns a richer response than the README implies:

README states: `Returns {"status": "ok"}` when healthy.
Actual implementation returns:
```json
{"status": "ok", "service": "galley-api", "db": "ok"}
```

and when the database is unreachable:
```json
{"status": "degraded", "service": "galley-api", "db": "unreachable"}
```

The `GET /api/v1/health/ai` endpoint is also implemented and undocumented in the API spec. It returns `ai_enabled`, `reachable`, `model`, and `error`.

**Recommendation:**

Add a Health Endpoints section to `docs/07_api/api-spec.md` (or `implemented-api.md`) documenting both `GET /api/health` and `GET /api/v1/health/ai` with their full response shapes. Correct the README to show the actual three-field response.

---

## 10. CLAUDE.md Implementation Status Section Is Partially Stale

**Severity: Medium**
**Affects:** CLAUDE.md

**Finding:**

The Implementation Status section in CLAUDE.md states: "Frontend (`apps/web/`): ... Settings page (real load/save)." However the README explicitly lists `/settings` as a "placeholder" in the "What Works Today" section. These two statements are contradictory.

The CLAUDE.md Implementation Status section also lists "112 tests across `apps/api/tests/`" but does not note that test counts change with development. More importantly, it does not note the parallel pytest / SQLite DB corruption gotcha in the same sentence — the test count reference and the corruption gotcha are separated, which means contributors may not connect them.

CLAUDE.md also states "shared-types, shared-taxonomy, shared-ui-tokens" are "not yet implemented" in the packages description, but `implemented-taxonomy.md` confirms `packages/shared-taxonomy` is implemented and actively consumed by both frontend and backend. This is incorrect.

**Recommendation:**

Correct the packages note: `packages/shared-taxonomy` is implemented. Clarify the settings page status: the backend settings API exists and the page loads/saves `default_verification_state` and `library_default_sort`, but the full settings UI surface is still a placeholder. Add a cross-reference note next to the test count pointing to the "Parallel pytest runs corrupt the test DB" gotcha.

---

## 11. `intake_service.py` Has No Module Docstring

**Severity: Medium**
**Affects:** `apps/api/src/services/intake_service.py`

**Finding:**

`recipe_service.py` has a well-structured module docstring listing its responsibilities. `intake_service.py` has a module docstring but it describes responsibilities only as intake type handling and ignores the commit/flush pattern distinction that is the most surprising aspect of the file. There is no explanation of why `intake_service` uses flush-only while other services commit internally.

**Recommendation:**

Expand the `intake_service.py` module docstring to include: "Transaction ownership: this module uses `db.flush()` throughout. Callers (route handlers) are responsible for calling `db.commit()`. This differs from `recipe_service` where each operation commits internally."

---

## 12. Schema Spec Describes Tables Not Yet Surfaced, Without Clear Status

**Severity: Low**
**Affects:** `docs/08_database/schema-spec.md`

**Finding:**

The schema spec §3 lists `recipe_notes`, `recipe_sources`, `candidate_ingredients`, `candidate_steps`, `media_assets`, `ai_jobs`, and `settings` as part of the schema. The current-state gap note acknowledges these are defined but "not fully surfaced." However, `ai_jobs` specifically has an important architectural decision attached to it (§4.4 of `implemented-ai.md`): it is intentionally kept as internal infrastructure and will never be a first-class API resource. This decision is documented in `implemented-ai.md` but not in the schema spec, where a contributor might wonder why the table has no associated API endpoint group.

**Recommendation:**

Add a brief note to the `ai_jobs` table entry in the schema spec (§4 or a table-level annotation) cross-referencing the architectural decision in `implemented-ai.md` §4.4: "`ai_jobs` is intentionally internal audit infrastructure. It has no API surface and no planned UI. See implemented-ai.md §4.4."

---

## 13. `docs/07_api/api-spec.md` Response Envelope Spec Contradicts Actual Error Shape in Some Routes

**Severity: Low**
**Affects:** `docs/07_api/api-spec.md`, `apps/api/src/routes/recipes.py`, `apps/api/src/routes/intake.py`

**Finding:**

The api-spec error envelope (§3) specifies:
```json
{"error": {"code": "...", "message": "...", "details": {}}}
```

The error handler in `main.py` correctly normalizes all `HTTPException` shapes. However, several route handlers in `recipes.py` and `intake.py` still pass `detail` as a raw dict `{"code": "...", "message": "..."}` rather than using the `error_detail()` helper from `schemas/common.py`. The exception handler correctly wraps these, so the final response is correct — but the route code does not follow the documented convention uniformly. CLAUDE.md correctly notes to use `error_detail()`, but in practice some routes bypass it.

**Recommendation:**

This is primarily a code consistency issue rather than a documentation gap, but it should be noted in CLAUDE.md Known Gotchas: "Some route handlers in `recipes.py` pass raw `{"code": ..., "message": ...}` dicts directly as `detail` rather than using `error_detail()`. The custom exception handler in `main.py` normalizes these, so responses are correct, but new code should always use `error_detail()` for consistency."

---

## Summary Table

| # | Severity | Area | Short Description |
|---|----------|------|--------------------|
| 1 | Critical | CORS + networking | LAN access blocked by CORS; contradicts core product promise |
| 2 | Critical | `get_recipe()` | Read function commits; undocumented side effect |
| 3 | Critical | Transaction convention | Services vs. routes own commits inconsistently; undocumented |
| 4 | High | api-spec.md | Multiple documented endpoints do not exist in implementation |
| 5 | High | api-spec.md | `dietary_flag`, `ingredient` filter params and sort options mismatch |
| 6 | High | pantry / AI docs | Empty ingredient context in pantry suggest not documented |
| 7 | Medium | Setup docs | `sys.path` workaround fix path absent from deployment docs |
| 8 | Medium | Architecture | No-auth decision not formally recorded |
| 9 | Medium | Health endpoint | Richer actual response shape undocumented in spec and README |
| 10 | Medium | CLAUDE.md | `shared-taxonomy` listed as not implemented; settings status inconsistent |
| 11 | Medium | `intake_service.py` | Module docstring does not explain flush-only convention |
| 12 | Low | schema-spec.md | `ai_jobs` architectural decision not cross-referenced |
| 13 | Low | Error envelope | Raw dict usage in some routes vs. `error_detail()` helper |
