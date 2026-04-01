# Sevastolink Galley Archive

## UX Implementation Backlog v1.0

---

## 1. Purpose

This document translates the current `docs/02_ux/` target-state UX set into a concrete implementation backlog.

It establishes:

* which UX-defined surfaces are already implemented
* which target-state surfaces are still missing
* which missing areas should be built first
* how the missing work maps back to the existing UX documents

This is an implementation-planning document. It should be read alongside:

* `docs/02_ux/implemented-routes-and-flows.md`
* `docs/00_overview/current-state.md`

---

## 2. Current implementation baseline

The frontend currently implements:

* library landing and browse surface
* free-text search and structured filtering within the library page
* recipe detail view
* kitchen mode
* intake hub
* manual entry flow
* paste-text intake flow with optional AI normalization
* settings placeholder page

The frontend does not yet implement:

* library sub-routes
* recipe editing
* URL import
* file or image intake
* intake review routes keyed by intake job
* standalone AI tools routes
* functional settings workflows
* broader shell and component patterns described by the UX specs

---

## 3. Backlog summary

| Priority | Area | Current state | Target state | Primary UX doc |
|---|---|---|---|---|
| P1 | Library expansion | Single library route with query/filter state | Dedicated library contexts and route states | `information-architecture.md`, `screen-blueprint-pack.md` |
| P1 | Recipe edit flow | Read-only recipe detail | Editable recipe workflow | `information-architecture.md`, `screen-blueprint-pack.md` |
| P1 | Intake expansion | Manual + paste only | URL import, file intake, review route | `intake-import-ux.md`, `screen-blueprint-pack.md` |
| P2 | Settings | Placeholder page only | Functional settings landing and sub-pages | `information-architecture.md`, `screen-blueprint-pack.md` |
| P2 | AI tools area | No routed AI area | Dedicated AI utility surfaces | `information-architecture.md`, `screen-blueprint-pack.md`, `component-inventory.md` |
| P3 | Storage-guidance surfaces | No first-class storage-guidance product module | Advisory storage-aware retrieval tied to archive and pantry workflows | `information-architecture.md`, `component-inventory.md` |
| P3 | Shell and navigation refinement | Side nav + main outlet only | Richer shell, context patterns, route hierarchy | `component-inventory.md`, `screen-blueprint-pack.md` |
| P3 | Component-system completion | Partial real component set | Broader component families from UX docs | `component-inventory.md` |

---

## 4. Backlog detail

### 4.1 P1: Library expansion

Current state:

* `/` and `/library` both render the same library page
* filtering and search live inside one route through URL parameters

Missing target-state items:

* `/library/favorites`
* `/library/recent`
* `/library/verified`
* `/library/drafts`
* `/library/search`
* stronger library context labeling and route-aware navigation state

Likely implementation work:

* add dedicated library child routes
* decide which views are real backend filters versus frontend aliases
* update navigation and page-level headings for route context
* define whether `recent` is persisted or derived
* extend tests for route-aware library behavior

Primary source docs:

* `docs/02_ux/information-architecture.md`
* `docs/02_ux/screen-blueprint-pack.md`

### 4.2 P1: Recipe edit flow

Current state:

* recipe detail is read-only apart from favorite toggle
* there is no `/recipe/:slug/edit`

Missing target-state items:

* recipe edit route
* structured recipe editing screen
* review/save flow for edited recipes

Likely implementation work:

* add `/recipe/:slug/edit`
* build editable recipe form using the current manual-entry and paste-text field patterns
* define PATCH payload handling and field-level validation
* decide whether source and trust-state editing belong in the first version

Primary source docs:

* `docs/02_ux/information-architecture.md`
* `docs/02_ux/screen-blueprint-pack.md`

### 4.3 P1: Intake expansion

Current state:

* `/intake`, `/intake/manual`, and `/intake/paste` are implemented
* intake hub explicitly marks URL and file/image intake as later work
* there is no review-by-job route

Missing target-state items:

* `/intake/url`
* `/intake/file`
* `/intake/review/:id`
* broader review queue concepts

Likely implementation work:

* add URL import route and page
* add file/image intake route and page shell
* add dedicated review route keyed by intake job
* refactor shared intake-review UI out of the paste-text page
* align web review surfaces with the current backend intake job lifecycle

Primary source docs:

* `docs/02_ux/intake-import-ux.md`
* `docs/02_ux/screen-blueprint-pack.md`

### 4.4 P2: Settings implementation

Current state:

* `/settings` exists but is a placeholder only

Missing target-state items:

* settings landing behavior
* archive settings
* UI preferences
* kitchen-mode preferences
* import settings
* AI / LM Studio settings
* backup / export settings

