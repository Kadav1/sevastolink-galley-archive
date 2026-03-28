# Sevastolink Galley Archive

## LM Studio Integration Spec v1.0

---

Current implementation note:

* LM Studio integration is real and used by multiple backend AI workflows today
* not every AI workflow described across the `05_ai` docs is fully surfaced in the routed product yet
* use [implemented-ai.md](./implemented-ai.md) for the current AI baseline
* use [implementation-backlog.md](./implementation-backlog.md) for the prioritized AI gap list

## 1. Purpose

This document defines how LM Studio integrates into Sevastolink Galley Archive as the local optional AI backend.

It establishes:

* the concrete responsibilities of the LM Studio integration
* the connection and configuration model
* how model roles are assigned
* how request and response handling works
* how structured outputs enter the normalization pipeline
* how degraded mode behaves when LM Studio is unavailable
* what is in scope for v1 and what is deferred

This document is subordinate to the archive-first product direction already established in the core foundations. It does not redefine AI's role. It specifies how the chosen local AI runtime is wired into the product.

---

## 2. Integration philosophy

### Established facts

* LM Studio is optional. The archive must remain fully usable without it.
* AI output is suggestion-only until a human reviews and accepts it.
* Raw source, structured candidate, and approved recipe are distinct product states and distinct data layers.
* Trust and verification state remain user-controlled.
* AI interactions are user-initiated. No background AI mutation is allowed.

### Integration standard

LM Studio should be treated as a local inference service, not as an application brain.

The product's AI integration must therefore:

* call LM Studio only for bounded tasks with explicit inputs and outputs
* prefer structured JSON over prose wherever reviewable fields are expected
* isolate LM Studio responses behind application-owned validation and normalization
* persist AI work as job output or staged suggestions, never as approved archive truth
* fail cleanly back to manual workflows without breaking intake, editing, browsing, or retrieval

The archive remains the system of record. LM Studio is a replaceable execution layer for local inference.

---

## 3. Why LM Studio is the chosen local AI layer

### Established facts

The product is local-first and must not require cloud AI services for core functionality.

### Rationale

LM Studio is the preferred local AI layer because it satisfies the product's operational constraints:

* it runs locally on the user's machine
* it exposes local HTTP APIs, which fit the product's architecture direction
* it allows user-selected local models rather than bundling a fixed model
* it supports OpenAI-compatible endpoints, which reduces application-specific coupling
* it supports structured output and embeddings workflows without introducing a cloud dependency

### Selection consequence

The application should integrate with LM Studio through its local HTTP API surface, using stable endpoint contracts rather than app automation, UI scripting, or shell-driven inference.

This keeps the integration:

* testable
* replaceable
* implementation-aware
* consistent with the product's archive-first posture

---

## 4. High-level architecture

### Integration components

The application should implement LM Studio through four explicit layers:

1. `AI Settings Store`
2. `AI Orchestrator`
3. `LM Studio Client`
4. `AI Result Validator / Mapper`

### Responsibilities

#### 4.1 AI Settings Store

Owns:

* endpoint base URL
* enabled / disabled state
* timeout and retry policy
* model role mapping
* optional authentication token if the user enables one
* fallback preferences

This is product configuration, not prompt logic.

#### 4.2 AI Orchestrator

Owns:

* accepting user-triggered AI actions
* building task-specific requests
* selecting the correct model role
* recording request lifecycle state
* routing raw responses to validation
* returning staged suggestions to the relevant workflow

This layer must understand product workflows, not transport details.

#### 4.3 LM Studio Client

Owns:

* HTTP communication with LM Studio
* connection tests
* model listing
* request execution
* timeout handling
* transport-level error mapping

This layer must not decide archive behavior.

#### 4.4 AI Result Validator / Mapper

Owns:

* JSON schema validation
* defensive parsing
* taxonomy normalization against allowed vocabularies
* conversion from model output into candidate recipe fields or suggestion sets
* rejection of malformed or provenance-inventing output

This layer protects the archive from weak model responses.

### Data boundary

LM Studio never writes directly to recipe records.

AI output may only enter the application as:

* a staged normalization candidate
* a staged metadata suggestion set
* a staged rewrite proposal
* a staged similarity or retrieval assistance result
* an error or partial result state

Approved recipe records are written only by the application after explicit human action.

---

## 5. Connection model

### Established facts

* LM Studio runs locally.
* The product uses local HTTP-based integration.
* The app must not assume AI is always available.

### Connection standard

The default integration target should be the standard local LM Studio server base URL:

