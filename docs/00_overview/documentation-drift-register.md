# Documentation Drift Register

**Last reviewed:** 2026-04-05
**Purpose:** track confirmed drift between repository documentation and the current implementation, and distinguish that from intentional gaps where the code is still narrower than the broader target-state specs.

---

## 1. How to use this register

This file tracks two different kinds of mismatch:

* **Documentation drift**: an implementation-aware doc or current-state note says something that is no longer true in code.
* **Implementation drift against target-state spec**: the code now diverges from the broader product, UX, or visual-system guidance in a way that should be consciously resolved.

Status values:

* **Open** — confirmed and not yet corrected in the source doc or code
* **Intentional gap** — the broader spec remains aspirational; no correction to the spec is needed
* **Resolved** — source docs and code have been brought back into alignment

---

## 2. Audit scope for this pass

Docs checked against code in this review:

* `docs/00_overview/current-state.md`
* `docs/01_product/implemented-product.md`
* `docs/02_ux/implemented-routes-and-flows.md`
* `docs/02_ux/information-architecture.md`
* `docs/02_ux/screen-blueprint-pack.md`
* `docs/03_visual-system/implemented-visual-system.md`
* `docs/03_visual-system/visual-system-spec.md`
* `docs/04_taxonomy/implemented-taxonomy.md`
* `docs/05_ai/implemented-ai.md`
* `docs/06_architecture/implemented-architecture.md`
* `docs/07_api/implemented-api.md`
* `docs/08_database/implemented-database.md`
* `docs/09_ops/implemented-ops.md`
* `docs/10_imports/implemented-imports.md`

Implementation surfaces checked in this review:

* frontend router, shell, and routed pages in `apps/web/src/`
* backend routers, settings/config, models, migrations, and services in `apps/api/src/`
* operational and import scripts in `scripts/`
* shared taxonomy package in `packages/shared-taxonomy/`

Areas checked with no confirmed implementation-aware drift in this pass:

* `docs/04_taxonomy/implemented-taxonomy.md`
* `docs/05_ai/implemented-ai.md`
* `docs/10_imports/implemented-imports.md`

---

## 3. Confirmed Documentation Drift

### DR-001 — Current-state and UX docs understate the shipped frontend surface

**Severity:** High
**Status:** Open

Affected docs:

* `docs/00_overview/current-state.md`
* `docs/01_product/implemented-product.md`
* `docs/02_ux/implemented-routes-and-flows.md`

What the docs currently say:

* `/settings` is still a placeholder-only route
* pantry is not part of the routed web product surface
* AI-backed pantry and settings workflows are not yet meaningfully surfaced in the UI

What the code currently does:

* the router ships `/pantry` and `/settings`
* the side navigation exposes Pantry as a primary destination
* the settings page reads and PATCHes persisted settings and checks LM Studio health
* the pantry page is a routed AI-assisted retrieval workspace

Verified in code:

* `apps/web/src/app/router.tsx`
* `apps/web/src/components/shell/SideNav.tsx`
* `apps/web/src/pages/SettingsPage.tsx`
* `apps/web/src/pages/PantryPage.tsx`
* `apps/web/src/hooks/useSettings.ts`
* `apps/web/src/lib/settings-api.ts`

Recommended action:

* update the current-state, implemented-product, and implemented-routes docs to describe settings as narrow-but-functional and pantry as a real routed surface
* keep the broader target-state settings sub-pages and AI route groups documented as still unimplemented

### DR-002 — The current-state placeholder inventory is stale

**Severity:** High
**Status:** Open

Affected docs:

* `docs/00_overview/current-state.md`

What the docs currently say:

* `packages/shared-taxonomy/` is documentation-only
* `scripts/dev/`, `scripts/migrate/`, and `scripts/seed/` remain placeholder directories
* current dev and operator ergonomics are still mostly direct-command only

What the code currently does:

* `packages/shared-taxonomy/src/index.ts` is populated and consumed in the frontend
* `scripts/dev/` contains working helper scripts
* `scripts/migrate/run.sh` exists
* `scripts/seed/seed_dev.py` exists and is wired into `make seed-dev`

Verified in code:

* `packages/shared-taxonomy/src/index.ts`
* `scripts/dev/check.sh`
* `scripts/dev/install_git_hooks.sh`
* `scripts/dev/reset.sh`
* `scripts/dev/scan_secrets.sh`
* `scripts/migrate/run.sh`
* `scripts/seed/seed_dev.py`
* `Makefile`

Recommended action:

* rewrite the placeholder inventory for shared taxonomy and script helper directories
* preserve the distinction between “implemented helper layer” and “fully mature workflow”

### DR-003 — The implemented API doc omits live endpoints and one live filter parameter

