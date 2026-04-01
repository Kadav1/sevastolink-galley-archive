# Sevastolink Galley Archive

## API Implementation Backlog v1.0

---

## 1. Purpose

This document translates `docs/07_api/api-spec.md` into a concrete implementation backlog.

It establishes:

* which API areas are already implemented
* which target-state resources are still missing
* which missing work should be prioritized first
* how the missing work maps back to the broader API spec

This is an implementation-planning document for backend API work.

---

## 2. Current implementation baseline

Already implemented:

* health endpoint
* recipe CRUD and archive/favorite actions
* deterministic recipe search through list filters and FTS-backed `q`
* intake job create/get/update/normalize/approve/evaluate flow
* AI-assisted recipe endpoints for metadata suggestion, rewrite, and similarity
* pantry suggestion endpoint

Still missing:

* separate `/search` resource group
* `/media-assets`
* `/ai-jobs`
* `/backups`
* `/system`
* full response-envelope consistency

---

## 3. Backlog summary

| Priority | Area | Current state | Target state |
|---|---|---|---|
| P1 | Error-envelope consistency | **Done** — unified `{"error": {...}}` envelope, custom exception handler in `main.py` | One stable API error contract |
| P1 | Schema/API alignment | **Done** — `IntakeJobOut` expanded, `ingredient_count` in `RecipeSummaryOut`, 3 new list filters, `title_desc` sort | ORM, schema, and spec in sync |
| P1 | Search resource decision | Search exists only through `/recipes` list behavior | Either dedicated `/search` resource or explicit decision not to create one |
| P1 | Settings API | **Done** — `GET/PATCH /api/v1/settings` mounted | Functional settings routes |
| P2 | Media assets API | Source attach, recipe cover attach, metadata GET, file serve — all implemented | No outstanding P2 media items |
| P2 | AI jobs API | AI capability exists, `ai_jobs` table exists, API absent | First-class AI job visibility if needed |
| P2 | Backup/system API decision | Shell workflows exist, API absent | Explicit surfaced operator resources or documented operator-only choice |
| P3 | Full target-state search facets | Current filters cover main taxonomy dimensions | Ingredient-family and multi-value filters if still desired |

---

## 4. Backlog detail

### 4.1 P1: Error-envelope consistency (implemented)

Current state:

* all error responses use `{"error": {"code": "...", "message": "..."}}` at the top level
* custom `HTTPException` and `RequestValidationError` handlers in `main.py` normalize all shapes
* `error_detail()` helper in `schemas/common.py` is used consistently across all routes and services
* no `detail` wrapper on any error response

Primary source:

* `docs/07_api/implemented-api.md §10`

### 4.2 P1: Search resource decision

Current state:

* search already works through `GET /recipes`
* there is no separate `/search` route group

Missing target-state items:

* either a dedicated search resource or an explicit architectural decision to keep search inside recipe listing

Likely implementation work:

* decide whether `/search` adds real value over the current list API
* if yes, extract and mount a search route group
* if not, simplify the target-state docs to match the chosen design

Primary source:

* `api-spec.md` §6
* `api-spec.md` §7

### 4.3 P1: Settings API (implemented)

Current state:

* `GET /api/v1/settings` and `PATCH /api/v1/settings` are mounted
* persisted preferences: `default_verification_state`, `library_default_sort`
* read-only runtime signal: `ai_enabled` (from `LM_STUDIO_ENABLED`)
* operator/infrastructure config is not exposed through the API

Primary source:

* `docs/07_api/implemented-api.md §8`

### 4.4 P2: Media assets API

Current state:

* media entities exist in schema and models
* `POST /api/v1/intake-jobs/{job_id}/media` is implemented — attaches a source image or PDF to an intake job, persists a `media_assets` row, and sets `source_media_asset_id`
* there is no standalone `/media-assets` resource group

Missing target-state items:

* standalone media retrieval and list endpoints if needed
* recipe image attachment workflows

Primary source:

* `api-spec.md`
* `docs/07_api/implemented-api.md §9`

### 4.5 P2: AI jobs API

Current state:

* AI capability exists through direct task endpoints
* `ai_jobs` table exists
* there is no first-class AI jobs API surface

Missing target-state items:

* job history or job inspection endpoints if those records become product-relevant

Primary source:

* `api-spec.md`

### 4.6 P2: Backup and system API decision

Current state:

* backup and operational workflows exist outside the API as shell tools
* `/backups` and `/system` are not mounted

Missing target-state items:

* either surfaced operator resources or explicit operator-only documentation

Primary source:

* `api-spec.md`

### 4.7 P3: Full target-state search facets

Current state:

* the recipe list endpoint already supports the main v1 filters
* some broader spec filters are not implemented today

Missing target-state items:

* broader filtering such as ingredient-family and other deeper taxonomy filters if still justified

Primary source:

* `api-spec.md` §7.1

---

## 5. Recommended implementation order

### Phase 1

Stabilize the current API surface:

* unify error envelopes
* decide the search-resource shape
* implement settings routes

### Phase 2

Surface the missing stored-resource domains if they remain worthwhile:

* media assets
* AI jobs
* backup/system operator decisions

### Phase 3

Expand deeper target-state filtering only after the core API surface is stable and needed by the frontend.

---

## 6. Contributor rule

When implementing against the API docs:

* treat `implemented-api.md` as the current-state truth
* treat `api-spec.md` as the broader target-state reference
* move backlog items into the implemented API doc only when the route, payload, and runtime behavior actually exist
