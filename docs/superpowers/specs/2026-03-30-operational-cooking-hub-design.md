# Sevastolink Galley Archive

## Operational Cooking Hub Design

Date: 2026-03-30

Status: proposed target-state design

---

## 1. Purpose

This document captures the approved target-state design direction for broadening Sevastolink Galley Archive into an operational cooking hub while preserving the repository's current documentation discipline.

It defines:

* the approved target-state product frame
* which external reference patterns are relevant
* which ideas are already implemented
* which ideas are already in the session pipeline
* which ideas are genuinely new target-state proposals
* which documentation changes are required before broader implementation planning

This document is a target-state design spec. It does not change the meaning of any implementation-aware document.

---

## 2. Documentation Rule

This design must follow the repository's existing documentation policy.

Current-state and implementation-aware documents remain the source of truth for shipped behavior:

* `README.md`
* `docs/00_overview/current-state.md`
* `docs/01_product/implemented-product.md`
* `docs/02_ux/implemented-routes-and-flows.md`
* `docs/03_visual-system/implemented-visual-system.md`
* `docs/05_ai/implemented-ai.md`
* `docs/07_api/implemented-api.md`

Target-state documents remain the correct place for broader direction:

* `docs/01_product/product-brief.md`
* `docs/02_ux/information-architecture.md`
* `docs/02_ux/intake-import-ux.md`
* `docs/04_taxonomy/content-taxonomy-spec.md`

Every major idea in this spec is labeled as one of:

* `Implemented now`
* `Already in pipeline`
* `New target-state proposal`
* `Future / not committed`

No implementation-aware document should be updated to describe a target-state feature until that feature exists in code.

---

## 3. Approved Direction

The approved product direction is:

`archive-first personal cooking system with storage-aware retrieval, light planning overlay, and recipe-level nutrition reference`

This direction is governed by these approved constraints:

* Galley remains local-first, archive-first, single-household, and private by default.
* The archive remains the system core.
* Pantry, storage, planning, and AI are support layers around the archive rather than separate product identities.
* AI remains optional, structured, user-initiated, and review-centric.
* Planning stays lighter than a full meal-planning or grocery-management application.
* Nutrition, if added, is recipe-level reference metadata only and not personal nutrition tracking.

This direction is consistent with the broader tone and product posture in:

* `docs/01_product/product-brief.md`
* `docs/02_ux/ui-ux-foundations.md`
* `docs/03_visual-system/visual-system-spec.md`

It does, however, require a target-state product-brief revision before recipe-level nutrition reference should be treated as approved product scope.

This direction does not change current shipped scope by itself.

---

## 4. Reference-Site Findings

The design was informed by a review of these sites:

* Tandoor Docs — `https://docs.tandoor.dev/`
* Mealie Docs — `https://docs.mealie.io/`
* StillTasty — `https://www.stilltasty.com/`
* Does It Go Bad — `https://www.doesitgobad.com/`
* MyFridgeFood — `https://myfridgefood.com/`
* GrubPick — `https://grubpick.com/`

### 4.1 Tandoor and Mealie

Strongest relevant patterns:

* self-hosted recipe-management seriousness
* breadth of intake and import paths
* household utility beyond simple recipe storage
* broader route completeness
* practical operations posture

Relevant for Galley:

* stronger intake breadth
* more complete archive organization
* planning-adjacent overlays
* operational trust for self-hosted home use

Should not be copied directly:

* generic recipe-manager aesthetics
* broader workflow sprawl without archive discipline

### 4.2 StillTasty and Does It Go Bad

Strongest relevant patterns:

* shelf-life lookup
* spoilage framing
* practical storage guidance
* clear "keep or toss" decision language

Relevant for Galley:

* advisory storage guidance
* use-soon / caution framing
* storage-aware recipe retrieval
* leftovers and preservation support

Should not be copied directly:

* article-farm style content expansion
* fake certainty about storage outcomes
* decontextualized SEO content

### 4.3 MyFridgeFood

Strongest relevant pattern:

* very low-friction ingredient-first retrieval

Relevant for Galley:

* fast pantry input
* "what can I make with this?" interaction
* immediate retrieval from available ingredients

Should not be copied directly:

* novelty-first presentation
* generic public recipe discovery framing

### 4.4 GrubPick

Signal quality was weaker than the others because the official site did not provide a strong crawlable primary-source text surface during review.

Useful signal only:

* AI-assisted import and organization
* planning and recipe-assistant framing

This should be treated as a weaker secondary reference rather than a design authority.

---

## 5. Product Model

The target-state model is:

`Archive core -> storage awareness -> planning and action overlay`

### 5.1 Archive Core

The archive remains the primary product layer.

Responsibilities:

* store structured recipe records
* preserve sources and trust state
* support retrieval, refinement, and kitchen use
* act as the canonical base for pantry, planning, and AI helpers

### 5.2 Storage-Awareness Layer

This layer adds practical domestic-cooking intelligence around:

* storage profile
* leftovers
* preservation
* use-soon decisions
* pantry and fridge input

This layer supports the archive; it does not replace it.

### 5.3 Planning and Action Overlay

This layer remains deliberately narrow.

Responsibilities:

* help the user decide what to cook next
* support light scheduling overlays
* connect pantry/storage context to archive retrieval

This layer must not become:

* a full meal-planning system
* a grocery list engine
* a household inventory platform

---

## 6. Idea Classification

### 6.1 Implemented now

These already exist in the repository and should not be described as future concepts:

* library browse surface
* recipe detail
* kitchen mode
* intake hub
* manual entry
* paste-text intake
* pantry page
* intake evaluation UX
* archive enrichment workflows on recipe detail
* retrieval assistance surfaces for pantry and similar recipes
* LM Studio diagnostics

Primary sources:

* `docs/00_overview/current-state.md`
* `docs/05_ai/implemented-ai.md`
* `docs/superpowers/sessions.md`

### 6.2 Already in pipeline

These are already represented by session prompts or backlog direction and should not be treated as new product invention:

* deterministic ingredient-first retrieval and inspiration browsing
  * `prompts/build/claude/sessions/session-39-ingredient-first-retrieval-and-inspiration.md`
* import-domain API and batch-execution decision
  * `prompts/build/claude/sessions/session-37-import-domain-api-and-batch-execution.md`
* unresolved responsive, primitive, overlay, iconography, and taxonomy completion work
  * sessions `22` through `31`
* AI-jobs visibility decision
  * `prompts/build/claude/sessions/session-42-ai-jobs-visibility-decision.md`

### 6.3 New target-state proposals

These are the main genuinely new proposals produced by this design:

* storage guidance as a first-class product module
* stronger storage-aware retrieval and use-soon framing
* recipe-level nutrition reference metadata

These require explicit target-state doc changes before implementation planning.

### 6.4 Future / not committed

These should remain explicitly uncommitted:

* shopping lists
* full meal-planning workflows
* pantry stock-management system
* personal nutrition tracking
* multi-user household coordination

---

## 7. Target-State Surfaces

### 7.1 Archive Surfaces

Status:

* core archive surfaces are `Implemented now`
* route expansion remains `Already in pipeline`

Target-state direction:

* library contexts for favorites, verified, drafts, and recent
* structured recipe edit flow
* richer recipe dossier with source, notes, storage cues, related records, and media
* clearer archive status presentation around trust and use

Relevant grounding:

* `docs/02_ux/information-architecture.md`
* `docs/02_ux/implementation-backlog.md`
* `prompts/build/claude/sessions/session-16-library-route-expansion.md`
* `prompts/build/claude/sessions/session-17-recipe-edit-flow.md`

### 7.2 Intake Surfaces

Status:

* manual and paste intake are `Implemented now`
* route expansion is `Already in pipeline`

Target-state direction:

* URL intake
* file / image / PDF intake
* review route keyed by intake job
* stronger source/candidate/evaluation/approval separation

Relevant grounding:

* `docs/02_ux/intake-import-ux.md`
* `docs/02_ux/implementation-backlog.md`
* `prompts/build/claude/sessions/session-18-intake-route-expansion-and-review.md`
* `prompts/build/claude/sessions/session-37-import-domain-api-and-batch-execution.md`

### 7.3 Pantry and Storage Surfaces

Status:

* pantry page and AI pantry assistance are `Implemented now`
* deterministic ingredient-first browsing is `Already in pipeline`
* storage guidance as a stronger module is a `New target-state proposal`

Target-state direction:

* low-friction ingredient entry
* deterministic ingredient-first retrieval
* use-soon and caution framing
* storage-profile visibility on recipes
* stronger leftovers and preservation-oriented retrieval
* advisory storage references tied to archive use

Relevant grounding:

* `docs/05_ai/prompt-contracts.md`
* `docs/04_taxonomy/content-taxonomy-spec.md`
* `prompts/build/claude/sessions/session-39-ingredient-first-retrieval-and-inspiration.md`
* `prompts/build/claude/sessions/session-44-retrieval-assistance-productization.md`

### 7.4 Planning Overlay

Status:

* light planning exists as target-state direction in product docs
* it is not yet a strongly defined session-driven implementation path
* therefore it is best treated as `Future / not committed` until explicitly expanded

Approved direction:

* planned date on recipes
* simple weekly planning view
* use-soon or cook-this-week overlays

Not approved:

* grocery lists
* full weekly planner logic
* pantry stock-management automation

Relevant grounding:

* `docs/01_product/product-brief.md`

