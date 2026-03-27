# Sevastolink Galley Archive

## API Spec v2.0

---

## 1. Purpose

This document defines the complete v1 backend API for Sevastolink Galley Archive.

It establishes:

* the full resource model and route list
* request and response shapes for every endpoint group
* HTTP status codes and error contracts
* query parameter definitions with types
* pagination strategy
* the intake workflow as an API sequence
* how AI endpoints are isolated from archive mutations
* authentication model for local home use
* versioning and forward-compatibility rules

This document supersedes API Spec v1.0. It is aligned with schema-spec v2.0 and ai-interaction-spec v1.0.

---

## 2. API Philosophy

### Core constraints

* Local-first. The API serves a single local application. It is not a public API.
* Archive-first. Recipes are the primary resource. All other resources support the archive.
* Explicit workflow. Raw source, structured candidate, and approved recipe are separate API resources with distinct endpoints.
* AI is optional. Every AI endpoint has a non-AI fallback path. AI endpoints never mutate approved records.
* Trust is explicit. Verification state is set by user action through a specific endpoint. It cannot be set implicitly by normalization, AI, or bulk operations.

### API standard

The API must reflect the product's actual data model. It must not hide the intake workflow behind a single opaque "save recipe" call, flatten candidates into recipes before review, or let AI output touch canonical record fields without user-initiated acceptance.

---

## 3. Conventions

### Base path

```
/api/v1
```

All routes in this document are relative to this base.

### Content type

All request and response bodies use `application/json` except file upload endpoints, which use `multipart/form-data`.

### Response envelope

All responses use a consistent envelope:

**Success:**
```json
{
  "data": { ... },
  "meta": { ... }
}
```

**Success — list:**
```json
{
  "data": [ ... ],
  "meta": {
    "total": 142,
    "limit": 50,
    "offset": 0
  }
}
```

**Error:**
```json
{
  "error": {
    "code": "not_found",
    "message": "Recipe not found.",
    "details": {}
  }
}
```

`meta` is always present on list responses. It may be omitted on single-resource responses when there is no useful metadata.

### Timestamps

All timestamps are returned as ISO 8601 UTC strings: `"2026-03-25T09:00:00Z"`.

### Identifiers

All resource IDs are ULID-format text strings. They are opaque to the client.

### Pagination

All list endpoints support:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | integer | `50` | Maximum records to return. Max `200`. |
| `offset` | integer | `0` | Number of records to skip. |

Responses include `meta.total` (total matching count), `meta.limit`, and `meta.offset`.

### Sorting

Where documented, `sort` accepts `field_direction` format:

* `updated_at_desc` (default)
* `created_at_desc`
* `title_asc`
* `last_cooked_at_desc`

### Partial updates

All `PATCH` endpoints accept partial payloads. Only provided fields are updated. Fields not present in the request body are unchanged.

---

## 4. HTTP Status Codes

| Code | Usage |
|---|---|
| `200 OK` | Successful GET, PATCH, or action |
| `201 Created` | Successful POST that creates a resource |
| `204 No Content` | Successful DELETE or action with no response body |
| `400 Bad Request` | Malformed JSON, missing required fields, invalid enum value |
| `404 Not Found` | Resource does not exist |
| `409 Conflict` | Slug collision, duplicate constraint violation |
| `415 Unsupported Media Type` | Wrong content type |
| `422 Unprocessable Entity` | Valid JSON but domain validation failed |
| `500 Internal Server Error` | Unexpected server error |
| `503 Service Unavailable` | AI backend unavailable (AI-specific routes only) |

---

## 5. Error Codes

| Code | Meaning |
|---|---|
| `validation_error` | One or more request fields failed validation |
| `domain_error` | Valid payload but fails product rules |
| `not_found` | Resource not found |
| `conflict` | Unique constraint or state conflict |
| `unsupported_media_type` | Invalid file type for upload |
| `file_too_large` | Upload exceeds size limit |
| `ai_not_configured` | AI is not enabled or endpoint is not set |
| `ai_unavailable` | AI endpoint is configured but not reachable |
| `ai_response_invalid` | AI returned a response that failed contract validation |
| `intake_state_error` | Operation is not valid for the current intake job state |
| `candidate_incomplete` | Candidate is missing required fields for recipe promotion |
| `backup_failed` | Backup could not be created |
| `restore_failed` | Restore could not be completed |
| `internal_error` | Unhandled server-side error |

Validation errors include a `details` object with field-level messages:
```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": {
      "title": "Title is required.",
      "verification_state": "Must be one of: Draft, Unverified, Verified, Archived."
    }
  }
}
```

---

## 6. Resources

```
/recipes
/recipes/:id/ingredients
/recipes/:id/steps
/recipes/:id/notes
/search
/intake-jobs
/intake-jobs/:id/candidate
/media-assets
/ai-jobs
/settings
/backups
/system
```

---

## 7. Recipe Endpoints

### 7.1 List recipes

```
GET /recipes
```

