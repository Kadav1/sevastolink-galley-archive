# Phase 2: Security & Performance Review

## Security Findings

### Critical

**S-C1 — Path Traversal in Media File Serving** (`routes/media.py:91`) · CWE-22
`file_path = settings.media_dir / asset.relative_path` with no containment check. A DB row where `relative_path` is `../../etc/passwd` serves arbitrary files. Attack surface is local/LAN-only (no auth required on the home network), but the fix is 3 lines.

```python
file_path = (settings.media_dir / asset.relative_path).resolve()
if not str(file_path).startswith(str(settings.media_dir.resolve())):
    raise HTTPException(status_code=403, detail=error_detail("forbidden", "Path rejected."))
```

### High

**S-H1 — Memory Exhaustion on Upload** (`services/media_service.py:58`) · CWE-400
`file.file.read()` loads the entire upload into RAM before the 20 MB guard fires. Any LAN device can send a large file and exhaust process memory. Fix: read in 64 KB chunks with a running counter.

**S-H2 — FTS5 Operator Injection → Unhandled 500** (`services/recipe_service.py:241-249`) · CWE-89 (adjacent)
User search strings passed directly to FTS5 MATCH. Unmatched quotes, `AND`, `NEAR(`, `*` are valid FTS5 syntax that causes `sqlite3.OperationalError`. The exception propagates as a 500 with no envelope. Fix: quote-escape tokens or wrap in a try/except that returns 400.

**S-H3 — `echo=True` Logs All SQL With Bound Parameters in Dev Mode** (`db/database.py:12`)
SQL echo dumps every query including recipe content and `raw_source_text` to stdout/logs when `NODE_ENV=development` (the default for local use). Not a remote risk, but raw source text (which may contain personal recipes, family notes) is exposed in plaintext logs.

### Medium

**S-M1 — CORS Blocks Intended LAN Use** (`main.py:90-95`)
`allow_origins` only lists `localhost:3000` and `127.0.0.1:3000`. The product spec states "accessible via browser over the home network" — any LAN IP origin is blocked. Fix: make `CORS_ORIGINS` an env variable with sane default.

**S-M2 — No Request Body Size Limit**
Neither FastAPI nor the nginx config sets a maximum request body size (nginx defaults to 1 MB but is not configured here). The 20 MB media limit exists only after full read-into-memory. For non-media endpoints (recipe create with very large `raw_source_text`), no size guard exists.

**S-M3 — FastAPI Auto-Docs Exposed to LAN** (`/docs`, `/redoc`, `/openapi.json`)
The interactive API docs are accessible to any LAN device. For a local-first tool with no auth, this is low-risk but exposes the full API surface. Consider disabling in "production" mode via `docs_url=None if not settings.debug else "/docs"`.

**S-M4 — Batch Intake Leaks Internal Exception Messages to Clients** (`routes/intake.py:117`)
`errors.append(BatchIntakeJobError(index=idx, message=str(exc)))` serialises raw Python exception text (including stack trace snippets) directly into the API response. For a local app this is acceptable debugging info, but it's worth noting as a data-exposure pattern.

### Low

**S-L1** — No authentication (intentional for single-user local app; documented risk). Any device on the LAN can read and write the full archive.
**S-L2** — Docker containers run as root (no `USER` directive in Dockerfiles). Escape from container yields root on host.
**S-L3** — Source maps enabled unconditionally in the Vite production build (`vite.config.ts`). Exposes full TypeScript source to anyone who can access the frontend bundle.
**S-L4** — `httpx` is listed only in dev dependencies (`pyproject.toml`) but is used in production AI code.
**S-L5** — No AI prompt injection defence. User-controlled recipe text is embedded directly into LM Studio prompts. For a local single-user archive this is self-attack only, but worth noting.

### Positive Observations
Parameterised SQL throughout, Pydantic validation on all inputs, AI output staging with human approval gate, MIME type allowlist on uploads, UUID-based file naming (no user-controlled filenames), no `dangerouslySetInnerHTML` in the frontend, no secrets in the codebase, comprehensive `.gitignore` (`.env` excluded).

---

## Performance Findings

### High (meaningful even for a single user with 300–500 recipes)

