# Stack Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a minimally runnable local foundation: FastAPI health endpoint + SQLite schema + React shell with routes.

**Architecture:** Single FastAPI service (Python 3.12) + React/Vite SPA sharing one SQLite database. No client-side DB access. Frontend proxies `/api` to `:8000` in dev. Production: backend serves built frontend from `apps/web/dist`.

**Tech Stack:** Python 3.12, FastAPI 0.128+, Pydantic v2, SQLAlchemy 2.0, SQLite (via aiosqlite), React 18, TypeScript 5, Vite 5, React Router v6, TanStack Query v5.

---

## File Map

### Backend (apps/api/)
- Create: `apps/api/pyproject.toml` — project metadata, deps, dev deps
- Create: `apps/api/src/__init__.py`
- Create: `apps/api/src/main.py` — FastAPI app, lifespan, CORS, health route mount
- Create: `apps/api/src/config/__init__.py`
- Create: `apps/api/src/config/settings.py` — Pydantic BaseSettings from env
- Create: `apps/api/src/routes/__init__.py`
- Create: `apps/api/src/routes/health.py` — GET /api/health
- Create: `apps/api/src/db/__init__.py`
- Create: `apps/api/src/db/database.py` — engine, session factory, get_db
- Create: `apps/api/src/db/init_db.py` — migration runner
- Create: `apps/api/src/db/migrations/001_initial_schema.sql` — complete v1 schema
- Create: `apps/api/src/models/__init__.py`
- Create: `apps/api/src/models/recipe.py` — SQLAlchemy ORM for recipes + related tables
- Create: `apps/api/src/models/intake.py` — intake_jobs, structured_candidates
- Create: `apps/api/src/models/media.py` — media_assets, ai_jobs
- Create: `apps/api/src/schemas/__init__.py`
- Create: `apps/api/src/schemas/recipe.py` — Pydantic response/request models
- Create: `apps/api/tests/__init__.py`
- Create: `apps/api/tests/test_health.py` — health endpoint test

### Frontend (apps/web/)
- Create: `apps/web/package.json`
- Create: `apps/web/vite.config.ts`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/tsconfig.node.json`
- Create: `apps/web/index.html`
- Create: `apps/web/src/vite-env.d.ts`
- Create: `apps/web/src/main.tsx`
- Create: `apps/web/src/App.tsx`
- Create: `apps/web/src/app/router.tsx`
- Create: `apps/web/src/styles/tokens.css`
- Create: `apps/web/src/styles/global.css`
- Create: `apps/web/src/components/shell/AppShell.tsx`
- Create: `apps/web/src/components/shell/SideNav.tsx`
- Create: `apps/web/src/pages/LibraryPage.tsx`
- Create: `apps/web/src/pages/RecipePage.tsx`
- Create: `apps/web/src/pages/KitchenPage.tsx`
- Create: `apps/web/src/pages/IntakePage.tsx`
- Create: `apps/web/src/pages/SettingsPage.tsx`

### Shared packages
- Create: `packages/shared-types/package.json`
- Create: `packages/shared-types/src/index.ts`

---

## Task 1: Backend project setup

**Files:** `apps/api/pyproject.toml`, `apps/api/src/__init__.py`

- [ ] Create `pyproject.toml` with fastapi, uvicorn[standard], pydantic-settings, sqlalchemy, aiosqlite, httpx as deps; pytest, httpx as dev deps
- [ ] Create empty `src/__init__.py`
- [ ] Run: `cd apps/api && pip install -e ".[dev]" --quiet`
- [ ] Verify: `python -c "import fastapi, pydantic, sqlalchemy; print('OK')"`

## Task 2: Backend config + health route

**Files:** `src/config/settings.py`, `src/routes/health.py`, `src/main.py`

- [ ] Write `settings.py` — Pydantic BaseSettings reading DATABASE_URL, MEDIA_DIR, API_PORT, LM_STUDIO_ENABLED, LM_STUDIO_BASE_URL
- [ ] Write `health.py` — GET /api/health returns `{"status": "ok", "service": "galley-api"}`
- [ ] Write `main.py` — FastAPI app with lifespan, CORS for localhost:3000, mount health router
- [ ] Verify: `python -c "from src.main import app; print(app.title)"`

## Task 3: Database schema migration

**Files:** `src/db/migrations/001_initial_schema.sql`, `src/db/database.py`, `src/db/init_db.py`

- [ ] Write complete v1 SQL schema into `001_initial_schema.sql` (all tables from schema-spec.md)
- [ ] Write `database.py` — SQLAlchemy async engine pointing at DATABASE_URL, `get_db` session dependency
- [ ] Write `init_db.py` — reads `schema_migrations`, runs unapplied `.sql` files in order
- [ ] Verify: `DATABASE_URL=sqlite+aiosqlite:///../../data/db/galley.sqlite python -c "import asyncio; from src.db.init_db import init_db; asyncio.run(init_db())"`
- [ ] Verify tables: `sqlite3 ../../data/db/galley.sqlite ".tables"`