Returns the recipe library. Primary endpoint for archive browse views.

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `q` | string | Text search against title, description, ingredient text, notes |
| `verification_state` | string | Filter by state: `Draft`, `Unverified`, `Verified`, `Archived` |
| `favorite` | boolean | `true` returns favorited recipes only |
| `archived` | boolean | `true` includes archived recipes. Default `false`. |
| `dish_role` | string | Exact match on `dish_role` |
| `primary_cuisine` | string | Exact match on `primary_cuisine` |
| `technique_family` | string | Exact match on `technique_family` |
| `complexity` | string | Exact match on `complexity` |
| `time_class` | string | Exact match on `time_class` |
| `sector` | string | Exact match on `sector` |
| `operational_class` | string | Exact match on `operational_class` |
| `heat_window` | string | Exact match on `heat_window` |
| `ingredient_family` | string | Match within `ingredient_families` JSON array |
| `dietary_flag` | string | Match within `dietary_flags` JSON array |
| `ingredient` | string | Substring match on ingredient item names |
| `sort` | string | Sort order. Default: `updated_at_desc` |
| `limit` | integer | Default: `50`. Max: `200` |
| `offset` | integer | Default: `0` |

**Response `200`:**
```json
{
  "data": [
    {
      "id": "01HZYX9YQ8Z7F5M4R3N2K1J0AB",
      "slug": "shakshuka",
      "title": "Shakshuka",
      "short_description": "Eggs poached in spiced tomato and pepper sauce.",
      "dish_role": "Breakfast",
      "primary_cuisine": "Levantine",
      "technique_family": "Simmer",
      "complexity": "Basic",
      "time_class": "15–30 min",
      "verification_state": "Verified",
      "favorite": true,
      "sector": "Fire Line",
      "operational_class": "Field Meal",
      "updated_at": "2026-03-25T09:00:00Z",
      "last_cooked_at": "2026-03-20T00:00:00Z"
    }
  ],
  "meta": {
    "total": 87,
    "limit": 50,
    "offset": 0
  }
}
```

List responses return summary fields only. Ingredients, steps, and notes are not included.

---

### 7.2 Get recipe detail

```
GET /recipes/:id
```

Returns the full recipe record including all sub-resources.

**Response `200`:**
```json
{
  "data": {
    "id": "01HZYX9YQ8Z7F5M4R3N2K1J0AB",
    "slug": "shakshuka",
    "title": "Shakshuka",
    "short_description": "Eggs poached in spiced tomato and pepper sauce.",
    "dish_role": "Breakfast",
    "primary_cuisine": "Levantine",
    "secondary_cuisines": ["North African", "Israeli"],
    "technique_family": "Simmer",
    "complexity": "Basic",
    "time_class": "15–30 min",
    "service_format": "Single Plate",
    "season": "All Year",
    "ingredient_families": ["Egg", "Tomato", "Chili", "Spice-forward"],
    "mood_tags": ["Comfort", "Spicy", "Rustic", "Everyday"],
    "storage_profile": ["Best Fresh"],
    "dietary_flags": ["Vegetarian", "Gluten-Free", "Dairy-Free"],
    "provision_tags": ["One-Pan", "Weeknight", "Pantry-Heavy"],
    "sector": "Fire Line",
    "operational_class": "Field Meal",
    "heat_window": "Medium Heat",
    "servings": "2",
    "prep_time_minutes": 10,
    "cook_time_minutes": 20,
    "total_time_minutes": 30,
    "rest_time_minutes": null,
    "verification_state": "Verified",
    "favorite": true,
    "archived": false,
    "rating": 5,
    "ingredients": [
      {
        "id": "01HZA...",
        "position": 1,
        "group_heading": null,
        "quantity": "2",
        "unit": "tbsp",
        "item": "olive oil",
        "preparation": null,
        "optional": false,
        "display_text": "2 tbsp olive oil"
      }
    ],
    "steps": [
      {
        "id": "01HZC...",
        "position": 1,
        "instruction": "Heat the oil in a wide pan over medium heat. Add onion and pepper. Cook until soft.",
        "time_note": "8 minutes",
        "equipment_note": "wide frying pan with lid"
      }
    ],
    "notes": [
      {
        "note_type": "service",
        "content": "Serve in the pan with bread. Do not overcook the eggs."
      }
    ],
    "source": {
      "source_type": "Manual",
      "source_title": "House Version",
      "source_url": null,
      "source_notes": "Personal version.",
      "raw_source_text": null
    },
    "intake_job_id": null,
    "created_at": "2026-03-01T12:00:00Z",
    "updated_at": "2026-03-25T09:00:00Z",
    "last_cooked_at": "2026-03-20T00:00:00Z",
    "last_viewed_at": "2026-03-25T08:55:00Z"
  }
}
```

**Response `404`:** Recipe not found.

---

### 7.3 Create recipe

```
POST /recipes
```

Creates a new recipe directly. Used for manual entry intake that bypasses the intake-job workflow.

