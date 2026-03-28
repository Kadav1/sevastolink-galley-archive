# Sevastolink Galley Archive

## Database Implementation Backlog v1.0

---

## 1. Purpose

This document translates `docs/08_database/schema-spec.md` into a concrete implementation backlog.

It establishes:

* which database areas are already implemented
* which parts of the target-state schema story are still missing
* which missing work should be prioritized first
* how the missing work maps back to the broader schema spec

This is an implementation-planning document for schema and persistence work.

---

## 2. Current implementation baseline

Already implemented:

* initial SQLite schema migration
* major archive, intake, candidate, media, settings, AI job, and FTS tables
* migration tracking
* JSON-array approach for multi-select taxonomy

Still missing or incomplete:

* surfaced workflows for some stored entities
* seed/example data workflows
* fuller alignment between stored schema breadth and currently exposed API models
* follow-up migrations beyond the initial schema

---

## 3. Backlog summary

| Priority | Area | Current state | Target state |
|---|---|---|---|
| P1 | Schema-to-API alignment | DB allows more than some API models expose | Storage and exposed contracts aligned deliberately |
| P1 | Settings/media/AI-job surfacing | Tables exist without full product/API surfaces | Stored entities used intentionally or pared back |
| P1 | Additional migration discipline | Only `001` exists | Follow-up migrations as the schema evolves |
| P2 | Seed/example data strategy | Spec mentions it, repo does not materially implement it | Real seed workflow or explicit removal from target-state promise |
| P2 | Candidate-schema breadth alignment | Candidate table is broader than candidate API update model | Review and candidate flows expose the intended fields |
| P3 | Historical data cleanup tooling | Drift is possible as fields surface gradually | Repair/migration support for legacy rows |

---

## 4. Backlog detail

### 4.1 P1: Schema-to-API alignment

Current state:

* the database stores some entities and values that the API does not yet expose fully

Missing target-state items:

* deliberate alignment between stored schema breadth and public/internal API contracts

Likely implementation work:

* decide which schema breadth is intentionally ahead of the product
* update API models where the extra stored fields should be editable or visible
* otherwise document dormant schema capacity explicitly

Primary source:

* `schema-spec.md`

### 4.2 P1: Settings, media, and AI-job surfacing

Current state:

* `settings`, `media_assets`, and `ai_jobs` tables exist
* surfaced workflows for them are still partial or absent

Missing target-state items:

* settings workflows
* media workflows
* AI job visibility if still needed

Likely implementation work:

* align these with the matching architecture and API backlogs
* avoid keeping large dormant schema areas undocumented

Primary source:

* `schema-spec.md`

### 4.3 P1: Additional migration discipline

Current state:

* only `001_initial_schema.sql` exists

Missing target-state items:

* follow-up migrations for new schema evolution
* stronger operational rhythm around migration changes

Likely implementation work:

* add new numbered SQL files for every real schema change
* avoid editing applied migrations casually

Primary source:

* `schema-spec.md`
* `migrations-and-data-lifecycle.md`

### 4.4 P2: Seed and example data strategy

Current state:

* the schema spec mentions seed and example data as part of the database story
* the repository does not yet materially implement seed tooling or seed datasets

Missing target-state items:

* repeatable seed workflow if still desired

Likely implementation work:

* either implement seed scripts and fixtures
* or narrow the target-state schema doc so it no longer implies a seed workflow exists

Primary source:

* `schema-spec.md`

### 4.5 P2: Candidate-schema breadth alignment

Current state:

* `structured_candidates` stores a broader field set than `CandidateUpdate` currently exposes

Missing target-state items:

* clear decision on whether the candidate workflow should expose the broader field set

Likely implementation work:

* expand candidate API models where the review workflow needs those fields
* otherwise document that candidates are intentionally narrowed in the current UX/API layer

Primary source:

* `schema-spec.md`

### 4.6 P3: Historical data cleanup tooling

Current state:

* as more schema fields and workflows are surfaced, legacy rows may become uneven

Missing target-state items:

* cleanup and normalization support for older rows

Likely implementation work:

* add migration helpers or repair scripts only when real drift justifies them

---

## 5. Recommended implementation order

### Phase 1

Stabilize the relationship between stored schema and surfaced contracts:

* schema/API alignment
* settings/media/AI-job surfacing decisions
* follow-up migration discipline

### Phase 2

Address supporting schema-operational gaps:

* seed/example data strategy
* broader candidate-schema alignment

### Phase 3

Add cleanup tooling only once real historical drift appears.

---

## 6. Contributor rule

When implementing against the database docs:

* treat `implemented-database.md` as the current-state truth
* treat `schema-spec.md` as the broader target-state reference
* move backlog items into implemented docs only when the migration, model, and runtime behavior actually exist
