# Documentation Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore trust in the repository’s implementation-aware documentation by correcting confirmed drift in the current-truth docs and keeping broader target-state specs clearly separate.

**Architecture:** Execute the repair wave in authority order: overview first, then implementation-aware UI/product/visual docs, then API, architecture, database, and ops. Use the drift register as the evidence base for every doc edit, and verify each claim against code references plus lightweight validation commands before marking the drift entry resolved.

**Tech Stack:** Markdown docs, git, ripgrep, sed, FastAPI route inspection, SQL migration file inspection, Makefile/script inspection, Vite production build verification

---

### Task 1: Refresh the overview truth layer

**Files:**
- Modify: `docs/00_overview/current-state.md`
- Modify: `docs/00_overview/documentation-drift-register.md`
- Reference: `apps/web/src/app/router.tsx`
- Reference: `apps/web/src/components/shell/SideNav.tsx`
- Reference: `apps/web/src/pages/SettingsPage.tsx`
- Reference: `apps/web/src/pages/PantryPage.tsx`
- Reference: `packages/shared-taxonomy/src/index.ts`
- Reference: `scripts/dev/check.sh`
- Reference: `scripts/migrate/run.sh`
- Reference: `scripts/seed/seed_dev.py`

- [ ] **Step 1: Re-open the overview and evidence docs together**

Run:

```bash
sed -n '60,180p' docs/00_overview/current-state.md
sed -n '248,446p' docs/00_overview/current-state.md
sed -n '1,260p' docs/00_overview/documentation-drift-register.md
```

Expected:

* `current-state.md` still describes `/settings` as a placeholder and omits `/pantry`
* the placeholder inventory still describes shared taxonomy and script helper directories as unimplemented
* the drift register contains the matching DR-001, DR-002, and DR-007 entries

- [ ] **Step 2: Verify the shipped UI and helper-layer facts before editing**

Run:

```bash
rg -n 'path: "pantry"|path: "settings"' apps/web/src/app/router.tsx
rg -n 'Pantry|Settings' apps/web/src/components/shell/SideNav.tsx
rg -n 'export function SettingsPage|export function PantryPage' apps/web/src/pages/SettingsPage.tsx apps/web/src/pages/PantryPage.tsx
find scripts/dev scripts/migrate scripts/seed -maxdepth 2 -type f | sort
rg -n 'export const DISH_ROLES|export const PRIMARY_CUISINES' packages/shared-taxonomy/src/index.ts
```

Expected:

* router and nav evidence confirm `/pantry` and `/settings` are live
* settings and pantry pages exist as routed pages
* helper scripts exist in `scripts/dev`, `scripts/migrate`, and `scripts/seed`
* `packages/shared-taxonomy/src/index.ts` is populated

- [ ] **Step 3: Update the frontend and deferred-surface sections in `current-state.md`**

Replace the stale frontend baseline with wording equivalent to:

```md
The frontend currently provides:

* library landing and browse flow
* recipe detail view
* kitchen mode route
* intake hub
* manual-entry flow
* paste-text intake flow
* pantry suggestion route
* settings management surface for persisted preferences and LM Studio status

The frontend does not currently provide implemented screens for:

* URL import
* file or image intake
* dedicated AI tools route group
* settings sub-pages
* review-specific intake pages keyed by intake job ID
```

Also replace stale deferred-area wording that still calls settings a placeholder or script helpers placeholders.

- [ ] **Step 4: Rewrite the placeholder inventory so it reflects current repo reality**

Update the shared-package and script sections in `docs/00_overview/current-state.md` to say:

```md
* `packages/shared-taxonomy/` is materially implemented and used by the frontend
* `scripts/dev/`, `scripts/migrate/`, and `scripts/seed/` contain lightweight but real helper tooling
* `tests/e2e/` and `tests/integration/` remain placeholder-only
```

Do not broaden this into a generic repo-tree rewrite. Only fix the areas verified in this audit.

- [ ] **Step 5: Mark the affected drift-register entries as resolved with short closure notes**

