# Sevastolink Galley Archive

## Current State Reference v1.0

---

## 1. Purpose

This document defines the current implemented state of Sevastolink Galley Archive.

It establishes:

* which major features are working today
* which routes and workflows are available in the current build
* which areas are present as placeholders only
* how the current codebase differs from the broader target-state specs
* where to look next for implementation-aware documentation

This document is the implementation baseline for contributors. It does not replace the canonical product, architecture, API, taxonomy, or database specs. It explains what is true in the repository now.

---

## 2. Current-state philosophy

### Established facts

* The repository already contains a runnable local stack with a FastAPI backend and React frontend.
* The current product is usable for recipe library browsing, recipe detail viewing, kitchen mode, manual recipe creation, paste-text intake, and AI-assisted normalization through LM Studio.
* The repository also contains prompt assets for more AI workflows than are currently surfaced in the product.
* The codebase also contains broader target-state specs that describe more functionality than is currently implemented.
* Contributors need a clean distinction between implemented behavior and planned behavior.

### Documentation standard

Current-state documentation should:

* describe only behavior that exists in the codebase now
* call out placeholders and deferred surfaces explicitly
* point back to the broader specs when those specs remain relevant
* avoid implying that an aspirational route or resource already works

---

## 3. Implemented application areas

### 3.1 Backend

The backend currently exposes:

* health endpoint under `/api/health`
* recipe endpoints under `/api/v1/recipes`
* intake endpoints under `/api/v1/intake-jobs`
* pantry suggestion endpoint under `/api/v1/pantry`
* settings endpoint under `/api/v1/settings`
* media attach and asset retrieval endpoints under `/api/v1/`
* automatic schema initialization on startup through the SQL migration runner

The backend does not currently expose separate implemented routers for:

* search
* AI job history
* backup management through HTTP
* system status endpoints beyond health

### 3.2 Frontend

The frontend currently provides:

* library landing and browse flow
* recipe detail view
* kitchen mode route
* intake hub
* manual-entry flow
* paste-text intake flow
* settings route placeholder

The frontend does not currently provide implemented screens for:

* URL import
* file or image intake
* dedicated AI tools screens
* settings sub-pages
* review-specific intake pages keyed by intake job ID

### 3.3 CLI and local operations

The repository currently includes working local scripts for:

* backup and restore
* raw recipe normalization into candidate bundles
* saved preprocessing artifacts for sequential one-model-at-a-time import runs
* candidate review, patching, ingest, and approval

These workflows are part of the working archive toolset even though they are not all surfaced in the web UI yet.

---

## 4. Current feature status

| Area | Status | Notes |
|---|---|---|
| Local Docker stack | Implemented | `make up`, `make up-detach`, `make up-proxy` |
| FastAPI health check | Implemented | `/api/health` |
| Recipe list/detail API | Implemented | CRUD plus favorite/archive actions |
| Intake job API | Implemented | create, get, update candidate, normalize, approve |
| LM Studio normalization | Implemented | Optional; degrades cleanly when disabled or unavailable |
| CLI preprocessing prompt flow | Implemented | The importer can emit saved `.preprocessed.txt` artifacts and later normalize from them |
| Library UI | Implemented | Main default route |
| Recipe detail UI | Implemented | Route-backed by slug |
| Kitchen mode UI | Implemented | Full-screen route |
| Manual entry UI | Implemented | Saves directly into archive |
| Paste-text intake UI | Implemented | Supports manual structuring and AI normalization |
| Settings UI | Placeholder | Route exists; page not implemented |
| URL import | Deferred | Mentioned in specs and intake UI as later work |
| File / image intake | Deferred | Mentioned in specs and intake UI as later work |
| Standalone AI tools area | Deferred | Not currently routed |
| HTTP settings API | Implemented | Settings persistence exists in the backend API, but the web settings page is still a placeholder |
| HTTP backup API | Deferred | Backup exists as shell workflow, not API resource |
| Runtime metadata / rewrite / pantry / similarity / evaluation prompt flows | Partially Implemented | Several AI-backed endpoints exist in the backend API, but they are not yet broadly surfaced as routed web product workflows |

---

## 5. Current route map

### 5.1 Web routes

The current frontend route model is:

* `/` → library
* `/library` → library
* `/recipe/:slug` → recipe detail
* `/recipe/:slug/kitchen` → kitchen mode
* `/intake` → intake hub
* `/intake/manual` → manual entry
* `/intake/paste` → paste-text intake
* `/settings` → settings placeholder

### 5.2 API routes

The current backend route model is:

* `/api/health`
* `/api/v1/recipes`
* `/api/v1/recipes/:id_or_slug`
* `/api/v1/recipes/:id_or_slug/archive`
* `/api/v1/recipes/:id_or_slug/unarchive`
* `/api/v1/recipes/:id_or_slug/favorite`
* `/api/v1/recipes/:id_or_slug/unfavorite`
* `/api/v1/recipes/:id_or_slug/suggest-metadata`
* `/api/v1/recipes/:id_or_slug/rewrite`
* `/api/v1/recipes/:id_or_slug/similar`
* `/api/v1/recipes/:id_or_slug/media`
* `/api/v1/intake-jobs`
* `/api/v1/intake-jobs/:job_id`
* `/api/v1/intake-jobs/:job_id/candidate`
* `/api/v1/intake-jobs/:job_id/normalize`
* `/api/v1/intake-jobs/:job_id/evaluate`
* `/api/v1/intake-jobs/:job_id/approve`
* `/api/v1/intake-jobs/:job_id/media`
* `/api/v1/pantry/suggest`
* `/api/v1/settings`
* `/api/v1/media-assets/:asset_id`
* `/api/v1/media-assets/:asset_id/file`

---

## 6. Current workflow summary

### 6.1 Recipe archive flow

The current archive flow is:

1. Browse recipes in the library.
2. Open a recipe by slug.
3. Toggle favorite state or archive state through the current recipe actions.
4. Enter kitchen mode from a recipe detail page.

### 6.2 Manual-entry flow

The current manual-entry flow is:

1. Go to `/intake/manual`.
2. Enter recipe fields directly.
3. Save the recipe into the canonical archive without an intake candidate review step.

### 6.3 Paste-text intake flow

The current paste-text flow is:

1. Go to `/intake/paste`.
2. Paste raw source text.
3. Create an intake job.
4. Optionally run AI normalization through LM Studio.
5. Edit the structured candidate fields.
6. Approve the intake job into a canonical recipe.

### 6.4 Bulk CLI import flow

The current CLI import flow is:

1. Place raw source files under `data/imports/raw/recipes`.
2. Run `scripts/import/normalize_recipes.py`.
3. Review candidate bundles with `scripts/import/review_candidates.py`.
4. Ingest or approve candidates through the intake service.

---

## 7. Relationship to the canonical specs

### Established facts

The repository contains mature target-state documents for:

* product direction
* UX and information architecture
* architecture
* API
* taxonomy
* database schema
* AI behavior
* operations

### Current-state interpretation

Those documents remain valuable, but they should be read as canonical design intent rather than a guarantee that every route, screen, or resource already exists in code.

When there is a conflict between:

* a target-state spec, and
* the currently implemented code

this document and the implementation-aware companion docs should be used to understand current behavior.

---

## 8. Companion implementation docs

Use these documents alongside this one:

* `docs/07_api/implemented-api.md` — implemented backend routes and payloads
* `docs/10_imports/recipe-import-workflow.md` — current CLI import and candidate review flow
* `docs/09_ops/configuration-reference.md` — current environment and runtime settings
* `docs/06_architecture/migrations-and-data-lifecycle.md` — current migration and persistence behavior
* `docs/02_ux/implemented-routes-and-flows.md` — current routed UI surfaces

---

## 9. Deferred areas

The following areas are clearly deferred in the current repository snapshot:

* settings management beyond the placeholder page
* standalone AI tools pages
* URL intake
* file and image intake
* standalone backend search and AI-job domains beyond the current mounted routes
* broader routed AI product surfaces beyond the currently implemented backend endpoints and intake normalization flow

---

## 10. Placeholder directory inventory

### 10.1 Purpose

The repository contains a number of scaffold directories retained with `.gitkeep`.

These should be interpreted as reserved implementation space, not as evidence that files are missing from the checkout.

### 10.2 Backend scaffold directories

The following backend directories currently exist as reserved structure but do not contain implemented module code:

* `apps/api/src/import/`
* `apps/api/src/media/`
* `apps/api/src/search/`

Current interpretation:

* these map to target-state domains described elsewhere in the docs
* the empty scaffold directories themselves are not the active implementation location
* media functionality is implemented today through mounted routes and services elsewhere in `apps/api/src/`

### 10.3 Frontend scaffold directories

The following frontend directories are currently scaffold-only:

* `apps/web/src/components/ai/`
* `apps/web/src/components/intake/`
* `apps/web/src/components/navigation/`
* `apps/web/src/features/ai/`
* `apps/web/src/features/intake/`
* `apps/web/src/features/library/`
* `apps/web/src/features/recipes/`
* `apps/web/src/features/search/`
* `apps/web/src/features/settings/`
* `apps/web/src/features/taxonomy/`

Current interpretation:

* the app currently uses a page-and-component structure rather than a populated feature-module structure
* these directories reserve future organization, but they are not where the current implementation lives

### 10.4 Shared package placeholders

The following package space is reserved but not materially implemented:

* `packages/shared-taxonomy/`

Current interpretation:

* this package has documentation only
* taxonomy truth currently lives in docs and runtime validation/constants, not in a populated shared package

### 10.5 Infra, scripts, and test placeholders

The following directories are present as reserved operational space without current implementation assets:

* `infra/docker/`
* `scripts/dev/`
* `scripts/migrate/`
* `scripts/seed/`
* `tests/e2e/`
* `tests/integration/`

