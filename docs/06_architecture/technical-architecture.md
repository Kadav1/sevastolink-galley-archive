# Sevastolink Galley Archive

## Technical Architecture Spec v1.0

---

## 1. Purpose

This document defines the technical architecture for Sevastolink Galley Archive.

It establishes:

* the recommended v1 stack
* the application architecture across frontend, backend, data, and media storage
* how search, intake, and AI fit into the system
* how local-first behavior is preserved
* how configuration, logging, backup, and restore should work
* what is in scope for v1 and what is deferred

This is the canonical target-state architecture reference for the product.

Current implementation note:

* the repository already implements the recommended core stack in broad terms
* the repository does not yet fully realize every target-state backend domain and layering boundary described here
* use `docs/06_architecture/implemented-architecture.md` for the current implementation baseline
* use `docs/06_architecture/implementation-backlog.md` for the prioritized target-state gap list

---

## Current-state gap note

Implemented today:

* React, Vite, React Router, and TanStack Query frontend stack
* FastAPI, Pydantic, SQLAlchemy, and SQLite backend stack
* SQLite FTS5 search
* local filesystem persistence under `data/`
* optional LM Studio integration
* compose-based local stack and shell-based backup workflows

Not yet fully implemented today:

* separate mounted backend domains for search, media, settings, backup, and system
* fully separated repository/data-access layer
* functional settings workflows
* real media-management surfaces
* richer dev, migrate, and seed helper tooling

The remainder of this document should therefore be read as target-state architecture guidance rather than as a complete description of the current runtime implementation.

---

## 2. Architecture philosophy

### Established facts

* The product is local-first.
* It is home-use focused.
* It is archive-first, not chat-first.
* AI is optional and assistive.
* Raw source, structured candidate, and approved recipe must remain distinct.
* Trust and verification state must remain explicit and user-controlled.

### Architecture standard

The architecture should optimize for:

* long-term local durability
* low operational complexity for one builder
* clear boundaries between archive data, intake jobs, and AI suggestions
* fast local retrieval
* graceful operation when optional services are absent

This means v1 should prefer:

* one local app shell
* one local API service
* one local database
* filesystem-based media storage
* deterministic search before semantic search
* optional AI through a user-configured local HTTP integration

### Design principle

The architecture should behave like a durable personal archive system, not a distributed platform.

That excludes early investment in:

* microservices
* remote-first sync infrastructure
* event buses
* cloud-only search layers
* AI-centric orchestration

---

## 3. Recommended stack

### Recommendation

The recommended v1 stack is:

* Frontend: React + TypeScript + Vite
* Styling/UI: CSS variables with a small in-repo design system layer
* Router: React Router
* State/query layer: TanStack Query plus local UI state via React state or a light store
* Backend: FastAPI
* API schema layer: Pydantic models
* Database: SQLite
* ORM / query layer: SQLAlchemy or SQLModel
* Search: SQLite FTS5 plus deterministic facet filtering
* Media storage: local filesystem under an application-owned data directory
* AI runtime integration: LM Studio via local HTTP
* Packaging/deployment: local development server first; later single-machine packaged deployment

### Alternative backend

Express is viable, but FastAPI is the stronger recommendation for v1 because:

* schema definition is clearer
* request and response validation is stronger by default
* typed internal contracts align well with the structured archive model
* local service complexity remains low

This is a recommendation, not an established fact.

---

## 4. Why the stack fits the product

### Frontend fit

React + TypeScript + Vite fits the product because:

* the UI has multiple structured surfaces: library, recipe detail, intake, review, settings
* the design system benefits from component composition
* the intake and review flows require precise state handling
* local development remains fast

### Backend fit

FastAPI fits the product because:

* the archive requires explicit structured APIs
* intake jobs, AI jobs, and recipe review operations map cleanly to typed endpoints
* schema validation reduces drift between UI and storage models

### Database fit

