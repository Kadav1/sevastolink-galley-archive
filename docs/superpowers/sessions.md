# Sevastolink Galley Archive — Build Sessions

Session prompts live in `prompts/build/claude/sessions/` (gitignored).
This document is the human-readable index.

---

## Phase 1 — Foundation (Sessions 01–12)

Core repository bootstrap, primary product surfaces, and infrastructure.

| # | Session | Description |
|---|---------|-------------|
| 01 | bootstrap | Repository setup: folder structure, tooling, initial schema migration, baseline API and frontend scaffold |
| 02 | library-and-detail | First archive-use vertical slice: Library page, Recipe Detail page, working data round-trip |
| 03 | intake | First intake workflow: paste-text job creation, candidate staging, approve-to-recipe pipeline |
| 04 | ai-normalization | AI-assisted intake: LM Studio client, normalize endpoint, AI pre-fill in intake form |
| 05 | kitchen-mode | Kitchen Mode: full-page recipe view outside AppShell, larger type, step-by-step reading experience |
| 06 | recipe-scaling-metadata-strip | Recipe scaling controls (½×, 1×, 2×, 3×) and metadata strip on Recipe Detail |
| 07 | docker-compose-integration | Docker Compose stack: web, API, and optional nginx in a single local compose file |
| 08 | local-deployment-backup-restore | Local deployment guide, backup and restore shell scripts, data directory discipline |
| 09 | nginx-reverse-proxy | Optional nginx reverse-proxy config for home-network serving |
| 10 | systemd-local-services | Optional systemd unit files for running the stack as persistent local services on Linux |
| 11 | shared-prompts-runtime-wiring | `packages/shared-prompts` package: prompt contract loader, backend wiring for all AI modules |
| 12 | shared-ui-tokens-and-adoption | `packages/shared-ui-tokens` package: canonical CSS token file, frontend adoption pass |

---

## Phase 2 — Feature Expansion (Sessions 13–21)

Search, editing, review flows, AI tools, and settings groundwork.

| # | Session | Description |
|---|---------|-------------|
| 13 | search-domain-and-library-search | Search domain decision, FTS5 + filter wiring, library search bar completion |
| 14 | ai-review-and-prompt-family-adoption | AI evaluation endpoint (`POST /intake-jobs/:id/evaluate`), prompt family adoption across all AI modules |
| 15 | dev-test-and-ops-scaffolding | Test scaffolding, dev tooling, ops helper scripts |
| 16 | library-route-expansion | Library page: sorting, pagination, filter sidebar, complexity and time-class filters |
| 17 | recipe-edit-flow | Recipe edit: in-place field editing, ingredient and step management on Recipe Detail |
| 18 | intake-route-expansion-and-review | Intake hub, manual-entry flow, intake review surface |
| 19 | settings-surface | First settings UI slice: placeholder settings page replaced with real preferences |
| 20 | ai-tools-area | AI tools route group: metadata suggestion, rewrite, and similar-recipe endpoints surfaced in the UI |
| 21 | shell-navigation-and-context-patterns | AppShell navigation, route context patterns, shell UX consistency pass |

---

## Phase 3 — Visual System (Sessions 22–26)

Responsive layout, shared primitives, and design system discipline.

| # | Session | Description |
|---|---------|-------------|
| 22 | responsive-layout-foundation | Responsive layout: AppShell breakpoints, mobile-aware grid, sidebar collapse |
| 23 | reusable-visual-primitives | Shared UI primitives: badges, status indicators, metadata chips |
| 24 | library-visual-refinement | Library page visual polish: recipe cards, filter panel, density and spacing pass |
| 25 | overlay-and-transient-surfaces | Overlay and transient surfaces: modals, drawers, confirmation dialogs |
| 26 | iconography-and-route-patterns | Icon system decision, route-level visual patterns, navigation icon consistency |

---

## Phase 4 — Taxonomy (Sessions 27–31)

Classification vocabulary, validation, and frontend adoption.

| # | Session | Description |
|---|---------|-------------|
| 27 | shared-taxonomy-foundation | `packages/shared-taxonomy` package: controlled vocabulary definitions, taxonomy exports |
| 28 | taxonomy-vocabulary-alignment | Backend vocabulary alignment: enum values, schema CHECK constraints, API validation |
| 29 | taxonomy-validation-expansion | Expanded taxonomy validation: broader field coverage, cross-field consistency |
| 30 | frontend-taxonomy-expansion | Frontend taxonomy adoption: dropdowns, multi-select controls, filter vocabulary |
| 31 | taxonomy-cleanup-and-drift-repair | Taxonomy drift repair: audit and fix mismatched values between code, schema, and docs |

---

## Phase 5 — Domain Completion (Sessions 32–44)

Settings API, media, error contracts, operations, AI productization.