**Severity:** High
**Status:** Open

Affected docs:

* `docs/07_api/implemented-api.md`

What the docs currently say:

* only the routes listed in `implemented-api.md` should be treated as live

What the code currently does beyond that list:

* `GET /api/v1/health/ai`
* `GET /api/v1/recipes/ingredient-families`
* `POST /api/v1/intake-jobs/batch`
* `GET /api/v1/recipes` also accepts the `ingredient_family` query parameter

Verified in code:

* `apps/api/src/main.py`
* `apps/api/src/routes/health.py`
* `apps/api/src/routes/recipes.py`
* `apps/api/src/routes/intake.py`

Recommended action:

* add the missing endpoints to `implemented-api.md`
* add `ingredient_family` to the query parameter table for `GET /api/v1/recipes`
* keep `/search`, `/ai-jobs`, `/backups`, and `/system` documented as intentionally unmounted

### DR-004 — The implemented architecture doc is stale about surfaced domains and tooling

**Severity:** Medium
**Status:** Open

Affected docs:

* `docs/06_architecture/implemented-architecture.md`

What the docs currently say:

* no standalone `media-assets` surface is mounted
* functional settings management is not implemented
* `scripts/dev`, `scripts/migrate`, and `scripts/seed` remain unimplemented richer tooling areas

What the code currently does:

* the media router mounts `GET /api/v1/media-assets/{asset_id}` and `GET /api/v1/media-assets/{asset_id}/file`
* the settings router exposes GET and PATCH behavior used by the web settings page
* helper scripts exist in `scripts/dev/`, `scripts/migrate/`, and `scripts/seed/`

Verified in code:

* `apps/api/src/main.py`
* `apps/api/src/routes/media.py`
* `apps/api/src/routes/settings.py`
* `scripts/dev/check.sh`
* `scripts/migrate/run.sh`
* `scripts/seed/seed_dev.py`

Recommended action:

* update the architecture doc to distinguish between “first-class resource domain” and “mounted operational surface”
* remove the claim that functional settings management does not exist

### DR-005 — The implemented database doc no longer matches the migration set and surfaced persistence

**Severity:** High
**Status:** Open

Affected docs:

* `docs/08_database/implemented-database.md`

What the docs currently say:

* the applied migration set is `001_initial_schema.sql`, `002_recipe_source_notes.sql`, and `003_intake_jobs_source_notes.sql`
* there is no mounted settings API
* there is no mounted media-assets API
* seed/example workflows are not materially implemented

What the code currently does:

* the migration set on disk is `001_initial_schema.sql`, `002_add_recipe_cover_media.sql`, `003_intake_jobs_source_notes.sql`, and `004_add_indexes.sql`
* `source_notes` for `recipe_sources` is already present in `001_initial_schema.sql`
* mounted settings and media-assets APIs exist
* a dev seed workflow exists via `scripts/seed/seed_dev.py`

Verified in code:

* `apps/api/src/db/init_db.py`
* `apps/api/src/db/migrations/001_initial_schema.sql`
* `apps/api/src/db/migrations/002_add_recipe_cover_media.sql`
* `apps/api/src/db/migrations/003_intake_jobs_source_notes.sql`
* `apps/api/src/db/migrations/004_add_indexes.sql`
* `apps/api/src/routes/settings.py`
* `apps/api/src/routes/media.py`
* `scripts/seed/seed_dev.py`

Recommended action:

* correct the migration inventory and the surfaced-persistence notes
* note that `ai_jobs` remains intentionally internal even though settings and media are now surfaced

### DR-006 — The implemented ops doc understates the current helper tooling

**Severity:** High
**Status:** Open

Affected docs:

* `docs/09_ops/implemented-ops.md`

What the docs currently say:

* there is no parallel `scripts/dev` layer
* there is no implemented `scripts/dev`, `scripts/migrate`, or `scripts/seed` helper layer
* there is no built-in scheduled backup tooling

What the code currently does:

* `scripts/dev/` contains environment checks, reset, secret scanning, and git-hook installation
* `scripts/migrate/run.sh` exists
* `scripts/seed/seed_dev.py` exists
* `scripts/backup/schedule-daily.sh` installs or removes a cron-based daily backup job
* the Makefile exposes `make dev-check`, `make seed-dev`, `make install-api`, `make install-web`, `make dev-api`, `make dev-web`, and `make build-web`

Verified in code:

* `scripts/dev/check.sh`
* `scripts/dev/install_git_hooks.sh`
* `scripts/dev/reset.sh`
* `scripts/dev/scan_secrets.sh`
* `scripts/migrate/run.sh`
* `scripts/seed/seed_dev.py`
* `scripts/backup/schedule-daily.sh`
* `Makefile`

