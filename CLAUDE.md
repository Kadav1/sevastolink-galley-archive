# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sevastolink Galley Archive** is a local-first, self-hosted recipe archive for serious home cooks. It runs entirely on the user's machine and is accessible via browser over the home network. AI assistance (via LM Studio) is optional — every workflow must function without it.

This is a **specification-first project** — read the specs before adding features. Implementation is underway. See the Implementation Status section below for what has been built.

## Workflow Preferences

- Be concise. Avoid exploratory brainstorming unless explicitly requested.
- When working on multi-phase plans, checkpoint progress so work can resume cleanly if usage limits are hit.

## Project Documentation Standards

- When creating or updating CLAUDE.md files, always analyze the actual codebase first (commands, architecture, dependencies, patterns) before writing.
- Include: build/dev commands, architecture overview, key patterns, design system details, and known gotchas.

## Change Safety

- Before major dependency upgrades or feature removals, thoroughly investigate what parts of the codebase will break BEFORE proposing a plan.
- Run tests after any structural changes (dependency updates, config changes, file moves).

## Essential Reading

Before implementing anything, read these in order:
1. `docs/01_product/product-brief.md` — Vision, scope, and what this is NOT
2. `docs/06_architecture/technical-architecture.md` — Complete stack and architectural decisions
3. `docs/08_database/schema-spec.md` — SQLite schema and data model
4. `docs/07_api/api-spec.md` — API endpoint contracts

## Technology Stack

**Backend:** Python 3.12, FastAPI, Pydantic, SQLAlchemy or SQLModel, SQLite (with FTS5)
**Frontend:** React + TypeScript, Vite, React Router, TanStack Query, CSS variables
**AI (optional):** LM Studio HTTP client (OpenAI-compatible endpoint)
**Infra:** Docker Compose, Nginx (optional), Systemd (optional)
**Node:** v20

**Primary languages:** TypeScript, Markdown, JSON. Always use TypeScript (not JavaScript) for new code files. CSS changes must respect the existing design token system (`packages/shared-ui-tokens/tokens.css`).

## Commands

**Working directory matters** — always run backend commands from `apps/api/` and frontend commands from `apps/web/`.

```bash
# Backend — from apps/api/
python -m pytest tests/test_intake.py -q          # intake tests
python -m pytest tests/ -q                        # all tests
python -m uvicorn src.main:app --reload           # dev server (port 8000)

# Frontend — from apps/web/
npm run type-check    # TypeScript check (no emit)
npm run dev           # Vite dev server
npm run build         # production build
```

Shared packages live in `packages/` (shared-types, shared-taxonomy, shared-prompts, shared-ui-tokens) — not yet implemented.

## Architecture

### Monolith, Not Microservices

Single FastAPI service + single React SPA + single SQLite database. No microservice decomposition in v1.

### Data Model (Non-Negotiable)

Three distinct entities must remain separate — this is architectural, not incidental:

```
Raw Source → Intake Job → Structured Candidate → Review → Approved Recipe
(preserved)              (staged, AI-enriched)  (edited)  (user-accepted)
```

- `intake_jobs` — tracks import workflow state
- `structured_candidates` — pre-approval staging; AI output lives here, never directly in recipes
- `recipes` — the canonical archive; only user-approved records

### Trust and Verification

Verification states (`Draft`, `Unverified`, `Verified`, `Archived`) are user-controlled only. AI cannot set or modify verification state. This boundary must be enforced at the API layer.

### Search Architecture (v1)

- **Full-text search:** SQLite FTS5 on title, notes, source text
- **Faceted filtering:** Direct SQL WHERE clauses on normalized taxonomy fields
- **Multi-select taxonomy:** Stored as JSON arrays, queried via `json_each()`
- **No semantic/vector search in v1** — directories exist for future embeddings but are out of scope

### Taxonomy System

11-layer classification (dish role, cuisine, technique family, ingredient families, complexity, time class, service format, season/mood, storage profile, dietary filters, Sevastolink overlay). All vocabularies are defined in `docs/04_taxonomy/content-taxonomy-spec.md` and will be implemented in `packages/shared-taxonomy/`.

