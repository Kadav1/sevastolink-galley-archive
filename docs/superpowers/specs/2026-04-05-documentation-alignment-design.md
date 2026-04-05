# Documentation Alignment Design

**Date:** 2026-04-05
**Scope:** documentation-only governance and planning for implementation-aware doc alignment

---

## 1. Purpose

This design defines how Sevastolink Galley Archive should start correcting documentation drift without mixing that work with code changes.

It establishes:

* the documentation artifacts that anchor current truth
* the role of the new drift register
* the boundary between implementation-aware docs and broader target-state specs
* the repair sequence for stale docs
* the verification standard for future documentation updates

This design is intentionally documentation-only. It does not authorize UI, API, routing, token, or product-behavior changes.

---

## 2. Problem Statement

The repository already has a strong documentation structure, but several implementation-aware docs have fallen behind the current codebase.

The highest-risk consequence is not that the target-state specs are aspirational. That separation is correct. The real problem is that contributors can no longer safely assume that the current-state and `implemented-*` docs are fully reliable entrypoints for present-day truth.

The current audit found drift in these areas:

* overview and routed UI truth
* product-surface description
* visual-system implementation notes
* implemented API inventory
* architecture implementation notes
* database migration and surfaced-persistence notes
* ops helper-layer and operational tooling notes

The audit did **not** find equivalent implementation-aware drift in:

* taxonomy
* AI implementation docs
* imports implementation docs

That distinction matters. The next step should not be a broad documentation rewrite. It should be a governance and sequencing pass that restores a trustworthy documentation hierarchy.

---

## 3. Design Goals

This initiative should:

* restore trust in the implementation-aware docs
* keep current truth separate from aspirational target-state specs
* preserve audit evidence without bloating baseline docs
* define a repeatable maintenance workflow for future contributors
* sequence repairs so the highest-authority docs are corrected first

This initiative should **not**:

* rewrite the stale docs in the same phase
* make product decisions that require code or UX changes
* silently reinterpret target-state docs as current truth
* turn baseline docs into long-lived audit notebooks

---

## 4. Documentation Architecture

The repository should use four distinct documentation layers for this process.

### 4.1 Current-state overview

`docs/00_overview/current-state.md` is the shortest implementation baseline.

Its job is to answer:

* what major application areas are implemented right now
* what major routed or mounted surfaces exist right now
* which areas are still deferred

It should remain concise and stable. It should not carry rolling audit appendices or detailed forensic notes beyond what is necessary to orient contributors.

### 4.2 Implementation-aware domain docs

The `implemented-*` documents are the domain-level source of present-day truth.

These docs should describe:

* current routed UI surfaces
* current visual-system implementation state
* current API endpoints and behavior
* current architecture, schema, ops, import, AI, and taxonomy reality

When code changes, these are the first domain docs that should be updated.

### 4.3 Broader target-state specs

The broader specs remain the canonical design intent for where the product should go.

These docs should stay aspirational unless one of these is true:

* the intended direction itself has changed
* the spec currently misstates the intended direction
* the repository has decided to abandon or materially revise a target-state assumption

A broader spec should not be rewritten simply because the implementation is still narrower than the target.

### 4.4 Drift register

`docs/00_overview/documentation-drift-register.md` is the rolling evidence log.

Its job is to hold:

* confirmed documentation drift
* confirmed implementation drift against broader specs
* severity
* affected docs
* code references
* recommended follow-up

This register is the right place for rolling discrepancies. It prevents `current-state.md` and the domain docs from accumulating stale audit sections.

---

## 5. Operating Model

Documentation alignment should follow a fixed review order.

### 5.1 Audit order

For any domain under review:

1. Start with `docs/00_overview/current-state.md`
2. Read the relevant `implemented-*` document
3. Inspect code
4. Only then compare against the broader target-state spec

This order prevents aspirational docs from being mistaken for current implementation truth.

### 5.2 Mismatch classification

Every confirmed mismatch should be classified as one of these:

* **Implementation-aware doc is stale**
  The code has changed and the current-truth doc no longer matches it.

* **Intentional implementation gap**
  The broader target-state spec is still correct, but the implementation remains narrower.

* **Implementation drift against intended direction**
  The code now diverges from the broader target-state guidance in a way that requires a product, UX, or visual-system decision.

* **Adjacent note only**
  Useful observation, but not yet significant enough to require repair work.

### 5.3 Repair authority

Repairs should be made in this order:

1. current-state overview
2. implementation-aware domain docs
3. broader target-state specs, only if the intended direction itself has changed

This keeps present-day truth authoritative without collapsing the distinction between current implementation and future design intent.

### 5.4 Evidence handling

Rolling evidence stays in the drift register.

Baseline docs should remain:

* concise
* implementation-facing
* stable enough to read as reference material