`http://127.0.0.1:1234/v1`

The application must allow the user to change this base URL in settings. The default is a convenience, not a hardcoded dependency.

### Endpoint usage

The integration should use the OpenAI-compatible LM Studio endpoints for application requests:

* `GET /models` for model availability checks
* `POST /chat/completions` for structured normalization, enrichment, and rewrite tasks
* `POST /embeddings` only when semantic retrieval is explicitly enabled in a later phase

Because the configured base URL already includes `/v1`, the concrete local requests are typically:

* `GET http://127.0.0.1:1234/v1/models`
* `POST http://127.0.0.1:1234/v1/chat/completions`
* `POST http://127.0.0.1:1234/v1/embeddings`

### Health checks

The app should support two connection checks:

* `Configuration check`: base URL present, AI enabled, at least one model role mapped
* `Runtime check`: LM Studio reachable and the configured model identifier appears in the model list or otherwise responds successfully to a test request

### State model

The connection state must map into the established UI states:

* `not_configured`
* `connecting`
* `connected`
* `disconnected`
* `error`

These states are surfaced in `/settings/ai` and in intake contexts where AI actions are available.

---

## 6. Configuration model

### Required settings

The product should persist the following AI configuration fields:

* `ai_enabled`: boolean
* `provider_type`: fixed to `lm_studio` in v1
* `base_url`: string
* `auth_mode`: `none` or `bearer_token`
* `bearer_token_ref`: secure reference, nullable
* `request_timeout_ms`: integer
* `max_retries`: integer
* `normalization_model`: string, nullable
* `metadata_model`: string, nullable
* `rewrite_model`: string, nullable
* `embedding_model`: string, nullable
* `fallback_to_manual`: boolean

### Configuration rules

* `ai_enabled = false` must disable AI actions without affecting non-AI workflows.
* Missing model assignments must disable only the dependent AI task, not all AI features.
* Credentials are not required for default local use.
* If the user configures authentication, the token must be stored securely and never in plaintext project config files.

### Recommended defaults

These are recommendations, not established product facts:

* `base_url = http://127.0.0.1:1234/v1`
* `auth_mode = none`
* `request_timeout_ms = 45000`
* `max_retries = 0` for generation requests
* `fallback_to_manual = true`

Generation should favor predictability over retry loops. A failed request should usually return control to the user quickly.

---

## 7. Model responsibility split

### Established direction

The information architecture already anticipates model role mapping in settings.

### Integration standard

The application should assign models by responsibility, not by a single global "AI model" field.

#### 7.1 Normalization model

Used for:

* paste-text normalization
* later URL-to-structured candidate normalization
* later OCR text-to-structured candidate normalization

Required characteristics:

* reliable JSON output
* instruction following
* tolerance for messy source text
* adequate context length for long recipes

#### 7.2 Metadata model

Used for:

* taxonomy suggestions
* ingredient family suggestions
* cuisine and technique classification
* note or context enrichment proposals

Required characteristics:

* strong classification consistency
* lower hallucination tendency
* stable short-form structured output

#### 7.3 Rewrite model

Used for:

* archive-format rewrites
* concise step cleanup
* note condensation
* readability-oriented restructuring that does not invent facts

Required characteristics:

* good transformation quality
* high obedience to "preserve meaning, preserve evidence" rules

#### 7.4 Embedding model

Used for:

* semantic similarity
* concept-level recipe retrieval
* related recipe suggestions

Required characteristics:

* embeddings endpoint support
* stable dimensionality for local index storage

### Role-mapping rule

If only one model is configured, it may serve multiple roles. The role abstraction still must remain in the settings and code so that v2 can split tasks without a migration of the entire AI layer.

---

## 8. Request/response flow

### Standard flow

Every LM Studio request should pass through the same lifecycle:

1. User initiates an AI action.
2. The application verifies AI is enabled and the required model role is configured.
3. The AI Orchestrator creates an `ai_job` record with task type, source record reference, request state, and timestamps.
4. The Orchestrator fetches the exact workflow input snapshot.
5. The Orchestrator builds a task-specific request contract.
6. The LM Studio Client sends the request to the configured endpoint.
7. The raw response is stored as transport output for debugging, subject to local retention policy.
8. The Validator parses and validates the response.
9. The Mapper converts valid output into staged candidate data or suggestion records.
10. The workflow UI renders the result in a reviewable AI panel.
11. The user accepts, edits, or rejects some or all suggestions.
12. Only accepted content is promoted into candidate or recipe persistence writes.

### Request record requirements