For `DR-001`, `DR-002`, and `DR-007` in `docs/00_overview/documentation-drift-register.md`, change status lines from:

```md
**Status:** Open
```

to:

```md
**Status:** Resolved
```

Add one short note under each recommended-action block naming the repaired docs:

```md
Resolution note:

* Repaired in `docs/00_overview/current-state.md` on 2026-04-05.
```

- [ ] **Step 6: Verify the overview truth layer edits**

Run:

```bash
git diff --check -- docs/00_overview/current-state.md docs/00_overview/documentation-drift-register.md
rg -n '/pantry|settings management surface|shared-taxonomy|scripts/dev|scripts/migrate|scripts/seed' docs/00_overview/current-state.md
```

Expected:

* `git diff --check` prints no output
* the overview doc now references pantry, functional settings, shared taxonomy, and helper scripts

- [ ] **Step 7: Commit the overview-layer repairs**

Run:

```bash
git add docs/00_overview/current-state.md docs/00_overview/documentation-drift-register.md
git commit -m "docs: align current-state overview"
```

Expected:

* one docs-only commit recording the overview truth-layer repairs

### Task 2: Refresh routed UI, product, and visual-system implementation docs

**Files:**
- Modify: `docs/02_ux/implemented-routes-and-flows.md`
- Modify: `docs/01_product/implemented-product.md`
- Modify: `docs/03_visual-system/implemented-visual-system.md`
- Modify: `docs/00_overview/documentation-drift-register.md`
- Reference: `apps/web/src/app/router.tsx`
- Reference: `apps/web/src/components/shell/AppShell.tsx`
- Reference: `apps/web/src/components/shell/SideNav.tsx`
- Reference: `apps/web/src/components/ui/ConfirmDialog.tsx`
- Reference: `apps/web/src/pages/SettingsPage.tsx`
- Reference: `apps/web/src/pages/PantryPage.tsx`
- Reference: `apps/web/src/pages/RecipePage.tsx`

- [ ] **Step 1: Re-verify UI surfaces and visual patterns before editing**

Run:

```bash
rg -n 'path: "pantry"|path: "settings"' apps/web/src/app/router.tsx
rg -n 'navOpen|backdrop|overlay' apps/web/src/components/shell/AppShell.tsx apps/web/src/components/shell/SideNav.tsx
rg -n 'ConfirmDialog' apps/web/src/pages/RecipePage.tsx apps/web/src/components/ui/ConfirmDialog.tsx
rg -n 'AI Tools|Suggest metadata|Rewrite recipe|Find similar' apps/web/src/pages/RecipePage.tsx
```

Expected:

* pantry and settings routes are present
* overlay nav and confirm dialog are implemented
* recipe-detail AI tools are visibly surfaced

- [ ] **Step 2: Update `implemented-routes-and-flows.md` to match the shipped route map**

Make these concrete edits:

```md
* change the route philosophy note so Settings is described as a narrow functional configuration surface rather than placeholder-only
* add `/pantry` to the current route map with status `Implemented`
* add a Pantry route behavior subsection describing ingredient-driven AI retrieval
* rewrite the Settings subsection to describe GET/PATCH-backed preferences plus LM Studio health checks
```

Use route names exactly as implemented:

```md
| `/pantry` | Implemented | Pantry suggestion workspace |
| `/settings` | Implemented | Settings surface for persisted preferences and AI status |
```

- [ ] **Step 3: Update `implemented-product.md` so product-surface claims match the shipped UI**

Rewrite the stale product summary and gap list to include:

```md
* pantry suggestion as a routed product surface
* settings management as a narrow implemented product area
* settings sub-pages still missing
* pantry still narrower than the broader retrieval target-state
```

Do not overstate Pantry as fully aligned with the broader IA. Keep it described as implemented but narrower than the target-state model.

- [ ] **Step 4: Update `implemented-visual-system.md` to reflect the actual transient surfaces**

Replace the stale “does not yet implement overlay, drawer, sheet, or modal surfaces” wording with language equivalent to:

```md
* the current frontend now implements limited transient surfaces:
  * mobile overlay navigation
  * modal confirmation dialog
* these are implemented as local component/page patterns rather than as a reusable primitive system
```

Also keep the broader “not yet fully implemented” caveat for a formal overlay/drawer/modal system.

- [ ] **Step 5: Resolve the matching drift-register entries**

In `docs/00_overview/documentation-drift-register.md`, update:

* `DR-001` -> `Resolved`
* `DR-004` visual portion remains `Open`

Add closure notes naming:

```md
* `docs/02_ux/implemented-routes-and-flows.md`
* `docs/01_product/implemented-product.md`
* `docs/03_visual-system/implemented-visual-system.md`
```

Do not resolve `SD-001` or `SD-002`; those are broader spec-alignment issues, not stale implementation-aware docs.

- [ ] **Step 6: Verify the UI/product/visual doc repairs**

Run:

```bash
git diff --check -- docs/02_ux/implemented-routes-and-flows.md docs/01_product/implemented-product.md docs/03_visual-system/implemented-visual-system.md docs/00_overview/documentation-drift-register.md
cd apps/web && npm run build
```

Expected:

* `git diff --check` prints no output
* the web build succeeds

- [ ] **Step 7: Commit the UI/product/visual repairs**

Run:

```bash
git add docs/02_ux/implemented-routes-and-flows.md docs/01_product/implemented-product.md docs/03_visual-system/implemented-visual-system.md docs/00_overview/documentation-drift-register.md
git commit -m "docs: align implemented ui and visual docs"
```

Expected:

* one docs-only commit for the routed UI, product, and visual-system baseline repairs

### Task 3: Refresh the implemented API reference

**Files:**
- Modify: `docs/07_api/implemented-api.md`
- Modify: `docs/00_overview/documentation-drift-register.md`
- Reference: `apps/api/src/main.py`
- Reference: `apps/api/src/routes/health.py`
- Reference: `apps/api/src/routes/recipes.py`
- Reference: `apps/api/src/routes/intake.py`
- Reference: `apps/api/src/routes/media.py`
- Reference: `apps/api/src/routes/settings.py`

- [ ] **Step 1: Re-run the API route inventory**

Run:

```bash
rg -n '@router\.(get|post|patch|delete)|include_router' apps/api/src/main.py apps/api/src/routes/*.py
```

Expected:

* output includes `/health/ai`
* output includes `/recipes/ingredient-families`
* output includes `/intake-jobs/batch`
* output includes the media-assets and settings routes

- [ ] **Step 2: Update the API scope section to include all mounted surfaces**

In `docs/07_api/implemented-api.md`, add these to the implementation-aware inventory:

```md
* `/api/v1/health/ai`
* `GET /api/v1/recipes/ingredient-families`
* `POST /api/v1/intake-jobs/batch`
```

Keep the existing statements that `/search`, `/ai-jobs`, `/backups`, and `/system` are not standalone route groups.

- [ ] **Step 3: Update the `GET /api/v1/recipes` parameter table**

Add the missing live filter row:

```md
| `ingredient_family` | string | Exact-match against a member of the recipe ingredient-family JSON array |
```

Do not invent any undocumented parameters beyond what the route handler actually accepts.

- [ ] **Step 4: Add missing endpoint sections for AI health, ingredient families, and batch intake**

Write short endpoint sections for:

```md
GET /api/v1/health/ai
GET /api/v1/recipes/ingredient-families
POST /api/v1/intake-jobs/batch
```

For `GET /api/v1/health/ai`, explicitly document the `ai_enabled`, `reachable`, `model`, and `error` response fields.

- [ ] **Step 5: Resolve the API drift-register entry**

In `docs/00_overview/documentation-drift-register.md`, change `DR-003` to `Resolved` and add:

```md
Resolution note:

* Repaired in `docs/07_api/implemented-api.md` on 2026-04-05.
```

- [ ] **Step 6: Verify the implemented API doc**

Run:

```bash
git diff --check -- docs/07_api/implemented-api.md docs/00_overview/documentation-drift-register.md
rg -n 'health/ai|ingredient-families|/batch|ingredient_family' docs/07_api/implemented-api.md
```

Expected:

* `git diff --check` prints no output
* the implemented API doc now includes each missing live endpoint and parameter

- [ ] **Step 7: Commit the API-doc repair**

Run:

```bash
git add docs/07_api/implemented-api.md docs/00_overview/documentation-drift-register.md
git commit -m "docs: align implemented api reference"
```

Expected:

* one docs-only commit for the implemented API repair

### Task 4: Refresh architecture, database, and ops implementation docs

**Files:**
- Modify: `docs/06_architecture/implemented-architecture.md`
- Modify: `docs/08_database/implemented-database.md`
- Modify: `docs/09_ops/implemented-ops.md`
- Modify: `docs/00_overview/documentation-drift-register.md`
- Reference: `apps/api/src/main.py`
- Reference: `apps/api/src/routes/media.py`
- Reference: `apps/api/src/routes/settings.py`
- Reference: `apps/api/src/db/init_db.py`
- Reference: `apps/api/src/db/migrations/001_initial_schema.sql`
- Reference: `apps/api/src/db/migrations/002_add_recipe_cover_media.sql`
- Reference: `apps/api/src/db/migrations/003_intake_jobs_source_notes.sql`
- Reference: `apps/api/src/db/migrations/004_add_indexes.sql`
- Reference: `scripts/dev/check.sh`
- Reference: `scripts/migrate/run.sh`
- Reference: `scripts/seed/seed_dev.py`
- Reference: `scripts/backup/schedule-daily.sh`
- Reference: `Makefile`

- [ ] **Step 1: Re-verify architecture, migration, and ops facts**

Run:

```bash
nl -ba apps/api/src/main.py | sed -n '89,98p'
find apps/api/src/db/migrations -maxdepth 1 -type f | sort
find scripts/dev scripts/migrate scripts/seed -maxdepth 2 -type f | sort
nl -ba scripts/backup/schedule-daily.sh | sed -n '1,80p'
```

Expected:

* `main.py` includes media and settings routers
* migrations include `002_add_recipe_cover_media.sql` and `004_add_indexes.sql`
* helper scripts and backup scheduler exist

- [ ] **Step 2: Update `implemented-architecture.md` to reflect mounted and helper surfaces**

Make these targeted edits:

```md
* change the media-domain wording from “first surfaced endpoint” to “limited mounted media surface”
* describe settings as a mounted functional preference surface
* replace the claim that `scripts/dev`, `scripts/migrate`, and `scripts/seed` are unimplemented with “lightweight helper tooling exists”
```

Keep the document honest about what is still missing:

* no standalone search domain
* no `/ai-jobs`, `/backups`, or `/system`
* no fuller repository-pattern separation

- [ ] **Step 3: Correct the migration and surfaced-persistence notes in `implemented-database.md`**

Replace the stale migration inventory with:

```md
* `001_initial_schema.sql`
* `002_add_recipe_cover_media.sql`
* `003_intake_jobs_source_notes.sql`
* `004_add_indexes.sql`
```

Also update the surfaced-persistence note so it says:

```md
* settings has a mounted API and a narrow web surface
* media-assets have mounted metadata/file endpoints
* `ai_jobs` remains internal-only
* a dev seed workflow exists, but there is not a broad operator seed pipeline
```

- [ ] **Step 4: Correct the helper-layer and backup-scheduler notes in `implemented-ops.md`**

Replace stale “not implemented” wording with text equivalent to:

```md
* `scripts/dev` now contains lightweight helper scripts
* `scripts/migrate/run.sh` exists as a migration wrapper
* `scripts/seed/seed_dev.py` exists as a dev seeding helper
* cron-based scheduled backup installation exists via `scripts/backup/schedule-daily.sh`
```

Keep the document clear that these are still lightweight operator helpers, not a richer admin UI or API.

- [ ] **Step 5: Resolve the remaining implementation-aware drift entries**

