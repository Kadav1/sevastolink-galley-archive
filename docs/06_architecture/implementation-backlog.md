# Sevastolink Galley Archive

## Architecture Implementation Backlog v1.0

---

## 1. Purpose

This document translates `docs/06_architecture/technical-architecture.md` into a concrete implementation backlog.

It establishes:

* which architectural areas are already implemented
* which parts of the target architecture are still missing
* which missing work should be prioritized first
* how the missing work maps back to the architecture spec

This is an implementation-planning document for technical architecture work.

---

## 2. Current implementation baseline

Already implemented:

* real local-first stack across web, API, SQLite, and filesystem persistence
* deterministic search via SQLite FTS5 and filters
* AI backend integration through LM Studio
* migration runner and startup initialization
* backup and restore shell workflows

Still missing:

* fuller mounted backend domain separation
* repository/data-access layer separation
* surfaced media domain
* stronger operator tooling around migrations, seeds, and dev flows

---

## 3. Backlog summary

| Priority | Area | Current state | Target state |
|---|---|---|---|
| P1 | Search domain completion | Search exists inside recipe service | Dedicated search domain and cleaner boundary |
| P1 | Settings domain completion | **Done** — settings API and UI implemented | Settings API and UI are functional |
| P1 | Dev/migrate/seed ergonomics | Startup migration works, helper dirs are empty | Real operator/developer command layer |
| P2 | Media domain completion | First endpoint implemented: `POST /intake-jobs/{job_id}/media` | Broader media workflows if still needed |
| P2 | Data-access separation | Services perform DB orchestration directly | Clearer service/repository split where useful |
| P2 | Backup/system domain surfacing | Shell workflows exist only outside API | Better surfaced operational architecture |
| P3 | AI domain productization | AI backend capabilities exist unevenly across UX | Cleaner product-facing AI domain surfaces |

---

## 4. Backlog detail

### 4.1 P1: Search domain completion

Current state:

* search works operationally
* FTS and filters live inside the recipe service
* `apps/api/src/search/` is still scaffold-only

Missing target-state items:

* dedicated search module boundary
* clearer separation between archive CRUD and retrieval logic
* optional search-specific API surface if still desired

Likely implementation work:

* extract search logic from `recipe_service.py`
* define whether search remains part of recipe routes or gains its own mounted router
* align code structure with the already documented target-state search domain

Primary source:

* `technical-architecture.md` §6
* `technical-architecture.md` §9

### 4.2 P1: Settings domain completion

Current state (implemented):

* settings table exists and is used
* `GET /api/v1/settings` and `PATCH /api/v1/settings` are mounted
* two persisted user preferences: `default_verification_state`, `library_default_sort`
* `ai_enabled` is exposed read-only from `LM_STUDIO_ENABLED`
* SettingsPage.tsx replaced with real load/save UI

Settings boundary is explicit: persisted product preferences are writable through the API; operator/infrastructure config (database path, LM Studio URL, port) remains file-driven only.

Primary source:

* `technical-architecture.md`
* `docs/07_api/implemented-api.md §8`

### 4.3 P1: Dev, migrate, and seed ergonomics

Current state:

* migrations work through startup and shared init helpers
* backup scripts exist
* `scripts/dev`, `scripts/migrate`, and `scripts/seed` remain placeholders

Missing target-state items:

* migration convenience commands
* seed workflows
* clearer operator command set beyond direct service startup

Likely implementation work:

* add thin wrappers around existing startup and backup behavior
* add seed scripts once seed data model is agreed
* avoid duplicating logic already handled in the app runtime

Primary source:

* `technical-architecture.md`
* `migrations-and-data-lifecycle.md`

### 4.4 P2: Media domain completion

Current state:

* media tables and model placeholders exist
* `POST /api/v1/intake-jobs/{job_id}/media` is implemented — first real media API surface
* media files are persisted to `data/media/intake/` with checksum and metadata
* `source_media_asset_id` on `intake_jobs` is now populated by the endpoint

Missing target-state items:

* recipe image attachment workflows
* standalone media retrieval endpoints if needed

Likely implementation work:

* let the first use case prove the storage and metadata model before expanding further

Primary source:

* `technical-architecture.md` §8
* `docs/07_api/implemented-api.md §9`

### 4.5 P2: Data-access separation

Current state:

* services own business logic and direct DB orchestration

Missing target-state items:

* clearer repository/data-access split where complexity justifies it

Likely implementation work:

* do not introduce repository layers speculatively
* extract data-access helpers only where service complexity is becoming a maintenance problem

Primary source:

* `technical-architecture.md` §6

### 4.6 P2: Backup and system domain surfacing

Current state:

* backup and restore exist as shell workflows
* optional nginx and systemd files exist
* there is no surfaced backup or system API domain

Missing target-state items:

* better architectural surfacing of operational domains
* clearer boundary between app runtime and operator tooling

Likely implementation work:

* decide whether backup/system should become API surfaces or remain operator-only
* document that choice explicitly once made

Primary source:

* `technical-architecture.md`

### 4.7 P3: AI domain productization

Current state:

* the backend has multiple real AI capabilities
* only part of that capability is exposed as complete product workflow

Missing target-state items:

* fuller routed UX for AI-backed flows
* clearer lifecycle handling for AI job records if those become first-class

Likely implementation work:

* align future AI UX rollout with the already implemented backend capabilities
* avoid building product surfaces for prompts that remain experimental

Primary source:

* `technical-architecture.md` §10

---

## 5. Recommended implementation order

### Phase 1

Complete the most operationally important missing domains:

* search boundary cleanup
* settings domain
* dev/migrate/seed ergonomics

### Phase 2

Address the missing structural and operational domains:

* media
* clearer data-access boundaries
* backup/system surfacing decisions

### Phase 3

Expand AI architecture into fuller product-facing workflows once the surrounding operational architecture is stronger.

---

## 6. Contributor rule

When implementing against the architecture docs:

* treat `implemented-architecture.md` as the current-state truth
* treat `technical-architecture.md` as the broader target-state reference
* treat `migrations-and-data-lifecycle.md` as the practical current data-lifecycle document
* move backlog items into implemented docs only when the runtime code and surfaced workflows actually exist