### 7.5 Nutrition Reference

Status:

* `New target-state proposal`

Approved scope:

* recipe-level nutrition metadata
* per-serving estimates
* dietary and allergen reference cues
* retrieval support later

Explicitly not approved:

* intake logging
* daily compliance tracking
* personal goal systems
* nutrition dashboards

---

## 8. Rollout Priorities

The roadmap implied by this design is:

### 8.1 Finish pipeline-aligned work first

Highest-value next work:

* Session `39` deterministic ingredient-first retrieval
* unresolved sessions `22` through `31` for responsive, component, and taxonomy completion
* Session `37` import-domain architecture tightening
* Session `42` AI-jobs visibility decision

Rationale:

* these sessions already support the approved direction
* they reduce architecture and UX debt
* they avoid inventing new product scope before the current pipeline is complete

### 8.2 Add one new storage-aware proposal after pipeline alignment

Best candidate:

* storage guidance as a first-class advisory module

Rationale:

* this is the clearest differentiator relative to generic recipe managers
* it fits the archive-first identity
* it supports daily usefulness without changing the product category

### 8.3 Add nutrition reference only after brief revision

Nutrition should not be planned for implementation until the target-state product brief is explicitly updated to permit recipe-level nutrition reference.

### 8.4 Keep broader planning work deferred

Planning should remain narrow until:

* the product explicitly wants a dedicated planning slice
* the brief is updated
* a dedicated session or backlog item exists

---

## 9. Required Documentation Changes

### 9.1 Update now

These target-state docs should change if this direction is adopted:

* `docs/01_product/product-brief.md`
  * allow recipe-level nutrition reference
  * clarify storage-aware retrieval as a target-state strength
  * keep planning bounded and lighter than a full planner
* `docs/02_ux/information-architecture.md`
  * clarify where stronger pantry/storage guidance belongs
  * keep those surfaces archive-connected
* `docs/01_product/implementation-backlog.md`
  * distinguish already-implemented, already-pipelined, and genuinely new proposals
* `docs/02_ux/implementation-backlog.md`
  * note that deterministic ingredient-first retrieval is already owned by Session `39`
  * add storage-guidance work as a new proposal if adopted

### 9.2 Verify before changing

This spec assumes `docs/04_taxonomy/content-taxonomy-spec.md` may already support much of the storage side through existing taxonomy fields. That should be verified before any taxonomy rewrite is proposed.

### 9.3 Do not update until implementation lands

The following must remain implementation-aware and should only change when code changes:

* `docs/00_overview/current-state.md`
* `docs/01_product/implemented-product.md`
* `docs/02_ux/implemented-routes-and-flows.md`
* `docs/05_ai/implemented-ai.md`
* `docs/07_api/implemented-api.md`

---

## 10. Acceptance Criteria For This Direction

This design is correctly applied if:

* the archive remains the product center
* pantry, storage, AI, and planning remain supporting layers
* implemented features are not re-documented as future concepts
* existing session-pipeline work is used before inventing parallel efforts
* storage guidance is framed as advisory and provenance-aware
* nutrition remains recipe-level reference only
* implementation-aware docs remain strict about shipped behavior

This design is incorrectly applied if:

* Galley starts being described as a planner, grocery tool, or nutrition tracker
* AI becomes the default retrieval path
* storage guidance is presented as certainty rather than advisory help
* target-state features are documented as current behavior

---

## 11. Sources

External reference sources reviewed:

* `https://docs.tandoor.dev/`
* `https://docs.mealie.io/`
* `https://www.stilltasty.com/`
* `https://www.doesitgobad.com/`
* `https://myfridgefood.com/`
* `https://grubpick.com/`

Repository sources used for grounding:

* `README.md`
* `docs/00_overview/current-state.md`
* `docs/01_product/product-brief.md`
* `docs/02_ux/ui-ux-foundations.md`
* `docs/02_ux/information-architecture.md`
* `docs/02_ux/intake-import-ux.md`
* `docs/02_ux/implementation-backlog.md`
* `docs/03_visual-system/implemented-visual-system.md`
* `docs/04_taxonomy/content-taxonomy-spec.md`
* `docs/05_ai/implemented-ai.md`
* `docs/05_ai/prompt-contracts.md`
* `docs/07_api/implemented-api.md`
* `docs/superpowers/sessions.md`
* `prompts/build/claude/sessions/README.md`
* `prompts/build/claude/sessions/session-37-import-domain-api-and-batch-execution.md`
* `prompts/build/claude/sessions/session-39-ingredient-first-retrieval-and-inspiration.md`
* `prompts/build/claude/sessions/session-42-ai-jobs-visibility-decision.md`
* `prompts/build/claude/sessions/session-44-retrieval-assistance-productization.md`