### AI Integration Constraints

- All AI calls are user-initiated — no background enrichment
- AI suggestions go to `structured_candidates`, never directly to `recipes`
- Every AI workflow has a manual fallback path
- LM Studio integration via `LM_STUDIO_BASE_URL` (default: `http://localhost:1234/v1`)
- Recommended local normalization model: `Qwen/Qwen2.5-7B-Instruct`

## Local Data Paths

```
data/db/galley.sqlite       — SQLite database
data/media/                 — Recipe photos and media assets
data/imports/               — Raw source files (preserved, never modified)
data/exports/               — Backup/restore archives
data/embeddings/            — Future semantic search (v1 out of scope)
data/logs/                  — Application logs
```

## Environment Configuration

Copy `.env.example` to `.env`. Key variables:
- `DATABASE_URL=sqlite:./data/db/galley.sqlite`
- `LM_STUDIO_ENABLED=false` — AI is off by default
- `LM_STUDIO_BASE_URL=http://localhost:1234/v1`
- `LM_STUDIO_BASE_URL=http://192.168.1.91:1234/v1` — example if LM Studio runs on another machine on the home network
- `LM_STUDIO_MODEL=Qwen/Qwen2.5-7B-Instruct` — recommended tested normalization model, still optional

## Implementation Status

**Backend (`apps/api/`):** Recipe CRUD + search, intake pipeline (create job → update candidate → approve), AI normalize endpoint (`POST /intake-jobs/:id/normalize`), LM Studio client + normalizer.

**Frontend (`apps/web/`):** Library page, Recipe Detail, Kitchen Mode (`/recipe/:slug/kitchen`), Intake Hub, Manual Entry, Paste Text (with AI normalize button).

**Tests:** `apps/api/tests/test_intake.py` — 13 tests covering intake lifecycle and normalize endpoint.

## Known Gotchas

**DB CHECK constraints** — SQLite enforces enum values at commit time, not at ORM level. Allowed values:
- `intake_jobs.status`: `captured | in_review | approved`
- `intake_jobs.review_status`: `not_started | in_progress | saved_partial | completed`
- `structured_candidates.candidate_status`: `pending | in_review | accepted | discarded`
- `SourceType` enum (Python): `Manual, Book, Website, Family Recipe, Screenshot, PDF, Image / Scan, AI-Normalized, Composite / Merged` — no `paste_text` value

**TypeScript lib** — `tsconfig.json` uses `lib: ["ES2022", ...]` (not ES2020) to support `Array.at()`.

**AI module imports** — import `normalize_recipe` at module level in route files, not inside function bodies, or mock patching in tests will fail.

**AI prompt/schema paths** — normalizer loads from:
- `prompts/runtime/normalization/recipe-normalization-v1.md`
- `prompts/schemas/recipe-normalization-output.schema.json`

**Kitchen Mode** — `/recipe/:slug/kitchen` lives outside `AppShell` (no side nav). Root element uses `data-mode="kitchen"` which activates larger type/spacing overrides already defined in `apps/web/src/styles/tokens.css`.

**CSS tokens** — `packages/shared-ui-tokens/tokens.css` is the canonical token source. `apps/web/src/styles/tokens.css` is a thin `@import` shim — do not add tokens there.

**Step-text scaling** — `scaleStepText()` in `apps/web/src/lib/scaling.ts`; used by both `StepList` (recipe detail) and `KitchenSteps` (kitchen mode). `KitchenSteps` already accepts `scale: ScaleFactor` prop.

**Favorite toggle** — `apps/web/src/hooks/useFavorite.ts`; used by both `RecipeRow` and `RecipePage`. Invalidates `["recipes"]` and `["recipe", slug]` on success.

## What Is Explicitly Out of Scope (v1)

Do not implement: multi-user collaboration, cloud hosting, real-time sync, distributed workers, remote vector databases, background AI enrichment at scale, or microservice decomposition.
