# Sevastolink Galley Archive

## AI Interaction Spec v1.0

---

## 1. Purpose

This document defines the role of AI in Sevastolink Galley Archive.

It establishes:

* what AI is allowed to do
* what AI must never do
* how AI appears in the UI
* which workflows use AI
* which workflows must never rely on AI
* how trust is preserved when AI is involved
* what happens when AI is unavailable
* what is in scope for v1 and what is deferred

This document governs all AI behavior in the product, including intake, archive enrichment, retrieval assistance, and any future AI-adjacent features.

This document defines the target-state AI interaction model. For the current implemented AI surface and missing AI work, see [implemented-ai.md](./implemented-ai.md) and [implementation-backlog.md](./implementation-backlog.md).

---

## 2. AI Philosophy

Sevastolink Galley Archive is an **archive-first product**. AI is an optional assistive layer, not a product foundation.

The archive must be fully functional without any AI connection. AI improves throughput and reduces manual work, but it does not create trust, define correctness, or gate any core workflow.

### Core principles

#### 2.1 AI serves the archive. The archive does not serve AI.

Every AI feature must reduce the cost of maintaining archive quality. It must never compromise it.

#### 2.2 AI output is always a suggestion

No AI output is treated as truth until a human reviews and accepts it. This applies to every field, every inference, every suggestion.

#### 2.3 AI is optional at every step

If LM Studio is unavailable, misconfigured, or not installed, the product should degrade gracefully. Every intake path and archive workflow must function without AI.

#### 2.4 Transparency over smoothness

It is better to show the user that AI was involved, that uncertainty exists, or that something needs review — than to produce a smooth, polished surface that obscures provenance.

#### 2.5 The archive must never drift silently

AI-assisted changes must be visible and reversible. The system must not allow AI to quietly modify trusted data.

---

## 3. What AI Is Allowed to Do

The following are permitted AI behaviors.

### 3.1 Intake assistance

* Parse unstructured or messy text into structured recipe fields
* Suggest title, ingredients, steps, timings, notes from raw source text
* Suggest taxonomy fields: dish role, cuisine, technique family, complexity, ingredient families
* Clean up source text for human review
* Reformat raw recipe content into the archive field structure

### 3.2 Archive enrichment

* Suggest missing metadata fields on an existing recipe
* Suggest alternative taxonomy labels
* Propose a cuisine or technique tag when one is absent
* Suggest notes or context that the recipe may be missing

### 3.3 Retrieval assistance

* Help formulate search queries from natural language
* Suggest related recipes based on ingredients or technique
* Surface taxonomy connections across the archive

### 3.4 Reprocessing

* Re-run normalization on a previously imported recipe
* Regenerate a single field suggestion on demand
* Offer alternative interpretations of ambiguous ingredients or instructions

All of the above are **proposal behaviors** only. None write directly to approved archive data without explicit human action.

---

## 4. What AI Must Not Do

The following behaviors are explicitly prohibited.

### 4.1 Never silently update a trusted record

AI must not modify a Verified or Approved recipe record without user-initiated review.

### 4.2 Never set verification state

AI must not determine, set, or imply a recipe's trust state. Trust state is set by the user.

### 4.3 Never overwrite raw source

The original raw source — pasted text, extracted URL content, uploaded file — must never be replaced by AI output. The raw source is permanent archive evidence.

### 4.4 Never invent provenance

AI must not fabricate source URLs, author names, publication dates, or attribution details. If a field cannot be extracted from source, it should be blank or marked unknown.

### 4.5 Never present itself as certain

AI output in the UI must always be visually distinguished from confirmed archive data. AI-suggested fields must never appear identical to user-approved fields.

### 4.6 Never block archive operations

If AI is unavailable, the user must still be able to: intake recipes, browse the archive, open recipes, edit, save, and manage all records.

### 4.7 Never be required for v1 core functions

The following must work without AI:

