# Proposal 3: Migration Plan From The Current Importer To The Semantics-First Pipeline

## Purpose

This document describes how to evolve the current importer into the proposed semantics-first translation and normalization workflow without breaking the existing candidate-bundle review process.

This is intentionally a migration plan, not a greenfield redesign.

---

## Current foundation to preserve

The current importer already has important pieces that should remain in place:

* raw Swedish source as the evidence layer
* preprocessing / translation as a distinct stage
* normalization into the archive candidate schema
* warnings and `review_flags` as approval safety tools
* active Swedish reference files
* CLI-first batch import workflow

The migration should preserve those strengths.

---

## Non-goals

This migration is not trying to:

* replace the candidate bundle model
* replace `review_candidates.py`
* replace the current intake approval flow
* immediately introduce a brand-new web import product

The goal is to improve semantic reliability while keeping the current archive workflow intact.

---

## Migration phases

## Phase 1: Strengthen current stage-1 output

### Goal

Extend the translation stage from a minimal text-only payload into a richer payload with semantic traceability.

### Changes

* revise `prompts/schemas/recipe-translation-output.schema.json`
* revise `prompts/runtime/translation/recipe-translation-v1.md`
* keep `translated_text` for backward compatibility
* add `segments` as optional first
* add bounded `uncertainty_flags`

### Compatibility rule

The importer should accept both:

* old stage-1 payloads
* new enriched stage-1 payloads

Exit criterion for this phase:

* the code can consume enriched stage-1 payloads without breaking existing text-only preprocessing output

### Why first

This gives better semantic evidence without forcing an immediate redesign of normalization.

---

## Phase 2: Add explicit reference matching

### Goal

Introduce a deterministic handoff stage between translation and normalization.

### Changes

* add a new runtime module for reference matching
* consume:
  * `data/reference/swedish_recipe_units.json`
  * `data/reference/swedish_recipe_terms.json`
* produce:
  * unit matches
  * term matches
  * contextual matches
  * drift signals

### Suggested module boundary

Add a focused module such as:

* `scripts/import/recipe_import/reference_match.py`

Responsibilities:

* read stage-1 output
* use the current reference files as source authority
* emit a bounded reference-match object

### Compatibility rule

If no explicit reference-match object exists yet, the importer should fall back to the current guardrail behavior.

---

## Phase 3: Make normalization consume policy explicitly

### Goal

Stop relying on an implicit stage-2 request shape.

### Changes

* build a formal stage-2 request object
* include:
  * enriched stage-1 output
  * reference-match output
  * render profile
  * locale
  * normalization policy

### Suggested module boundary

Add a request-builder layer such as:

* `scripts/import/recipe_import/normalization_request.py`

Responsibilities:

* assemble stage-2 input
* keep request construction deterministic and testable

### Compatibility rule

The final normalization response should still map into the current candidate bundle model.

---

## Phase 4: Attach semantic uncertainty to candidate review behavior

### Goal

Translate semantic uncertainty into importer outcomes instead of leaving it as only model prose.

### Changes

* formalize severity mapping
* decide which semantic failures produce:
  * warning only
  * warning + review flag
  * hard approval block

### Recommended mapping

* unit parity drift -> warning + review flag
* contextual term drift -> review flag
* archive vocabulary mismatch -> warning + review flag
* unresolved ingredient identity -> review flag
* source contradiction -> approval block unless explicitly overridden

Approval consequences should be made explicit:

* warnings alone do not block ingestion or approval
* `review_flags` block approval by default
* source-evidence contradiction should be treated as a stronger class than an ordinary `review_flag`, even if it still reuses the same operator workflow initially

### Compatibility rule

This phase should strengthen the meaning of `review_flags`, not replace them.

---

## Phase 5: Add stage-1 failure and weak-output handling

### Goal

Make weak preprocessing behavior explicit so the importer does not appear more confident than it is.

### Changes

Define fallback behavior for:

* empty or unusable stage-1 output
* semantically weak but still parseable stage-1 output
* widespread uncertainty markers from stage 1

### Recommended handling

* unusable stage-1 output -> stop before normalization and emit a failed run result
* semantically weak stage-1 output -> continue only with explicit warning and `review_flag` escalation
* strong contextual drift signals -> keep candidate approval-blocked by default

### Compatibility rule

This phase should reuse the current report, warning, and `review_flags` model before inventing new operational states.

---

## Phase 6: Optional decomposition of reference assets

### Goal

Improve maintainability without creating parallel truth sources.

### Changes

If the current reference files become too broad:

* split them into focused subsets or generated derivatives
* keep one declared canonical authority

Recommended rule:

* either the current two files remain canonical
* or the new file set is explicitly declared canonical and the old files become generated artifacts or are retired

Do not allow both systems to evolve independently.

---

## File-level implementation path

### Current files likely to change first

* `prompts/runtime/translation/recipe-translation-v1.md`
* `prompts/schemas/recipe-translation-output.schema.json`
* `scripts/import/recipe_import/transport.py`
* `scripts/import/recipe_import/pipeline.py`
* `scripts/import/recipe_import/references.py`

### New files likely to be added

* `scripts/import/recipe_import/reference_match.py`
* `scripts/import/recipe_import/normalization_request.py`

### Current files that should stay stable if possible

* `scripts/import/review_candidates.py`
* candidate bundle schema shape
* intake approval flow

---

## Testing strategy

Each phase should come with targeted tests.

### Phase 1 tests

* translation schema compatibility tests
* segment payload validation tests
* translategemma transport compatibility tests

### Phase 2 tests

* reference-match tests for Swedish unit aliases
* contextual-term tests for:
  * `spad`
  * `vitlökspulver`
  * `lökpulver`
  * `rörs kall`
  * `10 min + vila`

### Phase 3 tests

* stage-2 request assembly tests
* policy-aware request-shape tests

### Phase 4 tests

* warning and `review_flags` severity mapping tests
* approval-safety regression tests

### Phase 5 tests

* empty stage-1 output handling tests
* weak semantic output escalation tests
* approval-blocking regression tests for source contradictions

### End-to-end tests

Use real Swedish fixtures and at least one live LM Studio verification path after each major phase.

---

## Recommended rollout order

The safest order is:

1. enrich translation output
2. add reference matching
3. formalize normalization request assembly
4. strengthen review-state mapping
5. add weak-stage-1 fallback behavior
6. optionally decompose reference assets

This order keeps the importer usable at every step.

---

## Success criteria

The migration is successful when:

* preprocessing drift is easier to explain from artifacts alone
* normalization gets cleaner semantic inputs
* review flags reflect real semantic risk, not just generic model oddities
* the current candidate review and approval workflow still works
* the importer is more trustworthy on Swedish source material without losing provenance

---

## Worked migration example: `Burgarsås`

Use the existing `Burgarsås` fixture as a migration test anchor.

Phase expectations:

1. Phase 1:
   stage 1 still returns `translated_text`, but now may also return segmented evidence for `spad`, `vitlökspulver`, `lökpulver`, `10 min + vila`, and `rörs kall`.
2. Phase 2:
   the reference-match stage should explicitly identify:
   * `tsk`
   * `spad från relish eller pickles`
   * `vitlökspulver`
   * `lökpulver`
   * no-heat semantics
   * rest requirement
3. Phase 3:
   stage 2 should consume those matches along with render policy.
4. Phase 4:
   if `tsk` becomes `tbsp`, or `spad` becomes relish itself, the candidate should carry blocking `review_flags`.
5. Phase 5:
   if translation quality is weak overall, the importer should either fail before normalization or emit a clearly blocked candidate.

---

## Recommended next implementation step

If this proposal set is accepted, the first implementation task should be:

* revise stage-1 translation output to add segmented semantic evidence while preserving the current `translated_text` field for compatibility

That gives the biggest semantic improvement with the smallest disruption to the current importer.
