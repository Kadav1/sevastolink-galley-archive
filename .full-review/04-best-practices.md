# Phase 4: Best Practices & Standards

## Framework & Language Findings

### High

**BP-H1 — SQLAlchemy 1.x Query Style Throughout** (`services/recipe_service.py`, `services/intake_service.py`, `services/media_service.py`, `services/settings_service.py`)
The codebase uses `db.query(Model).filter(...)` everywhere — the SQLAlchemy 1.x legacy query interface. SQLAlchemy 2.0 deprecated this in favour of `select(Model)` with `db.execute(select(...)).scalars()`. The engine is pinned to `sqlalchemy>=2.0` in `pyproject.toml`, meaning the project is running a 2.x engine with 1.x queries.

```python
# Current (1.x style)
recipe = db.query(Recipe).filter(Recipe.slug == slug).first()

# SQLAlchemy 2.x idiomatic
from sqlalchemy import select
recipe = db.execute(select(Recipe).where(Recipe.slug == slug)).scalar_one_or_none()
```

This is not broken today (1.x query API is still present in SQLAlchemy 2.x as a legacy shim), but it will require a migration pass before upgrading to any future SQLAlchemy 3.x. Severity: High — the entire service layer uses this pattern.

**BP-H2 — `httpx` Listed Only as Dev Dependency but Used in Production** (`pyproject.toml:20-24`)
`httpx` appears in `[project.optional-dependencies] dev` but is used in `apps/api/src/ai/lm_studio_client.py` — production AI code. If the package is installed without `[dev]` extras (e.g., in a production Docker image), `import httpx` will raise `ModuleNotFoundError` and all AI endpoints will fail at startup.

```toml
# Fix: move httpx to production dependencies
[project]
dependencies = [
    ...
    "httpx>=0.27",
]
```

**BP-H3 — `aiosqlite` Listed as Production Dependency but Unused**
`pyproject.toml:17` lists `aiosqlite>=0.20` as a production dependency. The codebase uses synchronous SQLAlchemy (`sessionmaker`, `create_engine`) with no async engine — `aiosqlite` is never imported. This is dead weight in the production dependency set.

### Medium

**BP-M1 — FastAPI Lifespan Used Correctly, but `init_db()` Is Blocking in an Async Context** (`main.py:36-42`)
The `lifespan` context manager is the modern FastAPI pattern (vs deprecated `on_event`) — this is correct. However, `init_db()` calls `sqlite3.connect()` synchronously inside the `async` lifespan function. For a local app with sub-second DB init this is harmless, but it blocks the event loop during startup.

**BP-M2 — `db.query(Model)` with `.filter()` Uses Deprecated Keyword Syntax in Places** (`services/recipe_service.py`)
Some filter calls use positional comparison expressions (`Recipe.archived == False`) which is idiomatic for both 1.x and 2.x, but mixed throughout with raw `text()` SQL. The pattern is consistent but would benefit from full 2.x migration.

**BP-M3 — No `response_model` on Several Routes** (`routes/recipes.py`, `routes/intake.py`)
Several route handlers return dicts or call `model_dump()` manually rather than using FastAPI's `response_model` parameter with automatic serialisation. This bypasses FastAPI's automatic OpenAPI schema generation for those responses and means extra serialisation code in the route function.

```python
# Current
@router.get("/{id_or_slug}")
async def get_recipe(...):
    ...
    return {"data": detail.model_dump()}

# Idiomatic FastAPI
@router.get("/{id_or_slug}", response_model=RecipeDetailResponse)
async def get_recipe(...):
    ...
    return RecipeDetailResponse(data=detail)
```

**BP-M4 — Pydantic v2 `model_config` Used Correctly, But Some Models Missing It** (`schemas/recipe.py`)
`RecipeCreate` and `RecipeUpdate` have no `model_config`. `RecipeDetail` has `model_config = {"from_attributes": True}` — correct for ORM objects. `RecipeCreate` and `RecipeUpdate` are input models and don't need `from_attributes`, which is fine. However, `CandidateOut` in `schemas/intake.py` appears to need `from_attributes` but relies on manual field mapping instead (finding M-5 from Phase 1).