* Manual entry
* Paste text intake (without normalization)
* URL capture (without content analysis)
* Archive browsing
* Recipe detail view
* Kitchen Mode
* Search by field value
* Export

---

## 5. AI User-Facing Workflows

AI surfaces in the product in three contexts.

### 5.1 Intake normalization

The user explicitly requests AI assistance during the intake flow. AI converts raw source into a structured candidate. The user reviews and approves.

### 5.2 Archive enrichment

The user explicitly requests enrichment on an existing recipe. AI suggests missing or alternative fields. The user applies or discards suggestions field by field.

### 5.3 Retrieval assistance

The user interacts with a search or suggestion interface that uses AI to improve results. AI proposes results or query expansions. The user selects what to use.

In all three contexts, the AI interaction is **initiated by the user**, not triggered automatically.

---

## 6. AI-Assisted Intake Workflows

### 6.1 Paste Text → Normalize

**Trigger:** User pastes raw recipe text and clicks Normalize.

**Flow:**

1. User pastes raw text into intake form.
2. User clicks Normalize.
3. System sends text to LM Studio API.
4. LM Studio returns structured JSON candidate.
5. System renders structured candidate in Review panel.
6. AI-generated fields are visually marked (see §11).
7. User reviews field by field.
8. User edits any field.
9. User selects trust state and saves.

**Rules:**

* Raw text is retained and visible at all times.
* If LM Studio is unavailable: show error inline, allow user to continue manually.
* AI-generated candidate is never auto-approved.

---

### 6.2 URL Import → Analyze

**Trigger:** User submits a URL and requests AI content analysis.

**Flow:**

1. System fetches URL content.
2. User reviews fetched raw HTML or text.
3. User requests AI normalization.
4. AI attempts to extract title, ingredients, steps, and metadata.
5. Results appear as a structured candidate.
6. User reviews and approves.

**Rules:**

* URL must be preserved regardless of extraction outcome.
* If extraction is partial, the partial result is presented for review.
* AI must not invent content that was absent from the source page.

---

### 6.3 File Intake → OCR / Extract

**Trigger:** User uploads image or PDF and requests AI extraction.

**Flow:**

1. File is stored locally and linked.
2. OCR or vision model processes the file.
3. Extracted text is shown to user.
4. User optionally requests structured normalization.
5. Structured candidate presented for review.

**Rules:**

* Original file remains linked permanently.
* Extracted text is shown before and after normalization.
* Default trust state for file intake is Draft or Unverified.

---

### 6.4 Manual Entry → Field Suggestions

**Trigger:** User is in manual entry and requests AI assistance on a specific field.

**Flow:**

1. User types partial content into a field.
2. User requests suggestion for that field.
3. AI returns suggestion.
4. Suggestion appears inline, visually marked.
5. User accepts, edits, or discards.

**Rules:**

* This is a field-level operation, not a full normalization.
* Other fields are not changed.
* AI suggestions are not applied automatically.

---

## 7. AI-Assisted Archive Workflows

### 7.1 Enrichment panel

Available on existing recipe records.

The user opens an Enrich panel and requests AI analysis of the current recipe.

AI may suggest:

* missing cuisine label
* missing technique family
* alternative tags
* additional notes
* complexity estimate

All suggestions appear in a staged review. None are applied without explicit user action.

**Rules:**

* Enrichment is never triggered automatically.
* Enrichment suggestions are labeled AI-Suggested until accepted.
* Accepted enrichments record that they were AI-suggested (for transparency in history, if implemented).

---

### 7.2 Re-normalize

The user requests that AI re-process a recipe that was imported with poor normalization.

**Flow:**

1. User opens the recipe.
2. User initiates Re-normalize.
3. System retrieves raw source (if available) or current field content.
4. AI returns new structured candidate.
5. User reviews diff against current approved content.
6. User accepts, discards, or applies field by field.

**Rules:**