**Request body:**
```json
{
  "title": "Chicken Stock",
  "short_description": "A clear, neutral base stock for soups and sauces.",
  "dish_role": "Pantry Staple",
  "primary_cuisine": "Global / Mixed",
  "technique_family": "Simmer",
  "complexity": "Basic",
  "time_class": "2–4 hr",
  "service_format": "Kitchen Use",
  "ingredient_families": ["Poultry", "Vegetable", "Herb-forward"],
  "provision_tags": ["Freezer-Build", "Batch Cook Friendly"],
  "sector": "House Stock",
  "operational_class": "Base Component",
  "heat_window": "Low Heat",
  "servings": "2 litres",
  "prep_time_minutes": 15,
  "cook_time_minutes": 180,
  "verification_state": "Verified",
  "ingredients": [
    {
      "position": 1,
      "quantity": "1",
      "unit": "kg",
      "item": "chicken carcasses",
      "preparation": "rinsed",
      "optional": false,
      "display_text": "1 kg chicken carcasses, rinsed"
    }
  ],
  "steps": [
    {
      "position": 1,
      "instruction": "Place carcasses in a large pot. Cover with cold water. Bring to a gentle simmer.",
      "time_note": "20 minutes to reach simmer"
    }
  ],
  "notes": [
    {
      "note_type": "storage",
      "content": "Freeze in 500ml portions. Label with date."
    }
  ],
  "source": {
    "source_type": "Manual",
    "source_notes": "Standard house version."
  }
}
```

**Required fields:** `title`, `verification_state`, at least one ingredient, at least one step.

**Response `201`:** Full recipe object (same shape as GET detail).

**Response `400`:** Validation error with field details.

**Response `409`:** Slug collision — a recipe with this slug already exists.

---

### 7.4 Update recipe

```
PATCH /recipes/:id
```

Partial update of an existing recipe. Any combination of top-level fields, ingredients, steps, or notes may be provided.

When `ingredients` or `steps` arrays are provided, they **replace** the existing rows entirely for that recipe. Partial row-level patching within arrays is not supported in v1 — send the full updated array.

**Request body (example — update metadata only):**
```json
{
  "complexity": "Intermediate",
  "mood_tags": ["Comfort", "Rich", "Cold Weather"],
  "rating": 4,
  "verification_state": "Verified"
}
```

**Response `200`:** Full updated recipe object.

**Response `404`:** Recipe not found.

**Response `422`:** Domain validation failed (e.g., invalid state transition).

---

### 7.5 Archive recipe

```
POST /recipes/:id/archive
```

Sets `verification_state` to `Archived` and `archived` flag to `true`. The recipe is preserved but excluded from default archive browse queries.

**Request body:** none.

**Response `200`:**
```json
{ "data": { "id": "...", "verification_state": "Archived", "archived": true } }
```

---

### 7.6 Unarchive recipe

```
POST /recipes/:id/unarchive
```

Restores an archived recipe. Sets `archived` to `false` and `verification_state` to `Unverified` (the previous active state is not reconstructed).

**Response `200`:** Updated recipe summary.

---

### 7.7 Delete recipe

```
DELETE /recipes/:id
```

Permanently deletes the recipe record and all dependent rows (ingredients, steps, notes). The linked `recipe_source` record is retained. The intake job link is set to null.

This endpoint should not be the default removal UX. The UI should use archive/unarchive for normal use. Hard delete is for explicit administrative removal.

**Response `204`:** No content.

**Response `404`:** Recipe not found.

---

### 7.8 Favorite / unfavorite

```
POST /recipes/:id/favorite
POST /recipes/:id/unfavorite
```

Sets `favorite` flag.

**Response `200`:**
```json
{ "data": { "id": "...", "favorite": true } }
```

---

### 7.9 Mark as cooked

```
POST /recipes/:id/mark-cooked
```

Sets `last_cooked_at` to current UTC timestamp.

**Optional request body:**
```json
{ "cooked_at": "2026-03-24T19:00:00Z" }
```

If `cooked_at` is not provided, the server uses the current time.

**Response `200`:**
```json
{ "data": { "id": "...", "last_cooked_at": "2026-03-24T19:00:00Z" } }
```

---

## 8. Search Endpoints

### 8.1 Recipe search

```
GET /search/recipes
```

Full-text and structured filter search. Combines FTS query with column filters in a single request. This is the primary search endpoint for the library and filter views.

**Query parameters:** Same as `GET /recipes` plus FTS is applied when `q` is present.

**Sort options when `q` is present:**

* `relevance` (FTS rank, default when query is provided)
* `updated_at_desc`
* `title_asc`

**Response `200`:** Same shape as `GET /recipes` list response. Results include a `score` field in each item when FTS is active:

```json
{
  "data": [
    {
      "id": "...",
      "title": "Shakshuka",
      "score": 4.2,
      ...
    }
  ],
  "meta": { "total": 3, "limit": 50, "offset": 0, "query": "egg tomato" }
}
```

---

### 8.2 Search facets

```
GET /search/facets
```

Returns the available values and counts for filterable fields, scoped to the current archive (excluding archived recipes by default).

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `include_archived` | boolean | Include archived recipes in counts. Default `false`. |

**Response `200`:**
```json
{
  "data": {
    "verification_state": {
      "Verified": 42,
      "Unverified": 31,
      "Draft": 14
    },
    "dish_role": {
      "Main": 38,
      "Sauce": 12,
      "Breakfast": 8,
      "Side": 7
    },
    "primary_cuisine": {
      "Italian": 14,
      "Japanese": 9,
      "Levantine": 7
    },
    "technique_family": {
      "Simmer": 19,
      "Bake": 11,
      "Stir-Fry": 8
    },
    "complexity": {
      "Basic": 28,
      "Intermediate": 41,
      "Advanced": 14,
      "Project": 4
    }
  }
}
```

