# Sevastolink Galley Archive

## Product Implementation Backlog v1.0

---

## 1. Purpose

This document lists the main product work still missing between the current repository and the broader target-state product brief.

It complements:

* [implemented-product.md](./implemented-product.md)
* [product-brief.md](./product-brief.md)

---

## 2. Priority summary

### P1

* implement recipe editing as a real product flow
* implement broader review-oriented intake surfaces
* implement URL intake in the current product
* expand retrieval surfaces for trusted, draft, and recent recipe access

### P2

* implement file, image, and PDF intake
* implement a real settings surface
* deepen ingredient-first and inspiration-oriented retrieval

### P3

* broaden archive enrichment and AI-assisted refinement flows
* add fuller organizational features only if the archive workflow still needs them
* only later consider versioning, collections, or planning overlays

---

## 3. Backlog details

### 3.1 Recipe refinement and editing

Current state:

* the product supports reading and approving recipes
* it does not expose a dedicated user-facing edit route for refining existing recipes

Missing work:

* recipe edit route and page
* update flow for structured recipe fields
* clearer verification/refinement workflow after cooking

### 3.2 Intake expansion

Current state:

* the product supports manual and paste-text intake
* broader source types are still absent from the routed experience

Missing work:

* URL intake
* image and PDF intake
* stronger candidate review flow in the web product

### 3.3 Retrieval and browsing expansion

Current state:

* the library page supports searching and filtering
* the broader browsing model described in the product brief is only partly surfaced

Missing work:

* recent, verified, and draft-oriented views
* stronger inspiration browsing by cuisine or technique
* clearer ingredient-first retrieval

### 3.4 Settings and product completeness

Current state:

* settings is a routed placeholder
* some product promises depend on configuration or review affordances that are not fully surfaced yet

Missing work:

* a real settings page
* clearer user-facing control over optional AI and local runtime assumptions where appropriate

### 3.5 Later product layers

Current state:

* the current product is still focused on archive, intake, and cooking

Missing work:

* collections
* version history
* richer media support
* planning overlays

These should remain secondary until the core archive and intake product is complete.

---

## 4. Recommended implementation order

1. recipe edit flow
2. intake review and URL intake
3. retrieval surface expansion
4. settings completion
5. only then the broader enrichment and organization layers