* Re-normalize never overwrites approved fields automatically.
* The original approved content is preserved until the user confirms a change.

---

## 8. AI-Assisted Retrieval Workflows

### 8.1 Natural language search

The user types a natural language query into the search bar.

AI may be used to:

* interpret intent
* expand query terms
* map natural language to taxonomy fields
* rank results

**Rules:**

* AI-assisted retrieval is supplementary. Direct field search always works without AI.
* AI must not hide results that match the user's query in favor of AI-selected results.
* If AI is unavailable, search falls back to direct field matching.

---

### 8.2 Related recipe suggestions

On a recipe detail view, AI may suggest related recipes based on shared ingredients, technique, or cuisine.

**Rules:**

* Suggestions are clearly labeled as related suggestions, not part of the recipe.
* Suggestions are a link panel, not a structural change to the recipe.
* Feature is off by default; user enables it in settings.

---

### 8.3 Ingredient-based suggestions

User specifies ingredients they have. AI suggests recipes that use them.

**Rules:**

* This is a retrieval aid. Suggestions are links to existing archive records.
* AI does not generate or invent recipe content.
* Feature requires AI connection.

---

## 9. AI Trust Boundaries

These are firm boundaries that define where AI authority ends.

| Boundary | Rule |
|---|---|
| Verification state | Set by user only. Never by AI. |
| Raw source | Never replaced or altered by AI. |
| Approved recipe fields | Never modified by AI without explicit user review. |
| Source attribution | Never fabricated by AI. |
| Archive-level actions | Never triggered by AI (delete, export, merge, archive). |
| Recipe identity | Never defined by AI (a recipe is what the user says it is). |
| Trust indicators | Displayed by the system only after user action. |

---

## 10. Raw Source vs AI Suggestion vs Approved Data Model

These three layers must remain distinct in the data model and in the UI.

### 10.1 Raw Source

What entered the system as-is. Permanent record of origin.

* pasted text verbatim
* URL content snapshot or reference
* original file link
* manual entry field content before any AI intervention

Rules:
* Raw source is write-once after intake is saved.
* It is never replaced by a normalized version.
* It is accessible from the recipe detail view and intake history.

---

### 10.2 AI Suggestion

AI output that has not yet been accepted by the user.

Characteristics:
* Visually distinct from approved content.
* Stored in a pending/suggestion state.
* Discarded if user declines.
* Becomes user-edited content if the user accepts and modifies.
* Becomes accepted content if the user accepts without modification.

The distinction between user-edited and accepted-as-is may be recorded in the data model for transparency, but this is a v2 concern.

---

### 10.3 Approved Archive Data

Content that the user has explicitly accepted and saved into the archive.

Characteristics:
* No AI badge or qualifier needed once approved.
* May have originated as AI suggestion, but user responsibility has been transferred.
* Shown as clean archive data.

The origin (AI-assisted, manual, imported) may be retained as metadata, but it does not change the displayed content's status.

---

## 11. AI UI Rules

These rules govern how AI appears in the interface.

### 11.1 AI must be visually identifiable

Any field populated by AI that has not yet been approved by the user must carry a visual indicator. This indicator must not be subtle to the point of invisibility.

Suggested visual treatment:
* a small label or badge: `AI` or `Suggested`
* a left border color distinct from normal field borders
* a distinct background tone within the design system

### 11.2 AI interactions must feel calm

AI must not arrive with dramatic animations, aggressive notifications, or anything that implies authority.

AI interaction states:
* `Requesting...` — calm, subdued loading indicator
* `Suggestion ready` — minimal notification, no interruption
* `Unable to connect` — inline, non-blocking error

### 11.3 AI must not crowd approved content

AI suggestions must appear in their own visual zone or as clearly subordinate to the existing approved record. They must not overlay, replace, or obscure approved content.

### 11.4 AI controls are opt-in

