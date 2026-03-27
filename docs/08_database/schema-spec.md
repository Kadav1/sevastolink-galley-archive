# Sevastolink Galley Archive

## Database Schema Spec v2.0

---

## 1. Purpose

This document defines the complete v1 SQLite database schema for Sevastolink Galley Archive.

It establishes:

* all tables, columns, types, and constraints
* the relationship model between recipes, sources, intake, candidates, media, and AI jobs
* which multi-select fields use JSON arrays vs junction tables in v1
* indexing strategy for retrieval performance
* the schema migration and versioning approach
* seed and example data for testing
* forward-compatibility notes for v2 additions

This document supersedes schema-spec v1.0. It is aligned with content-taxonomy-spec v2.0.

---

## 2. Schema Philosophy

### Established facts

* The product is local-first. SQLite is the correct v1 database engine.
* Raw source, structured candidate, and approved recipe must remain distinct entities.
* Trust and verification state are explicit, user-controlled, and schema-enforced.
* AI fields are optional and must never become canonical recipe truth.
* The archive is a system of record. Durability and queryability take precedence over schema convenience.

### Multi-select field approach for v1

The taxonomy spec v2.0 recommends JSON arrays stored in a single `TEXT` column for multi-select fields in v1. Junction tables are deferred to v2.

**Rationale:** For a single-user personal archive at household scale, JSON arrays reduce table count, simplify queries, and impose no measurable performance cost. SQLite's `json_each()` function provides adequate filtering capability. If performance or query complexity requires it, a migration to junction tables is straightforward.

**Fields stored as JSON arrays in v1:**
* `secondary_cuisines` — `TEXT` JSON array
* `ingredient_families` — `TEXT` JSON array
* `mood_tags` — `TEXT` JSON array
* `storage_profile` — `TEXT` JSON array
* `dietary_flags` — `TEXT` JSON array
* `provision_tags` — `TEXT` JSON array

All other taxonomy fields are first-class `TEXT` columns.

### Reserved word avoidance

The taxonomy uses `class` as a field name. `class` is a reserved keyword in SQL, Python, JavaScript, and most other contexts. In the schema, this field is named `operational_class` throughout.

Similarly, `group` is reserved in SQL. Ingredient group headings use `group_heading`.

---

## 3. Table List

| Table | Purpose |
|---|---|
| `schema_migrations` | Schema version tracking |
| `recipes` | Approved archive records |
| `recipe_ingredients` | Ordered ingredient rows |
| `recipe_steps` | Ordered method steps |
| `recipe_notes` | Typed note fields |
| `recipe_sources` | Provenance and raw source |
| `intake_jobs` | Intake workflow tracking |
| `structured_candidates` | Pre-approval intermediate records |
| `candidate_ingredients` | Candidate ingredient rows |
| `candidate_steps` | Candidate method steps |
| `media_assets` | Local file registry |
| `ai_jobs` | AI request and response records |
| `settings` | Application configuration |
| `recipe_search_fts` | FTS5 full-text search index |

---

## 4. Complete SQL Schema

### 4.1 Schema migrations

```sql
CREATE TABLE schema_migrations (
  version     TEXT    PRIMARY KEY,
  applied_at  TEXT    NOT NULL,
  description TEXT
);
```

Seed row for v1 initial schema:
```sql
INSERT INTO schema_migrations (version, applied_at, description)
VALUES ('001', datetime('now'), 'Initial v1 schema');
```

---

### 4.2 Recipes

The core approved archive record. Every recipe in the system has exactly one row here.