Each AI job should record at minimum:

* `id`
* `task_type`
* `source_entity_type`
* `source_entity_id`
* `input_snapshot_ref`
* `model_role`
* `model_id`
* `request_state`
* `error_code`
* `started_at`
* `completed_at`

### Response handling rule

A successful HTTP response is not a successful archive result.

The result becomes usable only after:

* schema validation passes
* taxonomy values are normalized against allowed vocabularies
* prohibited fabrications are not detected
* the output can be rendered as staged review data

---

## 9. Structured output strategy

### Established facts

Structured outputs are preferred over freeform prose where possible.

### Integration standard

For any workflow that proposes fields for archive data, the application should require schema-constrained JSON output.

That includes:

* normalization
* metadata enrichment
* similarity explanation metadata
* field rewrite proposals when the result maps into specific fields

### Schema rule

The application owns the schema. The model must conform to the product's schema, not the other way around.

The schema should:

* use explicit nullable fields
* require arrays where arrays are expected
* forbid silent extra top-level fields where practical
* distinguish extracted facts from inferred suggestions where needed

### Validation rule

The application must validate model output before it reaches UI review.

Validation stages should be:

1. transport-level JSON parse
2. schema validation
3. field-shape normalization
4. taxonomy vocabulary normalization
5. provenance safety checks

### Freeform exception

Freeform prose is acceptable only when the output is explicitly displayed as commentary rather than structured recipe data, for example:

* an optional explanation of why a recipe appears similar
* a non-binding note in a rewrite preview

Even then, the prose must remain visually subordinate to structured results.

---

## 10. Normalization workflow integration

### Established facts

v1 AI scope includes paste-text normalization with field-level review.

### Workflow standard

Normalization is the primary LM Studio workflow in v1.

#### Input

The normalization request should include:

* intake job identifier
* raw source text snapshot
* intake type
* allowed taxonomy vocabularies relevant to v1
* explicit JSON schema
* instructions to preserve uncertainty rather than invent values

#### Output

The normalization response should map into a structured candidate record containing:

* title
* ingredients
* steps
* prep_time_minutes
* cook_time_minutes
* total_time_minutes
* servings
* dish role
* primary_cuisine
* secondary_cuisines
* technique family
* ingredient_families
* notes
* source credit
* ambiguities

#### Integration rule

The normalization result is stored as `structured_candidate` data linked to the intake job. It does not overwrite:

* the raw source
* the extracted source text
* any existing approved recipe

#### Review rule

The intake review UI must support:

* per-field accept
* edit before accept
* reject
* reject all and continue manually
* save partial progress

#### Taxonomy rule

If the model returns a taxonomy value outside the approved vocabulary, the application should:

* attempt deterministic normalization to a known allowed value
* otherwise mark the field as unresolved suggestion
* never silently create a new canonical taxonomy value in v1

---

## 11. Metadata enrichment workflow integration

### Established facts

Metadata enrichment is architecturally anticipated but out of scope for v1 execution.

### Integration standard

When implemented, metadata enrichment should run only on explicit user request from an existing recipe or candidate record.

#### Input

The enrichment request should include:

* current structured recipe snapshot
* selected fields to enrich
* allowed taxonomy vocabularies
* source context if available
* instructions not to alter trust state or provenance fields

#### Output

The response should return only the requested fields plus optional confidence notes for internal review rendering.

Typical outputs:

* dish role suggestion
* cuisine suggestion
* secondary cuisine suggestions
* technique family suggestion
* ingredient family suggestions
* complexity suggestion
* contextual notes suggestion

#### Integration rule

Enrichment output must render as a suggestion overlay or side panel against the existing approved record. It must never replace visible approved values by default.

#### Persistence rule

Accepted enrichments should write as standard recipe field updates with suggestion provenance logged locally. Rejected suggestions should remain discardable without changing the recipe.

---

## 12. Rewrite workflow integration

### Established facts

Rewrite behaviors are allowed only as proposals. They must not invent facts or overwrite trusted content automatically.

### Integration standard

Rewrite is a transformation task, not a truth-generation task.

It should be limited to explicit user-triggered operations such as:

* rewrite steps into archive house style
* condense notes
* clarify instruction phrasing
* convert a loose ingredient list into archive formatting while preserving stated quantities

#### Input

The rewrite request should include:

* source fields to transform
* target field structure
* preserve-meaning instruction
* do-not-invent instruction
* original source excerpt when relevant for grounding

#### Output

The response should return only rewritten field candidates for the targeted fields.