No AI action is triggered automatically. Every AI interaction begins with an explicit user action: a button, a menu option, or a deliberate request.

### 11.5 AI availability state must be visible

The app must show clearly whether AI is connected, disconnected, or unavailable. This state should be visible in settings and relevant intake contexts. It should not be hidden.

Suggested states:
* `AI Connected` — LM Studio is reachable and responding
* `AI Unavailable` — LM Studio is not reachable
* `AI Not Configured` — no AI connection has been set up

### 11.6 AI must not masquerade as the product

AI labels like "Galley AI" or "Archive Intelligence" are acceptable identity language. AI must not be named in ways that imply it is the primary interface (e.g., "Ask Galley", "Chat with your archive").

---

## 12. Review and Approval Rules

### 12.1 Human review is mandatory for all AI output that reaches the archive

No AI-generated content enters the archive as approved data without passing through a review step.

### 12.2 Review must be actionable

The review interface must allow the user to:
* Accept a suggestion as-is
* Edit a suggestion before accepting
* Reject a suggestion
* Reject all suggestions and continue manually
* See the raw source alongside the suggestions

### 12.3 Bulk approval requires explicit affirmation

If the system provides a way to accept all suggestions at once, this action must require an explicit, unambiguous user action. It must not be the default.

### 12.4 Partial approval must be supported

The user must be able to accept ingredient suggestions and reject taxonomy suggestions. No field group must be all-or-nothing.

### 12.5 Review state must persist

If the user closes the intake review without completing it, the state (raw source, AI suggestions, partial edits) must be recoverable. Work in progress must not be silently discarded.

---

## 13. Failure and Fallback Behavior

### 13.1 LM Studio unreachable

* Show inline message: `AI normalization unavailable. Continue manually.`
* Intake flow continues without AI.
* All intake paths work without AI.
* Archive remains fully functional.

### 13.2 LM Studio returns empty or malformed response

* Show inline message: `AI returned no usable content. Review source and continue manually.`
* Raw source is preserved.
* User is directed to manual cleanup.

### 13.3 LM Studio returns a partial response

* Show what was returned.
* Mark missing fields clearly.
* User fills in missing fields manually.
* Partial AI result + manual fields = acceptable outcome.

### 13.4 AI enrichment fails on existing recipe

* Show inline message in enrichment panel.
* Current approved content is unchanged.
* User can retry or dismiss.

### 13.5 AI retrieval fails

* Search falls back to direct field matching.
* Natural language query is attempted as a literal keyword search.
* User is shown a note that AI-assisted search is unavailable.

### 13.6 General principle

Every AI failure must leave the archive in a clean state. No failure should result in corrupted records, lost user input, or forced error screens that block navigation.

---

## 14. AI State Model

These are the states the AI system moves through within the product.

### 14.1 Connection states

| State | Meaning |
|---|---|
| `not_configured` | No LM Studio connection has been set up. AI features are disabled. |
| `connecting` | System is testing connectivity to LM Studio. |
| `connected` | LM Studio is reachable and the configured model is available. |
| `disconnected` | LM Studio was previously connected but is no longer reachable. |
| `error` | A connection error has occurred and further attempts have been paused. |

---

### 14.2 Request states (per AI interaction)

| State | Meaning |
|---|---|
| `idle` | No active AI request. |
| `pending` | AI request has been sent. Waiting for response. |
| `processing` | Response is being parsed or normalized. |
| `ready` | AI output is available for review. |
| `accepted` | User has accepted AI output (or portions of it). |
| `rejected` | User has discarded AI output. |
| `failed` | Request failed. Error shown. User continues manually. |

---

### 14.3 Field-level AI suggestion states

| State | Meaning |
|---|---|
| `suggested` | AI has proposed this value. Not yet reviewed. |
| `accepted` | User has accepted this value without modification. |
| `edited` | User accepted and then modified this value. |
| `rejected` | User discarded this suggestion. Field is empty or shows prior value. |
| `manual` | Field was filled by user independent of AI. |