Current interpretation:

* these areas signal intended expansion
* they should not be documented as active workflows until files are added and wired into the repo toolchain

### 10.6 Implementation guidance

When evaluating an empty scaffold directory in this repository:

* check whether current code imports or mounts that area
* check whether current-state docs describe it as implemented
* if neither is true, treat it as reserved structure rather than missing code

---

## 11. Build Prompt Coverage

### 11.1 Purpose

The repository contains a substantial build-time prompt archive under `prompts/build/`.

This material should be read as design and implementation provenance rather than as a guarantee that every prompted feature was fully executed in code.

### 11.2 Areas that clearly materialized

The following build-prompt areas largely correspond to real outputs in the repository:

* specification prompts under `prompts/build/claude/specs/` map closely to canonical docs under `docs/`
* many implementation session prompts under `prompts/build/claude/sessions/` map to real code or infra
* bootstrap, intake, AI normalization, kitchen mode, backup/restore, nginx, systemd, shared prompts, and shared UI tokens all have concrete repository outputs

### 11.3 Areas that only partially materialized

The following build-prompt themes are only partially reflected in the implemented codebase:

* search-domain and search-API work
* AI review/evaluation flow beyond the normalization path
* broader dev/migrate/seed scaffolding
* higher-level integration and end-to-end testing layers

### 11.4 Current interpretation

When reviewing `prompts/build/`:

* treat `specs/` as upstream prompt material for docs that mostly exist
* treat `sessions/` and `codegen/` as implementation history with partial completion in some areas
* do not assume that every prompt in `build/` corresponds to a finished feature in the running product

### 11.5 Session mapping for partial areas

The clearest build-session ownership for the remaining partial areas is:

* search-domain and search-API work:
  * `prompts/build/claude/sessions/session-02-library-and-detail.md`
  * companion codegen prompt: `prompts/build/claude/codegen/recipe-crud-search-api.md`
* AI review/evaluation flow beyond normalization:
  * `prompts/build/claude/sessions/session-04-ai-normalization.md`
  * companion codegen prompt: `prompts/build/claude/codegen/ai-normalization-review-flow.md`
* broader runtime prompt-family adoption beyond normalization:
  * `prompts/build/claude/sessions/session-11-shared-prompts-runtime-wiring.md`
  * companion codegen prompt: `prompts/build/claude/codegen/shared-prompts-package.md`
* higher-level dev/test/seed/migrate scaffolding:
  * no single numbered session fully owns this area
  * the closest implementation prompt is `prompts/build/claude/codegen/tests-and-dev-ergonomics.md`
  * `prompts/build/claude/sessions/session-07-docker-compose-integration.md` also references migrate/seed follow-through

---

## 12. Audit findings and next implementation areas

### 12.1 Search is only partially implemented

The current repository does support free-text recipe search and structured filtering on the recipe list endpoint.

However:

* search logic still lives inside the generic recipe service layer
* `apps/api/src/search/` remains scaffold-only
* there is no separately mounted search router matching the broader target-state API shape

Search therefore exists as implemented behavior, but not yet as a completed standalone backend domain.

### 12.2 AI review and prompt-family adoption are incomplete

The repository does implement AI-assisted normalization and approval through the current intake pipeline.

However:

* the practical review flow is still centered on paste-text intake and CLI candidate review
* there is no broader dedicated routed AI review surface keyed around evaluation or job-history workflows
* runtime prompt families for evaluation, metadata, rewrite, pantry, and similarity are implemented in the backend API, but not yet broadly productized in the routed web UI

Normalization is implemented, and several adjacent AI endpoints now exist, but the wider routed AI workflow implied by the prompt inventory has not fully materialized.

### 12.3 Dev, test, and operator scaffolding remain thin

The repository has working core commands, backend tests, and a passing frontend build.

However:

* `scripts/dev/`, `scripts/migrate/`, and `scripts/seed/` remain placeholder directories
* `tests/e2e/` and `tests/integration/` remain placeholder directories
* current developer and operator workflows still rely mostly on direct commands and documented manual steps rather than higher-level wrappers

This means the application is usable, but the surrounding ergonomics and higher-level safety rails remain thinner than some build prompts imply.

### 12.4 Settings is still a routed placeholder

The frontend exposes `/settings`, but the current settings page remains a placeholder surface rather than an implemented management workflow.

There is now a matching implemented HTTP settings API in the backend, but the routed web settings management workflow has not yet been built out.

### 12.5 New session prompts created from the audit

The repository now includes follow-on session prompts for the clearest unfinished areas:

* `prompts/build/claude/sessions/session-13-search-domain-and-library-search.md`
* `prompts/build/claude/sessions/session-14-ai-review-and-prompt-family-adoption.md`
* `prompts/build/claude/sessions/session-15-dev-test-and-ops-scaffolding.md`

These are next-step implementation prompts, not evidence that those areas are already complete.