```sql
CREATE TABLE recipes (
  -- Identity
  id                    TEXT    PRIMARY KEY,
  slug                  TEXT    NOT NULL UNIQUE,
  title                 TEXT    NOT NULL,
  short_description     TEXT,

  -- Primary taxonomy (single-select, first-class columns)
  dish_role             TEXT,
  primary_cuisine       TEXT,
  technique_family      TEXT,
  complexity            TEXT,
  time_class            TEXT,
  service_format        TEXT,
  season                TEXT,

  -- Multi-select taxonomy (JSON arrays)
  secondary_cuisines    TEXT    NOT NULL DEFAULT '[]',
  ingredient_families   TEXT    NOT NULL DEFAULT '[]',
  mood_tags             TEXT    NOT NULL DEFAULT '[]',
  storage_profile       TEXT    NOT NULL DEFAULT '[]',
  dietary_flags         TEXT    NOT NULL DEFAULT '[]',
  provision_tags        TEXT    NOT NULL DEFAULT '[]',

  -- Sevastolink overlay (single-select)
  sector                TEXT,
  operational_class     TEXT,
  heat_window           TEXT,

  -- Timing
  servings              TEXT,
  prep_time_minutes     INTEGER,
  cook_time_minutes     INTEGER,
  total_time_minutes    INTEGER GENERATED ALWAYS AS (
                          COALESCE(prep_time_minutes, 0) +
                          COALESCE(cook_time_minutes, 0)
                        ) VIRTUAL,
  rest_time_minutes     INTEGER,

  -- Trust and state
  verification_state    TEXT    NOT NULL DEFAULT 'Draft'
                          CHECK (verification_state IN
                            ('Draft', 'Unverified', 'Verified', 'Archived')),
  favorite              INTEGER NOT NULL DEFAULT 0 CHECK (favorite IN (0, 1)),
  archived              INTEGER NOT NULL DEFAULT 0 CHECK (archived IN (0, 1)),
  rating                INTEGER CHECK (rating IS NULL OR (rating BETWEEN 1 AND 5)),

  -- Search support (derived, maintained by application on save)
  ingredient_text       TEXT,

  -- Linkage
  source_id             TEXT    REFERENCES recipe_sources(id) ON DELETE SET NULL,
  intake_job_id         TEXT    REFERENCES intake_jobs(id)    ON DELETE SET NULL,

  -- Timestamps
  created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  last_viewed_at        TEXT,
  last_cooked_at        TEXT
);
```

**Notes:**

`total_time_minutes` is a generated virtual column in SQLite 3.31+. If the target SQLite version is older, compute and store this value in the application layer instead, remove the `GENERATED ALWAYS AS` clause, and keep the column as a plain `INTEGER`.

`ingredient_text` is a denormalized flat string of all ingredient item names for this recipe, maintained by the application at every save. Example value: `"beef onion celery carrot tomato paste wine"`. Used by the FTS index. Not displayed to the user.

---

### 4.3 Recipe ingredients

Ordered structured ingredient rows belonging to a recipe.

```sql
CREATE TABLE recipe_ingredients (
  id            TEXT    PRIMARY KEY,
  recipe_id     TEXT    NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  position      INTEGER NOT NULL,
  group_heading TEXT,
  quantity      TEXT,
  unit          TEXT,
  item          TEXT    NOT NULL,
  preparation   TEXT,
  optional      INTEGER NOT NULL DEFAULT 0 CHECK (optional IN (0, 1)),
  display_text  TEXT
);
```

**Field notes:**

`group_heading` — optional section label for grouped ingredient lists (e.g., `"For the sauce"`, `"Marinade"`). NULL when no grouping is used. Rows within the same group share a heading value and are sorted by `position`.

`quantity` — stored as `TEXT` to support fractional and descriptive quantities (`"1/2"`, `"a handful"`, `"to taste"`).

`display_text` — the rendered ingredient line as a full string. Maintained by the application. Used for display and search. Example: `"500 g beef mince, not too lean"`.

---

### 4.4 Recipe steps

Ordered method rows belonging to a recipe.

```sql
CREATE TABLE recipe_steps (
  id             TEXT    PRIMARY KEY,
  recipe_id      TEXT    NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  position       INTEGER NOT NULL,
  instruction    TEXT    NOT NULL,
  time_note      TEXT,
  equipment_note TEXT
);
```

---

### 4.5 Recipe notes

Typed note fields for a recipe. Stored as separate rows by note type to allow nullable sections without a sprawling column set on the recipes table.