---

## 15. Security and Privacy Principles for Local Use

Sevastolink Galley Archive is a local-first product. The following principles govern AI in that context.

### 15.1 All AI processing is local

LM Studio runs on the user's machine. Recipe content must not be sent to remote AI services unless the user has explicitly configured a remote endpoint and confirmed they understand the implications.

### 15.2 No data leaves the machine by default

The default configuration must not transmit archive content to external servers, analytics services, or cloud AI APIs.

### 15.3 LM Studio endpoint is user-configured

The app must not assume or hardcode an LM Studio URL. The user must explicitly configure the connection. The default should point to the standard local LM Studio endpoint.

### 15.4 No AI model is bundled

Sevastolink Galley Archive does not ship with a model. AI capability depends on the user's local LM Studio installation and model selection.

### 15.5 API keys are not required by default

For local LM Studio use, no API key should be required. If the user configures a remote AI endpoint that requires a key, that key must be stored securely (not in plaintext config files).

### 15.6 Archive content is never used for model training

The product must not send recipe content to any external service for training, fine-tuning, or telemetry purposes. This must be a hard architectural constraint, not a preference setting.

---

## 16. v1 AI Scope

The following AI features are in scope for v1.

### In scope

* LM Studio connection configuration in settings
* AI availability status display (connected / unavailable / not configured)
* AI normalization during paste text intake
* Field-level review of AI-suggested content (title, ingredients, steps, taxonomy suggestions)
* Inline AI error handling and fallback to manual flow
* AI model selection in settings (to select from installed LM Studio models)

### Out of scope for v1 (but architecturally anticipated)

See §17.

### v1 AI model requirements

The prompt contracts used in v1 must be defined in `docs/05_ai/prompt-contracts.md`. The following outputs must be requested from any normalization prompt:

* `title` — string
* `ingredients` — array of structured objects
* `steps` — array of structured step objects
* `prep_time_minutes` — integer, nullable
* `cook_time_minutes` — integer, nullable
* `total_time_minutes` — integer, nullable
* `servings` — string, nullable
* `dish_role` — string from taxonomy vocabulary, nullable
* `primary_cuisine` — string from taxonomy vocabulary, nullable
* `secondary_cuisines` — array, required even if empty
* `technique_family` — string from taxonomy vocabulary, nullable
* `ingredient_families` — array, required even if empty
* `notes` — string, nullable
* `source_credit` — string, nullable
* `ambiguities` — array, required even if empty

The AI response must be parseable as JSON. The system must handle non-JSON or malformed responses gracefully.

---

## 17. Deferred AI Scope

The following are not in scope for v1 but are anticipated in the architecture.

### 17.1 URL content analysis

AI-assisted extraction and normalization of web content fetched from a URL.

### 17.2 OCR and image extraction

AI-assisted extraction of text from uploaded images or PDF pages.

### 17.3 Archive enrichment panel

On-demand AI enrichment of existing recipe records for missing or alternative metadata.

### 17.4 Re-normalize existing records

AI re-processing of previously imported recipes when the normalization quality was poor.

### 17.5 Related recipe suggestions

AI-driven related content panel on recipe detail view.

### 17.6 Ingredient-based recipe lookup

Natural language ingredient input returning relevant archive records.

### 17.7 Natural language search

AI-interpreted search queries mapped to structured taxonomy fields.

### 17.8 Field-level suggestion history

Logging whether a field's current value was AI-assisted, AI-edited, or manual.

### 17.9 Multi-model routing

Routing different AI tasks to different LM Studio models based on task type and model capability.

### 17.10 Remote AI configuration

Support for user-configured remote AI endpoints as an alternative to local LM Studio, with appropriate privacy disclosure.

---

## 18. Anti-Patterns

These behaviors must be avoided in all AI design decisions.