SQLite fits v1 because:

* it is local-first by default
* it is operationally simple for home use
* it supports transactional integrity for recipe, intake, and AI job records
* it supports FTS5 for local full-text search

### Architecture fit

This stack keeps the product:

* maintainable by one builder
* usable without network connectivity
* easy to back up
* easy to reason about
* aligned with the archive-first product model

---

## 5. Frontend architecture

### Application shell

The frontend should be a route-based single-page application with a stable shell around the major product zones:

* Library
* Intake
* AI Tools
* Settings

Recipe detail and Kitchen Mode should behave as focused route states within the same application.

### Frontend module boundaries

The frontend should be organized around the established product structure:

* `library`
* `recipe`
* `kitchen`
* `intake`
* `ai`
* `settings`
* `shared-ui`
* `shared-data`

### State model

The frontend should separate:

* server state
* local draft state
* ephemeral UI state

Recommended handling:

* server state via query/mutation layer
* intake review edits via local draft state
* shell controls, open panels, and view preferences via local UI state

### Review architecture

The review surfaces must preserve the distinction between:

* raw source
* extracted or normalized candidate
* approved recipe fields

That means the frontend should render separate view models for:

* intake source snapshot
* AI suggestion set
* editable candidate record
* approved recipe record

The UI should not flatten these into one generic form object.

### Frontend API boundary

The frontend should not:

* talk directly to SQLite
* talk directly to LM Studio
* own schema normalization rules

Those responsibilities belong in the backend.

---

## 6. Backend architecture

### Service model

The backend should be a single local application service with modular internal domains.

Recommended domain modules:

* `recipes`
* `taxonomy`
* `intake`
* `search`
* `media`
* `ai`
* `settings`
* `backup`

### Internal architecture

The backend should use a layered structure:

* API layer
* service layer
* repository/data-access layer
* infrastructure layer

### API layer responsibilities

* validate request payloads
* map route input to service calls
* return stable response shapes

### Service layer responsibilities

* enforce archive rules
* handle workflow orchestration
* preserve trust and provenance constraints
* coordinate AI and import operations

### Repository/data-access responsibilities

* database reads and writes
* transaction handling
* search index synchronization

### Infrastructure responsibilities

* filesystem access
* LM Studio client
* backup and restore I/O
* local configuration loading

### Background work

v1 should keep background processing minimal.

Acceptable v1 background work:

* import extraction jobs
* AI normalization jobs
* thumbnail generation if later needed

This can be implemented with an in-process task runner and persisted job records rather than a separate queue system.

---

## 7. Data/storage architecture

### Primary persistence model

SQLite is the primary source of truth for structured application data.

The database should store:

* recipes
* recipe field data
* intake jobs
* structured candidates
* AI job records
* taxonomy values or controlled vocabularies
* application settings
* review and status metadata

### Core entity separation

The storage model must keep distinct entities for:

* `source asset or source snapshot`
* `intake_job`
* `structured_candidate`
* `recipe`
* `ai_job`

This is an established architectural requirement derived from the trust model.

### Suggested v1 database tables

At minimum, v1 should include tables equivalent to:

* `schema_migrations`
* `recipes`
* `recipe_ingredients`
* `recipe_steps`
* `recipe_notes`
* `recipe_sources`
* `intake_jobs`
* `structured_candidates`
* `ai_jobs`
* `media_assets`
* `settings`
* `recipe_search_fts`

### Field modeling rules

Structured fields should remain first-class columns where retrieval matters:

* title
* slug
* dish role
* primary cuisine
* technique family
* verification state
* favorite
* timing fields

Lists should be stored according to the canonical schema split:

* ingredients and steps use dedicated relational tables
* multi-select taxonomy fields use JSON arrays in the recipe row for v1
* multi-select filtering uses SQLite JSON functions such as `json_each()` where needed

### JSON usage rule

JSON columns are acceptable for:

* staged AI output snapshots
* raw normalized payloads
* contract debug payloads
* optional auxiliary metadata

JSON should not replace the core archive schema in v1.

### Migration strategy

The backend should own database migrations from the start, even for SQLite. The schema should not be managed manually once development begins.

---

## 8. Media storage architecture

### Media storage standard

All media and source assets should be stored on the local filesystem, not inside the SQLite database as large blobs.

Examples:

* uploaded images
* PDFs
* extracted source snapshots
* later thumbnails

### Media directory model

The application should use an app-owned data root with subdirectories such as:

* `media/originals`
* `media/derived`
* `imports/raw`
* `backups`
* `logs`

### Database linkage

The database should store metadata and references for media assets:

* asset id
* local relative path
* mime type
* source association
* checksum
* created timestamp

### Preservation rule

Original source assets must be preserved even if extraction or normalization fails.

The architecture must never treat derived text or AI output as a substitute for original source evidence.

---

## 9. Search architecture for v1

### Established facts

The archive must support retrieval by:

* title
* ingredient
* cuisine
* dish role
* time
* complexity
* status
* tags and facets

### v1 search standard

v1 search should be deterministic and local.

Recommended components:

* SQLite FTS5 for title, notes, and source text search
* normalized fields for direct filtering
* `ingredient_text` as a denormalized recipe column maintained by the application
* JSON-array filtering for multi-select taxonomy facets via SQLite JSON functions

### Search layers

#### 9.1 Direct text search

Use FTS for:

* title
* short description
* notes
* source notes
* optionally raw source text excerpts

#### 9.2 Faceted filtering

Use standard SQL filters for:

* verification state
* favorite
* dish role
* cuisine
* technique family
* time class or derived time ranges
* ingredient families

#### 9.3 Ingredient lookup

Ingredient search should use normalized ingredient names or ingredient tokens separate from raw display strings.

#### 9.4 Semantic search

Semantic search is deferred. The architecture should allow later addition of embeddings without making them part of v1 retrieval correctness.

### Search result rule

The search system must still provide useful results when AI is disabled or LM Studio is unavailable.

---

## 10. AI integration architecture

### Established facts

* AI is optional.
* LM Studio is the local optional inference backend.
* AI output must remain staged and reviewable.
* The app must not depend on AI for core archive use.

### Architecture standard

The backend should own AI orchestration through a dedicated `ai` domain with four internal responsibilities:

* settings and model-role resolution
* AI job creation and state tracking
* LM Studio HTTP communication
* result validation and mapping

### AI boundary

The frontend should call application API endpoints such as:

* `POST /api/intake/:id/normalize`
* `POST /api/recipes/:id/metadata-suggestions`
* `POST /api/recipes/:id/rewrite`
* `POST /api/search/query-interpretation`

The backend then decides:

* whether AI is enabled
* whether the required model role is configured
* how to build the prompt contract
* how to validate the response

### Persistence rule

AI output should be stored as:

* `ai_job` records
* raw response snapshots where configured
* validated staged suggestion payloads

AI output must not be written straight into approved recipe records.

### Degraded mode rule

If LM Studio is unavailable:

* AI routes return workflow-level failure states
* intake and recipe editing remain usable
* search falls back to deterministic behavior only

---

## 11. Import pipeline architecture

### Established facts

The intake flow moves through:

* capture
* parse / structure
* review
* approve
* refine later

### Pipeline standard

The backend should model import as explicit pipeline stages attached to an `intake_job`.

### Stage model

#### 11.1 Capture stage

Persists:

* intake type
* raw source or source reference
* initial status
* timestamps

#### 11.2 Extraction stage

Creates:

* extracted text from URL fetch or file processing
* source metadata
* extraction errors where present

For manual and paste-text intake, this stage may be trivial.

#### 11.3 Normalization stage

Creates:

* structured candidate fields
* AI or deterministic parse metadata
* partial-result state if incomplete