| # | Session | Description |
|---|---------|-------------|
| 32 | settings-domain-and-api | Settings domain: `GET/PATCH /api/v1/settings`, persisted preferences, `ai_enabled` read-only signal |
| 33 | media-domain-first-slice | Media domain: source image/PDF attach to intake jobs and recipes, metadata retrieval, file serving |
| 34 | api-error-envelope-unification | API error contract: unify error response shape across all routes |
| 35 | schema-api-alignment | Schema/API alignment pass: close gaps between ORM models, Pydantic schemas, and API spec |
| 36 | migration-discipline-and-seed-strategy | Migration discipline: numbered SQL migration files, seed data strategy |
| 37 | import-domain-api-and-batch-execution | Import domain: batch intake API, file-based import workflows |
| 38 | ops-scheduling-and-observability | Ops maturity: logging discipline, scheduled backup, observability helpers |
| 39 | ingredient-first-retrieval-and-inspiration | Deterministic ingredient-first browsing: ingredient index, "what can I cook?" without AI |
| 40 | intake-evaluation-and-review-ux | Intake review UX: evaluation results display, candidate comparison, review decision flow |
| 41 | archive-enrichment-workflows | Archive enrichment: metadata suggestion (per-field apply) and rewrite (read-only) surfaced on Recipe Detail |
| 42 | ai-jobs-visibility-decision | AI jobs domain decision: expose `ai_jobs` records as a first-class API surface or document as internal |
| 43 | lm-studio-diagnostics-and-health | LM Studio diagnostics: health check endpoint, connection status in UI, degraded-mode messaging |
| 44 | retrieval-assistance-productization | AI retrieval assistance: pantry suggestion and similar-recipe finding surfaced as product flows |

---

## Status summary

Sessions implemented as of 2026-03-30:

- **01–12** — all implemented (foundation complete)
- **13** — search implemented (inside recipe service, no separate route group)
- **14** — evaluate endpoint implemented
- **16** — library filters and sort implemented
- **17** — recipe edit implemented
- **18** — intake hub, manual entry, paste text implemented
- **19, 32** — settings surface and API implemented
- **20** — AI tools endpoints implemented (metadata, rewrite, similar, pantry)
- **33** — media domain implemented (intake attach, recipe cover, metadata GET, file serve)

- **34** — API error envelope unification implemented
- **35** — Schema/API alignment: `IntakeJobOut` expanded (6 new fields), `ingredient_count` in `RecipeSummaryOut`, `sector`/`operational_class`/`heat_window` list filters, `title_desc` sort, migration 003 (`source_notes` on `intake_jobs`)
- **40** — Intake evaluation UX: `evaluateCandidate()` in `intake-api.ts`, "Evaluate normalization" button + inline `EvaluationPanel` on `PasteTextPage`
- **41** — Archive enrichment: `recipe-ai-api.ts` (types + API calls), `patchRecipe()` in `api.ts`, AI Tools section on Recipe Detail with per-field metadata apply and read-only rewrite panel
- **43** — LM Studio diagnostics: `GET /api/v1/health/ai` endpoint (`ai_router` in health.py), "Check connection" button on Settings page with inline reachability result, 3 new tests
- **44** — Retrieval assistance: `PantryPage` at `/pantry` (ingredient textarea → match cards + quick ideas), similar recipes panel on Recipe Detail ("Find similar" in AI Tools section), "Pantry" added to SideNav
- **21** — Shell navigation: root `/` redirects to `/library` (Library nav item now always active at root), `RecipePage` back button changed from `navigate(-1)` to `Link to="/library"` with consistent xs/tertiary/underline back-link style
- **36** — Migration discipline and seed strategy: `scripts/migrate/run.sh` (operator migration runner), `scripts/seed/seed_dev.py` (4 representative dev fixture recipes — shakshuka, braised short ribs, roast chicken, green salad — idempotent), `scripts/dev/reset.sh` (drop + remigrate + reseed with confirmation guard). `note_type` CHECK constraint values confirmed: `recipe`, `service`, `storage`, `substitution`, `source`.
- **15** — Dev/test/ops scaffolding: `apps/api/tests/conftest.py` (shared `async_client` fixture using `tmp_path` — parallel-safe, new tests use this instead of hand-rolling DB setup), `scripts/dev/check.sh` (verifies Python ≥ 3.12, API deps, Node ≥ 20, npm, node_modules, .env, data dirs, Docker), Makefile additions: `test-api-q`, `test-api-k K=<keyword>`, `dev-check`, `seed-dev`.

- **38** — Ops scheduling and observability: `src/config/logging_config.py` (stdout + rotating file handler, 5 MB × 3, UTC timestamps, silences sqlalchemy/httpx/uvicorn.access), `LOG_LEVEL`/`logs_dir` added to Settings, `configure_logging()` call replaces `basicConfig` in `main.py`, request logging middleware (`galley.request` logger — method/path/status/ms per request), DB connectivity ping in `/api/health` (`db: "ok"|"unreachable"`, `status: "ok"|"degraded"`), `scripts/backup/schedule-daily.sh` cron installer (idempotent, supports `remove` arg). Also fixed pre-existing bug: `settings.py` REPO_ROOT was `parents[3]` (= `apps/`) — corrected to `parents[4]` (= repo root); seed fixtures re-applied to the correct `data/db/galley.sqlite`.

- **22** — Responsive layout foundation: `useBreakpoint.ts` hook (`useIsDesktop()` via `matchMedia`, SSR-safe, 1024px threshold), `AppShell` updated with mobile top bar (fixed, 52px, brand + hamburger), backdrop overlay, `SideNav` only rendered when needed on mobile, `SideNav` updated with `overlay`/`onClose` props (position:fixed z-index:30 on mobile, nav links auto-close overlay on tap), `BREAKPOINTS` constant added to shared-ui-tokens. Zero TypeScript errors.

- **23** — Reusable visual primitives: `Badge` (4 variants: default/info/advisory/muted — for complexity, cuisine, dietary flags), `MetaItem` (label/value pair, sizes base/sm — replaces inline PrimaryItem/SecondaryItem in MetadataStrip), `Chip` (taxonomy facet tag, active/passive/removable states). `MetadataStrip` updated to import and use `MetaItem` via `style` prop override for padding/border. Zero TypeScript errors.

Sessions **37, 39, 42** and remaining sessions from phases 2–4 remain unexecuted (except 22, 23 now done).
