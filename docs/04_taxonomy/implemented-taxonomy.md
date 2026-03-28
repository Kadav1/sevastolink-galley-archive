# Sevastolink Galley Archive

## Implemented Taxonomy v1.0

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

The current repository implements taxonomy in three different layers:

* database columns and API schemas
* normalization-time vocabulary checks
* frontend filter and form option lists

The current repository does not yet implement:

* a shared runtime taxonomy package
* one canonical machine-readable taxonomy source used by backend and frontend together
* full runtime enforcement for every field described by the broader taxonomy spec

### Current interpretation

The repository supports a real taxonomy model today, but that model is only partially centralized.

Contributors should treat taxonomy as operationally implemented, but still split across docs and code.

---

## 3. Implemented field coverage

### 3.1 First-class taxonomy fields in the data model

The current recipe and candidate models include these primary fields:

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

These fields exist in the backend models and schemas, even when they are not all surfaced in the web UI today.

### 3.2 Taxonomy fields actively surfaced in the current frontend

The current web app actively uses only a subset of the available taxonomy:

* `verification_state`
* `dish_role`
* `primary_cuisine`
* `technique_family`
* `complexity`
* `time_class`
* `heat_window`

These are used for:

* library filtering
* recipe summary metadata
* recipe detail metadata strip
* manual entry and paste-text intake forms

### 3.3 Taxonomy fields present in schemas but not meaningfully surfaced in the web UI

The following fields exist in backend and API structures but are not yet major first-class frontend surfaces:

* `secondary_cuisines`
* `service_format`
* `season`
* `ingredient_families`
* `mood_tags`
* `storage_profile`
* `dietary_flags`
* `provision_tags`
* `sector`
* `operational_class`

They may appear in payloads and database rows, but they are not yet central to current routed frontend workflows.

---

## 4. Current vocabulary enforcement

### 4.1 Explicitly enforced vocabularies in the normalizer

The AI normalizer currently validates and constrains only these single-select vocabularies:

* `dish_role`
* `primary_cuisine`
* `technique_family`

This validation happens in `apps/api/src/ai/normalizer.py`.

### 4.2 Frontend hardcoded lists

The frontend currently hardcodes option lists for:

* `verification_state`
* `dish_role`
* `primary_cuisine`
* `technique_family`
* `complexity`
* `time_class`

These lists live in the web components and pages rather than in a shared taxonomy source.

### 4.3 Schema-level reality

Most taxonomy fields in the backend schemas are currently typed as strings or string arrays without strict vocabulary validation.

This means:

* the fields exist structurally
* some filtering and display behavior exists
* full controlled-vocabulary enforcement is not yet universal

---

## 5. Current source-of-truth split

Taxonomy truth currently lives across:

* `docs/04_taxonomy/content-taxonomy-spec.md`
* backend schemas under `apps/api/src/schemas/`
* backend models under `apps/api/src/models/`
* normalizer vocabulary constants in `apps/api/src/ai/normalizer.py`
* hardcoded frontend option lists in the web app

The shared taxonomy package does not yet hold operational taxonomy assets.

---

## 6. Current gaps relative to the full taxonomy spec

The broader taxonomy spec describes a larger and more disciplined taxonomy system than the current runtime implementation provides.

Not yet fully implemented:

* one shared taxonomy package used by backend and frontend
* one canonical value source for all controlled vocabularies
* complete UI support for the broader taxonomy field set
* complete validation for all controlled taxonomy fields
* full alignment between spec vocabulary and hardcoded frontend lists

---

## 7. Contributor note

When working on taxonomy:

* treat this document as the current implementation baseline
* treat `content-taxonomy-spec.md` as the broader target-state taxonomy reference
* avoid assuming `packages/shared-taxonomy/` is already wired into the app
* verify changes against both current runtime code and the canonical taxonomy spec