#### Integration rule

Rewrite proposals must appear as before-and-after review rows or equivalent field-diff UI. The user must be able to:

* accept rewritten text
* edit rewritten text
* keep the original text

#### Prohibition

Rewrite must not:

* alter trust state
* fabricate missing amounts, timings, or provenance
* silently restyle the entire recipe in the background

---

## 13. Similarity / retrieval workflow integration

### Established facts

AI-assisted retrieval is anticipated by the IA and AI specs but is not required for core archive search.

### Integration standard

Search remains hybrid and archive-first:

* deterministic field and taxonomy retrieval remains the baseline
* AI-assisted similarity is a secondary enhancement
* if AI retrieval fails, the system falls back to standard search

### Retrieval modes

#### 13.1 Query interpretation

A generation model may translate a natural-language query into structured search hints, such as:

* likely dish role
* cuisine
* ingredient families
* technique family

These hints should feed the existing retrieval system rather than bypass it.

#### 13.2 Embedding similarity

When an embedding model is configured, the application may generate and store embeddings for:

* approved recipes
* optionally structured candidates in later phases

The local index should remain local-only and rebuildable from archive data.

#### 13.3 Similar recipe panels

Similarity results shown on recipe detail pages should be derived from:

* deterministic overlap first
* embeddings second where available
* optional model-generated explanation text last

### Integration rule

Similarity and retrieval must not create a separate AI-only content layer. They should strengthen retrieval of the canonical archive.

---

## 14. Error handling and degraded mode behavior

### Established facts

The app must remain fully usable if LM Studio is unavailable.

### Integration standard

Every LM Studio failure must resolve into one of three outcomes:

* manual continuation
* partial reviewable output
* retryable transient failure

Never a blocked archive workflow.

### Error classes

#### 14.1 Not configured

Behavior:

* show `AI Not Configured`
* disable AI actions
* keep manual workflow fully available

#### 14.2 Connection failure

Behavior:

* show `AI normalization unavailable. Continue manually.`
* preserve all user input
* keep the intake or edit session open

#### 14.3 Timeout

Behavior:

* mark request as failed
* allow one explicit retry
* do not spin indefinitely or auto-retry repeatedly

#### 14.4 Malformed response

Behavior:

* preserve raw response for local debugging if logging is enabled
* show a clean inline failure message
* do not present invalid structured fields as suggestions

#### 14.5 Partial response

Behavior:

* surface valid fields only
* mark missing fields clearly
* allow manual completion

#### 14.6 Model missing or unloaded

Behavior:

* show task-specific configuration error
* guide the user back to `/settings/ai`
* do not disable unrelated non-AI features

### Degraded mode principle

The degraded mode experience should feel complete, not apologetic. The product still functions as the archive and cooking workspace even when AI is absent.

---

## 15. Logging and observability recommendations

### Established facts

No external telemetry is required or appropriate by default.

### Recommendations

Observability should be local-only in v1.

The application should log the following locally for AI jobs:

* task type
* request start and end times
* configured model identifier
* connection target host and port
* request outcome
* parse and validation failures
* acceptance or rejection summary counts

### Sensitive logging rules

* Raw recipe content should not be logged by default at info level.
* Full prompts and full responses should be stored only in an explicitly enabled debug mode.
* Debug logs must remain on the local machine.
* Logs must never be shipped to remote analytics services by default.

### Recommended local diagnostics surfaces

* AI settings connection test result
* last successful model list fetch time
* recent AI job history with status
* last error code and message

This is sufficient for local troubleshooting without turning the product into an AI developer console.

---

## 16. Security/privacy notes

### Established facts

* Local processing is the default.
* No data leaves the machine by default.
* API keys are not required for local LM Studio use.

### Integration standard

The LM Studio integration must preserve those guarantees at the implementation layer.

#### 16.1 Local by default

The default endpoint must target loopback or localhost. The UI should make it obvious when the configured endpoint is non-local.

#### 16.2 Explicit remote override only

If the user points the app at a non-local endpoint in a future expansion, the product must require explicit confirmation because the privacy posture changes.

#### 16.3 Credential handling

If bearer-token auth is supported, the token must be stored securely using an OS-appropriate secret store where available, not plaintext files.

#### 16.4 Training prohibition

The product must not send archive data to any remote training or telemetry system.

#### 16.5 File and source preservation

AI processing must never destroy:

* raw pasted source
* fetched source text
* uploaded source files
* provenance references

These remain archive evidence regardless of AI output quality.

---

## 17. v1 integration scope

