# Sevastolink Galley Archive

## Implemented Architecture v1.0

---

## 1. Purpose

This document defines the architecture that is implemented in the repository now.

It establishes:

* the real stack currently used by the application
* the actual deployed service boundaries
* the internal architectural patterns that exist today
* which parts of the broader architecture spec are still only target-state

This is the implementation-aware architecture baseline for contributors.

---

## 2. Current stack reality

### Established facts

The current repository implements:

* React + TypeScript + Vite in `apps/web`
* React Router for frontend routing
* TanStack Query for frontend server-state access
* FastAPI in `apps/api`
* Pydantic for request and response schemas
* SQLAlchemy ORM with SQLite
* SQLite FTS5 for recipe text search
* local filesystem storage under `data/`
* optional LM Studio integration over local HTTP
* Docker Compose for the local multi-service stack

This is not merely the recommended stack. It is the actual implemented stack in the repository now.

---

## 3. Current service boundaries

### 3.1 Runtime services

The current runnable services are:

* web frontend
* API backend
* optional nginx reverse proxy
* host-run LM Studio outside the compose stack

### 3.2 Current backend route domains

The backend currently mounts:

* `health`
* `recipes`
* `intake`
* `pantry`
* `settings`

The media domain has a first surfaced endpoint via the intake workflow:

* `POST /api/v1/intake-jobs/{job_id}/media` — attach a source image or PDF to an intake job

The backend does not currently mount separate route groups for:

* `search`
* standalone `media-assets`
* `backup`
* `system`

Some corresponding tables or model placeholders do exist, but they are not yet fully surfaced application domains.

---

## 4. Current internal architecture pattern

### Established facts

The backend currently uses a partially layered structure:

* route layer
* service layer
* model/schema layer
* infrastructure helpers for DB, settings, and LM Studio

### Current interpretation

This is not yet a fully separated repository-pattern architecture.

In practice:

* routes call service functions directly
* services perform both business logic and database access
* FTS synchronization is handled inside service logic
* there is no distinct repository package or module boundary

The architecture is therefore modular and workable, but still lighter-weight and more direct than the full target-state spec suggests.

---

## 5. Current frontend architecture pattern

The frontend currently uses:

* a route-based SPA
* `pages/` as the main route-surface boundary
* `components/` for reusable UI pieces
* `hooks/` for query and mutation wrappers
* `lib/` for API and utility helpers

The frontend does not yet materially implement the fuller feature-module architecture described in some target-state documents.

The scaffold directories under `src/features/` remain reserved structure rather than active module boundaries.

---

## 6. Current data and persistence model

### Established facts

The current system of record is SQLite under `data/db/`.

The current persistent filesystem model includes:

* `data/db/`
* `data/media/`
* `data/imports/`
* `data/exports/`
* `data/backups/`
* `data/logs/`

### Current implementation note

The data model already includes:

* recipes and related sub-resources
* intake jobs
* structured candidates
* media assets
* AI jobs
* settings
* FTS search index

However, not every stored entity has a corresponding complete application surface yet.

Examples:

* `media_assets` has a first API surface (`POST /intake-jobs/{job_id}/media`) but no standalone resource group
* `ai_jobs` exists in schema/models but is not yet a first-class surfaced API domain

---

## 7. Current search architecture

The current repository implements deterministic search through:

* SQLite FTS5 for free-text lookup
* direct SQL filters for common facets
* denormalized ingredient text maintained by the application

Search is implemented today, but not as a standalone backend domain.

In practice:

* list search and filtering are handled through the recipe service and recipe routes
* `apps/api/src/search/` remains scaffold-only
* semantic search is not implemented

---

## 8. Current AI architecture

### Established facts

The repository already includes real AI integration code for:

* normalization
* candidate evaluation
* metadata suggestion
* rewrite
* similarity
* pantry suggestion

### Current implementation note

AI orchestration is implemented inside the backend and does not run directly from the frontend to LM Studio.

However, only some of these capabilities are surfaced as major product workflows today.

Most implemented AI surfaces are API-level or CLI-level capabilities rather than complete frontend product areas.

The current architecture therefore already has a real `ai` technical layer, even though the UX layer for it is still partial.

---

## 9. Current operational architecture

The repository currently implements:

* compose-based local startup
* optional nginx proxy for single-port access
* systemd unit files under `infra/systemd/`
* shell-based backup and restore workflows
* startup-triggered migration application

The repository does not yet implement:

* dedicated migration CLI wrappers
* richer operator scripts under `scripts/dev`, `scripts/migrate`, or `scripts/seed`
* a fuller documented production packaging story beyond the existing local/single-machine shape

---

## 10. Current gaps relative to the full architecture spec

The broader architecture spec describes a more complete target-state domain model than the current repository fully realizes.

Not yet fully implemented:

* separate mounted backend domains for search, media, settings, backup, and system
* a fuller repository/data-access layer separation
* functional settings management
* complete media-management workflows
* a dedicated search domain package
* stronger operational tooling for migrations, seeding, and dev ergonomics

---

## 11. Contributor note

When working on architecture:

* treat this document as the current implementation baseline
* treat `technical-architecture.md` as the broader target-state architecture reference
* treat `migrations-and-data-lifecycle.md` as the practical current data-lifecycle reference
* avoid describing a target-state domain as implemented until it has real runtime code and surfaced workflows