This endpoint is used to populate filter dropdowns and show non-zero facet options. Zero-count values are omitted.

---

### 8.3 Ingredient search

```
GET /search/ingredients
```

Returns distinct ingredient item names from the archive. Used for autocomplete in search and filter inputs.

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `q` | string | Substring match on ingredient item names |
| `limit` | integer | Default: `20`. Max: `50` |

**Response `200`:**
```json
{
  "data": ["anchovies", "anchovy paste", "chicken breast", "chicken thigh"],
  "meta": { "total": 4 }
}
```

---

### 8.4 Related recipes

```
GET /recipes/:id/related
```

Returns recipes related to the given recipe based on shared taxonomy fields. Deterministic in v1 — no AI required.

**Matching logic (in priority order):**
1. Same `dish_role` + shared `primary_cuisine`
2. Same `technique_family` + shared `ingredient_families`
3. Same `primary_cuisine`

**Response `200`:**
```json
{
  "data": [
    {
      "id": "...",
      "slug": "miso-soup",
      "title": "Miso Soup",
      "dish_role": "Soup",
      "primary_cuisine": "Japanese",
      "technique_family": "Simmer",
      "verification_state": "Verified"
    }
  ],
  "meta": { "total": 3, "limit": 6, "offset": 0 }
}
```

---

## 9. Intake Job Endpoints

### 9.1 The intake workflow

The intake workflow as an API sequence:

```
1. POST /intake-jobs                     → create job, capture source
2. POST /intake-jobs/:id/media           → (optional) attach file
3. POST /intake-jobs/:id/normalize       → trigger parse or AI normalization
4. GET  /intake-jobs/:id/candidate       → retrieve structured candidate for review
5. PATCH /intake-jobs/:id/candidate      → save user edits to candidate
6. POST /intake-jobs/:id/approve         → promote candidate to recipe (trust gate)
```

At any point after step 1, the job may also be abandoned:
```
POST /intake-jobs/:id/abandon
```

---

### 9.2 Create intake job

```
POST /intake-jobs
```

Creates a new intake workflow record and captures source material.

**Request body:**
```json
{
  "intake_type": "paste_text",
  "raw_source_text": "Shakshuka\n\n2 tbsp olive oil\n1 onion, sliced...",
  "source_url": null,
  "source_notes": "Copied from a saved note."
}
```

| Field | Required | Description |
|---|---|---|
| `intake_type` | Yes | `manual`, `paste_text`, `url`, `file` |
| `raw_source_text` | Conditional | Required for `paste_text`. Optional for others. |
| `source_url` | Conditional | Required for `url`. |
| `source_notes` | No | Free text. |

**Response `201`:**
```json
{
  "data": {
    "id": "01HZINTAKE001",
    "intake_type": "paste_text",
    "status": "captured",
    "parse_status": "not_started",
    "ai_status": "not_requested",
    "review_status": "not_started",
    "source_url": null,
    "resulting_recipe_id": null,
    "created_at": "2026-03-25T09:00:00Z",
    "updated_at": "2026-03-25T09:00:00Z"
  }
}
```

---

### 9.3 List intake jobs

```
GET /intake-jobs
```

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `status` | string | Filter by intake status |
| `review_status` | string | Filter by review status |
| `intake_type` | string | Filter by intake type |
| `has_recipe` | boolean | `true` = completed jobs only; `false` = incomplete only |
| `sort` | string | Default: `created_at_desc` |
| `limit` | integer | Default: `50` |
| `offset` | integer | Default: `0` |

**Response `200`:** List of intake job summaries.

---

### 9.4 Get intake job

```
GET /intake-jobs/:id
```

**Response `200`:**
```json
{
  "data": {
    "id": "01HZINTAKE001",
    "intake_type": "paste_text",
    "status": "in_review",
    "parse_status": "complete",
    "ai_status": "ready",
    "review_status": "in_progress",
    "raw_source_text": "Shakshuka\n\n2 tbsp olive oil...",
    "source_url": null,
    "source_snapshot_path": null,
    "error_code": null,
    "error_message": null,
    "resulting_recipe_id": null,
    "candidate_id": "01HZCAND001",
    "created_at": "2026-03-25T09:00:00Z",
    "updated_at": "2026-03-25T09:05:00Z",
    "completed_at": null
  }
}
```

---

### 9.5 Attach file to intake job

```
POST /intake-jobs/:id/media
Content-Type: multipart/form-data
```

Uploads a source file and attaches it to the intake job.

**Form fields:**

| Field | Required | Description |
|---|---|---|
| `file` | Yes | The uploaded file |
| `asset_kind` | No | Default: `source_image`. Options: `source_image`, `source_pdf`, `source_screenshot` |

**Accepted MIME types:** `image/jpeg`, `image/png`, `image/webp`, `application/pdf`

**Max file size:** Configurable. Default: 20MB.

