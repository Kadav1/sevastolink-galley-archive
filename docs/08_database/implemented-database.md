# Sevastolink Galley Archive

## Implemented Database v1.0

---

## 1. Purpose

This document defines the database schema and persistence behavior that is implemented in the repository now.

It establishes:

* which tables and indexes are actually created by the current migration set
* which schema patterns are actively exercised by the application
* where the database implementation is narrower than the broader schema spec
* what contributors should treat as current database truth

This is the implementation-aware database baseline for contributors.

---

## 2. Current implementation baseline

### Established facts

The current repository uses:

* SQLite as the system of record
* one SQL migration file for the initial schema
* startup-driven migration application through `init_db()`
* SQLAlchemy models mapped to the current SQLite schema

The current schema already creates these major table groups:

* archive tables
* intake and candidate tables
* media and AI job tables
* settings table
* FTS5 search table
* schema migration tracking table

### Current interpretation

The current database is not merely planned. It is materially implemented.

However, not every created table is equally surfaced through application routes and workflows today.

---

## 3. Current schema reality

### 3.1 Tables created by the current migration set

The current `001_initial_schema.sql` migration creates:

* `schema_migrations`
* `media_assets`
* `recipe_sources`
* `intake_jobs`
* `recipes`
* `recipe_ingredients`
* `recipe_steps`
* `recipe_notes`
* `structured_candidates`
* `candidate_ingredients`
* `candidate_steps`
* `ai_jobs`
* `settings`
* `recipe_search_fts`

### 3.2 Indexes and search support

The current migration also creates:

* recipe indexes for key browse fields
* intake and AI job indexes
* `recipe_search_fts` as an FTS5 virtual table

Deterministic text search is therefore a real implemented database feature, not just a design note.

---

## 4. Current schema usage patterns

### 4.1 Heavily exercised tables

The current application actively uses:

* `recipes`
* `recipe_ingredients`
* `recipe_steps`
* `recipe_notes`
* `recipe_sources`
* `intake_jobs`
* `structured_candidates`
* `candidate_ingredients`
* `candidate_steps`
* `recipe_search_fts`
* `schema_migrations`

These tables are part of the main runtime product flows.

### 4.2 Present but only partially surfaced tables

The schema also includes:

* `media_assets`
* `ai_jobs`
* `settings`

These tables exist in the database and model layer, but they are not yet fully surfaced as first-class user-facing application domains.

---

## 5. Current mismatches between stored schema and surfaced workflows

### 5.1 Intake type breadth

The database schema allows these intake types:

* `manual`
* `paste_text`
* `url`
* `file`

The current API schema for intake job creation only accepts:

* `manual`
* `paste_text`

This means the database is ahead of the currently exposed intake API.

### 5.2 Candidate field breadth

The `structured_candidates` table mirrors the broader recipe schema more fully than the currently exposed `CandidateUpdate` API model.

This means:

* the database can store richer candidate taxonomy and metadata fields
* the current intake API only updates a narrower subset directly

### 5.3 Settings, media, and AI job persistence

The database already stores these concepts structurally.

However:

* there is no mounted settings API
* there is no mounted media-assets API
* there is no first-class AI jobs API

The schema is therefore broader than the currently surfaced product behavior.

---

## 6. Current modeling rules that are truly implemented

The following database design choices from the spec are already real in the current schema:

* multi-select taxonomy stored as JSON arrays in `TEXT` columns
* `operational_class` used instead of reserved `class`
* `group_heading` used instead of reserved `group`
* separate source, intake, candidate, and approved recipe entities
* FTS support through a dedicated virtual table
* migration tracking through `schema_migrations`

---

## 7. Current gaps relative to the full schema spec

The broader schema spec still overstates a few things relative to the live repository.

Not yet materially implemented:

* seed/example data workflows described as part of the schema story
* a broader operator seed pipeline
* full runtime use of every created table and column
* complete surfaced workflows for settings, media assets, and AI job persistence

---

## 8. Contributor note

When working on database behavior:

* treat this document as the current implementation baseline
* treat `schema-spec.md` as the broader target-state schema reference
* treat `migrations-and-data-lifecycle.md` as the practical current migration/lifecycle document
* avoid assuming every table or column that exists in schema is already a fully surfaced product feature
