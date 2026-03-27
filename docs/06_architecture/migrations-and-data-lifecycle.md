# Sevastolink Galley Archive

## Migration and Data Lifecycle v1.0

---

## 1. Purpose

This document defines the current schema migration behavior and the practical data lifecycle used by Sevastolink Galley Archive.

It establishes:

* how the database is initialized
* how SQL migrations are discovered and applied
* when migration logic runs
* how this interacts with backup and restore
* how archive data moves through raw source, intake, candidate, and approved states
* what contributors should do when changing schema or data paths

This is a practical implementation document for the current codebase.

---

## 2. Migration philosophy

### Established facts

* SQLite is the current system of record.
* Schema changes are migration-backed.
* The application initializes the schema automatically on startup.
* Intake data and approved recipes are distinct layers and should remain distinct.

### Current standard

Migration handling should remain:

* file-based
* deterministic
* local-first
* compatible with backup-before-change workflows

Manual schema drift outside the migration system is out of standard.

---

## 3. Current migration model

### Migration directory

SQL migrations live under:

`apps/api/src/db/migrations/`

### Tracking table

Applied migrations are tracked in:

`schema_migrations`

### Current runner behavior

The migration runner:

1. resolves the SQLite database path from current settings
2. creates the parent directory if needed
3. enables SQLite WAL journal mode
4. enables foreign-key enforcement
5. bootstraps `schema_migrations` if needed
6. reads all `.sql` files from the migrations directory in sorted order
7. skips versions already recorded in `schema_migrations`
8. executes each pending migration file
9. records the applied version and timestamp

---

## 4. When migrations run

### API startup

The FastAPI application runs schema initialization during startup lifespan handling.

That means:

* local `uvicorn` runs apply pending migrations on startup
* Docker API container startup applies pending migrations on startup

### CLI review workflow

The candidate review tooling also initializes the database before using the intake service layer.

This keeps the CLI workflow aligned with the same schema assumptions as the API.

---

## 5. Current data lifecycle

### 5.1 Raw source

Raw recipe source files live under:

`data/imports/raw/`

These are preserved source artifacts.

### 5.2 Candidate artifact

Normalization can produce candidate bundles under:

`data/imports/parsed/recipes-candidates/`

These are review artifacts, not canonical archive rows.

### 5.3 Intake database state

When a candidate is ingested or created through paste-text intake, it enters:

* `intake_jobs`
* `structured_candidates`

This is the reviewable structured state.

### 5.4 Approved archive state

When an intake job is approved, canonical archive records are written into:

* `recipes`
* related recipe tables such as ingredients, steps, notes, and source records

This is the durable archive state surfaced to the main product.

---

## 6. Persistent data layout

Current persistent directories under `data/` are:

* `data/db/` — SQLite database
* `data/media/` — media assets
* `data/imports/` — raw and parsed intake material
* `data/exports/` — export path
* `data/backups/` — timestamped backups
* `data/logs/` — local logs

These directories are bind-mounted into the API container in Docker use and remain outside container image state.

---

## 7. Backup relationship

### Established facts

* backup and restore already exist as operational shell workflows
* database changes can affect irreplaceable local archive data

### Current standard

Take a backup before:

* changing schema
* editing migration files
* restoring a prior state
* running higher-risk local development work against valuable real archive data

For current backup and restore procedures, use:

* `docs/09_ops/backup-restore.md`

---

## 8. Contributor workflow for schema changes

When changing schema in the current project:

1. Create a new numbered SQL migration under `apps/api/src/db/migrations/`.
2. Do not modify previously applied migration files casually.
3. Update any impacted ORM models, schemas, and service logic.
4. Update relevant docs if the schema change affects current behavior.
5. Run the backend or migration-aware tests against a clean database.
6. Verify that existing local data can still be migrated safely.

### Current warning

Do not rely on manual table edits or one-off SQLite console changes as a substitute for a tracked migration.

---

## 9. Test-database behavior

The backend test suite uses SQLite test databases under `data/db/`.

Current expectation:

* tests initialize schema through the same migration runner rather than bypassing it

This is important because it keeps test schema behavior closer to real runtime behavior.

---

## 10. Current limitations

The current migration system is intentionally simple.

It does not currently provide:

* a dedicated migration CLI separate from app startup
* automatic pre-migration backup creation inside the runner itself
* multi-database support
* remote database orchestration

These omissions are acceptable for the current local-first single-machine architecture, but they should remain explicit rather than assumed away.