```sql
CREATE TABLE recipe_notes (
  id          TEXT    PRIMARY KEY,
  recipe_id   TEXT    NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  note_type   TEXT    NOT NULL
                CHECK (note_type IN (
                  'recipe',
                  'service',
                  'storage',
                  'substitution',
                  'source'
                )),
  content     TEXT    NOT NULL,
  created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

Maximum one row per `(recipe_id, note_type)` combination is enforced at the application layer, not by a unique constraint, to avoid migration complexity if additional note types are added later.

---

### 4.6 Recipe sources

Provenance and raw source records. One primary source per recipe in v1.

```sql
CREATE TABLE recipe_sources (
  id                    TEXT    PRIMARY KEY,
  source_type           TEXT    NOT NULL
                          CHECK (source_type IN (
                            'Manual',
                            'Book',
                            'Website',
                            'Family Recipe',
                            'Screenshot',
                            'PDF',
                            'Image / Scan',
                            'AI-Normalized',
                            'Composite / Merged'
                          )),
  source_title          TEXT,
  source_author         TEXT,
  source_url            TEXT,
  source_notes          TEXT,
  raw_source_text       TEXT,
  source_media_asset_id TEXT    REFERENCES media_assets(id) ON DELETE SET NULL,
  created_at            TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

`raw_source_text` — the unmodified original text as received during intake. This field is write-once after the intake is saved. The application must not overwrite it during normalization or editing.

---

### 4.7 Intake jobs

Workflow tracking records for all intake paths. These exist independently of the resulting recipe.

```sql
CREATE TABLE intake_jobs (
  id                    TEXT    PRIMARY KEY,
  intake_type           TEXT    NOT NULL
                          CHECK (intake_type IN (
                            'manual',
                            'paste_text',
                            'url',
                            'file'
                          )),
  status                TEXT    NOT NULL DEFAULT 'captured'
                          CHECK (status IN (
                            'captured',
                            'extracting',
                            'structured',
                            'in_review',
                            'approved',
                            'failed',
                            'abandoned'
                          )),
  parse_status          TEXT    NOT NULL DEFAULT 'not_started'
                          CHECK (parse_status IN (
                            'not_started',
                            'in_progress',
                            'partial',
                            'complete',
                            'failed'
                          )),
  ai_status             TEXT    NOT NULL DEFAULT 'not_requested'
                          CHECK (ai_status IN (
                            'not_requested',
                            'pending',
                            'processing',
                            'ready',
                            'partial',
                            'failed'
                          )),
  review_status         TEXT    NOT NULL DEFAULT 'not_started'
                          CHECK (review_status IN (
                            'not_started',
                            'in_progress',
                            'saved_partial',
                            'completed'
                          )),
  raw_source_text       TEXT,
  source_url            TEXT,
  source_media_asset_id TEXT    REFERENCES media_assets(id) ON DELETE SET NULL,
  source_snapshot_path  TEXT,
  error_code            TEXT,
  error_message         TEXT,
  resulting_recipe_id   TEXT    REFERENCES recipes(id) ON DELETE SET NULL,
  created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  completed_at          TEXT
);
```

`abandoned` is added to `status` to handle intake jobs the user started but deliberately closed without completing. This avoids leaving jobs in `in_review` indefinitely.

---

### 4.8 Structured candidates

The reviewable intermediate record produced during intake. One candidate per intake job in v1.

```sql
CREATE TABLE structured_candidates (
  id                    TEXT    PRIMARY KEY,
  intake_job_id         TEXT    NOT NULL UNIQUE
                          REFERENCES intake_jobs(id) ON DELETE CASCADE,
  candidate_status      TEXT    NOT NULL DEFAULT 'pending'
                          CHECK (candidate_status IN (
                            'pending',
                            'in_review',
                            'accepted',
                            'discarded'
                          )),

  -- Taxonomy fields mirror recipes table (nullable — candidates are incomplete by nature)
  title                 TEXT,
  short_description     TEXT,
  dish_role             TEXT,
  primary_cuisine       TEXT,
  secondary_cuisines    TEXT    NOT NULL DEFAULT '[]',
  technique_family      TEXT,
  complexity            TEXT,
  time_class            TEXT,
  service_format        TEXT,
  season                TEXT,
  ingredient_families   TEXT    NOT NULL DEFAULT '[]',
  mood_tags             TEXT    NOT NULL DEFAULT '[]',
  storage_profile       TEXT    NOT NULL DEFAULT '[]',
  dietary_flags         TEXT    NOT NULL DEFAULT '[]',
  provision_tags        TEXT    NOT NULL DEFAULT '[]',
  sector                TEXT,
  operational_class     TEXT,
  heat_window           TEXT,

  servings              TEXT,
  prep_time_minutes     INTEGER,
  cook_time_minutes     INTEGER,
  total_time_minutes    INTEGER,
  rest_time_minutes     INTEGER,

  -- Notes (single field on candidates — typed notes only needed on approved recipes)
  notes                 TEXT,
  service_notes         TEXT,
  source_credit         TEXT,

  -- The full AI-suggested payload preserved for reference
  ai_payload_json       TEXT,

  created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at            TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

`ai_payload_json` — the raw JSON as returned by the AI normalization request. Preserved for debugging and re-review. Not used as a source of truth for any displayed field.

---

### 4.9 Candidate ingredients

```sql
CREATE TABLE candidate_ingredients (
  id            TEXT    PRIMARY KEY,
  candidate_id  TEXT    NOT NULL REFERENCES structured_candidates(id) ON DELETE CASCADE,
  position      INTEGER NOT NULL,
  group_heading TEXT,
  quantity      TEXT,
  unit          TEXT,
  item          TEXT,
  preparation   TEXT,
  optional      INTEGER NOT NULL DEFAULT 0 CHECK (optional IN (0, 1)),
  display_text  TEXT
);
```

---

### 4.10 Candidate steps

```sql
CREATE TABLE candidate_steps (
  id            TEXT    PRIMARY KEY,
  candidate_id  TEXT    NOT NULL REFERENCES structured_candidates(id) ON DELETE CASCADE,
  position      INTEGER NOT NULL,
  instruction   TEXT,
  time_note     TEXT,
  equipment_note TEXT
);
```

---

### 4.11 Media assets

Registry of local files stored outside the database. The database stores metadata and relative paths only. No binary content is stored in SQLite in v1.

```sql
CREATE TABLE media_assets (
  id                TEXT    PRIMARY KEY,
  asset_kind        TEXT    NOT NULL
                      CHECK (asset_kind IN (
                        'source_image',
                        'source_pdf',
                        'source_screenshot',
                        'import_snapshot',
                        'recipe_photo',
                        'derived_image'
                      )),
  original_filename TEXT,
  mime_type         TEXT,
  relative_path     TEXT    NOT NULL,
  checksum          TEXT,
  byte_size         INTEGER,
  width             INTEGER,
  height            INTEGER,
  duration_seconds  REAL,
  created_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

`relative_path` — path relative to the configured media storage root. Example: `uploads/recipes/2026/03/bolognese-source.jpg`. The media root is stored in `settings`.

`checksum` — SHA-256 hex digest of the file content. Recorded at upload time. Used for backup verification and duplicate detection.

`recipe_photo` is added to `asset_kind` to support recipe images in v1, even if the full photo management feature is deferred.

---

### 4.12 AI jobs

Optional records for AI requests and responses. Created when an AI normalization or enrichment request is made. Retained for debugging and audit.

```sql
CREATE TABLE ai_jobs (
  id                    TEXT    PRIMARY KEY,
  task_type             TEXT    NOT NULL
                          CHECK (task_type IN (
                            'normalize_recipe',
                            'enrich_metadata',
                            'suggest_tags',
                            'extract_url',
                            'extract_file',
                            'renormalize'
                          )),
  contract_name         TEXT,
  contract_version      TEXT,
  source_entity_type    TEXT    NOT NULL
                          CHECK (source_entity_type IN (
                            'intake_job',
                            'structured_candidate',
                            'recipe'
                          )),
  source_entity_id      TEXT    NOT NULL,
  model_id              TEXT,
  request_state         TEXT    NOT NULL DEFAULT 'pending'
                          CHECK (request_state IN (
                            'pending',
                            'processing',
                            'ready',
                            'partial',
                            'failed'
                          )),
  error_code            TEXT,
  error_message         TEXT,
  raw_prompt_text       TEXT,
  raw_response_json     TEXT,
  validated_output_json TEXT,
  started_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  completed_at          TEXT
);
```

`raw_prompt_text` — the exact prompt sent to the model. Retained for debugging and prompt contract verification.

`validated_output_json` — the parsed and schema-validated version of the model response, if validation passed. NULL if the response was malformed or validation failed.

---

### 4.13 Settings

Application configuration as a key/value store.

```sql
CREATE TABLE settings (
  key           TEXT    PRIMARY KEY,
  value_json    TEXT    NOT NULL,
  updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

**Seed rows for v1:**

```sql
INSERT INTO settings (key, value_json) VALUES
  ('app.schema_version',          '"001"'),
  ('app.theme',                   '"dark"'),
  ('ai.enabled',                  'false'),
  ('ai.provider',                 '"lmstudio"'),
  ('ai.endpoint',                 '"http://localhost:1234/v1"'),
  ('ai.model_id',                 'null'),
  ('ai.timeout_seconds',          '30'),
  ('media.storage_root',          '"./media"'),
  ('archive.default_view',        '"grid"'),
  ('archive.default_sort',        '"updated_at_desc"');
```

---

### 4.14 Full-text search virtual table

```sql
CREATE VIRTUAL TABLE recipe_search_fts USING fts5(
  recipe_id       UNINDEXED,
  title,
  short_description,
  ingredient_text,
  notes_combined,
  source_title,
  source_notes,
  tokenize = 'unicode61 remove_diacritics 1'
);
```

`notes_combined` — a concatenation of all note content for the recipe, assembled by the application at index update time.

`tokenize = 'unicode61 remove_diacritics 1'` — enables accent-insensitive matching. `crème` matches `creme`. Essential for a culinary archive with international content.

**Synchronization strategy:** The FTS table is maintained by the application layer, not by SQLite triggers. On every recipe save, the application:

1. Deletes the existing FTS row for `recipe_id`.
2. Rebuilds the row from current recipe and notes data.
3. Inserts the updated row.

This is simpler than trigger maintenance and avoids trigger debugging complexity in v1.

---

## 5. Indexes

```sql
-- Recipes: primary retrieval paths
CREATE UNIQUE INDEX idx_recipes_slug
  ON recipes(slug);

CREATE INDEX idx_recipes_verification_state
  ON recipes(verification_state);

CREATE INDEX idx_recipes_favorite
  ON recipes(favorite)
  WHERE favorite = 1;

CREATE INDEX idx_recipes_dish_role
  ON recipes(dish_role);

CREATE INDEX idx_recipes_primary_cuisine
  ON recipes(primary_cuisine);

CREATE INDEX idx_recipes_technique_family
  ON recipes(technique_family);

CREATE INDEX idx_recipes_complexity
  ON recipes(complexity);

CREATE INDEX idx_recipes_time_class
  ON recipes(time_class);

CREATE INDEX idx_recipes_sector
  ON recipes(sector);

CREATE INDEX idx_recipes_operational_class
  ON recipes(operational_class);

CREATE INDEX idx_recipes_updated_at
  ON recipes(updated_at DESC);

CREATE INDEX idx_recipes_created_at
  ON recipes(created_at DESC);

CREATE INDEX idx_recipes_last_cooked_at
  ON recipes(last_cooked_at DESC);

-- Recipe ingredients: item search and ordering
CREATE INDEX idx_recipe_ingredients_recipe_id
  ON recipe_ingredients(recipe_id);

CREATE INDEX idx_recipe_ingredients_item
  ON recipe_ingredients(item);

CREATE INDEX idx_recipe_ingredients_position
  ON recipe_ingredients(recipe_id, position);

-- Recipe steps: ordering
CREATE INDEX idx_recipe_steps_recipe_id_position
  ON recipe_steps(recipe_id, position);

-- Recipe notes: type lookup
CREATE INDEX idx_recipe_notes_recipe_id
  ON recipe_notes(recipe_id);

CREATE INDEX idx_recipe_notes_type
  ON recipe_notes(recipe_id, note_type);

-- Recipe sources: type and URL lookup
CREATE INDEX idx_recipe_sources_source_type
  ON recipe_sources(source_type);

CREATE INDEX idx_recipe_sources_source_url
  ON recipe_sources(source_url)
  WHERE source_url IS NOT NULL;

-- Intake jobs: workflow management
CREATE INDEX idx_intake_jobs_status
  ON intake_jobs(status);

CREATE INDEX idx_intake_jobs_intake_type
  ON intake_jobs(intake_type);

CREATE INDEX idx_intake_jobs_created_at
  ON intake_jobs(created_at DESC);

CREATE INDEX idx_intake_jobs_resulting_recipe_id
  ON intake_jobs(resulting_recipe_id)
  WHERE resulting_recipe_id IS NOT NULL;

-- Structured candidates: intake linkage
CREATE UNIQUE INDEX idx_structured_candidates_intake_job_id
  ON structured_candidates(intake_job_id);

-- Candidate ingredients: ordering
CREATE INDEX idx_candidate_ingredients_candidate_id_position
  ON candidate_ingredients(candidate_id, position);

-- Candidate steps: ordering
CREATE INDEX idx_candidate_steps_candidate_id_position
  ON candidate_steps(candidate_id, position);

-- AI jobs: task and state lookup
CREATE INDEX idx_ai_jobs_task_type
  ON ai_jobs(task_type);

CREATE INDEX idx_ai_jobs_request_state
  ON ai_jobs(request_state);

CREATE INDEX idx_ai_jobs_source_entity
  ON ai_jobs(source_entity_type, source_entity_id);

-- Media assets: kind lookup
CREATE INDEX idx_media_assets_asset_kind
  ON media_assets(asset_kind);
```

---

## 6. Relationship Model

```
recipes
  ├── recipe_ingredients     (recipe_id FK, CASCADE DELETE)
  ├── recipe_steps           (recipe_id FK, CASCADE DELETE)
  ├── recipe_notes           (recipe_id FK, CASCADE DELETE)
  ├── recipe_sources         (source_id FK on recipes, SET NULL)
  └── intake_jobs            (intake_job_id FK on recipes, SET NULL)
       └── structured_candidates  (intake_job_id FK UNIQUE, CASCADE DELETE)
            ├── candidate_ingredients  (candidate_id FK, CASCADE DELETE)
            └── candidate_steps        (candidate_id FK, CASCADE DELETE)

media_assets
  ├── referenced by recipe_sources.source_media_asset_id (SET NULL)
  └── referenced by intake_jobs.source_media_asset_id    (SET NULL)

ai_jobs
  └── references intake_jobs / structured_candidates / recipes
      via (source_entity_type, source_entity_id) — no FK enforced
      (polymorphic reference; FK enforcement handled in application layer)
```

**Key rules:**

* Deleting a recipe cascades to its ingredients, steps, and notes. Source and intake records are not deleted — they represent historical evidence and workflow history.
* Deleting an intake job cascades to its structured candidate and all candidate rows.
* Media assets are never auto-deleted. Orphan cleanup is a manual admin operation.
* AI jobs are never auto-deleted. They are append-only audit records.

---

## 7. Query Patterns

### 7.1 Archive browse — verified recipes by cuisine

```sql
SELECT id, slug, title, dish_role, primary_cuisine, technique_family,
       complexity, time_class, verification_state, favorite, updated_at
FROM recipes
WHERE verification_state = 'Verified'
  AND primary_cuisine = 'Italian'
ORDER BY updated_at DESC;
```

### 7.2 Filter by multi-select field (JSON array)

```sql
-- Recipes tagged with ingredient family "Beef"
SELECT id, title
FROM recipes
WHERE EXISTS (
  SELECT 1 FROM json_each(ingredient_families)
  WHERE value = 'Beef'
);
```

```sql
-- Recipes with any of: Vegan, Gluten-Free
SELECT id, title
FROM recipes
WHERE EXISTS (
  SELECT 1 FROM json_each(dietary_flags)
  WHERE value IN ('Vegan', 'Gluten-Free')
);
```

### 7.3 Full-text search

```sql
-- FTS search across title, description, ingredients, notes
SELECT r.id, r.title, r.dish_role, r.primary_cuisine
FROM recipe_search_fts fts
JOIN recipes r ON r.id = fts.recipe_id
WHERE recipe_search_fts MATCH 'lamb shoulder'
ORDER BY rank;
```

### 7.4 Ingredient lookup

```sql
-- All recipes containing "anchovies" in any ingredient row
SELECT DISTINCT r.id, r.title
FROM recipes r
JOIN recipe_ingredients ri ON ri.recipe_id = r.id
WHERE ri.item LIKE '%anchov%';
```

### 7.5 Kitchen mode — open recipe with all content

```sql
-- Single query join for recipe detail
SELECT
  r.*,
  rs.source_type, rs.source_title, rs.source_url, rs.source_notes
FROM recipes r
LEFT JOIN recipe_sources rs ON rs.id = r.source_id
WHERE r.slug = 'ragu-alla-bolognese';

-- Then in separate queries:
SELECT * FROM recipe_ingredients WHERE recipe_id = ? ORDER BY position;
SELECT * FROM recipe_steps       WHERE recipe_id = ? ORDER BY position;
SELECT * FROM recipe_notes       WHERE recipe_id = ?;
```

### 7.6 Intake — resume in-progress job

```sql
SELECT ij.*, sc.*
FROM intake_jobs ij
LEFT JOIN structured_candidates sc ON sc.intake_job_id = ij.id
WHERE ij.status IN ('captured', 'structured', 'in_review')
ORDER BY ij.updated_at DESC;
```

---

## 8. Example Complete Record

### JSON representation

```json
{
  "recipe": {
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
    "favorite": 1,
    "archived": 0,
    "rating": 5,
    "ingredient_text": "olive oil onion red pepper garlic cumin paprika chilli flakes tin tomatoes egg salt pepper parsley",
    "created_at": "2026-03-25T09:00:00Z",
    "updated_at": "2026-03-25T09:00:00Z",
    "last_cooked_at": "2026-03-20T00:00:00Z"
  },
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
    },
    {
      "id": "01HZB...",
      "position": 2,
      "group_heading": null,
      "quantity": "1",
      "unit": null,
      "item": "onion",
      "preparation": "finely sliced",
      "optional": false,
      "display_text": "1 onion, finely sliced"
    }
  ],
  "steps": [
    {
      "id": "01HZC...",
      "position": 1,
      "instruction": "Heat the oil in a wide, deep frying pan over medium heat. Add the onion and pepper. Cook until soft, about 8 minutes.",
      "time_note": "8 minutes",
      "equipment_note": "wide frying pan with lid"
    }
  ],
  "notes": [
    {
      "note_type": "service",
      "content": "Do not overcook the eggs. Serve in the pan with bread for scooping. Dukkah works well on top."
    },
    {
      "note_type": "substitution",
      "content": "Feta crumbled on top before serving is a good variant. Add a pinch of sumac."
    }
  ],
  "source": {
    "source_type": "Manual",
    "source_title": "House Version",
    "source_author": null,
    "source_url": null,
    "source_notes": "Personal version, built up from several references. Settled after about five attempts.",
    "raw_source_text": null
  }
}
```

---

## 9. Migration Approach

### 9.1 Versioning

Every schema change is applied as a numbered migration. The `schema_migrations` table records applied versions.

Migration files are named: `NNN_description.sql` where `NNN` is a zero-padded integer.

Example:
```
migrations/
  001_initial_schema.sql
  002_add_rest_time_minutes.sql
  003_add_recipe_photos_table.sql