### In scope

* LM Studio enable / disable setting
* user-configured local HTTP base URL
* connection test and status display
* model listing via local API
* model role mapping in settings, even if one model fills multiple roles
* paste-text normalization using structured JSON output
* field-level review of normalization results
* inline error handling and manual fallback
* local-only AI job status tracking

### Explicitly out of scope for v1 execution

* automatic background enrichment
* URL-content AI analysis
* OCR and vision extraction
* semantic retrieval backed by embeddings
* related-recipe panels generated from embeddings
* multi-provider abstraction beyond LM Studio
* chat-first archive interaction
* automatic taxonomy creation from model output

### v1 implementation boundary

v1 should build the orchestration and validation layers once, then use them for normalization first. The integration should not be broadened into multiple unfinished AI features.

---

## 18. v2 expansion options

These are recommendations for later expansion, not v1 commitments.

* URL-import normalization using fetched article text as input
* OCR-to-normalization pipeline for file intake
* metadata enrichment panel on recipe detail
* rewrite actions for steps, notes, and archive format cleanup
* embedding-backed semantic search and related recipe suggestions
* re-normalization of old candidate records with diff review
* per-field suggestion provenance history
* task-specific model quality diagnostics
* support for LM Studio native API features if a clear product need appears

### Expansion rule

Any v2 addition must still preserve:

* explicit user initiation
* staged review
* raw-source preservation
* trust-state separation
* full manual fallback

---

## 19. Anti-patterns

The following integration patterns are prohibited.

### 19.1 Direct recipe writes from LM Studio responses

LM Studio output must never be written straight into approved recipe records.

### 19.2 Single opaque "AI layer"

The application must not hide normalization, enrichment, rewrite, and retrieval behind an undefined generic AI service with no task boundaries.

### 19.3 Prompt-only validation

Prompt wording is not sufficient validation. Schema checks and application-side normalization are mandatory.

### 19.4 Blocking UI on AI availability

Recipe intake, editing, browsing, and cooking must not depend on a successful LM Studio connection.

### 19.5 Taxonomy drift through freeform labels

Model output must not silently create new cuisines, dish roles, or technique families.

### 19.6 Silent retries with hidden state changes

The app must not keep resubmitting requests in the background while the user believes nothing is happening.

### 19.7 Treating prose as structured truth

A paragraph returned by a model is not a recipe record. If the app needs fields, it must request fields.

### 19.8 Coupling the product to one specific model family

The integration should target role capabilities and API contracts, not a single hardcoded model brand or checkpoint.

### 19.9 Making LM Studio installation status a product gate

The app should work as a complete archive even when LM Studio is not installed.

---

## 20. Final integration standard

LM Studio is the local optional inference runtime for Sevastolink Galley Archive.

Its role is narrow and concrete:

* accept bounded local HTTP requests
* return structured or reviewable suggestions
* support archive maintenance tasks without owning the archive

The application owns:

* workflow control
* validation
* taxonomy integrity
* trust state
* final persistence

If an LM Studio integration decision makes AI feel foundational, hides provenance, weakens review, or blurs the line between source, candidate, and approved recipe, that decision is out of standard.

---

## Decisions made

1. LM Studio is confirmed as the local optional AI backend for Sevastolink Galley Archive.
2. The integration uses local HTTP with a user-configured base URL, defaulting to the standard local LM Studio server address.
3. The application integrates through explicit layers: settings store, orchestrator, LM Studio client, and validator/mapper.
4. Structured JSON is the default response mode for any workflow that proposes archive fields.
5. Model assignment is role-based: normalization, metadata, rewrite, and embeddings.
6. LM Studio output is always staged for review and never written directly to approved recipes.
7. v1 scope is limited to local configuration, connection status, model selection, and paste-text normalization with review.
8. Retrieval, enrichment, rewrite expansion, and embeddings are deferred to later phases.

## Open questions

1. Should the app recommend one baseline normalization model profile in `/settings/ai`, or remain fully model-agnostic in the UI?
2. Should `ai_job` raw request and response payload retention be off by default, or kept for a short local debugging window?
3. When metadata enrichment ships, should confidence indicators be shown to the user or kept as internal diagnostics only?
4. For v2 retrieval, should embeddings be generated only for approved recipes, or also for structured candidates awaiting review?

## Deliverables created

1. `/docs/05_ai/lm-studio-integration.md`

## What document should be created next

`docs/09_ops/local-deployment.md`

This document should define how the local application service and optional LM Studio backend are run, configured, and connected in local-first deployment.