**Response `201`:**
```json
{
  "data": {
    "media_asset_id": "01HZMEDIA001",
    "asset_kind": "source_image",
    "original_filename": "recipe-scan.jpg",
    "mime_type": "image/jpeg",
    "byte_size": 1842304,
    "width": 2400,
    "height": 3200
  }
}
```

---

### 9.6 Normalize intake job

```
POST /intake-jobs/:id/normalize
```

Triggers normalization of the intake job's source material. If AI is enabled and configured, uses AI normalization. Otherwise uses deterministic parsing.

**Request body:**
```json
{
  "method": "ai"
}
```

| Field | Required | Description |
|---|---|---|
| `method` | No | `ai` or `deterministic`. Default: `ai` if AI is configured, else `deterministic`. |

**Behavior:**

* Creates or replaces the `structured_candidate` for this intake job.
* Raw source is never modified.
* Sets `intake_jobs.parse_status` and `ai_status` based on outcome.
* If AI is unavailable and `method` is `ai`, returns `503` with `ai_unavailable` code. Does not change intake job state. The user may retry with `deterministic` or proceed to manual candidate editing.

**Response `200` (normalization complete, candidate ready):**
```json
{
  "data": {
    "intake_job_id": "01HZINTAKE001",
    "candidate_id": "01HZCAND001",
    "parse_status": "complete",
    "ai_status": "ready",
    "ai_job_id": "01HZAIJOB001"
  }
}
```

**Response `503`:** AI unavailable.
```json
{
  "error": {
    "code": "ai_unavailable",
    "message": "AI normalization is not available. Use deterministic parsing or continue manually.",
    "details": { "method_available": "deterministic" }
  }
}
```

---

### 9.7 Get structured candidate

```
GET /intake-jobs/:id/candidate
```

Returns the current structured candidate for the intake job, including all suggested fields, ingredients, and steps.

**Response `200`:**
```json
{
  "data": {
    "id": "01HZCAND001",
    "intake_job_id": "01HZINTAKE001",
    "candidate_status": "in_review",
    "title": "Shakshuka",
    "short_description": "Eggs poached in spiced tomato sauce.",
    "dish_role": "Breakfast",
    "primary_cuisine": "Levantine",
    "secondary_cuisines": [],
    "technique_family": "Simmer",
    "complexity": "Basic",
    "time_class": "15–30 min",
    "service_format": "Single Plate",
    "ingredient_families": ["Egg", "Tomato", "Chili"],
    "sector": "Fire Line",
    "operational_class": "Field Meal",
    "servings": "2",
    "prep_time_minutes": 10,
    "cook_time_minutes": 20,
    "ingredients": [
      {
        "id": "01HZCANDI001",
        "position": 1,
        "quantity": "2",
        "unit": "tbsp",
        "item": "olive oil",
        "preparation": null,
        "optional": false,
        "display_text": "2 tbsp olive oil"
      }
    ],
    "steps": [
      {
        "id": "01HZCANDS001",
        "position": 1,
        "instruction": "Heat oil in a wide pan. Add onion and pepper. Cook until soft."
      }
    ],
    "notes": null,
    "service_notes": null,
    "source_credit": null,
    "ai_payload_json": null,
    "created_at": "2026-03-25T09:05:00Z",
    "updated_at": "2026-03-25T09:05:00Z"
  }
}
```

**Response `404`:** No candidate exists yet for this intake job. The user must run normalize first or create the candidate manually.

---

### 9.8 Update structured candidate

```
PATCH /intake-jobs/:id/candidate
```

Saves user edits to the candidate during review. Full array replacement applies to `ingredients` and `steps` when present.

**Request body (partial example):**
```json
{
  "dish_role": "Breakfast",
  "primary_cuisine": "Levantine",
  "secondary_cuisines": ["North African"],
  "dietary_flags": ["Vegetarian", "Gluten-Free"],
  "ingredients": [
    {
      "position": 1,
      "quantity": "2",
      "unit": "tbsp",
      "item": "olive oil",
      "display_text": "2 tbsp olive oil"
    },
    {
      "position": 2,
      "quantity": "1",
      "unit": null,
      "item": "onion",
      "preparation": "finely sliced",
      "display_text": "1 onion, finely sliced"
    }
  ]
}
```

**Response `200`:** Updated candidate object.

---

### 9.9 Approve intake into recipe

```
POST /intake-jobs/:id/approve
```

The trust gate. Creates a new recipe record from the reviewed candidate.

This endpoint does not edit an existing recipe. It creates a new one. The `resulting_recipe_id` on the intake job is set after successful creation.

**Request body:**
```json
{
  "verification_state": "Unverified",
  "overrides": {
    "title": "Shakshuka",
    "season": "All Year"
  }
}
```

| Field | Required | Description |
|---|---|---|
| `verification_state` | Yes | The trust state to apply to the new recipe |
| `overrides` | No | Final field values to apply over the candidate data |

**Validation before promotion:**

The API checks that the candidate has:
* a `title`
* at least one ingredient row
* at least one step row

If any are missing, returns `422` with `candidate_incomplete`.

**Response `201`:**
```json
{
  "data": {
    "recipe_id": "01HZRECIPE001",
    "slug": "shakshuka",
    "intake_job_id": "01HZINTAKE001",
    "verification_state": "Unverified"
  }
}
```