Recommended action:

* update the ops docs to describe these helpers as real but still lightweight
* keep richer admin UI/API capabilities documented as still absent

### DR-007 — The current-state audit appendix is stale about AI surfacing and dev scaffolding

**Severity:** Medium
**Status:** Open

Affected docs:

* `docs/00_overview/current-state.md`

What the docs currently say:

* AI review and adjacent prompt-family adoption are not broadly productized in the routed UI
* `scripts/dev/`, `scripts/migrate/`, and `scripts/seed/` remain placeholders
* settings remains a routed placeholder despite the backend API existing

What the code currently does:

* recipe detail surfaces metadata suggestion, rewrite, and similar recipes
* pantry is routed in the web UI
* helper scripts and seed flows exist
* settings is functional enough to read and update persisted preferences

Verified in code:

* `apps/web/src/pages/RecipePage.tsx`
* `apps/web/src/pages/PantryPage.tsx`
* `apps/web/src/pages/SettingsPage.tsx`
* `scripts/dev/check.sh`
* `scripts/migrate/run.sh`
* `scripts/seed/seed_dev.py`

Recommended action:

* either update or retire the stale audit appendix in `current-state.md`
* prefer moving rolling drift observations into this register instead of embedding them in the current-state baseline

---

## 4. Confirmed Implementation Drift Against Broader Target-State Specs

### SD-001 — Pantry is exposed as a top-level route even though the IA says pantry assistance should stay subordinate

**Severity:** Medium
**Status:** Open

Target-state docs:

* `docs/02_ux/information-architecture.md`
* `docs/02_ux/screen-blueprint-pack.md`

What the broader docs say:

* pantry-driven decision support should live inside archive and retrieval flows
* AI tools are optional later utility surfaces
* the stable primary navigation is `Library`, `Intake`, `AI Tools`, and `Settings` in the blueprint pack, or `Library`, `Intake`, and `Settings` with optional later AI tools in the IA

What the code currently does:

* exposes Pantry as a top-level primary navigation destination
* routes Pantry at `/pantry`
* renders pantry suggestions as standalone result cards rather than handing users back into archive retrieval

Verified in code:

* `apps/web/src/components/shell/SideNav.tsx`
* `apps/web/src/app/router.tsx`
* `apps/web/src/pages/PantryPage.tsx`

Recommended action:

* decide whether Pantry should remain a top-level product surface or be folded back under archive or AI utility flows
* once that product decision is made, update either the code or the broader UX docs

### SD-002 — The settings screen violates the shared-token visual-system contract

**Severity:** Medium
**Status:** Open

Target-state docs:

* `docs/03_visual-system/visual-system-spec.md`
* `docs/03_visual-system/implemented-visual-system.md`

What the broader docs say:

* shared semantic tokens are the visual-system foundation
* the app should stay within the dark archive-first tonal system

What the code currently does:

* uses undeclared token names such as `--surface-base`, `--surface-muted`, `--color-error`, `--color-success`, and `--color-success-subtle`
* falls back to light success and muted backgrounds that are outside the shared token layer

Verified in code:

* `apps/web/src/pages/SettingsPage.tsx`
* `packages/shared-ui-tokens/tokens.css`

Recommended action:

* replace the undeclared tokens with shared visual-system tokens
* document any intentionally new tokens in the shared token source before using them in page code

---

## 5. Intentional Gaps That Are Still Narrower Than Target-State Specs

These are not documentation-drift findings from this pass. They remain legitimate implementation gaps relative to the broader target-state docs.

* no standalone `/search` backend domain; search remains part of recipe listing and filtering
* no `/ai-jobs`, `/backups`, or `/system` API domains
* no URL intake, file intake, or intake review routes in the web app
* no `/recipe/:slug/edit` route
* no settings sub-pages such as `/settings/archive` or `/settings/ai`
* no broad web review queue for filesystem candidate bundles
* no semantic search or embeddings runtime despite `EMBEDDINGS_DIR` in `.env.example`
* `ai_jobs` remains intentionally internal infrastructure rather than a surfaced product resource

---

## 6. Recommended Update Order

Suggested documentation repair order:

1. `docs/00_overview/current-state.md`
2. `docs/02_ux/implemented-routes-and-flows.md`
3. `docs/01_product/implemented-product.md`
4. `docs/07_api/implemented-api.md`
5. `docs/06_architecture/implemented-architecture.md`
6. `docs/08_database/implemented-database.md`
7. `docs/09_ops/implemented-ops.md`

Rationale:

* the highest-risk drift is in the “current truth” docs contributors are most likely to trust first
* API, architecture, database, and ops docs should then be corrected to match the now-expanded implementation surface