**BP-M5 — `Generator` Import from `typing` Instead of `collections.abc`** (`db/database.py:4`)
```python
from typing import Generator  # deprecated in Python 3.9+
```
Python 3.9+ recommends `from collections.abc import Generator`. The `typing` aliases still work in 3.12 but emit deprecation warnings in some linting contexts.

**BP-M6 — Source Maps Always Enabled in Production Build** (`vite.config.ts:29-31`)
```typescript
build: {
  outDir: "dist",
  sourcemap: true,  // always on, including production
}
```
Source maps expose the full TypeScript source to anyone accessing the bundle. For a home-network app this is low risk, but it's not idiomatic — the standard pattern is `sourcemap: process.env.NODE_ENV !== 'production'` or a separate `vite.config.prod.ts`.

**BP-M7 — No Frontend Test Runner Configured** (`package.json`)
The `scripts` section has `dev`, `build`, `preview`, `type-check` — no `test` script. Vitest is not installed. This is consistent with the zero frontend test coverage finding from Phase 3, but it means there's no framework in place to add tests.

### Low

**BP-L1** — `Mapped[str]` for JSON array columns (`models/recipe.py:47-52`). These should be `Mapped[str]` typed as `Text` columns — which they are — but a custom SQLAlchemy `TypeDecorator` that handles JSON serialisation/deserialisation at the ORM layer would eliminate the manual `json.dumps`/`json.loads` calls scattered across the service and schema layers.

**BP-L2** — `dataclass` used for AI error/result types in all AI modules. Python 3.12's `dataclass` is fine, but since these are immutable result containers, `@dataclass(frozen=True)` would be more appropriate and self-documenting.

**BP-L3** — TanStack Query `queryKey` arrays are constructed inline in each hook/component rather than using a centralised query key factory. For example, `["recipes", params]`, `["recipe", slug]`, `["settings"]` are scattered across `useRecipes.ts`, `useRecipe.ts`, `useSettings.ts`, and `LibraryPage.tsx`. A `queryKeys` factory object is the idiomatic TanStack Query v5 pattern.

**BP-L4** — `react-router-dom` is pinned to `^6.26.2`. React Router v7 was released and introduces the new framework mode. No action needed for v1, but worth noting for future upgrades.

**BP-L5** — No `.nvmrc` or `engines` field in `package.json` to enforce Node 20+. The `check.sh` script verifies this at runtime, but the package metadata doesn't declare the constraint.

---

## CI/CD & DevOps Findings

### High

**DO-H1 — Both Dockerfiles Run as Root**
Neither `apps/api/Dockerfile` nor `apps/web/Dockerfile` adds a `USER` directive. The API container runs as root inside Docker. Container escape or a path traversal exploit yields root-level access to the host filesystem — particularly relevant given the path traversal finding (S-C1) and the volume-mounted full repo.

```dockerfile
# Add to both Dockerfiles before CMD:
RUN addgroup --system galley && adduser --system --ingroup galley galley
USER galley
```

Note: data directory permissions must also be set to allow the non-root user to write.

**DO-H2 — Production Docker Image Installs Dev Dependencies** (`apps/api/Dockerfile:9`)
```dockerfile
RUN pip install --no-cache-dir -e ".[dev]"
```
The `[dev]` extras include `pytest`, `pytest-asyncio`, and `httpx` (see BP-H2 above). A production image should install only `pip install -e "."`. The `[dev]` extras should only be present in a dev/test image stage.

A multi-stage Dockerfile would resolve both this and DO-H1:
```dockerfile
FROM python:3.12-slim AS base
WORKDIR /repo/apps/api
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e "."  # production deps only

FROM base AS dev
RUN pip install --no-cache-dir -e ".[dev]"
```