```

### 9.2 Startup check

On application startup, the backend:

1. Connects to the SQLite database.
2. Queries `schema_migrations` for applied versions.
3. Compares against the list of available migration files.
4. Applies any unapplied migrations in order.
5. Records each applied migration with a timestamp.

If `schema_migrations` does not exist, the schema is new. Apply all migrations from the beginning.

### 9.3 Forward-compatibility rules

* Never DROP a column or table without a clear migration path and data preservation step.
* Never rename a column without migrating existing data.
* New nullable columns may be added safely in later migrations.
* New tables are always safe to add.
* Changing a CHECK constraint requires recreating the table (SQLite limitation). Plan constraint values carefully.

### 9.4 Backup before migration

The application must create a timestamped database backup before applying any migrations. This is non-negotiable.

```
backups/
  galley-archive-2026-03-25T09-00-00Z-pre-migration-002.db
```

---

## 10. v2 Forward-Compatibility Notes

The following additions are anticipated in v2. The v1 schema accommodates them without redesign.

### 10.1 Junction tables for multi-select fields

If query performance requires it, migrate `secondary_cuisines`, `ingredient_families`, `mood_tags`, `storage_profile`, `dietary_flags`, and `provision_tags` from JSON arrays to junction tables:

```sql
-- Example junction table pattern
CREATE TABLE recipe_ingredient_families (
  recipe_id         TEXT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  ingredient_family TEXT NOT NULL,
  PRIMARY KEY (recipe_id, ingredient_family)
);
```

The migration reads the existing JSON arrays and inserts the normalized rows.

### 10.2 AI embeddings

Add a `recipe_embeddings` table or use a SQLite vector extension (e.g., `sqlite-vec`):

```sql
CREATE TABLE recipe_embeddings (
  recipe_id     TEXT PRIMARY KEY REFERENCES recipes(id) ON DELETE CASCADE,
  model_id      TEXT NOT NULL,
  embedding     BLOB NOT NULL,  -- raw float32 vector bytes
  dimensions    INTEGER NOT NULL,
  generated_at  TEXT NOT NULL
);
```

### 10.3 Recipe revision history

```sql
CREATE TABLE recipe_revisions (
  id           TEXT PRIMARY KEY,
  recipe_id    TEXT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  revision_num INTEGER NOT NULL,
  snapshot_json TEXT NOT NULL,
  changed_by   TEXT,
  created_at   TEXT NOT NULL
);
```

### 10.4 Multiple sources per recipe

Convert the current `source_id` FK on `recipes` to a junction:

```sql
CREATE TABLE recipe_source_links (
  recipe_id     TEXT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  source_id     TEXT NOT NULL REFERENCES recipe_sources(id) ON DELETE CASCADE,
  is_primary    INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (recipe_id, source_id)
);
```

### 10.5 Collections

```sql
CREATE TABLE collections (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  description TEXT,
  created_at  TEXT NOT NULL
);