In `docs/00_overview/documentation-drift-register.md`, change these entries to `Resolved`:

* `DR-004`
* `DR-005`
* `DR-006`

Add resolution notes naming the repaired docs for each entry.

- [ ] **Step 6: Verify the architecture/database/ops doc repairs**

Run:

```bash
git diff --check -- docs/06_architecture/implemented-architecture.md docs/08_database/implemented-database.md docs/09_ops/implemented-ops.md docs/00_overview/documentation-drift-register.md
rg -n 'media-assets|functional settings|scripts/dev|scripts/migrate|scripts/seed|schedule-daily|004_add_indexes|002_add_recipe_cover_media' docs/06_architecture/implemented-architecture.md docs/08_database/implemented-database.md docs/09_ops/implemented-ops.md
```

Expected:

* `git diff --check` prints no output
* the updated docs now mention the mounted media/settings surfaces, the current migration set, the helper tooling, and the backup scheduler

- [ ] **Step 7: Commit the architecture/database/ops repairs**

Run:

```bash
git add docs/06_architecture/implemented-architecture.md docs/08_database/implemented-database.md docs/09_ops/implemented-ops.md docs/00_overview/documentation-drift-register.md
git commit -m "docs: align implementation reference docs"
```

Expected:

* one docs-only commit for the architecture, database, and ops repair wave

### Task 5: Final documentation reconciliation and handoff

**Files:**
- Modify: `docs/00_overview/documentation-drift-register.md`
- Modify: `docs/00_overview/current-state.md` (only if the repair wave exposed a remaining stale cross-link)
- Reference: `docs/superpowers/specs/2026-04-05-documentation-alignment-design.md`
- Reference: `docs/superpowers/plans/2026-04-05-documentation-alignment.md`

- [ ] **Step 1: Review the drift register after all source-doc repairs**

Run:

```bash
sed -n '1,320p' docs/00_overview/documentation-drift-register.md
```

Expected:

* implementation-aware drift entries repaired in Tasks 1-4 now show `Resolved`
* broader spec-alignment items such as Pantry navigation and settings token discipline remain `Open`
* intentional-gap section still lists genuine target-state gaps

- [ ] **Step 2: Normalize the register so only unresolved broader questions stay open**

Ensure the open items remaining are limited to:

```md
* `SD-001` — Pantry as a top-level product surface
* `SD-002` — Settings token misuse against the visual-system contract
* any still-unrepaired implementation-aware entry discovered during execution
```

Do not close broader design questions just because the implementation-aware docs were repaired.

- [ ] **Step 3: Run the final documentation verification pass**

Run:

```bash
git diff --check -- docs/00_overview docs/01_product docs/02_ux docs/03_visual-system docs/06_architecture docs/07_api docs/08_database docs/09_ops docs/superpowers/specs/2026-04-05-documentation-alignment-design.md docs/superpowers/plans/2026-04-05-documentation-alignment.md
cd apps/web && npm run build
```

Expected:

* `git diff --check` prints no output
* the frontend build succeeds

- [ ] **Step 4: Write the execution summary for the user**

Prepare a short summary covering:

```md
* which implementation-aware docs were repaired
* which drift-register entries were resolved
* which broader spec-alignment issues remain open
* which verification commands were run and their outcomes
```

Keep this summary in the final assistant response, not as a new repo file.

- [ ] **Step 5: Commit the final reconciliation pass**

Run:

```bash
git add docs/00_overview/documentation-drift-register.md docs/00_overview/current-state.md docs/01_product/implemented-product.md docs/02_ux/implemented-routes-and-flows.md docs/03_visual-system/implemented-visual-system.md docs/06_architecture/implemented-architecture.md docs/07_api/implemented-api.md docs/08_database/implemented-database.md docs/09_ops/implemented-ops.md docs/superpowers/specs/2026-04-05-documentation-alignment-design.md docs/superpowers/plans/2026-04-05-documentation-alignment.md
git commit -m "docs: complete documentation alignment wave"
```

Expected:

* one final docs-only commit capturing the completed documentation repair wave and plan artifacts
