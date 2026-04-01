# Sevastolink Galley Archive

## Implemented AI v1.0

---

## 1. Purpose

This document defines the AI behavior and AI-backed workflows that are implemented in the repository now.

It is the implementation-aware companion to:

* [ai-interaction-spec.md](./ai-interaction-spec.md)
* [lm-studio-integration.md](./lm-studio-integration.md)
* [prompt-contracts.md](./prompt-contracts.md)

Use this document when the question is:

* which AI flows actually exist today
* how AI is surfaced in the current product and tooling
* which AI capabilities are implemented only as backend endpoints or prompt assets

---

## 2. Current AI baseline

### Established facts

* AI is optional and LM Studio-backed.
* The archive remains usable without AI.
* AI is implemented as structured task-specific workflows, not as a chat surface.
* The repository already has multiple real AI contracts and backend consumers.
* The current product exposes only part of that AI capability as complete user-facing workflows.

### Current implementation standard

The current AI model is:

* prompt-contract-driven
* LM Studio over local HTTP
* structured output validated against schemas where appropriate
* user-initiated
* review-centric rather than auto-applying

---

## 3. Implemented AI workflows

### 3.1 Intake normalization

Implemented today:

* paste-text intake can create an intake job
* the user can request AI normalization
* AI output is applied to the intake candidate for review
* the user can edit the candidate before approval

Current surfaces:

* `POST /api/v1/intake-jobs/{job_id}/normalize`
* web paste-text intake page

Interpretation:

* this is the clearest fully implemented AI product workflow

### 3.2 Intake evaluation

Implemented today:

* the backend can run a read-only AI evaluation of a candidate against its raw source
* the paste-text intake page exposes an "Evaluate normalization" button after a job has been created
* the evaluation result renders inline in the raw source panel with a recommendation badge, fidelity assessment, and issue lists
* result is dismissable; does not modify the candidate

Current surfaces:

* `POST /api/v1/intake-jobs/{job_id}/evaluate`
* web paste-text intake page — evaluate button visible once `job_id` is set (after normalize or save)

Interpretation:

* evaluation is a read-only review aid during the intake workflow
* the recommendation badge (safe / caution / needs correction) gives a quick quality signal before approval

### 3.3 Recipe metadata suggestion

Implemented today:

* the backend can suggest structured taxonomy and metadata fields for an existing recipe
* the Recipe Detail page exposes a "Suggest metadata" button in an AI Tools section at the bottom
* AI-suggested fields are shown in a panel with per-field "Apply" buttons
* applying a field PATCHes the recipe and invalidates the TanStack Query cache
* the `"class"` alias returned by the AI is mapped to `"operational_class"` in the PATCH body
* confidence and uncertainty notes are displayed below the field list
* AI unavailable state shows an inline message without crashing

Current surfaces:

* `POST /api/v1/recipes/{id_or_slug}/suggest-metadata`
* web Recipe Detail page — AI Tools section (bottom of page)

Interpretation:

* metadata suggestion is now a complete user-facing workflow
* users can selectively apply individual suggested fields or dismiss the panel

### 3.4 Recipe rewrite

Implemented today:

* the backend can return an archive-style rewrite suggestion for an existing recipe
* the Recipe Detail page exposes a "Rewrite recipe" button in the AI Tools section
* the rewrite is shown in a read-only panel with title, description, ingredients, steps, and notes
* the panel is dismissable; it does not modify the stored recipe

Current surfaces:

* `POST /api/v1/recipes/{id_or_slug}/rewrite`
* web Recipe Detail page — AI Tools section (bottom of page)

Interpretation:

* rewrite is now surfaced as a visible suggestion workflow in the UI
* it remains read-only and does not apply changes to stored recipes

### 3.5 Similar recipes

Implemented today:

* the backend can rank similar recipes relative to a source recipe

Current surfaces:

* `POST /api/v1/recipes/{id_or_slug}/similar`
* web Recipe Detail page — AI Tools section (bottom of page)

Interpretation:

* similarity is implemented in the API and surfaced from the recipe detail workflow
* it is not yet a larger standalone discovery product surface

