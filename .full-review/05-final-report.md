# Comprehensive Code Review Report — Sevastolink Galley Archive

**Review date:** 2026-04-03
**Phases completed:** Code Quality, Architecture, Security, Performance, Testing, Documentation, Best Practices, CI/CD & DevOps
**Repository:** `/media/blndsft/SLP-ARCH-01/azwerks/sevastolink-galley-archive`

---

## Executive Summary

The Galley Archive is a well-structured, specification-first project. The three-entity data pipeline (Raw Source → Candidate → Approved Recipe), the AI boundary enforcement, the shared taxonomy package, and the error envelope contract are all cleanly implemented and consistently applied. The codebase is in better shape than most v1 projects at this stage.

The most pressing issues are three targeted security fixes (path traversal, upload memory exhaustion, FTS5 injection) that are each under 15 lines of code, plus two architectural corrections (CORS for LAN access, and the `get_recipe()` write-on-read side effect) that touch core flows. After those, the dominant theme is **duplication**: taxonomy vocabularies, validator logic, AI module boilerplate, and FTS helpers are all defined in multiple places and will drift unless consolidated.

---

## Findings by Priority

### P0 — Critical: Fix Immediately

**[S-C1] Path Traversal in Media File Serving** · `routes/media.py:91` · CWE-22
File path built from `asset.relative_path` with no containment check. A malicious DB row serves arbitrary files from the host.
```python
file_path = (settings.media_dir / asset.relative_path).resolve()
if not str(file_path).startswith(str(settings.media_dir.resolve())):
    raise HTTPException(status_code=403, detail=error_detail("forbidden", "Path rejected."))
```

**[S-H1] Upload Reads Entire File Into Memory Before Size Check** · `services/media_service.py:58` · CWE-400
`file.file.read()` before the 20 MB guard — any LAN device can exhaust server memory.
Fix: read in 64 KB chunks with a running byte counter; abort on overflow.

**[S-H2] FTS5 Accepts Raw User Input → Unhandled 500** · `services/recipe_service.py:241` · CWE-89 (adjacent)
Special FTS5 operators in search strings propagate as unhandled `sqlite3.OperationalError`.
```python
def _sanitize_fts_query(q: str) -> str:
    return " ".join(f'"{token}"' for token in q.strip().split() if token)
```

**[DO-H1] Both Dockerfiles Run as Root**
No `USER` directive in either Dockerfile. Container escape yields root on the host — especially relevant given S-C1.

---

### P1 — High: Fix Before Next Feature Work

**[M-8 / D-C1] CORS Blocks Intended LAN Access** · `main.py:90-95`
`allow_origins` only lists `localhost:3000`. Every home-network device is CORS-blocked. This contradicts the product spec and deployment documentation. Make origins configurable via `.env`.

**[H-4 / A-H2 / D-C2] `get_recipe()` Commits on Every Call Including Mutations** · `recipe_service.py:185-197`
Writes and commits `last_viewed_at` on every internal call, including `update_recipe`, `archive_recipe`, `delete_recipe`. Causes double-commits on all mutation paths, semantically incorrect `last_viewed_at` on archive/delete, and an uncommitted-state risk on composed write paths. Split into a pure-read `_get_recipe()` and a view-tracking `touch_last_viewed()` called only from the GET route handler.

**[H-3 / A-H3 / D-C3] Transaction Ownership Convention Inconsistent and Undocumented**
`recipe_service`, `media_service`, `settings_service` commit internally; `intake_service` does not. Prevents transactional composition and confuses contributors. Choose one convention (services flush, routes commit is preferred) and apply it uniformly. Document in CLAUDE.md.

**[H-2 / A-H1] Taxonomy Vocabulary Triplicated** · `ai/normalizer.py:33-77`, `schemas/taxonomy.py`, `packages/shared-taxonomy/src/index.ts`
The normalizer maintains its own Python lists for dish roles, cuisines, and technique families, independent of `taxonomy.py`. AI can suggest values the API rejects, or fail to suggest newly added values.
Fix: import from `src.schemas.taxonomy` in the normalizer.

