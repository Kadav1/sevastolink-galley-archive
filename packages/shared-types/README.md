# Sevastolink Galley Archive

## Shared Types Package v1.0

---

## 1. Purpose

This package defines shared TypeScript types used across the frontend-facing code.

It establishes:

* lightweight common archive types
* cross-surface type reuse for basic entities
* the intended relationship between TypeScript types and backend Pydantic schemas

This package is intentionally small in the current repository state.

---

## 2. Package role

### Established facts

* The package currently contains a narrow set of shared TypeScript types.
* These types mirror backend schema concepts.
* Sync between backend schemas and this package is currently manual.

### Current standard

The package should contain:

* stable shared types that are clearly useful across frontend code
* only types that actually benefit from centralization

It should not become an unreviewed duplicate schema universe.

---

## 3. Current contents

The package currently defines:

* `VerificationState`
* `IntakeStatus`
* `IntakeType`
* `RecipeSummary`
* `HealthResponse`

These are lightweight mirrors of backend schema concepts rather than generated code.

---

## 4. Sync guidance

When backend schema shapes change:

1. update the relevant backend Pydantic schema first
2. update this package if the shared TypeScript type is still needed
3. verify the frontend uses the updated shape consistently

### Current warning

There is no code generation pipeline here yet. Drift is possible if backend and shared frontend types are updated separately.