**Response `422`:** Candidate is incomplete.
```json
{
  "error": {
    "code": "candidate_incomplete",
    "message": "Candidate must have a title, at least one ingredient, and at least one step before promotion.",
    "details": { "missing": ["steps"] }
  }
}
```

---

### 9.10 Abandon intake job

```
POST /intake-jobs/:id/abandon
```

Marks the intake job as abandoned. The job and candidate are retained for history but excluded from active workflows.

**Response `200`:**
```json
{ "data": { "id": "...", "status": "abandoned" } }
```

---

## 10. Media Asset Endpoints

### 10.1 List media assets

```
GET /media-assets
```

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `asset_kind` | string | Filter by kind |
| `limit` | integer | Default: `50` |
| `offset` | integer | Default: `0` |

**Response `200`:** List of media asset records.

---

### 10.2 Get media asset metadata

```
GET /media-assets/:id
```

**Response `200`:**
```json
{
  "data": {
    "id": "01HZMEDIA001",
    "asset_kind": "recipe_photo",
    "original_filename": "bolognese-final.jpg",
    "mime_type": "image/jpeg",
    "relative_path": "uploads/recipes/2026/03/bolognese-final.jpg",
    "checksum": "a3f1b2...",
    "byte_size": 2048000,
    "width": 1920,
    "height": 1280,
    "created_at": "2026-03-25T09:00:00Z"
  }
}
```

---

### 10.3 Upload media asset

```
POST /media-assets
Content-Type: multipart/form-data
```

Standalone media upload not attached to a specific intake job. Used for recipe photos.

**Form fields:**

| Field | Required | Description |
|---|---|---|
| `file` | Yes | The file |
| `asset_kind` | No | Default: `recipe_photo` |

**Response `201`:** Media asset record.

---

### 10.4 Delete media asset

```
DELETE /media-assets/:id
```

Deletes the media asset record and the underlying file from disk. Will fail if the asset is currently referenced by a recipe source or intake job.

**Response `204`:** Deleted.

**Response `409`:** Asset is referenced and cannot be deleted.

---

### 10.5 Serve media file

```
GET /media-assets/:id/file
```

Streams the file content. Used by the UI to render images and serve source PDFs.

**Response `200`:** File content with appropriate `Content-Type` header.

**Response `404`:** Asset record not found or file missing from disk.

---

## 11. AI Job Endpoints

### 11.1 AI status

```
GET /settings/ai/status
```

Returns the current AI connection state. Does not trigger a connection test — returns the last known state.

**Response `200`:**
```json
{
  "data": {
    "enabled": true,
    "provider": "lmstudio",
    "endpoint": "http://localhost:1234/v1",
    "model_id": "mistral-7b-instruct-q4",
    "status": "connected",
    "last_checked_at": "2026-03-25T09:00:00Z"
  }
}
```

`status` values: `connected`, `disconnected`, `not_configured`, `error`.

---

### 11.2 Test AI connection

```
POST /settings/ai/test-connection
```

Triggers an active probe of the configured AI endpoint.

**Response `200` (success):**
```json
{
  "data": {
    "status": "connected",
    "endpoint": "http://localhost:1234/v1",
    "model_id": "mistral-7b-instruct-q4",
    "response_time_ms": 142
  }
}
```

**Response `503` (unreachable):**
```json
{
  "error": {
    "code": "ai_unavailable",
    "message": "Could not reach AI endpoint at http://localhost:1234/v1.",
    "details": { "endpoint": "http://localhost:1234/v1" }
  }
}
```

---

### 11.3 Suggest recipe metadata

```
POST /recipes/:id/suggest-metadata
```

Requests AI-generated metadata suggestions for an existing recipe. Creates an `ai_job` record. Returns staged suggestions — does not modify the recipe.

**Request body:**
```json
{
  "fields": ["dish_role", "primary_cuisine", "technique_family", "ingredient_families", "mood_tags"]
}
```

`fields` is optional. If omitted, the AI suggests all missing or low-confidence fields.

**Response `200`:**
```json
{
  "data": {
    "ai_job_id": "01HZAIJOB002",
    "request_state": "ready",
    "suggestions": {
      "dish_role": "Main",
      "primary_cuisine": "Levantine",
      "technique_family": "Simmer",
      "ingredient_families": ["Egg", "Tomato", "Chili"],
      "mood_tags": ["Comfort", "Spicy"]
    }
  },
  "meta": { "staged": true }
}
```

Suggestions are not applied until the client sends a `PATCH /recipes/:id` with the accepted values.

**Response `503`:** AI unavailable.

---

### 11.4 Apply accepted suggestions

Accepted suggestions from metadata enrichment or normalization are applied by a standard `PATCH /recipes/:id` request. There is no separate "accept suggestions" endpoint. The client reads the staged suggestions, lets the user approve or modify them, and sends the resulting field values in a patch.

---

### 11.5 Get AI job

```
GET /ai-jobs/:id
```