They should not become a running archive of every audit finding.

### 5.5 Verification standard

A documentation claim that something is implemented should be backed by:

* at least one concrete code reference, and
* a verification step when practical

Examples:

* routed UI claim: code reference plus `cd apps/web && npm run build`
* API claim: route reference plus route inspection
* migration claim: migration-file inspection plus `init_db()` runner reference
* ops claim: script reference plus Makefile wiring where applicable

This is a documentation standard, not a promise that every doc change requires a full test suite run.

---

## 6. Deliverables for This Phase

This documentation-only phase should produce four concrete outputs.

### 6.1 Drift register

The drift register already exists at:

* `docs/00_overview/documentation-drift-register.md`

It serves as the working evidence base for the rest of the initiative.

### 6.2 Governance spec

This design document is the governance spec for how documentation alignment should work.

Location:

* `docs/superpowers/specs/2026-04-05-documentation-alignment-design.md`

### 6.3 Documentation-only implementation plan

A dedicated implementation plan should be written after this spec is approved.

That plan should sequence:

* which docs to repair first
* what each repair should cover
* what verification is required per repair task
* how resolved drift entries should be tracked

### 6.4 Overview pointer

The current-state overview should include a pointer to the drift register so contributors can find the active discrepancy log quickly.

That small navigation change is allowed in this phase because it strengthens the documentation architecture without changing domain truth.

---

## 7. Repair Sequence

The first repair wave should be ordered like this:

1. `docs/00_overview/current-state.md`
2. `docs/02_ux/implemented-routes-and-flows.md`
3. `docs/01_product/implemented-product.md`
4. `docs/03_visual-system/implemented-visual-system.md`
5. `docs/07_api/implemented-api.md`
6. `docs/06_architecture/implemented-architecture.md`
7. `docs/08_database/implemented-database.md`
8. `docs/09_ops/implemented-ops.md`

This order is intentional.

Why:

* contributors are most likely to trust the overview and routed-UX docs first
* product and visual-system docs shape interpretation of the frontend next
* API, architecture, database, and ops should then be corrected against a stabilized present-day baseline

The following implementation-aware docs do not need repair in the first wave based on the current audit:

* `docs/04_taxonomy/implemented-taxonomy.md`
* `docs/05_ai/implemented-ai.md`
* `docs/10_imports/implemented-imports.md`

They can be rechecked in later review cycles, but they should not be rewritten just for symmetry.

---

## 8. Ownership and Lifecycle

### 8.1 Drift register lifecycle

When a mismatch is found:

* add or update an entry in the drift register
* include affected docs
* include concrete code references
* classify the mismatch
* assign severity

When a source doc is repaired:

* keep the register entry
* change status from `Open` to `Resolved`
* add a short note naming the repaired source docs

This preserves a short-term audit trail instead of erasing context immediately.

### 8.2 Source-doc lifecycle

A source doc should only be updated when:

* the mismatch has been verified against code
* the update is limited to current-truth claims within that doc’s scope
* the broader target-state docs remain clearly distinct

### 8.3 Broader spec lifecycle

Broader specs should only change when:

* product intent has changed
* UX direction has changed
* visual-system direction has changed
* a spec statement is itself wrong as design intent

Implementation alone is not enough to justify rewriting broader specs.

---

## 9. Risks and Controls

### Risk 1: Baseline docs turn into audit logs again

Control:

* keep rolling discrepancies in the drift register
* keep baseline docs concise

### Risk 2: Contributors collapse current truth and target-state intent

Control:

* enforce audit order: current-state -> implemented doc -> code -> broader spec
* document classification rules clearly

### Risk 3: The plan becomes a rewrite of the whole docs tree

Control:

* constrain the first wave to the docs confirmed as stale by the current audit
* leave unaffected implementation-aware docs alone

### Risk 4: Documentation claims are updated without fresh verification

Control:

* require code references and practical verification steps for implementation claims

---

## 10. Success Criteria

This initiative succeeds when:

* contributors can start from `current-state.md` and the relevant `implemented-*` doc without being misled by known stale claims
* the drift register becomes the one obvious place to track confirmed discrepancies
* broader target-state specs remain clearly aspirational where implementation is still narrower
* documentation repairs can be executed in a predictable sequence without reopening product or code decisions

This initiative does **not** require the stale docs to be repaired immediately. It requires that the repo now has a trustworthy structure for repairing them deliberately.

---

## 11. Out of Scope

Explicitly out of scope for this design:

* rewriting the stale domain docs in this same phase
* code-side visual-token cleanup
* Pantry route or navigation decisions
* UI or API behavior changes
* frontend primitive extraction
* route additions, deletions, or redesigns

Those may follow later, but they are not part of this documentation-governance phase.