#### 11.4 Review stage

Supports:

* user edits to the structured candidate
* field-level acceptance and rejection
* save and resume

#### 11.5 Approval stage

Creates or updates:

* the final recipe record
* source linkage
* trust state chosen by the user

### Import rule

The import pipeline must be resumable. A failed or incomplete intake must remain recoverable without losing source material or partial work.

---

## 12. Local network access model

### Architecture assumption

The product is intended for local machine use first, with optional access from the local home network later.

### v1 model

v1 should support:

* localhost access by default
* optional LAN binding through explicit configuration

### Local-only default

By default, the backend should bind to loopback only.

The frontend may be:

* served by the backend in packaged mode
* or run separately in development

### Optional LAN access

If LAN access is enabled later or in advanced local setups:

* binding host must be explicitly configured
* the UI should indicate that the archive is reachable on the local network
* no public internet exposure should be assumed or configured by default

### Security consequence

LAN access is a convenience feature, not a cloud architecture requirement.

---

## 13. Configuration/environment strategy

### Configuration model

The application should separate:

* stable application configuration
* user-editable preferences
* sensitive secrets

### Application configuration

Examples:

* data directory path
* database path
* log level
* server bind host and port
* backup directory

### User preferences

Examples:

* UI density
* kitchen mode preferences
* import defaults
* AI enabled state
* LM Studio endpoint and model mappings

These should be stored in the application database or a local app config layer.

### Sensitive values

Examples:

* optional bearer tokens for non-default AI endpoints

These should use OS-appropriate secure storage where available and should not be written in plaintext config files.

### Environment usage rule

Environment variables are appropriate for development and advanced local overrides. They should not be the primary UX for normal home-use configuration.

---

## 14. Logging/backups/restore direction

### Logging direction

Logging should be local and pragmatic.

v1 should log:

* server startup and shutdown
* import job state transitions
* AI job state transitions
* validation failures
* backup and restore operations
* recoverable filesystem errors

The system should avoid verbose logs of recipe content by default.

### Backup direction

Backup should be first-class because the product is an archive.

v1 backup should capture:

* SQLite database
* media directory
* import/source assets
* application settings

### Restore direction

Restore should support:

* full archive restore onto the same machine
* restore onto a new machine with path remapping where necessary

### Recommendation

Backups should be file-based and human-comprehensible at the directory level. v1 does not need a complex snapshot orchestration system beyond consistent export packaging.

---

## 15. Security model for home-local use

### Established facts

The product is local-first and home-use focused.

### Security standard

The v1 security model should focus on:

* safe local defaults
* preserving user data integrity
* avoiding accidental network exposure
* protecting optional secrets

### Required security behaviors

* bind to localhost by default
* do not transmit archive content externally by default
* preserve source and archive data against AI failures
* validate uploads and imported file types before processing
* sanitize file paths and prevent path traversal in media handling
* store optional credentials securely

### Non-goals for v1

v1 does not need:

* multi-user identity and roles
* enterprise auth
* cloud IAM integration
* zero-trust network design

Those would overcomplicate the product relative to its use case.

---

## 16. v1 architecture boundary

### In scope

* local WebUI
* single local API service
* SQLite-backed archive storage
* filesystem media storage
* deterministic search and faceting
* intake jobs with resumable review flow
* optional LM Studio integration for user-initiated AI workflows
* local settings, backup, and restore support

### Explicitly out of scope

* multi-user collaboration
* cloud-hosted architecture
* real-time sync across devices
* distributed workers
* remote vector databases
* background AI enrichment at scale
* event-driven microservice decomposition

### Boundary rule

v1 should be optimized for solidity and clarity, not breadth.

---

## 17. Deferred architecture concerns

These are anticipated but not required for v1:

* semantic search with local embeddings
* OCR and vision extraction pipeline
* recipe revision history beyond basic update tracking
* local network multi-device access hardening
* optional packaged desktop distribution
* import deduplication heuristics
* richer pantry and inventory models
* later sync or export interoperability layers

These should be designed for later extension, not prematurely built into v1 as full subsystems.

---

## 18. Technical risks

### 18.1 Schema drift between candidate and recipe models

Risk:

The distinction between structured candidate and approved recipe can collapse if both are treated as the same payload shape without explicit workflow rules.

Mitigation:

Keep separate entities and service methods for candidate review versus recipe persistence.

### 18.2 Overuse of JSON blobs

Risk:

Storing too much recipe structure in JSON will weaken search, filtering, and migration clarity.

Mitigation:

Keep core archive fields relational and queryable.

### 18.3 AI response instability

Risk:

LM Studio model output quality may vary across user configurations.

Mitigation:

Keep strong application-side validation and full manual fallback.

### 18.4 Filesystem drift

Risk:

Media paths can become invalid if file handling is inconsistent.

Mitigation:

Use application-owned relative paths, checksums, and controlled import directories.

### 18.5 One-builder operational sprawl

Risk:

Adding too many subsystems early will make the product fragile.

Mitigation:

Keep one service, one database, one search approach, and optional AI.

---

## 19. Anti-patterns

### 19.1 Microservice decomposition in v1

This would increase operational cost without matching product needs.

### 19.2 Cloud-first assumptions

The architecture must not assume hosted databases, hosted search, or hosted AI.

### 19.3 Direct frontend access to AI runtime

The frontend must not call LM Studio directly because validation, configuration, and trust boundaries belong in the application backend.

### 19.4 Treating AI output as canonical storage

AI output is staged suggestion data, not archive truth.

### 19.5 Blob-only recipe storage

The archive must remain queryable and structured.

### 19.6 Overengineering background jobs

v1 does not need a separate queue broker, worker fleet, or job orchestration platform.

### 19.7 Premature sync architecture

Do not design the whole system around future multi-device sync before the local archive model is stable.

### 19.8 Conflating source assets with recipe content

Raw files, extracted text, structured candidates, and approved recipes must stay distinct.

---

## 20. Final architecture standard

Sevastolink Galley Archive should be implemented as a durable local archive application with:

* a typed WebUI
* a single local API service
* SQLite as the core structured store
* filesystem media preservation
* deterministic search
* optional LM Studio integration behind application-controlled validation

The architecture succeeds if it keeps the archive trustworthy, searchable, recoverable, and usable without network dependence or AI dependence.

If a technical choice makes the system more distributed, more opaque, or more AI-dependent than the product requires, that choice is out of standard.

---

## Decisions made

1. v1 uses a local-first WebUI architecture with React, TypeScript, and Vite on the frontend.
2. FastAPI is the recommended backend for the single local application service.
3. SQLite is the primary structured data store for v1.
4. Source files and media are stored on the local filesystem, not as database blobs.
5. Search in v1 is deterministic, using SQLite FTS and structured facet filtering.
6. AI integration is backend-mediated, optional, and built around LM Studio as a local HTTP dependency only when configured.
7. Intake jobs, structured candidates, AI jobs, and approved recipes are separate architectural entities.
8. Local backup and restore are first-class architecture concerns in v1.

## Open questions

1. Should v1 store ingredients in a fully normalized token table from the start, or begin with simpler ingredient rows plus a lightweight search index?
2. Should packaged deployment target a browser-served local app only, or eventually wrap the same stack in a desktop shell?
3. For LAN access, should the product include an explicit read/write warning state when bound beyond localhost?
4. How much revision history should be captured in v1 before a dedicated history system exists?

## Deliverables created

1. `/docs/06_architecture/technical-architecture.md`

## What document should be created next

`docs/09_ops/local-deployment.md`

This document should define how the local-first stack is run, configured, packaged, and optionally exposed on a home local network.