**Response `200`:**
```json
{
  "data": {
    "id": "01HZAIJOB001",
    "task_type": "normalize_recipe",
    "contract_name": "normalize_v1",
    "contract_version": "1.0",
    "source_entity_type": "intake_job",
    "source_entity_id": "01HZINTAKE001",
    "model_id": "mistral-7b-instruct-q4",
    "request_state": "ready",
    "error_code": null,
    "error_message": null,
    "started_at": "2026-03-25T09:05:00Z",
    "completed_at": "2026-03-25T09:05:03Z"
  }
}
```

---

### 11.6 List AI jobs

```
GET /ai-jobs
```

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `task_type` | string | Filter by task type |
| `request_state` | string | Filter by state |
| `source_entity_type` | string | `intake_job`, `structured_candidate`, `recipe` |
| `limit` | integer | Default: `50` |
| `offset` | integer | Default: `0` |

---

## 12. Settings Endpoints

### 12.1 Get all settings

```
GET /settings
```

**Response `200`:**
```json
{
  "data": {
    "app": {
      "schema_version": "001",
      "theme": "dark"
    },
    "ai": {
      "enabled": true,
      "provider": "lmstudio",
      "endpoint": "http://localhost:1234/v1",
      "model_id": "mistral-7b-instruct-q4",
      "timeout_seconds": 30
    },
    "archive": {
      "default_view": "grid",
      "default_sort": "updated_at_desc"
    },
    "media": {
      "storage_root": "./media"
    }
  }
}
```

---

### 12.2 Update settings group

```
PATCH /settings/:group
```

`group` is one of: `ai`, `archive`, `media`, `app`.

**Request body (example — update AI config):**
```json
{
  "enabled": true,
  "endpoint": "http://localhost:1234/v1",
  "model_id": "phi-3-mini-instruct",
  "timeout_seconds": 45
}
```

**Response `200`:** Updated settings group object.

---

## 13. Backup Endpoints

### 13.1 Create backup

```
POST /backups
```

Creates a timestamped backup of the database and media assets.

**Request body:** none.

**Response `201`:**
```json
{
  "data": {
    "id": "01HZBKUP001",
    "filename": "galley-archive-2026-03-25T09-00-00Z.db",
    "database_path": "backups/galley-archive-2026-03-25T09-00-00Z.db",
    "media_included": false,
    "byte_size": 2048000,
    "created_at": "2026-03-25T09:00:00Z"
  }
}
```

`media_included` indicates whether media files were bundled. Full media backup is configurable. The database-only backup is always created.

---

### 13.2 List backups

```
GET /backups
```

**Response `200`:** List of backup metadata records, newest first.

---

### 13.3 Get backup metadata

```
GET /backups/:id
```

**Response `200`:** Single backup metadata record.

---

### 13.4 Download backup

```
GET /backups/:id/download
```

Streams the backup file to the client.

**Response `200`:** File stream with `Content-Disposition: attachment` header.

---

### 13.5 Restore from backup

```
POST /backups/:id/restore
```

Restores the archive from a selected backup. This is a destructive operation on the current database.

**Behavior:**

1. Creates a pre-restore backup of the current database.
2. Replaces the active database with the backup file.
3. Applies any pending schema migrations.
4. Returns success or failure with detail.

**Request body:** none.

**Response `200`:**
```json
{
  "data": {
    "restored_from": "01HZBKUP001",
    "pre_restore_backup": "01HZBKUP002",
    "schema_version": "001",
    "recipe_count": 87
  }
}
```

**Response `500`:** Restore failed. Current database is preserved.

---

### 13.6 Export recipe

```
GET /recipes/:id/export
```

Exports a single recipe as a portable JSON document.

**Response `200`:** `Content-Disposition: attachment; filename="shakshuka.json"`

```json
{
  "export_version": "1",
  "exported_at": "2026-03-25T09:00:00Z",
  "recipe": { ... }
}
```

---

## 14. System Endpoints

### 14.1 Health check

```
GET /system/health
```

Confirms the API is running and the database is reachable.

**Response `200`:**
```json
{
  "data": {
    "status": "ok",
    "database": "connected",
    "schema_version": "001",
    "uptime_seconds": 3842
  }
}
```

**Response `500`:** Service is not healthy.

---

### 14.2 System info

```
GET /system/info
```

Returns application version and environment information.

**Response `200`:**
```json
{
  "data": {
    "app_version": "0.1.0",
    "schema_version": "001",
    "recipe_count": 87,
    "media_asset_count": 34,
    "database_size_bytes": 2097152,
    "media_storage_size_bytes": 104857600,
    "ai_status": "connected"
  }
}
```

---

## 15. Authentication

### v1 model

v1 assumes local home network use. No user authentication is required.

The server binds to the local network interface configured in deployment. All clients on the home network can reach the API without credentials.

**What is still required regardless of no-auth:**

* File upload validation (type, size, path traversal protection)
* No path traversal in file serving endpoints
* Settings endpoints must not expose raw secrets through API responses (e.g., mask API keys if remote AI providers are configured in v2)
* Rate limiting on AI endpoints to prevent accidental runaway calls to a local model

### LAN access

The API is accessible to all devices on the home network when the server binds to `0.0.0.0` or the host's LAN IP. This is the default operational mode.

### v2 consideration

Optional simple access control (a single shared passcode) may be added in v2 for households that want light protection. This is not in v1 scope.

