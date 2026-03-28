# Sevastolink Galley Archive

## Implemented Product v1.0

---

## 1. Purpose

This document defines the current implemented product surface for Sevastolink Galley Archive.

It is the implementation-aware companion to:

* [product-brief.md](./product-brief.md)

Use this document when the question is:

* what the product actually does today
* which product goals are already materially satisfied
* which parts of the product brief are still target-state rather than shipped behavior

---

## 2. Current product baseline

### Established facts

* The product is a local-first recipe archive and cooking workspace.
* The product runs as a self-hosted web application with a FastAPI backend and React frontend.
* The core implemented experience is archive browse, recipe detail, kitchen mode, and intake.
* Optional LM Studio integration is implemented for AI-assisted normalization and related structured tasks.
* The product is still narrower than the full `product-brief.md` target-state description.

### Current product standard

The currently shipped product is best described as:

* a working local recipe archive
* a one-at-a-time intake workflow
* a cooking-oriented recipe reader
* a CLI-capable bulk import system

It is not yet the full product surface implied by every v1 statement in the product brief.

---

## 3. Implemented user-facing product areas

### 3.1 Archive and retrieval

Current implemented product behavior includes:

* recipe library browsing
* query/filter-driven retrieval inside the library page
* recipe detail view
* direct recipe opening by slug

Interpretation:

* archive retrieval is real and central
* search and filtering exist, but the broader target-state navigation model is not fully surfaced yet

### 3.2 Intake

Current implemented intake behavior includes:

* manual entry
* paste-text intake
* AI normalization for paste-text intake when LM Studio is available
* candidate editing before approval
* approval into canonical recipes

Interpretation:

* intake is a real product surface
* the current routed UI covers only a subset of the broader intake brief

### 3.3 Kitchen mode

Current implemented product behavior includes:

* dedicated kitchen-mode route
* full-screen recipe reading surface separate from the main shell

Interpretation:

* the product is already useful during active cooking
* more advanced step-flow or hands-free behavior is still beyond the current implementation

### 3.4 Optional AI features

Current implemented AI-assisted behavior includes:

* intake normalization
* candidate evaluation
* recipe metadata suggestion
* recipe rewrite
* similar-recipe suggestion
* pantry suggestion endpoints in the API

Interpretation:

* the product already has meaningful structured AI affordances
* AI remains optional rather than foundational

### 3.5 Local deployment and resilience

Current implemented operational product behavior includes:

* local Docker-based deployment
* optional nginx-based single-port access
* optional systemd startup integration
* local backup and restore
* local data ownership

Interpretation:

* the local-first and home-hosted product promise is materially real today

---

## 4. Current product gaps against the product brief

### Established facts

The current product does not yet expose the full v1 brief as a routed, polished user-facing experience.

Main current gaps include:

* no URL intake in the current web product
* no image, PDF, or photo-based intake in the current web product
* no broad web review queue for imported candidate bundles
* no in-product recipe edit route for refining existing recipes
* no broader favorites, recent, verified, or drafts navigation surfaces
* settings remains a placeholder page
* ingredient-first search and inspiration browsing are only partially surfaced

### Current interpretation

The product brief describes the intended product direction and the broader v1 target.

The currently implemented product is already useful, but it is still narrower than that target in several user-facing areas.

---

## 5. Product goals already materially satisfied

### Mostly satisfied today

* reliable archiving
* useful in a kitchen
* clean local deployment
* backup and restore
* local-first operation
* AI remains optional rather than required

### Only partially satisfied today

* fast, accurate retrieval across all intended product paths
* trustworthy content distinctions across all intended workflow surfaces
* clean intake workflow for every intended source type
* home-network accessibility as a polished end-user experience rather than just an ops capability

---

## 6. Recommended reading order

Use the product docs in this order:

1. this document for current implemented product scope
2. [product-brief.md](./product-brief.md) for the broader intended product direction
3. [implementation-backlog.md](./implementation-backlog.md) for missing product work
