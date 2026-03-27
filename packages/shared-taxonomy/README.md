# Sevastolink Galley Archive

## Shared Taxonomy Package v1.0

---

## 1. Purpose

This document defines the intended role and current status of the shared taxonomy package.

It establishes:

* what this package is meant to hold
* what it currently contains
* where taxonomy truth currently lives in practice
* how contributors should interpret this package today

This is a status document for a package that is not yet materially implemented.

---

## 2. Current status

### Established facts

* The package currently contains only a placeholder file.
* Canonical taxonomy meaning currently lives primarily in the repository documentation.
* Some runtime taxonomy behavior also exists in code constants and validation logic.

### Current interpretation

`packages/shared-taxonomy/` is reserved space for a future shared taxonomy layer. It is not yet the operational source of truth.

---

## 3. Where taxonomy currently lives

At present, taxonomy definition and use are split across:

* `docs/04_taxonomy/content-taxonomy-spec.md`
* backend schema and validation logic
* normalization tooling constants and mapping logic

This means contributors should not assume the package is already wired into the app.

---

## 4. Intended future role

If adopted, this package should become the shared home for:

* common taxonomy value lists
* stable field names
* possibly shared validation metadata for frontend and backend consumers

That adoption has not happened yet in the current repository state.

---

## 5. Contributor guidance

For current work:

* treat this package as a placeholder
* verify taxonomy truth against the docs and current implementation
* avoid documenting this package as an active shared runtime dependency until real taxonomy assets are added
