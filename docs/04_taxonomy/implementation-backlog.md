# Sevastolink Galley Archive

## Taxonomy Implementation Backlog v1.0

---

## 1. Purpose

This document translates `docs/04_taxonomy/content-taxonomy-spec.md` into a concrete implementation backlog.

It establishes:

* which taxonomy areas are already implemented
* which parts of the target taxonomy system are still missing
* which missing work should be prioritized first
* how the missing work maps back to the taxonomy spec

This is an implementation-planning document for taxonomy and classification work.

---

## 2. Current implementation baseline

Already implemented:

* core taxonomy fields in recipe and intake data models
* library filtering on the main taxonomy subset
* recipe metadata display for the main taxonomy subset
* AI normalizer vocabulary checks for a limited subset

Still missing:

* shared runtime taxonomy package
* universal controlled-vocabulary enforcement
* consistent frontend/backend reuse of taxonomy value lists
* broader UI support for the full taxonomy field set

---

## 3. Backlog summary

| Priority | Area | Current state | Target state |
|---|---|---|---|
| P1 | Shared taxonomy source | Split across docs and code | Canonical machine-readable taxonomy assets shared across app layers |
| P1 | Vocabulary alignment | Frontend and normalizer use partial hardcoded lists | Unified value lists aligned to the taxonomy spec |
| P1 | Validation expansion | Only limited fields are strictly normalized | Controlled vocab validation for all intended controlled fields |
| P2 | Frontend taxonomy expansion | UI uses only a narrow subset | Broader editing, filtering, and display support |
| P2 | Shared types and package alignment | Shared types include fields but not taxonomy metadata | Shared taxonomy package plus shared type alignment |
| P3 | Migration and cleanup | Existing rows may contain drift | Data cleanup and normalization against canonical vocabularies |

---

## 4. Backlog detail

### 4.1 P1: Shared taxonomy source

Current state:

* taxonomy meaning is split across the spec, backend code, and frontend option lists
* `packages/shared-taxonomy/` is still placeholder-only

Missing target-state items:

* canonical value lists in `packages/shared-taxonomy/`
* stable field metadata shared by backend and frontend
* one source for controlled vocabulary updates

Likely implementation work:

* populate `packages/shared-taxonomy/` with machine-readable value lists
* define naming and export structure
* make the package the source of truth for controlled taxonomies

Primary source:

* `content-taxonomy-spec.md`

### 4.2 P1: Vocabulary alignment

Current state:

* the frontend hardcodes one set of option lists
* the normalizer hardcodes another set
* the spec defines a much broader vocabulary universe

Missing target-state items:

* alignment between spec vocabulary and runtime value lists
* elimination of duplicate hardcoded lists where possible

Likely implementation work:

* compare current frontend lists to spec values
* compare current normalizer lists to spec values
* decide which subset is truly v1 and document that subset clearly

Primary source:

* `content-taxonomy-spec.md`

### 4.3 P1: Validation expansion

Current state:

* only a few taxonomy fields are actually validated against allowed vocabularies in normalization
* most schema fields accept raw strings or arrays

Missing target-state items:

* controlled validation for all fields intended to be controlled vocabularies
* consistent API-side validation on create and update

Likely implementation work:

* identify which fields are truly controlled versus intentionally free text
* add validators or shared validation helpers
* ensure normalization and direct manual entry obey the same vocabulary rules where appropriate

Primary source:

* `content-taxonomy-spec.md`

### 4.4 P2: Frontend taxonomy expansion

Current state:

* the UI mainly uses role, cuisine, technique, complexity, time, heat, and verification state

Missing target-state items:

* broader filter support
* broader metadata display
* broader editing support in manual entry, paste-text review, and future recipe edit screens

Likely implementation work:

* expand only the taxonomy surfaces that improve retrieval or comprehension
* avoid overwhelming the current forms before route and workflow expansion lands

Primary source:

* `content-taxonomy-spec.md`

### 4.5 P2: Shared types and package alignment

Current state:

* shared types mirror backend structures at a basic level
* shared taxonomy package is still not implemented

Missing target-state items:

* clear boundary between field types and taxonomy metadata
* shared consumer-friendly exports for frontend and backend tooling

Likely implementation work:

* keep `packages/shared-types/` focused on data shape
* move taxonomy values and metadata into `packages/shared-taxonomy/`

### 4.6 P3: Migration and cleanup

Current state:

* data structures allow taxonomy drift where validation is loose
* existing records and candidates may already contain mixed values

Missing target-state items:

* migration strategy for normalizing legacy rows
* cleanup tooling for vocabulary drift

Likely implementation work:

* audit stored values
* add repair scripts or migration helpers
* normalize historical data once the shared vocabulary source is stable

---

## 5. Recommended implementation order

### Phase 1

Build the shared taxonomy source and align current vocabularies:

* populate `packages/shared-taxonomy/`
* define the canonical v1 controlled vocabularies
* remove duplicated runtime lists where practical

### Phase 2

Expand validation and UI support:

* API validation
* normalizer alignment
* broader frontend editing and filtering support

### Phase 3

Clean up existing data and operational drift after the shared taxonomy layer is stable.

---

## 6. Contributor rule

When implementing against the taxonomy docs:

* treat `implemented-taxonomy.md` as the current-state truth
* treat `content-taxonomy-spec.md` as the broader target-state taxonomy reference
* treat `packages/shared-taxonomy/` as planned infrastructure until real assets are added
* move backlog items into implemented docs only when the runtime code actually uses them