### 18.1 Silent enrichment

AI must never enrich or modify archive records in the background without user initiation and review.

### 18.2 Trust laundering

A flow that makes it easy to accept AI output without reading it is a trust risk. Review UX must require engagement, not just allow it.

### 18.3 AI as primary interface

No AI feature should become the main way users interact with their archive. Chat-first, prompt-first, or AI-assistant-first patterns are not appropriate for this product.

### 18.4 Confident display of uncertain content

AI suggestions must never look like approved data. Using identical typography, spacing, and color for AI-suggested and user-approved content is a design error.

### 18.5 AI-gated features

No core archive operation should require AI to work. Locking browsing, editing, or saving behind AI availability is an architectural mistake.

### 18.6 Auto-verify

No flow should set a recipe's verification state to Verified without an explicit user action. AI normalization does not constitute verification.

### 18.7 Prompt exposure as UX

The interface must not expose raw prompt strings to the user as part of normal operation. Prompt templates belong in `docs/05_ai/prompt-contracts.md` and in the application layer, not in the UI.

### 18.8 AI branding as product identity

The product's value is the archive, the design, the structure, and the data the user builds over time. AI is a tool. It should not be the face of the product.

### 18.9 Degraded UX when AI is absent

The non-AI experience must not feel broken, reduced, or apologetic. It must feel complete. AI adds throughput; it does not complete the product.

---

## 19. Final AI Standard

Every AI design decision in Sevastolink Galley Archive should be judged by this question:

**Does this AI feature help the user build and maintain a trustworthy, personal culinary archive — without creating uncertainty, obscuring provenance, or undermining the user's authority over their own data?**

If the answer is no, or unclear, the feature does not belong in this product.

AI serves the archive. The archive serves the user. That order never reverses.

---

## Decisions Made

1. AI is confirmed as optional and assistive. It is not a hard dependency for any core function.
2. LM Studio is the designated AI runtime for local use. It must be user-configured, not bundled or assumed.
3. Three distinct data layers are canonical: raw source, AI suggestion, approved archive data. These must be distinct in the data model and in the UI.
4. Trust state is user-set only. AI cannot set, imply, or suggest verification state.
5. All AI interactions are user-initiated. No AI behavior is automatic or background.
6. AI availability is displayed to the user in settings and relevant intake contexts.
7. v1 AI scope is limited to paste text normalization with field-level review.
8. All AI prompts are defined in `docs/05_ai/prompt-contracts.md`.
9. The default AI configuration is local only. No remote AI by default.
10. Archive content must never be sent to external services for training or telemetry.

---

## Open Questions

1. **Suggestion history in the data model** — Should the final recipe record retain a field indicating whether its current value was AI-assisted, AI-edited, or fully manual? This affects transparency features in v2. Decision deferred.
2. **Partial response handling strategy** — Should partial AI responses be shown as-is with missing fields blank, or should the system prompt again for missing fields before presenting? Behavior to be specified in prompt-contracts.md.
3. **LM Studio model default** — Should the system recommend a specific model for normalization tasks, or leave model selection entirely to the user? Recommendation language to be defined in lm-studio-integration.md.
4. **Enrichment panel position** — Where does the enrichment panel live in the recipe detail view? This is a component and layout question for the UI spec, not resolved here.
5. **Re-normalize diff presentation** — When re-normalizing an existing recipe, what diff format best serves the user? Side-by-side, inline diff, field-by-field? Decision deferred to component spec.

---

## Deliverables Created

* `docs/05_ai/ai-interaction-spec.md` — this document

---

## What Document Should Be Created Next

**`docs/05_ai/prompt-contracts.md` — AI Prompt Contracts**

This document now exists and should remain aligned with:

* schema-safe field names such as `primary_cuisine` and `servings`
* structured step and ingredient object contracts
* taxonomy v2.0 vocabulary expansions
* staged review and validation requirements
