# Sevastolink Galley Archive

## AI Implementation Backlog v1.0

---

## 1. Purpose

This document translates the `docs/05_ai/` target-state AI set into a concrete implementation backlog.

It complements:

* [implemented-ai.md](./implemented-ai.md)
* [ai-interaction-spec.md](./ai-interaction-spec.md)
* [lm-studio-integration.md](./lm-studio-integration.md)
* [prompt-contracts.md](./prompt-contracts.md)

---

## 2. Current implementation baseline

Already implemented:

* LM Studio integration
* shared runtime prompt registry
* structured prompt contracts and schemas
* intake normalization
* intake evaluation endpoint
* metadata suggestion endpoint
* rewrite endpoint
* similarity endpoint
* pantry suggestion endpoint
* importer translation support

Still missing:

* broader routed productization of AI workflows
* dedicated AI tools area
* richer intake-review UX for evaluation
* clearer archive enrichment UX for metadata and rewrite
* deliberate `ai_jobs` visibility strategy
* stronger runtime diagnostics and health visibility for LM Studio

---

## 3. Backlog summary

| Priority | Area | Current state | Target state |
|---|---|---|---|
| P1 | Intake review and evaluation UX | Normalize exists in web flow, evaluation is API-only | Review-centered intake AI surface |
| P1 | Archive enrichment UX | Metadata and rewrite exist as endpoints | Real enrichment flow on recipe pages or AI tools area |
| P1 | Dedicated AI tools area | AI is embedded, not routed as its own area | Honest optional AI route group |
| P2 | AI job visibility decision | **Done** — decided internal infrastructure, not a surfaced resource (see `implemented-ai.md §4.4`) | Explicit architectural decision recorded |
| P2 | LM Studio diagnostics and degraded-mode visibility | Errors surface inline, ops visibility is thin | Clearer local AI health and troubleshooting flow |
| P3 | Retrieval-assistance productization | Similarity and pantry endpoints exist | Stronger user-facing retrieval assistance if still worthwhile |

---

## 4. Backlog detail

### 4.1 P1: Intake review and evaluation UX

Current state:

* normalization is surfaced in the paste-text intake flow
* evaluation exists only as an API endpoint

Missing work:

* routed review UI for evaluation results
* clearer side-by-side or staged raw-vs-candidate review
* stronger human-review affordances before approval

### 4.2 P1: Archive enrichment UX

Current state:

* metadata suggestion and rewrite are implemented in the backend
* there is no real recipe-level enrichment surface in the product

Missing work:

* enrichment entry points on recipe pages or in an AI tools area
* review/apply flow for suggestions
* explicit handling of suggestion-only behavior

### 4.3 P1: Dedicated AI tools area

Current state:

* AI is mostly embedded within existing flows
* there is no routed AI area

Missing work:

* AI tools landing route
* honest route group exposing only mature workflows
* shared AI result and degraded-mode framing

### 4.4 P2: AI job visibility decision

Current state:

* `ai_jobs` table exists
* current product flows do not expose job history or inspection

Missing work:

* decide whether `ai_jobs` should become a first-class product/API surface
* if yes, implement inspection/history
* if not, document it as internal infrastructure

### 4.5 P2: LM Studio diagnostics and degraded-mode visibility

Current state:

* the app degrades when AI is disabled or unreachable
* diagnostics are still mostly operational rather than product-facing

Missing work:

* clearer AI availability checks
* clearer user/operator-facing diagnostics
* tighter troubleshooting path for local LM Studio failures

### 4.6 P3: Retrieval-assistance productization

Current state:

* similarity and pantry logic are implemented as endpoints
* they are not yet a stronger user-facing retrieval layer

Missing work:

* decide whether these should remain specialist tools or become more visible product flows

---

## 5. Recommended implementation order

1. intake review and evaluation UX
2. archive enrichment UX
3. dedicated AI tools area
4. AI job visibility decision
5. LM Studio diagnostics
6. retrieval-assistance productization
