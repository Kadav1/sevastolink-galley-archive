# Sevastolink Galley Archive

## Implemented Imports v1.0

---

## 1. Purpose

This document defines the current implemented import and candidate-processing model for Sevastolink Galley Archive.

It is the implementation-aware companion to:

* [recipe-import-workflow.md](./recipe-import-workflow.md)

Use this document when the question is:

* what import surfaces actually exist today
* which parts of the import pipeline are CLI-driven
* which areas are still missing from the broader target-state import model

---

## 2. Current import baseline

### Established facts

* Bulk recipe import is implemented primarily as a filesystem and CLI workflow.
* Raw source, candidate bundle, intake database row, and approved recipe are distinct states.
* Raw source files are preserved under `data/imports/raw/`.
* Candidate bundles are emitted under `data/imports/parsed/`.
* Candidate ingest and approval reuse the existing intake service rather than bypassing the application model.
* The web app supports one-at-a-time intake, not broad batch review.

### Current import standard

The current supported pipeline is:

* raw source files on disk
* normalization into `.candidate.json` artifacts
* manual review and patching
* optional deterministic repair pass
* ingest into intake tables
* approval into canonical recipes

This is implemented today. It is not just a target-state design.

---

## 3. Implemented import surfaces

### 3.1 Raw source preservation

Raw import evidence is implemented as filesystem content under:

* `data/imports/raw/recipes/`

Interpretation:

* the system treats raw source files as evidence, not as mutable working copies
* this is an archive-first import model rather than a direct overwrite flow

### 3.2 Normalization CLI

Bulk and single-file normalization are implemented in:

* `scripts/import/normalize_recipes.py`

Current implemented behavior includes:

* single-file normalization
* directory normalization
* LM Studio-backed normalization
* optional translation model support in the script
* candidate bundle emission to disk
* prompt/schema provenance recorded in output artifacts
* overwrite control and batch file resolution

Interpretation:

* normalization is a real implemented stage
* it is still a local script, not an orchestrated background service

### 3.3 Candidate review CLI

Candidate review tooling is implemented in:

* `scripts/import/review_candidates.py`

Current implemented commands include:

* `list`
* `show`
* `edit`
* `ingest`
* `approve`

Current implemented behavior includes:

* in-place patching of candidate bundles
* review-flag and warning handling
* intake database creation through the backend intake service
* approval into canonical recipes
* `--force-new` handling for already-ingested bundles

Interpretation:

* review and promotion are implemented
* they are still operator/CLI workflows rather than a broader web review product surface

### 3.4 Deterministic repair pass

Bulk deterministic repair is implemented in:

* `scripts/import/repair_candidates.py`

Current behavior includes:

* scalar taxonomy cleanup
* ingredient normalization cleanup
* time-class inference cleanup
* display-text repair

Interpretation:

* the repository now includes a post-normalization repair stage for recurring machine-generated drift
* this is implementation-backed local tooling, not an API surface

### 3.5 API intake flow

The backend intake API is implemented for one-at-a-time intake work.

Current implemented endpoints include:

* create intake job
* get intake job
* patch candidate
* normalize candidate
* evaluate candidate
* approve intake job

Interpretation:

* the intake API is real and supports interactive web intake
* it is not yet a bulk-import orchestration API

### 3.6 Web import surfaces

The current web app supports:

* manual entry
* paste-text intake
* AI normalization during paste-text intake
* approval into recipes

Interpretation:

* the current web flow handles individual recipe intake
* it does not replace the CLI for bulk source-file imports

---

## 4. Current missing or incomplete import areas

### Established facts

Several import areas remain incomplete relative to the broader target-state model.

Current gaps include:

* no dedicated web review queue for filesystem candidate bundles
* no URL import flow in the current web app
* no image or PDF import flow in the current web app
* no background job orchestration for bulk imports
* no first-class admin surface for bulk candidate review
* no dedicated import-domain API beyond intake-job-oriented flows

### Current interpretation

Imports are functional today, but the implementation is split intentionally:

* bulk work is CLI-first
* interactive one-off intake is web-first
* candidate review at scale still lives outside the web app

---

## 5. Runtime model split

### Current split

The import system currently has two different operating modes:

* filesystem + CLI for bulk archive ingestion
* API + web UI for one-at-a-time intake and approval

This split is important because it explains why the import feature set feels broader in scripts than in the routed frontend.

---

## 6. Recommended reading order

Use the import docs in this order:

1. this document for current implemented import scope
2. [recipe-import-workflow.md](./recipe-import-workflow.md) for the detailed CLI workflow
3. [implementation-backlog.md](./implementation-backlog.md) for missing import work