**[T-H1] Test Fixture Fragmentation** · 10 of 13 test files
10 test files use fixed-path SQLite databases instead of the shared `async_client` fixture from `conftest.py`. Parallel test runs corrupt each other. All should migrate to the `tmp_path`-based fixture.

**[T-H4] Zero Frontend Test Coverage**
No Vitest, no Playwright, no test script in `package.json`. 8 pages, 20+ components, 5 hooks, and 6 API modules are completely untested.

**[DO-H2] Production Image Installs Dev Dependencies** · `apps/api/Dockerfile:9`
`pip install -e ".[dev]"` in production — installs `pytest`, `pytest-asyncio`. Use a multi-stage build; production stage installs only `pip install -e "."`.

**[DO-H3] No Health Check in `docker-compose.yml`**
`galley-web` starts before the API is ready to serve. Add a `healthcheck:` with `curl -f /api/health` and `depends_on: condition: service_healthy`.

**[BP-H2] `httpx` Listed Only as Dev Dependency**
`httpx` is used in production AI code (`lm_studio_client.py`) but declared only under `[dev]` extras. A production install without extras causes `ModuleNotFoundError` at AI endpoint startup.

---

### P2 — Medium: Plan for Next Sprint

**[H-5] Taxonomy Validators Duplicated 16× Between `RecipeCreate` and `RecipeUpdate`** · `schemas/recipe.py`
Extract a `TaxonomyValidatorsMixin` shared by both classes.

**[H-6] AI Module Boilerplate Repeated 5×** · `evaluator.py`, `metadata_suggester.py`, `rewriter.py`, `similarity_engine.py`, `pantry_suggester.py`
Identical error enums, result dataclasses, `_validate_required()`, `_parse_response()`, `kind_map` — all copy-pasted. Extract a base utility in `src/ai/base.py`.

**[H-1] `_now()` and `_sync_fts()` Duplicated Across Services**
Extract to `src/utils/timestamps.py` and `src/db/fts.py` respectively.

**[L-8 / A-M7] Pantry Always Sends Empty Ingredient Arrays** · `routes/pantry.py:50`
`"ingredients": []` hardcoded — ingredient data is loaded via `selectinload` but never forwarded to the AI. Taxonomy-only matching severely limits suggestion quality.

**[M-2 / A-M6] `PasteTextPage.tsx` Uses Stale Hardcoded Taxonomy Options** · `pages/PasteTextPage.tsx:67-82`
"Lunch", "Dinner", "Sauce / Condiment", "North African" etc. are not canonical. Values selected here will be rejected by `RecipeCreate` validators at approval time. Import from `@galley/shared-taxonomy`.

**[M-3] FTS5 Query Accepts Raw User Input** *(also P0 above — the fix is the sanitiser; this medium item is about adding a test)*

**[M-6] Batch Intake Error Handling May Leave Session Dirty** · `routes/intake.py:93-123`
A DB-level error inside the per-item loop may corrupt session state. Use `db.begin_nested()` (savepoints) for per-item isolation.

**[P-H2] Missing Indexes for Common Query Paths** · `migrations/001_initial_schema.sql`
No index on `(archived, updated_at DESC)` — the default library view full-scans the recipes table. Add via a new migration:
```sql
CREATE INDEX IF NOT EXISTS idx_recipes_archived_updated ON recipes (archived, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_recipes_updated_at ON recipes (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_recipes_last_cooked_at ON recipes (last_cooked_at DESC);
CREATE INDEX IF NOT EXISTS idx_recipes_archived ON recipes (archived);
```

**[P-M1] No SQLite Connection Pragmas on SQLAlchemy Engine** · `db/database.py`
WAL mode set only on a transient raw connection. Add via `event.listens_for(engine, "connect")`: `journal_mode=WAL`, `synchronous=NORMAL`, `cache_size=-32000`, `foreign_keys=ON`.

**[P-M3] Synchronous `httpx` Blocks Async Event Loop During AI Calls**
All AI routes are `async def` but call synchronous `httpx.Client`. Long LM Studio inferences (10–240 s) block all other requests. Fix: `await asyncio.to_thread(ai_function, ...)` or switch to `httpx.AsyncClient`.

