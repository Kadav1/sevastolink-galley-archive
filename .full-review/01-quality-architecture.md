# Phase 1: Code Quality & Architecture Review

## Code Quality Findings

### Critical

**C-1 — Path Traversal Risk in Media File Serving** (`routes/media.py:91`, `services/media_service.py:64`)
The file path is built from `asset.relative_path` without verifying the resolved path stays under `media_dir`. A corrupted or injected DB row with `../../etc/passwd` would be served.
Fix: add `file_path.resolve()` containment guard before serving.

**C-2 — Media Upload Reads Entire File Into Memory Before Size Check** (`services/media_service.py:58`)
`file.file.read()` loads the entire upload into memory, then checks against `MAX_BYTES`. A large file exhausts memory before the limit fires. Fix: read in 64 KB chunks, abort if cumulative size exceeds limit.

### High

**H-1 — `_now()` and `_sync_fts()` Duplicated Between Services** (`recipe_service.py:30-61`, `intake_service.py:29-49`)
Both helpers are identically copy-pasted. FTS schema changes require dual updates; drift causes search inconsistency.

**H-2 — Taxonomy Vocabulary Duplicated: `normalizer.py` vs `taxonomy.py`** (`ai/normalizer.py:33-77`, `schemas/taxonomy.py`)
The normalizer maintains its own Python lists for `DISH_ROLES`, `PRIMARY_CUISINES`, `TECHNIQUE_FAMILIES` independent of the canonical frozensets. Silent drift means the AI can suggest values the validators reject.

**H-3 — Transaction Management Inconsistency**
Mixed commit ownership: `recipe_service`, `settings_service`, `media_service` commit internally; `intake_service` relies on routes to commit. Impossible to compose service calls in a single transaction.

**H-4 — `get_recipe()` Has a Write Side Effect** (`services/recipe_service.py:193-197`)
Updates `last_viewed_at` and calls `db.commit()` on every call, including internal calls from `update_recipe`, `archive_recipe`, `delete_recipe`, `similar_recipes`, etc. Pollutes `last_viewed_at` semantics and produces double-commits on mutation paths.

**H-5 — Taxonomy Validators Duplicated Verbatim Between `RecipeCreate` and `RecipeUpdate`** (`schemas/recipe.py:180-296` and `336-458`)
~120 lines of identical `@field_validator` methods copy-pasted between the two classes.

**H-6 — Identical Boilerplate Across 5 AI Modules** (`evaluator.py`, `metadata_suggester.py`, `rewriter.py`, `similarity_engine.py`, `pantry_suggester.py`)
Each defines the same 3-value error enum, identical error dataclass, identical `_validate_required()`, identical `_parse_response()`, identical `kind_map`. ~60 lines duplicated 5×.

### Medium

**M-1 — `RecipePage.tsx` is 942-line God Component** (`pages/RecipePage.tsx`)
10 `useState` calls for AI state alone, 5 async handlers, 3 inline component definitions, 280-line style object.

**M-2 — `PasteTextPage.tsx` Hardcodes Stale Taxonomy Options** (`pages/PasteTextPage.tsx:67-82`)
"Lunch", "Dinner", "Sauce / Condiment", "North African", "Cure / Preserve" etc. diverge from canonical vocabulary. `ManualEntryPage` correctly imports from `@galley/shared-taxonomy`; `PasteTextPage` does not.

**M-3 — FTS5 Query Accepts Raw User Input** (`services/recipe_service.py:241-249`)
User search strings passed directly to FTS5 MATCH. Special characters (`AND`, `OR`, `"`, `*`, `(`) are FTS5 operators — an unterminated token causes an unhandled 500.

**M-4 — New `httpx.Client` Created Per AI Request** (`ai/lm_studio_client.py:71,112`)
Each call to `check_availability` and `chat_completion` opens and tears down a new TCP connection. Fine for low volume but wasteful.

**M-5 — `_candidate_out` Manually Maps Every Field** (`routes/intake.py:32-73`)
40-line function hand-mapping all ORM fields instead of using Pydantic `from_attributes`.

**M-6 — Batch Intake Error Handling May Leave Session Dirty** (`routes/intake.py:93-123`)
A DB-level error during `db.flush()` inside the per-item loop corrupts session state. Broad `except Exception` doesn't rollback. Fix: use `db.begin_nested()` (savepoints) for per-item isolation.

**M-7 — `json_each()` Queries Have No Index** (`services/recipe_service.py:200-217, 286-296`)
Full table scan on every ingredient-family facet count and filter call.

**M-8 — CORS Blocks LAN Access** (`main.py:90-95`)
`allow_origins` only lists `localhost:3000` and `127.0.0.1:3000`. The product spec says accessible "via browser over the home network" — any LAN IP (e.g. `192.168.1.x:3000`) is blocked by CORS.

