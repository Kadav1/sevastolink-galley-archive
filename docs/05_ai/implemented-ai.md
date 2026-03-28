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

Current surface:

* `POST /api/v1/intake-jobs/{job_id}/evaluate`

Interpretation:

* evaluation is implemented in the API
* it is not yet a fully surfaced routed web review workflow

### 3.3 Recipe metadata suggestion

Implemented today:

* the backend can suggest structured taxonomy and metadata fields for an existing recipe

Current surface:

* `POST /api/v1/recipes/{id_or_slug}/suggest-metadata`

Interpretation:

* metadata suggestion is implemented in the API
* it is not yet a broader dedicated user-facing route area

### 3.4 Recipe rewrite

Implemented today:

* the backend can return an archive-style rewrite suggestion for an existing recipe

Current surface:

* `POST /api/v1/recipes/{id_or_slug}/rewrite`

Interpretation:

* rewrite is implemented as a suggestion workflow
* it does not directly modify stored recipes

### 3.5 Similar recipes

Implemented today:

* the backend can rank similar recipes relative to a source recipe

Current surface:

* `POST /api/v1/recipes/{id_or_slug}/similar`

Interpretation:

* similarity is implemented as an API capability
* it is not yet a larger routed discovery product surface

### 3.6 Pantry suggestions

Implemented today:

* the backend can suggest candidate recipe directions from available ingredients

Current surface:

* `POST /api/v1/pantry/suggest`

Interpretation:

* pantry suggestion is implemented in the API
* it is not yet a broader dedicated pantry product area

### 3.7 Translation in import tooling

Implemented today:

* the CLI importer supports an optional translation pass before normalization

Current surface:

* `scripts/import/normalize_recipes.py`

Interpretation:

* translation is implemented as importer tooling, not as a routed product workflow

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
* no broader web review flow for intake evaluation
* no user-facing archive enrichment panel on recipe pages
* no first-class routed surfaces for rewrite, metadata suggestion, pantry, or similarity
* no surfaced `ai_jobs` resource even though the table exists
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
