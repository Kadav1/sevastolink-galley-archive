# Sevastolink Galley Archive

## Imports Implementation Backlog v1.0

---

## 1. Purpose

This document lists the main import work still missing between the current repository and the broader target-state import model.

It complements:

* [implemented-imports.md](./implemented-imports.md)
* [recipe-import-workflow.md](./recipe-import-workflow.md)

---

## 2. Priority summary

### P1

* add a dedicated web review queue for candidate bundles
* add a review-by-id or review-by-job web flow beyond the current paste-text screen
* decide whether candidate repair should remain script-only or become part of the review pipeline

### P2

* implement URL intake in the current product
* implement file, image, or PDF intake in the current product
* decide whether bulk imports need a dedicated import-domain API surface

### P3

* add background job orchestration for larger import batches
* add richer operator tooling for bulk import status and retries
* only later consider broader import automation beyond the current local archive workflow

---

## 3. Backlog details

### 3.1 Web review queue

Current state:

* candidate review is implemented as a CLI workflow
* the web app does not expose a generalized candidate queue or bundle-review surface

Missing work:

* candidate listing and status review in the web app
* opening an existing candidate or intake job for structured review
* clearer promotion flow from candidate to approved recipe in-browser

### 3.2 Web intake expansion

Current state:

* the web app supports manual entry and paste-text intake
* URL and file/image intake are still unimplemented in the current routed product

Missing work:

* URL import
* file upload intake
* image or PDF parsing intake
* alignment between import docs and surfaced UI once those paths land

### 3.3 Import-domain API decisions

Current state:

* the API exposes intake-job-oriented endpoints
* bulk import orchestration remains local-script-driven

Missing work:

* decide whether bulk candidate operations should stay script-only
* only add import-specific endpoints if they improve the actual product workflow

### 3.4 Background execution

Current state:

* normalization and review commands are foreground local scripts
* there is no queueing, scheduling, or retry system for bulk imports

Missing work:

* optional background job handling for long-running import batches
* better monitoring of batch progress if the archive keeps growing

### 3.5 Repair and evaluation integration

Current state:

* deterministic repair exists as a separate script
* AI evaluation exists as an API capability for intake jobs
* these are not yet unified into one broader import-review product flow

Missing work:

* decide how deterministic repair should fit into the standard import path
* decide whether AI evaluation should become part of bundle-level review tooling

---

## 4. Recommended implementation order

1. candidate review queue and review-by-id web flow
2. URL intake and file/image intake
3. repair/evaluation integration decisions
4. bulk import API decisions
5. background execution only if the local archive workflow needs it
