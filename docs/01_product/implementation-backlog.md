# Sevastolink Galley Archive

## Product Implementation Backlog v1.0

---

## 1. Purpose

This document lists the main product work still missing between the current repository and the broader target-state product brief.

It complements:

* [implemented-product.md](./implemented-product.md)
* [product-brief.md](./product-brief.md)

Backlog items in this document should be read through four lenses:

* implemented now
* already in pipeline
* new target-state proposal
* future / not committed

Use the implementation-aware docs first. Where a backlog area is already owned by a named implementation session, that is called out inline instead of being treated as greenfield work.

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

Classification:

* deterministic ingredient-first retrieval is `already in pipeline` through Session 39 (`ingredient-first-retrieval-and-inspiration`)
* broader route contexts for trusted, draft, recent, and inspiration-oriented browsing remain `missing work`

Already in pipeline:

* deterministic ingredient-first retrieval through Session 39
* archive-first inspiration tied to that ingredient-first retrieval slice

Missing work:

* recent, verified, and draft-oriented views
* stronger inspiration browsing by cuisine or technique

Planning note:

* deterministic ingredient-first retrieval should be advanced through Session 39 rather than reintroduced as a separate greenfield proposal in the product backlog

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

Classification:

* collections, version history, richer media support, and planning overlays remain `future / not committed`
* storage guidance and stronger use-soon retrieval are `new target-state proposals`
* recipe-level nutrition reference is a `new target-state proposal` bounded to recipe metadata rather than personal tracking

Future / not committed:

* collections
* version history
* richer media support
* planning overlays

New target-state proposals:

* storage guidance as a first-class advisory product layer
* stronger use-soon and leftovers-aware retrieval
* recipe-level nutrition reference metadata, bounded to recipe-level reference rather than personal tracking

These should remain secondary until the core archive, intake, and retrieval pipeline work is complete.

---

## 4. Recommended implementation order

1. recipe edit flow
2. intake review and URL intake
3. retrieval surface expansion
4. settings completion
5. only then the broader enrichment and organization layers