### 3.6 Pantry suggestions

Implemented today:

* the backend can suggest candidate recipe directions from available ingredients

Current surfaces:

* `POST /api/v1/pantry/suggest`
* web Pantry page at `/pantry`

Interpretation:

* pantry suggestion is implemented in the API and exposed through a routed pantry workspace
* it is still narrower than the broader pantry target-state docs

### 3.7 Preprocessing in import tooling

Current status:

* the CLI importer can run a semantics-first staged pipeline before normalization for non-English source text
* stage 1 translation/preprocessing returns a `TranslationArtifact` with required `translated_text` and optional `segments`
* stage 1.5 performs deterministic reference matching against the active Swedish reference assets
* stage 2 assembles an explicit normalization request with `render_profile`, `locale`, `stage1_translation`, `stage1_reference_match`, and `normalization_policy`
* weak stage-1 quality checks can escalate into `warnings` and `review_flags` without blocking candidate emission
* the preprocessing stage can be executed inline or saved as `.preprocessed.txt` artifacts for later normalization
* when `--use-preprocessed-dir` has no matching saved artifact, the importer currently falls back to inline preprocessing instead of failing

Current surface:

* `scripts/import/normalize_recipes.py`

Interpretation:

* preprocessing is importer tooling, not a routed product workflow
* the saved-artifact mode exists to support one-model-at-a-time LM Studio setups
* the importer AI behavior is structured and review-centric rather than chat-based
* candidate-bundle output remains backward-compatible with `scripts/import/review_candidates.py`

---

## 4. Implemented AI infrastructure

### 4.1 Shared prompt registry

Implemented today:

* runtime prompt registry under `packages/shared-prompts`
* prompt loading and response-format construction
* registered families for:
  * normalization
  * translation
  * evaluation
  * metadata
  * rewrite
  * pantry
  * similarity

### 4.4 AI jobs table — internal infrastructure decision

**Decision (Session 42):** `ai_jobs` is internal infrastructure. It will not be surfaced as a first-class API or UI resource.

Rationale:

* This is a single-user personal archive. There is no stakeholder who needs to monitor or audit a job-history feed.
* Every AI operation is user-initiated and shows its result inline in the originating workflow (intake, recipe detail, pantry). The result is immediately visible; a separate history surface adds no product value.
* Exposing `ai_jobs` as a resource would create surface area to maintain without improving any real user workflow.

Current state:

* `ai_jobs` rows are written as audit records whenever an AI endpoint runs.
* No API route reads them. No UI surface exposes them.
* This is correct and intentional.

If this product ever becomes multi-user or a background AI enrichment queue is added, revisiting this decision is appropriate. For the current single-user local-archive model, the decision is to keep `ai_jobs` internal.

### 4.2 LM Studio integration

Implemented today:

* local LM Studio client
* OpenAI-compatible API calls
* degraded-mode handling for transport failure and disabled AI

### 4.3 Prompt assets and schemas

Implemented today:

* runtime prompt files under `prompts/runtime/`
* structured output schemas under `prompts/schemas/`

Interpretation:

* the prompt and client infrastructure is ahead of the current user-facing product rollout

---

## 5. Current gaps relative to the full AI spec

### Established facts

The broader AI docs describe more AI-facing product behavior than the current routed app exposes.

Current gaps include:

* no dedicated AI tools route group
* `ai_jobs` is intentionally internal infrastructure (see §4.4)
* no standalone routed surfaces dedicated solely to rewrite, metadata suggestion, or similarity beyond the Recipe Detail AI Tools section
* no AI-backed retrieval assistant beyond direct endpoint capability

### Current interpretation

AI capability is already substantial in the backend.

The main missing work is productization and workflow surfacing, not basic prompt infrastructure.

---

## 6. Contributor note

When working on AI:

* treat this document as the current implementation baseline
* treat the broader `05_ai` docs as target-state references
* distinguish prompt assets, backend capabilities, and routed product workflows carefully
* do not document a backend-only AI capability as a full product workflow until it is actually surfaced