### Low

**L-1** — `IntakeJobOut.from_orm` lazy-loads `candidate` relationship (N+1 risk if jobs are ever listed).
**L-2** — `total_time_minutes` excludes `rest_time_minutes`; consistency with DB generated column unverified.
**L-3** — Over-indented `warnings.append` in `normalizer.py:279-280` (valid Python but misleading).
**L-4** — `sys.path` manipulation in `main.py:8-11` for shared-prompts import; fragile if file structure changes.
**L-5** — AI action handlers in `RecipePage.tsx` silently swallow all errors with no user feedback.
**L-6** — `RecipeListParams` TypeScript interface missing `sector`, `operational_class`, `heat_window`, `archived` filter params.
**L-7** — `unique_slug` uses unbounded while-loop (`utils/slugify.py:20-25`).
**L-8** — Pantry route always passes `"ingredients": []` to AI context, severely limiting match quality.

---

## Architecture Findings

### High

**A-H1 — Taxonomy Vocabulary Triplicate** (`ai/normalizer.py`, `schemas/taxonomy.py`, `packages/shared-taxonomy/src/index.ts`)
Three independent copies with no automated sync check. The normalizer's copy diverging from `taxonomy.py` creates silent AI-validation mismatch: AI suggests values the API rejects.

**A-H2 — `get_recipe()` Commits on Every Call Including Mutations** (`services/recipe_service.py:185-197`)
Same as H-4 above — architectural impact: split-commit paths in mutation operations, semantically wrong `last_viewed_at` on archive/delete/update.

**A-H3 — Transaction Boundary Inconsistency** (across services and routes)
Same as H-3 above — prevents transactional service composition.

### Medium

**A-M1 — `sys.path` Manipulation for shared-prompts** (`main.py:8-11`)
Implicit coupling between test runner import order and this path setup. Fix: install as editable package.

**A-M2 — Inconsistent Error Detail Construction in Recipes Route** (`routes/recipes.py:107,117,127,140,153,160,171`)
Inline `{"code":..., "message":...}` dicts instead of `error_detail()` helper used everywhere else.

**A-M3 — JSON Array Columns Without Defensive Parsing in Summary** (`schemas/recipe.py:RecipeSummaryOut`)
`RecipeDetail.from_orm_recipe()` guards against malformed JSON; `RecipeSummaryOut.from_orm_with_json()` does not.

**A-M4 — `total_time_minutes` May Diverge From DB Generated Column**
Python computes `prep + cook` only; DB generated column definition unverified — may include `rest_time_minutes`.

**A-M5 — AI Module Boilerplate Repetition** (5 AI modules)
Same as H-6 above — adds maintenance burden for each new AI endpoint.

**A-M6 — `PasteTextPage` Taxonomy Divergence** (`pages/PasteTextPage.tsx:67-82`)
Non-canonical values accepted in the candidate but rejected at approval time by `RecipeCreate` validators. Hidden data quality failure at the seam between intake and approval.

**A-M7 — Pantry Route Sends Empty Ingredient Arrays** (`routes/pantry.py:42-53`)
`"ingredients": []` hardcoded — recipe ingredient data loaded via `selectinload` is available but never forwarded to the AI.

### Low

**A-L1** — Mixed timestamp formats: `_now()` produces `YYYY-MM-DDTHH:MM:SSZ`, `SettingEntry` server_default produces `YYYY-MM-DD HH:MM:SS`. Cross-table string sort of timestamps will break.
**A-L2** — `unique_slug` circular import guard (local import in `slugify.py`) — utility depends on domain model; acceptable for v1.
**A-L3** — Module-level AI contract loading causes full app startup failure if a prompt file is missing (intentional fail-fast, acceptable for local-first).
**A-L4** — LMStudioClient instantiated per-request; fine for v1 low volume.

---

## Critical Issues for Phase 2 Context

1. **Path traversal in media serving (C-1)** — needs security review; relative_path comes from DB, not user input, but worth examining the full injection surface.
2. **Memory exhaustion on media upload (C-2)** — DoS vector on the home LAN; low sophistication attack.
3. **CORS blocks LAN access (M-8)** — affects the intended home-network use case; may also have security implications if origins are opened too broadly.
4. **FTS5 raw user input (M-3)** — unhandled 500 on malformed queries; consider whether FTS5 syntax could be used for injection.
5. **Transaction boundary inconsistency (H-3/A-H3)** — race conditions possible if two requests mutate the same recipe concurrently; SQLite's writer lock mitigates this in practice.
6. **Pantry sends empty ingredients (L-8/A-M7)** — not a security issue but a functional correctness issue relevant to testing.
