# Sevastolink Galley Archive

## Implemented API Reference v1.0

---

## 1. Purpose

This document defines the backend API that is implemented in the repository now.

It establishes:

* the mounted API base paths
* the currently available route groups
* request and response expectations for the implemented endpoints
* the current error behavior used by the frontend and CLI tooling
* where the implemented API is narrower than the broader API spec

This document is implementation-aware. It does not replace `docs/07_api/api-spec.md`, which remains the broader target-state API document.

---

## 2. API scope

### Established facts

The current backend mounts:

* `/api/health`
* `/api/v1/recipes`
* `/api/v1/intake-jobs`

The backend does not currently mount implemented route groups for:

* `/search`
* `/media-assets`
* `/ai-jobs`
* `/settings`
* `/backups`
* `/system`

### Current standard

Consumers should treat only the routes documented here as available in the current application.

---

## 3. Base paths and envelopes

### Base paths

* Health: `/api`
* Application API: `/api/v1`

### Success envelopes

Single-resource responses use:

```json
{
  "data": {}
}
```

List responses use:

```json
{
  "data": [],
  "meta": {
    "total": 0,
    "limit": 50,
    "offset": 0
  }
}
```

### Error shape

The implemented API is not fully uniform yet.

Some endpoints return:

```json
{
  "error": {
    "code": "not_found",
    "message": "Message text."
  }
}
```

Some FastAPI exceptions currently return the same structure nested under `detail`.

Frontend consumers in this repository already handle this inconsistency in a lightweight way. New backend work should converge toward one consistent error envelope.

---

## 4. Health endpoint

### 4.1 Service health

```http
GET /api/health
```

Purpose:

* confirms that the API process is up
* provides the simplest service-level readiness check for local use

Current use:

* quick manual verification
* Docker and local smoke checks

---

## 5. Recipe endpoints

### 5.1 List recipes

```http
GET /api/v1/recipes
```

Supported query parameters:

| Parameter | Type | Notes |
|---|---|---|
| `q` | string | Free-text search |
| `verification_state` | string | Filter by trust state |
| `favorite` | boolean | Filter favorites |
| `archived` | boolean | Include archived recipes when `true` |
| `dish_role` | string | Exact-match filter |
| `primary_cuisine` | string | Exact-match filter |
| `technique_family` | string | Exact-match filter |
| `complexity` | string | Exact-match filter |
| `time_class` | string | Exact-match filter |
| `sort` | string | Defaults to `updated_at_desc` |
| `limit` | integer | Default `50`, max `200` |
| `offset` | integer | Default `0` |

Response:

* list envelope with `meta.total`, `meta.limit`, and `meta.offset`

### 5.2 Create recipe

```http
POST /api/v1/recipes
```

Purpose:

* create a recipe directly in the canonical archive

Current primary caller:

* manual-entry web flow

### 5.3 Get recipe

```http
GET /api/v1/recipes/{id_or_slug}
```

Purpose:

* fetch one recipe by ID or slug

### 5.4 Update recipe

```http
PATCH /api/v1/recipes/{id_or_slug}
```

Purpose:

* partially update an existing recipe

### 5.5 Archive recipe

```http
POST /api/v1/recipes/{id_or_slug}/archive
```

Purpose:

* mark a recipe as archived

### 5.6 Unarchive recipe

```http
POST /api/v1/recipes/{id_or_slug}/unarchive
```

Purpose:

* restore an archived recipe to active visibility

### 5.7 Favorite recipe

```http
POST /api/v1/recipes/{id_or_slug}/favorite
```

Purpose:

* mark a recipe as favorited

### 5.8 Unfavorite recipe

```http
POST /api/v1/recipes/{id_or_slug}/unfavorite
```

Purpose:

* remove favorite state

### 5.9 Delete recipe

```http
DELETE /api/v1/recipes/{id_or_slug}
```

Purpose:

* remove a recipe from the archive

Current behavior:

* success returns `204 No Content`

---

## 6. Intake endpoints

### 6.1 Create intake job

```http
POST /api/v1/intake-jobs
```

Purpose:

* create an intake job for either manual or paste-text intake

Current intake types used in the app:

* `manual`
* `paste_text`

Current validation:

* `paste_text` requires `raw_source_text`

### 6.2 Get intake job

```http
GET /api/v1/intake-jobs/{job_id}
```

Purpose:

* retrieve current intake job metadata and status

### 6.3 Update candidate

```http
PATCH /api/v1/intake-jobs/{job_id}/candidate
```

Purpose:

* create or update the structured candidate attached to an intake job

Current behavior:

* if the intake job exists but has no candidate yet, the backend creates one
* ingredient and step arrays are replaced by the submitted values

### 6.4 Normalize candidate

```http
POST /api/v1/intake-jobs/{job_id}/normalize
```

Purpose:

* run LM Studio normalization against the intake job's raw source text

Current behavior:

* requires `LM_STUDIO_ENABLED=true`
* returns AI-derived candidate fields
* applies those fields back onto the intake candidate
* does not approve or mutate canonical recipes directly

Degraded mode:

* if AI is disabled or unavailable, the user can continue with manual field entry

### 6.5 Approve intake job

```http
POST /api/v1/intake-jobs/{job_id}/approve
```

Purpose:

* promote the structured candidate into a canonical recipe

Current validation:

* intake job must exist
* intake job must not already be approved
* candidate must exist
* candidate must have a title

Current outcome:

* creates a recipe
* links the resulting recipe to the intake job
* marks the candidate as accepted

---

## 7. Current error behavior

### Common codes in current use

The implemented routes currently use these error codes in practice:

* `validation_error`
* `not_found`
* `candidate_incomplete`
* `conflict`
* `internal_error`
* `ai_disabled`
* `ai_unavailable`
* `no_source_text`

### Current caveat

The broader API spec defines a larger standardized error vocabulary. The implemented code has not adopted all of it yet.

This is a documentation and consistency gap, not a hidden feature.

---

## 8. Known differences from the broader API spec

The broader API spec documents a larger surface area than the current backend implements.

Notable differences:

* the resource list in `api-spec.md` is wider than the currently mounted routers
* not all target-state endpoint families exist yet
* the current error envelope is not fully uniform
* the current health route lives outside `/api/v1`
* the current app relies on a smaller subset of recipe and intake features than the target-state spec describes

When documenting or integrating against the live application, use this document first.