CREATE TABLE collection_recipes (
  collection_id TEXT NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
  recipe_id     TEXT NOT NULL REFERENCES recipes(id)     ON DELETE CASCADE,
  position      INTEGER,
  PRIMARY KEY (collection_id, recipe_id)
);
```

---

## 11. Anti-Patterns

### 11.1 Storing AI payload as the canonical recipe

`ai_payload_json` on `structured_candidates` and `raw_response_json` on `ai_jobs` are audit fields. They are never the source of truth for displayed recipe data.

### 11.2 Collapsing candidate into recipe at save

When a candidate is accepted, the application creates a new recipe record and new ingredient/step rows from the candidate data. It does not repurpose candidate rows as recipe rows. The candidate remains in the database as intake history.

### 11.3 Binary media blobs in SQLite

Images, PDFs, and screenshots are stored on the filesystem. The database holds the path and metadata only.

### 11.4 Hiding filtered fields in JSON

Fields used for filtering — `dish_role`, `primary_cuisine`, `technique_family`, `complexity`, `time_class`, `verification_state`, `sector`, `operational_class`, `heat_window` — are first-class columns. They are not buried in a JSON payload column.

### 11.5 Skipping migrations

Schema changes applied manually without migration records create an inconsistent state that will break clean restores and deployments. All changes go through the migration system.

### 11.6 Using INTEGER primary keys for exportable records

ULID or UUID text IDs are used for all primary keys. This preserves stable identity across backup/restore cycles, allows future record merging, and prevents ID collision if records are ever imported from another instance.

---

## 12. Final Schema Standard

The v1 schema succeeds if:

* every recipe is queryable by its taxonomy fields without parsing JSON
* raw source evidence is preserved and linked
* intake workflow state is separate from archive truth
* AI output is traceable and auditable but never canonical
* the schema can be backed up as a single file, restored on any machine, and opened with any SQLite-compatible tool
* migrations can be applied cleanly from version 001 to current without data loss

Any schema decision that blurs these boundaries — mixing candidates with approved records, embedding search-critical fields in JSON blobs, or treating AI state as recipe state — is out of standard.

---

## Decisions Made

1. Multi-select fields use JSON arrays in v1 (`TEXT` columns with `DEFAULT '[]'`). Junction tables deferred to v2.
2. `class` is renamed `operational_class` throughout to avoid SQL and language reserved word conflicts.
3. `group` is renamed `group_heading` on ingredient rows.
4. `total_time_minutes` is a SQLite generated virtual column. Application computes it as fallback for SQLite < 3.31.
5. `ingredient_text` is a denormalized flat text column on `recipes`, maintained by the application at save time, used as FTS source.
6. FTS5 uses `unicode61` tokenizer with `remove_diacritics 1` for accent-insensitive search.
7. FTS synchronization is handled by the application layer, not triggers.
8. `abandoned` added to `intake_jobs.status` to handle explicitly closed incomplete intake workflows.
9. `recipe_photo` added to `media_assets.asset_kind` to support recipe images from v1.
10. `raw_prompt_text` added to `ai_jobs` for debugging and prompt contract verification.
11. All PKs use ULID/UUID-style text identifiers. No INTEGER autoincrement PKs.
12. `schema_migrations` table tracks all applied migrations. Backup is mandatory before any migration run.
13. Notes stored as separate `recipe_notes` rows (not named columns on recipes) to keep the recipes table clean and allow future note types.
14. AI job records are append-only. No deletion of AI job history.

---

## Open Questions

1. **ULID vs UUID** — Which specific format? ULID is time-sortable and visually ordered. UUIDv7 achieves similar properties. This decision affects ID generation in the application layer. Recommendation: ULID. Needs confirmation before implementation.
2. **`total_time_minutes` generated column** — SQLite generated columns require version 3.31 (2020-01-22). What is the minimum SQLite version to target? If older versions must be supported, remove the generated column clause and compute in the application layer.
3. **Ingredient group headings** — Should `group_heading` be shared across adjacent rows by storing the heading once (on the first row of the group) or duplicated on each row within the group? Storing on first row is cleaner; duplicating makes queries simpler. Needs a decision before implementation.
4. **FTS on `raw_source_text`** — Should raw source text be included in the FTS index? It improves recall but adds noise. If included, it should have lower rank weight. Deferred to v1 implementation, where it can be empirically tested.
5. **Recipe photos in v1** — The asset_kind includes `recipe_photo` and the schema supports it, but the product brief deferred rich photo management to v2. Is a single primary photo field sufficient for v1, or should photos be deferred entirely?

---

## Deliverables Created

* `docs/08_database/schema-spec.md` v2.0 — this document (supersedes v1.0)

---

## What the Next Document Should Cover

**`docs/07_api/api-spec.md` — API Spec v2.0**

This document now exists and is the canonical API reference aligned with schema v2.0.

The next update pass should keep the API aligned with:

* JSON-array multi-select fields in recipe payloads
* `operational_class` as the public field name
* explicit intake, candidate, media, and AI job resources
* migration-backed local deployment assumptions