**[D-H1 / D-H2] `api-spec.md` Documents ~10 Non-Existent Endpoints; Filter Params Mismatch**
Remove or mark unimplemented endpoints as `[planned]`. Add `ingredient_family`, `operational_class`, `heat_window`, `title_desc` to the spec.

**[DO-M2] Nginx Config Missing Security Headers and Body Size Limit**
Add `client_max_body_size 25m`, `server_tokens off`, `X-Frame-Options SAMEORIGIN`, `X-Content-Type-Options nosniff`.

**[DO-M1] No CI Pipeline**
Add a minimal GitHub Actions workflow: pytest + type-check + secrets scan.

**[BP-H1] SQLAlchemy 1.x Query API Used Throughout**
Migrate `db.query(Model).filter(...)` to `db.execute(select(Model).where(...)).scalars()`. Low urgency for a home archive but needed before any SQLAlchemy 3.x upgrade.

**[BP-H3] `aiosqlite` Listed as Production Dependency but Never Imported**
Remove from `pyproject.toml` production dependencies.

**[D-H3] Pantry Limitation Undocumented** · `implemented-ai.md`
Document that pantry suggestion uses taxonomy metadata only, not actual ingredient content.

**[D-H4] CLAUDE.md States `shared-taxonomy` Is "Not Yet Implemented"**
Update — the package is fully implemented and consumed by both frontend and backend.

---

### P3 — Low: Track in Backlog

**Code quality:**
- [L-5] AI action handlers in `RecipePage.tsx` silently swallow errors — add user feedback
- [L-6] `RecipeListParams` TypeScript interface missing `sector`, `operational_class`, `heat_window`, `archived` filter params
- [L-7] `unique_slug()` unbounded while-loop — add 100-iteration guard
- [L-3] Over-indented `warnings.append` in `normalizer.py:279`
- [L-4] `sys.path` manipulation in `main.py` — replace with `pip install -e packages/shared-prompts`
- [M-1] `RecipePage.tsx` 942 lines — extract AI panels to components, AI state to custom hooks using `useMutation`
- [M-5] `_candidate_out` manual field mapping — replace with `model_validate(..., from_attributes=True)`

**Performance:**
- [P-L1] `httpx.Client` created per AI call — use persistent client in `__init__`
- [P-L4] `FilterPanel` not wrapped in `React.memo`
- [P-L2] `unique_slug()` queries once per collision — acceptable for now; note for bulk import

**Testing:**
- [T-H2] Pantry test doesn't assert ingredients are forwarded to AI
- [T-H3] No test verifies AI cannot modify `verification_state`
- [T-M4] AI module `_parse_response` / `_validate_required` have no unit tests
- [T-M5] Media upload boundary cases not tested
- [T-M6] Slug edge cases (Unicode, special chars) untested
- [T-L5] `repair_candidates.py` FIELD_MAPS have no automated test

**Documentation:**
- [D-M2] No-auth architectural decision not formally recorded
- [D-M3] `GET /api/v1/health/ai` not in `api-spec.md`
- [D-L2] No ops doc for backup retention/restore procedure

**DevOps:**
- [DO-M3] `backup-prune` uses filesystem mtime — parse name timestamp instead
- [DO-M4] No migration rollback strategy
- [DO-M5] `--reload` in production Dockerfile CMD
- [DO-L2] `scripts/dev/scan_secrets.sh` referenced by Makefile but does not exist
- [DO-L3] `scripts/dev/install_git_hooks.sh` referenced by Makefile but does not exist
- [DO-L5] `node:20-slim` base image approaching EOL — upgrade to `node:22-slim`

**Best practices:**
- [BP-L2] AI error/result dataclasses should use `frozen=True`
- [BP-L3] TanStack Query `queryKey` arrays scattered — centralise in a factory object
- [BP-M6] Source maps always on in production build — gate on `NODE_ENV`
- [BP-M7] No frontend test runner configured

---