## Task 4: SQLAlchemy models

**Files:** `src/models/recipe.py`, `src/models/intake.py`, `src/models/media.py`

- [ ] Write `recipe.py` — Recipe, RecipeIngredient, RecipeStep, RecipeNote, RecipeSource ORM classes
- [ ] Write `intake.py` — IntakeJob, StructuredCandidate, CandidateIngredient, CandidateStep ORM classes
- [ ] Write `media.py` — MediaAsset, AIJob ORM classes
- [ ] Verify: `python -c "from src.models.recipe import Recipe; from src.models.intake import IntakeJob; print('models OK')"`

## Task 5: Pydantic schemas

**Files:** `src/schemas/recipe.py`

- [ ] Write minimal Pydantic v2 schemas: VerificationState enum, RecipeBase, RecipeSummary, HealthResponse
- [ ] Verify: `python -c "from src.schemas.recipe import VerificationState; print(list(VerificationState))"`

## Task 6: Health endpoint test

**Files:** `tests/test_health.py`

- [ ] Write test using HTTPX AsyncClient + app fixture
- [ ] Run: `cd apps/api && pytest tests/test_health.py -v`
- [ ] Expected: PASSED

## Task 7: Frontend project setup

**Files:** `apps/web/package.json`, `vite.config.ts`, `tsconfig.json`, `tsconfig.node.json`, `index.html`

- [ ] Write `package.json` with react, react-dom, react-router-dom, @tanstack/react-query as deps; vite, @vitejs/plugin-react, typescript as devDeps
- [ ] Write `vite.config.ts` with react plugin + proxy `/api` → `http://localhost:8000`
- [ ] Write `tsconfig.json` targeting ES2020, strict mode
- [ ] Write `index.html` minimal HTML shell
- [ ] Run: `cd apps/web && npm install`
- [ ] Verify: `npm run build` passes

## Task 8: CSS design tokens + global styles

**Files:** `src/styles/tokens.css`, `src/styles/global.css`

- [ ] Write `tokens.css` — all CSS custom properties: surface hierarchy (bg/base → bg/overlay), text roles, border roles, state/signal colors, typography scale, spacing scale
- [ ] Write `global.css` — reset, body base, font stack import reference, box-sizing

## Task 9: App shell + routing

**Files:** `src/main.tsx`, `src/App.tsx`, `src/app/router.tsx`, `src/components/shell/AppShell.tsx`, `src/components/shell/SideNav.tsx`

- [ ] Write `router.tsx` — createBrowserRouter with routes: /, /library, /recipe/:slug, /recipe/:slug/kitchen, /intake, /settings
- [ ] Write `AppShell.tsx` — left SideNav + `<Outlet />` main area
- [ ] Write `SideNav.tsx` — NavLink entries for Library, Intake, AI Tools, Settings using token-based styles
- [ ] Write `App.tsx` — QueryClientProvider + RouterProvider
- [ ] Write `main.tsx` — ReactDOM.createRoot render

## Task 10: Page stubs

**Files:** all pages

- [ ] Write 5 page placeholder components (Library, Recipe, Kitchen, Intake, Settings) — each shows zone name in a structured placeholder, no lorem ipsum
- [ ] Verify: `npm run build` (TS + Vite compile check)
- [ ] Verify: `npm run type-check` if script defined, else `npx tsc --noEmit`

## Task 11: Shared types package

**Files:** `packages/shared-types/package.json`, `packages/shared-types/src/index.ts`

- [ ] Write `package.json` as a private ESM package
- [ ] Write `index.ts` exporting: VerificationState, IntakeStatus, IntakeType, RecipeSummary type stubs
- [ ] Verify: `cd packages/shared-types && npx tsc --noEmit` (or just ensure no errors)

---

## Verification Commands (final)

```bash
# Backend health check
cd /media/blndsft/SLP-ARCH-01/azwerks/sevastolink-galley-archive/apps/api
python -c "from src.main import app; print('API OK')"

# Database tables
sqlite3 /media/blndsft/SLP-ARCH-01/azwerks/sevastolink-galley-archive/data/db/galley.sqlite ".tables"

# Frontend build
cd /media/blndsft/SLP-ARCH-01/azwerks/sevastolink-galley-archive/apps/web
npm run build

# Run API
cd apps/api && uvicorn src.main:app --reload --port 8000
# Curl: curl http://localhost:8000/api/health
```
