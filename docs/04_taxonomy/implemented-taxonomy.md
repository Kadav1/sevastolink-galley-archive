# Sevastolink Galley Archive

## Implemented Taxonomy v1.1

---

## 1. Purpose

This document defines the taxonomy and classification behavior that is implemented in the repository now.

It establishes:

* which taxonomy fields exist in the current data model
* which taxonomy fields are actively used by the API and frontend
* which taxonomy vocabularies are currently enforced
* where taxonomy truth currently lives in practice

This is the implementation-aware taxonomy baseline for contributors.

---

## 2. Current implementation baseline

### Established facts

The current repository implements taxonomy in four coordinated layers:

* database columns and API schemas
* a shared canonical vocabulary package (`packages/shared-taxonomy`)
* backend Pydantic validators rejecting non-canonical values at intake
* frontend filter panels and forms consuming shared vocabulary constants

### Current interpretation

Taxonomy is centralized and enforced. The shared taxonomy package is the single source of truth for all controlled vocabularies. Backend and frontend both import from it — directly in TypeScript, and via a Python mirror for the API.

---

## 3. Implemented field coverage

### 3.1 First-class taxonomy fields in the data model

All of these fields exist in the backend models, schemas, and SQLite columns:

* `dish_role`
* `primary_cuisine`
* `secondary_cuisines`
* `technique_family`
* `complexity`
* `time_class`
* `service_format`
* `season`
* `ingredient_families`
* `mood_tags`
* `storage_profile`
* `dietary_flags`
* `provision_tags`
* `sector`
* `operational_class`
* `heat_window`

### 3.2 Taxonomy fields actively surfaced in the current frontend

The following are used in library filtering, recipe summary metadata, recipe detail metadata strip, or intake forms:

* `verification_state`
* `dish_role`
* `primary_cuisine`
* `technique_family`
* `complexity`
* `time_class`
* `ingredient_families` (library filter panel)
* `heat_window` (recipe detail metadata)

### 3.3 Taxonomy fields present in schemas but not meaningfully surfaced in the web UI

The following exist in backend and API structures but are not yet major first-class frontend surfaces:

* `secondary_cuisines`
* `service_format`
* `season`
* `mood_tags`
* `storage_profile`
* `dietary_flags`
* `provision_tags`
* `sector`
* `operational_class`

They appear in payloads and database rows but are not yet central to current routed frontend workflows.

---

## 4. Current vocabulary enforcement

### 4.1 Backend validation (API layer)

All controlled taxonomy fields are validated at the API layer via Pydantic `field_validator` decorators on `RecipeCreate` and `RecipeUpdate`.

The validators live in `apps/api/src/schemas/recipe.py` and import canonical vocabulary sets from `apps/api/src/schemas/taxonomy.py`.

Enforced on `RecipeCreate` and `RecipeUpdate`:

* `dish_role` — single value against `DISH_ROLES`
* `primary_cuisine` — single value against `PRIMARY_CUISINES`
* `secondary_cuisines` — all items against `PRIMARY_CUISINES`
* `technique_family` — single value against `TECHNIQUE_FAMILIES`
* `ingredient_families` — all items against `INGREDIENT_FAMILIES`
* `complexity` — single value against `COMPLEXITY_OPTIONS`
* `time_class` — single value against `TIME_CLASS_OPTIONS`
* `service_format` — single value against `SERVICE_FORMATS`
* `season` — single value against `SEASONS`
* `mood_tags` — all items against `MOOD_TAGS`
* `storage_profile` — all items against `STORAGE_PROFILES`
* `dietary_flags` — all items against `DIETARY_FLAGS`
* `provision_tags` — all items against `PROVISION_TAGS`
* `sector` — single value against `SECTORS`
* `operational_class` — single value against `OPERATIONAL_CLASSES`
* `heat_window` — single value against `HEAT_WINDOWS`

A request supplying an unknown taxonomy value is rejected with HTTP 422.

### 4.2 Shared vocabulary package

`packages/shared-taxonomy/src/index.ts` exports all canonical vocabulary arrays `as const` with derived TypeScript types.

The frontend imports these via the `@galley/shared-taxonomy` alias (configured in `apps/web/vite.config.ts` and `apps/web/tsconfig.json`).

Currently consuming `@galley/shared-taxonomy`:

* `apps/web/src/components/library/FilterPanel.tsx`
* `apps/web/src/pages/ManualEntryPage.tsx`

### 4.3 Backend Python mirror

`apps/api/src/schemas/taxonomy.py` mirrors the shared-taxonomy constants as Python `frozenset[str]` values. This is the import source for all API-layer validators.

When updating vocabulary, update both `packages/shared-taxonomy/src/index.ts` and `apps/api/src/schemas/taxonomy.py` together.

### 4.4 AI normalizer vocabulary

The AI normalizer (`apps/api/src/ai/normalizer.py`) embeds canonical vocabulary lists in its prompt-building logic. These are kept in sync with the shared taxonomy package but are formatted as plain strings for LM Studio prompt injection.

### 4.5 Repair script drift map

`scripts/import/repair_candidates.py` applies deterministic fixes to pre-ingested candidate bundles. Its `FIELD_MAPS` dictionary contains case-folded mappings from known stale or invented values to canonical spec values. This covers common AI drift patterns (gerund forms, compound values, broad-bucket cuisines) and is extended whenever new drift patterns are identified.

---

## 5. Current source-of-truth

| Layer | File |
|-------|------|
| Canonical spec | `docs/04_taxonomy/content-taxonomy-spec.md` |
| TypeScript source | `packages/shared-taxonomy/src/index.ts` |
| Python mirror | `apps/api/src/schemas/taxonomy.py` |
| API validators | `apps/api/src/schemas/recipe.py` |
| AI normalizer | `apps/api/src/ai/normalizer.py` |
| Repair drift map | `scripts/import/repair_candidates.py` |

---

## 6. Remaining gaps relative to the full taxonomy spec

Not yet implemented:

* Full UI support for the broader taxonomy field set (secondary cuisines, mood tags, storage profile, dietary flags, provision tags, sector, operational class)
* Taxonomy-aware intake approval validation (candidate values are not revalidated at approve time)
* Vocabulary enforcement at the `structured_candidates` layer (only `recipes` enforces it today)

---

## 7. Contributor note

When working on taxonomy:

* treat `content-taxonomy-spec.md` as the target-state taxonomy reference
* treat `packages/shared-taxonomy/src/index.ts` and `apps/api/src/schemas/taxonomy.py` as the runtime sources — keep them in sync
* when adding new drift corrections, update `repair_candidates.py` FIELD_MAPS
* never introduce new vocabulary values in component-level code; update the shared package first