**DO-H3 — No Health Check in `docker-compose.yml`**
Neither service has a `healthcheck:` directive. Docker has no way to know if the API is actually ready to serve requests — `galley-web`'s `depends_on: galley-api` only waits for the container to start, not for FastAPI to be ready. On slow machines or after a failed migration, the web container may start before the API is ready, causing connection errors on first load.

```yaml
galley-api:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 15s
```

### Medium

**DO-M1 — No CI Pipeline** (no `.github/` directory)
The project has no automated CI — no GitHub Actions, no pre-commit integration that runs server-side. `make secrets-scan` and `make install-git-hooks` suggest the infrastructure exists locally, but there's no server-side gate. A PR or push with broken tests, TypeScript errors, or hardcoded secrets would not be caught automatically.

A minimal GitHub Actions workflow would run:
1. `python -m pytest` (120 tests, ~2 min)
2. `npm run type-check`
3. `bash scripts/dev/scan_secrets.sh`

**DO-M2 — Nginx Config Has No Security Headers or Request Body Limit**
`infra/nginx/galley.conf` proxies requests but sets no:
- `client_max_body_size` (defaults to 1 MB; the API accepts up to 20 MB media, so this would silently 413 large uploads before they reach FastAPI)
- `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy` security headers
- `server_tokens off` (exposes nginx version)

```nginx
server {
    client_max_body_size 25m;  # slightly above the 20 MB API limit
    server_tokens off;

    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    ...
}
```

**DO-M3 — `backup-prune` Uses `find -mtime` Which Measures File Modification Time, Not Backup Age**
`Makefile:151`: `find data/backups/ -maxdepth 1 -type d -name 'galley-*' -mtime +$(KEEP_DAYS)`
`-mtime` measures when the directory entry was last modified, not when it was created. On some filesystems, moving or touching files inside the backup directory updates the parent's mtime. The backup timestamp is encoded in the directory name (`galley-YYYYMMDD-HHMMSS`) — pruning should parse that name instead of relying on filesystem mtime.

**DO-M4 — No Migration Rollback Strategy**
`scripts/migrate/run.sh` applies migrations in order with no rollback mechanism. If migration 004 fails halfway through, the database is in a partial state with no recovery path short of restoring from backup. For a local archive this is low-operational-risk (the operator can restore), but a `--dry-run` flag and a rollback SQL pattern (or at least a pre-migration backup step) would be safer.

**DO-M5 — `--reload` Flag in Production Dockerfile CMD**
`apps/api/Dockerfile:14`: `CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]`
`--reload` watches for file changes and restarts the server. This is appropriate for development but is wasteful in a deployed container where source files don't change. It also adds a file-watching process and can interfere with graceful shutdown. The CMD should use a production entrypoint without `--reload`, with a dev override in `docker-compose.yml` or a separate dev compose file.

### Low

**DO-L1** — `make clean` removes volumes (`docker compose down --volumes`) which could inadvertently wipe named volumes if any are ever added. The current compose uses only bind mounts, so this is safe today.

**DO-L2** — `make secrets-scan` references `scripts/dev/scan_secrets.sh` which does not appear to exist (not found in the file tree). If this script is absent, `make secrets-scan` fails silently or with an error.

**DO-L3** — `make install-git-hooks` references `scripts/dev/install_git_hooks.sh` which also does not appear to exist. Same risk as DO-L2.

**DO-L4** — No log rotation configuration for the rotating file handler beyond what's in `logging_config.py` (5 MB × 3 files). The `data/logs/` directory is not in `.gitignore` explicitly (though `data/` as a whole is excluded). The cron backup log at `data/logs/backup-cron.log` has no rotation.

**DO-L5** — The web Dockerfile uses `node:20-slim` as base. `node:20` is LTS but will reach end-of-life in April 2026 — upgrade to `node:22-slim` (current LTS) is warranted.