Likely implementation work:

* decide which settings are persisted in backend storage versus local browser state
* add settings information architecture and route structure
* replace placeholder page with real settings groups
* implement only the settings that already have meaningful runtime effect first

Primary source docs:

* `docs/02_ux/information-architecture.md`
* `docs/02_ux/screen-blueprint-pack.md`

### 4.5 P2: AI tools area

Current state:

* AI helper workflows exist, but they are not organized as a dedicated routed AI tools area
* there is no `AI Tools` route or navigation entry

Missing target-state items:

* `/ai`
* `/ai/normalize`
* `/ai/rewrite`
* `/ai/suggest-metadata`
* `/ai/pantry`

Likely implementation work:

* decide which prompt-backed flows are mature enough to expose first
* add AI tools landing page and route group
* define shared job/result/review UI patterns
* align route rollout with actually implemented backend prompt consumers

Retrieval note:

* deterministic ingredient-first retrieval and inspiration are already owned by Session 39
* AI-assisted pantry and similar-recipe work belongs to a separate AI-assisted retrieval track and should not be conflated with the deterministic Session 39 slice

Primary source docs:

* `docs/02_ux/information-architecture.md`
* `docs/02_ux/screen-blueprint-pack.md`
* `docs/02_ux/component-inventory.md`

### 4.6 P3: Storage-guidance surfaces

Current state:

* storage-related metadata exists, but there is no first-class storage-guidance module in the UX
* archive and pantry flows do not yet surface use-soon or caution modules as a coherent product layer

New target-state proposal:

* storage-guidance surfaces tied to recipe detail and pantry workflows
* advisory use-soon / caution modules
* leftovers and preservation-oriented retrieval framing

Likely implementation work:

* define where storage guidance belongs in recipe detail and ingredient-first retrieval
* extract advisory card and metadata-rail patterns rather than inventing a separate sub-app
* keep guidance explicitly advisory and archive-connected

Planning note:

* these surfaces are not yet owned by an existing implementation session and should remain proposal-level until a dedicated plan or session exists

Primary source docs:

* `docs/02_ux/information-architecture.md`
* `docs/02_ux/component-inventory.md`

### 4.7 P3: Shell and navigation refinement

Current state:

* shell is side navigation plus main content pane
* navigation includes Library, Intake, and Settings only
* there is no breadcrumb or context-trail pattern

Missing target-state items:

* richer top-level navigation model
* route-context headers and context trails
* possible top search/action zone
* possible right-side context pane
* stronger shell variants for intake and detail states

Likely implementation work:

* revisit shell layout after route expansion lands
* avoid adding shell complexity before the missing routes exist
* extract reusable section/context framing components

Primary source docs:

* `docs/02_ux/component-inventory.md`
* `docs/02_ux/screen-blueprint-pack.md`

### 4.8 P3: Component-system completion

Current state:

* real components exist for library, recipe detail, kitchen mode, shell, and parts of intake
* broader component families from the UX docs are not yet represented in the codebase

Missing target-state items:

* AI interaction components
* dedicated intake review components
* breadcrumb/context components
* nested settings group components
* richer feedback and overlay patterns

Likely implementation work:

* defer component-system expansion until routes and workflows needing them are real
* extract shared components from implemented flows instead of prebuilding empty abstractions

Primary source docs:

* `docs/02_ux/component-inventory.md`

---

## 5. Recommended implementation order

### Phase 1

Build the missing route-bearing surfaces that complete the current archive and intake model:

* library sub-routes
* recipe edit
* URL intake
* file intake
* intake review route

### Phase 2

Build the functional support areas that become credible once the core routes exist:

* settings
* first AI tools surfaces

### Phase 3

Refine the shell, navigation model, and component system after the real route map is in place.

This sequencing reduces speculative UI work and keeps the component layer grounded in actual product surfaces.

---

## 6. Suggested session-prompt alignment

The current implementation prompts should map approximately like this:

* `session-13-search-domain-and-library-search.md`
  * library expansion and search-oriented route work
* `session-14-ai-review-and-prompt-family-adoption.md`
  * intake review expansion and AI tools rollout
* a future settings-focused session prompt
  * settings landing and sub-pages
* a future recipe-editing session prompt
  * recipe edit route and shared form reuse
* `session-15-dev-test-and-ops-scaffolding.md`
  * supporting tests and ergonomics for the expanded route set

---

## 7. Contributor rule

When implementing against the UX docs:

* treat `implemented-routes-and-flows.md` as the current-state truth
* treat the other `docs/02_ux/` files as target-state guidance
* move backlog items from this document into implemented-route docs only when the route, page, and behavior actually ship
