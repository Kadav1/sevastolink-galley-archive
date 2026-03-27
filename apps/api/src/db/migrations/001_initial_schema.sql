-- Sevastolink Galley Archive — v1 Initial Schema
-- Migration 001
-- Aligned with schema-spec v2.0 and content-taxonomy-spec v2.0

PRAGMA foreign_keys = ON;

-- ─── Media assets ──────────────────────────────────────────────────────────────
-- Declared first because intake_jobs and recipe_sources reference it.

CREATE TABLE IF NOT EXISTS media_assets (
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

-- ─── Recipe sources ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS recipe_sources (
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

-- ─── Intake jobs ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS intake_jobs (
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
  resulting_recipe_id   TEXT,   -- FK to recipes added after recipes table
  created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  completed_at          TEXT
);

-- ─── Recipes ───────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS recipes (
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

  -- Multi-select taxonomy (JSON arrays — v1 approach per schema-spec §2)
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
                          CHECK (verification_state IN (
                            'Draft', 'Unverified', 'Verified', 'Archived'
                          )),
  favorite              INTEGER NOT NULL DEFAULT 0 CHECK (favorite IN (0, 1)),
  archived              INTEGER NOT NULL DEFAULT 0 CHECK (archived IN (0, 1)),
  rating                INTEGER CHECK (rating IS NULL OR (rating BETWEEN 1 AND 5)),

  -- Search support (denormalised ingredient string, maintained by app on save)
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

-- Add deferred FK from intake_jobs back to recipes
-- (SQLite does not support ALTER TABLE ADD FOREIGN KEY; the constraint is advisory here,
--  enforced at the application layer)

-- ─── Recipe ingredients ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS recipe_ingredients (
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

-- ─── Recipe steps ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS recipe_steps (
  id             TEXT    PRIMARY KEY,
  recipe_id      TEXT    NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  position       INTEGER NOT NULL,
  instruction    TEXT    NOT NULL,
  time_note      TEXT,
  equipment_note TEXT
);

-- ─── Recipe notes ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS recipe_notes (
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

-- ─── Structured candidates ─────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS structured_candidates (
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

  -- Taxonomy fields mirror recipes table (nullable — candidates are incomplete)
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

  -- Flat notes (typed notes only on approved recipes)
  notes                 TEXT,
  service_notes         TEXT,
  source_credit         TEXT,

  -- Raw AI payload preserved for debugging; never used as display truth
  ai_payload_json       TEXT,

  created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at            TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ─── Candidate ingredients ─────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS candidate_ingredients (
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

-- ─── Candidate steps ───────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS candidate_steps (
  id             TEXT    PRIMARY KEY,
  candidate_id   TEXT    NOT NULL REFERENCES structured_candidates(id) ON DELETE CASCADE,
  position       INTEGER NOT NULL,
  instruction    TEXT,
  time_note      TEXT,
  equipment_note TEXT
);

-- ─── AI jobs ───────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS ai_jobs (
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
  status                TEXT    NOT NULL DEFAULT 'pending'
                          CHECK (status IN (
                            'pending',
                            'processing',
                            'complete',
                            'failed',
                            'cancelled'
                          )),
  model_used            TEXT,
  prompt_tokens         INTEGER,
  completion_tokens     INTEGER,
  raw_response_json     TEXT,
  validated_payload     TEXT,
  error_message         TEXT,
  created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  completed_at          TEXT
);

-- ─── Settings ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS settings (
  key        TEXT    PRIMARY KEY,
  value      TEXT,
  updated_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ─── FTS5 search index ─────────────────────────────────────────────────────────
-- Standalone (not content-table) FTS5 index maintained by the application.
-- Populated and updated whenever a recipe is saved.

CREATE VIRTUAL TABLE IF NOT EXISTS recipe_search_fts USING fts5(
  recipe_id,
  title,
  short_description,
  notes,
  ingredient_text,
  tokenize = 'porter ascii'
);

-- ─── Indexes ───────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_recipes_slug
  ON recipes (slug);

CREATE INDEX IF NOT EXISTS idx_recipes_verification_state
  ON recipes (verification_state);

CREATE INDEX IF NOT EXISTS idx_recipes_favorite
  ON recipes (favorite);

CREATE INDEX IF NOT EXISTS idx_recipes_dish_role
  ON recipes (dish_role);

CREATE INDEX IF NOT EXISTS idx_recipes_primary_cuisine
  ON recipes (primary_cuisine);

CREATE INDEX IF NOT EXISTS idx_recipes_technique_family
  ON recipes (technique_family);

CREATE INDEX IF NOT EXISTS idx_recipes_time_class
  ON recipes (time_class);

CREATE INDEX IF NOT EXISTS idx_recipes_created_at
  ON recipes (created_at);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe_id
  ON recipe_ingredients (recipe_id, position);

CREATE INDEX IF NOT EXISTS idx_recipe_steps_recipe_id
  ON recipe_steps (recipe_id, position);

CREATE INDEX IF NOT EXISTS idx_intake_jobs_status
  ON intake_jobs (status);

CREATE INDEX IF NOT EXISTS idx_structured_candidates_intake_job_id
  ON structured_candidates (intake_job_id);

CREATE INDEX IF NOT EXISTS idx_ai_jobs_source_entity
  ON ai_jobs (source_entity_type, source_entity_id);