## Findings by Category

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Code Quality | 2 | 6 | 8 | 8 | **24** |
| Architecture | 0 | 3 | 7 | 4 | **14** |
| Security | 1 | 3 | 4 | 5 | **13** |
| Performance | 0 | 3 | 4 | 5 | **12** |
| Testing | 2 | 3 | 6 | 5 | **16** |
| Documentation | 3 | 4 | 4 | 2 | **13** |
| Best Practices | 0 | 3 | 7 | 5 | **15** |
| CI/CD & DevOps | 0 | 3 | 5 | 5 | **13** |
| **Total** | **8** | **28** | **45** | **39** | **120** |

---

## Recommended Action Plan

### Immediate (this week) — P0
1. **[small]** Path traversal guard in `media.py` — 3 lines
2. **[small]** Chunked upload read in `media_service.py` — ~15 lines
3. **[small]** FTS5 input sanitiser in `recipe_service.py` — ~5 lines + test
4. **[small]** Add `USER galley` to both Dockerfiles

### Before Next Feature — P1
5. **[small]** Move `httpx` to production deps in `pyproject.toml`; remove `aiosqlite`
6. **[medium]** CORS: make `allow_origins` configurable via `.env`; update deployment docs
7. **[medium]** Split `get_recipe()` side effect — pure read + `touch_last_viewed()` in GET route only
8. **[medium]** Standardise transaction ownership — services flush, routes commit; document in CLAUDE.md
9. **[small]** Remove duplicate taxonomy lists from `normalizer.py`; import from `taxonomy.py`
10. **[small]** Fix pantry route to include recipe ingredients in AI context
11. **[small]** Fix `PasteTextPage.tsx` to import from `@galley/shared-taxonomy`
12. **[medium]** Add `healthcheck:` to `docker-compose.yml`; fix production Dockerfile CMD (remove `--reload`)
13. **[medium]** Multi-stage Dockerfile: production stage without dev deps
14. **[small]** Update CLAUDE.md: `shared-taxonomy` is implemented; document transaction convention

### Next Sprint — P2
15. **[medium]** New migration: add missing indexes (`archived`, `updated_at`, composite)
16. **[small]** SQLAlchemy engine PRAGMA configuration via `event.listens_for`
17. **[medium]** `asyncio.to_thread()` for AI calls to unblock event loop
18. **[medium]** Migrate test fixtures to shared `async_client` from `conftest.py`
19. **[medium]** Extract `TaxonomyValidatorsMixin` from duplicated validators
20. **[medium]** Extract AI module boilerplate to `src/ai/base.py`
21. **[medium]** Extract `_sync_fts()` and `_now()` to shared utilities
22. **[small]** Nginx: add `client_max_body_size`, security headers, `server_tokens off`
23. **[medium]** Update `api-spec.md`: remove phantom endpoints, add implemented params
24. **[medium]** Add GitHub Actions CI (pytest + type-check + secrets scan)
25. **[medium]** Document no-auth decision and pantry limitation in relevant docs

### Backlog — P3
26. Decompose `RecipePage.tsx` into components + `useMutation` hooks
27. Add frontend test runner (Vitest) with initial hook and API module tests
28. Migrate SQLAlchemy query style from 1.x to 2.x `select()`
29. Centralise TanStack Query key factory
30. Fix `scan_secrets.sh` and `install_git_hooks.sh` missing scripts
31. Upgrade web base image to `node:22-slim`
32. Slug edge-case tests, AI module unit tests, media boundary tests

---

## Positive Highlights

Worth preserving as the codebase grows:

- **Three-entity pipeline** is cleanly enforced — AI output never reaches `recipes` without human approval
- **Error envelope contract** is consistent across all routes and tests
- **Shared taxonomy package** — single canonical vocabulary source now consumed by both frontend and backend validators
- **AI result/error tuple pattern** — explicit, no exceptions leaking across module boundaries
- **Design token system** — CSS custom properties used consistently; no hardcoded colours or spacing
- **Backup/restore scripts** — live round-trip tested and working; Makefile covers the full operator workflow
- **CLAUDE.md** — project context document is unusually thorough and kept reasonably current