---

## 16. Versioning

### Path versioning

All routes are under `/api/v1`. Future breaking changes require a `/api/v2` prefix. The v1 surface is maintained.

### Additive changes within v1

New optional response fields may be added within v1 without a version increment. Clients must tolerate unknown fields.

New optional query parameters may be added without a version increment.

### Breaking changes that require v2

* Removing or renaming a field
* Changing a field's type
* Removing an endpoint
* Changing an endpoint's method
* Modifying validation rules in a way that rejects previously valid payloads

### AI contract versioning

AI prompt contract versions are tracked independently in `ai_jobs.contract_version`. API version and AI contract version are separate.

---

## 17. Anti-Patterns

### 17.1 Single opaque save endpoint

`POST /save` or `POST /import-recipe` that collapses intake, candidate review, and recipe creation into one call destroys the trust model. Every stage must have its own endpoint.

### 17.2 AI-to-recipe direct write

No AI endpoint may write fields directly to a `recipes` row. AI endpoints return staged suggestions. Application of those suggestions requires a separate client-initiated `PATCH /recipes/:id`.

### 17.3 Implicit verification state

No endpoint other than `POST /recipes` (create), `PATCH /recipes/:id` (explicit edit), and `POST /intake-jobs/:id/approve` may set `verification_state`. Normalization cannot set it. AI cannot set it. Archive/unarchive actions set `archived` only.

### 17.4 Blocking UI on AI failure

AI endpoint failures return graceful error responses. The UI must continue functioning. The API must not return `500` when LM Studio is simply unreachable.

### 17.5 Mixing candidate and recipe response shapes

`GET /intake-jobs/:id/candidate` returns a candidate object. `GET /recipes/:id` returns a recipe object. They are different resources with different schemas. The API must not use the same response shape for both.

### 17.6 Hiding intake history

Once an intake job is `approved`, the intake record and its source must remain retrievable. The `intake_job_id` on the recipe links back to it. The API must not delete intake records on approval.

---

## 18. Final API Standard

The v1 API succeeds if:

* every recipe in the archive has a retrievable source record
* trust state can only be set by explicit user-initiated requests
* AI actions always produce staged suggestions, never direct mutations
* intake failure at any stage leaves source material intact
* the archive remains fully operable if LM Studio is not running
* a backup of the full archive can be created and downloaded without leaving the product

Any endpoint design that contradicts these conditions is out of standard.

---

## Decisions Made

1. `PATCH /recipes/:id` uses full array replacement for `ingredients` and `steps`. Field-level row patching is deferred to v2.
2. Accepting AI suggestions is a client-side operation (read suggestions, PATCH the recipe). No separate "accept suggestions" endpoint.
3. `POST /intake-jobs/:id/normalize` returns `503` when AI is unavailable but does not alter intake job state. Manual editing continues.
4. `POST /intake-jobs/:id/approve` validates title, ingredients, and steps before creating a recipe. Missing fields return `422`.
5. `abandoned` is the correct final state for explicitly closed incomplete intake jobs.
6. Hard delete (`DELETE /recipes/:id`) is in the API but should not be the default UX path.
7. `GET /search/facets` returns non-zero values only. Zero-count filter options are omitted.
8. Media assets are never auto-deleted. Deletion fails with `409` if the asset is referenced.
9. Restore creates a pre-restore backup before overwriting the active database.
10. All AI endpoints include `"staged": true` in `meta` to signal that no mutation has occurred.
11. `operational_class` used throughout (aligned with schema v2.0). `class` is not used anywhere in the API.

---

## Open Questions

1. **Normalize response — sync vs async** — For fast local models, normalization may complete in under two seconds. Should the normalize endpoint return synchronously with the completed candidate (if fast enough) or always return a pending state and require a follow-up GET? Sync-first with a timeout fallback to async is the recommended pattern but needs an implementation decision.
2. **FTS score normalization** — SQLite FTS5 rank scores are arbitrary floats. Should the API normalize them to a 0–1 scale or return raw rank values? Raw values are simpler; the UI can sort by them without interpreting the scale.
3. **`GET /recipes` vs `GET /search/recipes`** — Are these two endpoints necessary, or should a single `/recipes` with an optional `q` parameter replace both? The current split keeps browse and search conceptually separate but adds surface area.
4. **Ingredient family filter via multi-select JSON** — The `ingredient_family` filter matches a single value. Should the API support multi-value filtering (e.g., `ingredient_family=Beef&ingredient_family=Tomato`)? AND vs OR semantics would need to be defined.
5. **Media storage root configuration** — Should `media.storage_root` be settable via the settings API, or should it be environment-variable-only to prevent accidental misconfiguration through the UI?

---

## Deliverables Created

* `docs/07_api/api-spec.md` v2.0 — this document (supersedes v1.0)

---

## What the Next Document Should Cover

**`docs/09_ops/local-deployment.md` — Local Deployment**

This document should define how the canonical API and local application stack are run in development and local production, including:

* backend bind host and port behavior
* frontend/backend serving strategy
* SQLite path and media root configuration
* backup locations
* optional LM Studio connectivity from the backend
* localhost versus LAN access rules