**P-H1 — `get_recipe()` Commits `last_viewed_at` on Every Call Including Mutations** (`services/recipe_service.py:185-197`)
Every recipe page load, every AI endpoint, every archive/update/delete does a WAL write+commit for `last_viewed_at` before the actual operation. At `synchronous=FULL` (the SQLite default) this is ~3–8 ms added to every recipe interaction.

**P-H2 — Missing Composite Index for the Default Library Query** (`migrations/001_initial_schema.sql`)
No index on `(archived, updated_at DESC)` — the most common query path (non-archived recipes sorted by updated_at). Full table scan on every library page load. Perceptible above ~300 recipes. Also missing: `updated_at DESC` index, `last_cooked_at` index, `archived` standalone index.

**P-H3 — Double Commit on Every Mutation** (`recipe_service.py` write paths)
`update_recipe`, `archive_recipe`, `unarchive_recipe`, `set_favorite`, `delete_recipe` all begin by calling `get_recipe()` which commits `last_viewed_at`, then commit again for the actual change. Two WAL syncs per mutation.

### Medium

**P-M1 — No SQLite Connection Pragmas on SQLAlchemy Engine** (`db/database.py`)
WAL mode is set in `init_db.py` via a raw `sqlite3` connection that immediately closes; the SQLAlchemy engine has no PRAGMA configuration at all. Missing: `synchronous=NORMAL` (safe with WAL; halves fsync overhead), `cache_size=-32000` (32 MB page cache across requests), `temp_store=MEMORY`, `foreign_keys=ON`. Fix: add `event.listens_for(engine, "connect")` handler.

**P-M2 — `ingredient_family` Filter Runs Two Unindexed Full Scans** (`recipe_service.py:200-217, 285-296`)
Both the facet-counts endpoint and the `ingredient_family` filter use `json_each()` subqueries with no supporting index. Each call scans every row. At 500 recipes this is ~5–15 ms; worse under combined filters.

**P-M3 — Synchronous `httpx` Blocks the Async Event Loop** (`ai/lm_studio_client.py:65-83, 110-127`)
All AI route handlers are `async def` but call synchronous `httpx.Client`. A 60-second LM Studio inference blocks the uvicorn worker — the user cannot load the library or any other page while AI is running. Fix: `await asyncio.to_thread(...)` or switch to `httpx.AsyncClient`.

**P-M4 — `list_recipes()` Executes Two SQL Queries (count + fetch)** (`recipe_service.py:298-302`)
`query.count()` then `query.all()`. When `ingredient_family` filtering is active, the unindexed subquery runs twice.

### Low

**P-L1** — `httpx.Client` created and destroyed per AI call (minor TCP overhead; connection to localhost is ~0.1 ms).
**P-L2** — `unique_slug()` queries once per collision attempt (harmless for normal use; could spike during bulk import of 50 duplicate titles).
**P-L3** — `RecipeRow` spreads style object on every hover render (50 × sub-ms; imperceptible).
**P-L4** — `FilterPanel` not wrapped in `React.memo` (re-renders on every 300 ms search debounce; trivial at home-archive scale).
**P-L5** — `similar_recipes` serialises up to 21 full recipe ORM objects including all ingredients for the AI prompt (correct behaviour, but memory footprint grows with ingredient count).

### What Breaks First at 500 Recipes (ranked)
1. Library page slows — no `(archived, updated_at DESC)` index
2. Every page view adds unnecessary WAL commit — `last_viewed_at` on reads
3. Ingredient-family filter/counts — unindexed `json_each()` scan
4. AI operations block all other browser tabs
5. Double-commit per mutation — 2× WAL sync on archive/edit/favorite

---

## Critical Issues for Phase 3 Context

1. **S-C1 path traversal** — no test currently exercises the file-serving path with a malicious `relative_path`; a security test is warranted.
2. **S-H2 FTS5 injection** — no test sends special FTS5 characters in the search parameter; a test for the 500 → 400 error path is missing.
3. **S-M1 CORS** — no test verifies LAN-origin requests are handled; the intended home-network use case is untested at the HTTP layer.
4. **P-H2 missing indexes** — no migration adds the `(archived, updated_at DESC)` composite index; the schema-spec and migration files should be checked for consistency.
5. **P-M3 blocking AI calls** — the test suite mocks all AI calls; no test exercises the async/sync boundary.
6. **S-M4 batch exception leakage** — the batch test does verify error shape but does not assert that internal exception details are sanitised.
