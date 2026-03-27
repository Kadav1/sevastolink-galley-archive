# Sevastolink Galley Archive

## Prompt Contracts v1.0

---

## 1. Purpose

This document defines the prompt contracts and structured output contracts for AI workflows in Sevastolink Galley Archive.

It establishes:

* how prompts are framed as application contracts rather than ad hoc instructions
* how workflow inputs are packaged for model use
* how outputs must be structured and validated
* what each AI workflow is allowed to return
* how trust, review, and provenance boundaries are preserved
* how malformed or partial outputs are handled
* how prompt versions should evolve over time

This document sits below the AI Interaction Spec and the LM Studio Integration Spec. It does not redefine AI's role. It specifies the concrete task contracts the application sends to the model layer.

---

## 2. Prompt contract philosophy

### Established facts

* AI is optional and assistive.
* AI output is always suggestion-only until reviewed by a human.
* Raw source, structured candidate, and approved recipe are distinct states and must remain distinct in both the data model and the UI.
* Structured outputs are preferred over freeform prose where possible.
* AI must not invent provenance or set trust state.

### Contract standard

Prompts in this product are not treated as writing prompts. They are machine-facing contracts for bounded archive tasks.

Each contract must therefore:

* define a specific workflow goal
* define exact input context
* define required output shape
* constrain the model away from stylistic improvisation
* favor omission over invention
* preserve traceability back to source material

The product does not ask the model to "be helpful" in a broad sense. It asks the model to perform narrow transformation or suggestion tasks that the application can validate and stage for review.

---

## 3. General contract rules

### 3.1 One contract per task type

Normalization, metadata suggestion, rewrite, similarity, and pantry suggestion must each have distinct prompt contracts.

The application must not use one generic prompt for all AI behaviors.

### 3.2 Contracts are application-owned

The application owns:

* prompt templates
* workflow input assembly
* output schemas
* validation rules
* taxonomy vocabularies

The model does not define the archive shape.

### 3.3 Output shape is part of the contract

If a workflow produces fields, the prompt must request fields, not paragraphs.

### 3.4 Prompts must be source-aware

Whenever source material exists, the prompt must identify what content is source-derived and instruct the model not to fabricate absent facts.

### 3.5 Prompts must preserve uncertainty

If the source is incomplete or ambiguous, the model should return `null`, an empty array, or an unresolved note rather than inventing certainty.

### 3.6 Prompts must not include product-authority language

Prompts must not imply that the model is approving, verifying, publishing, or finalizing archive data.

### 3.7 Prompts should remain deterministic in intent

Prompt wording should minimize:

* persona language
* stylistic flourish
* motivational framing
* open-ended brainstorming
* conversational filler

The goal is stable archive assistance, not expressive copy generation.

---

## 4. Input contract model

### Input envelope standard

Every prompt contract should be assembled from a common application-side envelope.

Required envelope fields:

* `contract_name`
* `contract_version`
* `workflow_type`
* `source_kind`
* `source_snapshot`
* `record_context`
* `allowed_taxonomy`
* `output_schema`
* `behavior_rules`

### 4.1 `contract_name`

String identifier for the specific contract, for example:

* `recipe_normalization`
* `metadata_suggestion`
* `archive_rewrite`
* `related_recipe_retrieval`
* `pantry_suggestion`

### 4.2 `contract_version`

Explicit semantic version string for the contract template and schema pair, for example `1.0.0`.

### 4.3 `workflow_type`

Application workflow identifier, for example:

* `intake_normalization`
* `recipe_enrichment`
* `field_rewrite`
* `related_lookup`
* `pantry_lookup`

### 4.4 `source_kind`

Defines the current evidence basis:

* `raw_text`
* `url_extracted_text`
* `file_extracted_text`
* `candidate_recipe`
* `approved_recipe`
* `pantry_snapshot`

### 4.5 `source_snapshot`

The exact text or structured input snapshot for the request.

Rules:

* it must be immutable for the life of the AI job
* it must correspond to a saved application snapshot
* it must be recoverable for review and debugging

### 4.6 `record_context`

Optional structured context about the current candidate or recipe record.

Examples:

* current recipe fields
* known source metadata
* current taxonomy values
* current notes
* pantry inventory snapshot

### 4.7 `allowed_taxonomy`

Explicit vocabulary subsets relevant to the task.

The application should pass only the needed taxonomy domains, such as:

* allowed dish roles
* allowed primary cuisines
* allowed technique families
* allowed ingredient families

### 4.8 `output_schema`

The exact JSON shape expected from the model.

This must be supplied by the application, not inferred by the model.

### 4.9 `behavior_rules`

Task-specific behavioral instructions, such as:

* do not invent provenance
* use `null` for unknown scalar values
* return empty arrays rather than prose for missing lists
* preserve source wording where specificity matters
* do not set trust or verification state

---

## 5. Output contract model

### Output standard

Every prompt contract must return one of two output classes:

* `structured_result`
* `structured_failure`

The model should never be asked to return an unconstrained blob for archive-facing workflows.

### 5.1 Structured result

A valid structured result contains:

* `contract_name`
* `contract_version`
* `result_type`
* `data`
* `warnings`

Rules:

* `result_type` must identify the workflow result, such as `normalization_result`
* `data` must match the contract schema
* `warnings` is optional and must be an array of short machine-usable strings

### 5.2 Structured failure

Where supported by the model and prompt, failure may be returned as a structured object rather than malformed output.

Recommended fields:

* `contract_name`
* `contract_version`
* `result_type = failure`
* `failure_reason`
* `warnings`

### 5.3 Output boundaries

Model output must not contain:

* trust-state decisions
* approval state
* invented source URLs or authors
* hidden chain-of-thought
* UI copy
* commentary that is not explicitly part of the schema

---

## 6. Prompt contract for recipe normalization

### Purpose

Convert messy source material into a structured recipe candidate for intake review.

### Established facts

This is the primary v1 AI workflow.

### Input contract

Required input fields:

* `source_kind`
* `source_snapshot.raw_text`
* `record_context.source_metadata`, if available
* `allowed_taxonomy.dish_roles`
* `allowed_taxonomy.primary_cuisines`
* `allowed_taxonomy.technique_families`
* `output_schema.normalization_result`
* `behavior_rules.normalization`

### Required behavior rules

The normalization contract must instruct the model to:

* extract and structure recipe information from the provided source only
* preserve ambiguity rather than invent values
* leave unknown values as `null`
* preserve quantities and ingredient wording where source specificity matters
* return taxonomy labels only from provided vocabularies when possible
* avoid adding culinary commentary unless requested by schema
* never set trust state
* never imply the recipe is final or verified

### Output contract

The output must be a JSON object matching `normalization_result`.

Required top-level shape:

* `contract_name`
* `contract_version`
* `result_type`
* `data`
* `warnings`

### `data` payload

The normalization payload should include:

* recipe identity fields
* structured ingredient list
* ordered step list
* selected taxonomy suggestions
* source-derived notes where present
* unresolved ambiguity markers where needed

### Recommended contract style

The normalization contract should be framed as:

* task statement
* source block
* allowed taxonomy block
* output schema block
* explicit prohibitions

It should not be framed as:

* conversational roleplay
* creative rewriting
* editorial voice generation

---

## 7. Prompt contract for metadata suggestion

### Purpose

Suggest missing or alternative metadata for a structured candidate or existing recipe.

### Established facts

This workflow is allowed by the AI Interaction Spec but is not part of the required v1 execution surface.

### Input contract

Required input fields:

* `source_kind = candidate_recipe` or `approved_recipe`
* `record_context.recipe_snapshot`
* `allowed_taxonomy`
* `output_schema.metadata_suggestion_result`
* `behavior_rules.metadata`

### Required behavior rules

The metadata contract must instruct the model to:

* work from the provided structured recipe snapshot
* prefer broad, retrieval-useful taxonomy classifications
* avoid over-tagging
* choose dominant values where the taxonomy expects single-select output
* return `null` instead of guessing when evidence is weak
* avoid changing provenance or trust fields

### Output contract

The result should include only metadata suggestions and optional short rationale notes if the schema allows them.

Allowed output domains:

* dish role
* primary cuisine
* secondary cuisines
* technique family
* ingredient families
* complexity estimate if the product later adopts it formally
* optional context notes

### Recommendation

Rationale text should remain brief and structured. Long explanatory prose should not be the default output mode.

---

## 8. Prompt contract for recipe rewrite into archive style

### Purpose

Transform existing recipe text into archive-friendly field formatting without changing underlying meaning.

### Established facts

Rewrite is permitted only as a proposal workflow. It must not invent facts or silently restyle approved content.

### Input contract

Required input fields:

* `source_kind = candidate_recipe` or `approved_recipe`
* `record_context.source_fields`
* `record_context.target_fields`
* `output_schema.rewrite_result`
* `behavior_rules.rewrite`

### Required behavior rules

The rewrite contract must instruct the model to:

* preserve original culinary meaning
* preserve factual specificity already present
* improve structural clarity only where requested
* avoid introducing new ingredients, timings, or provenance
* avoid changing taxonomy unless that is the explicit target of the request

### Output contract

The result should return targeted field rewrites only.

Examples:

* rewritten steps array
* cleaned ingredient lines
* archive-style notes block
* short description candidate

### Recommendation

Rewrite prompts should include the original field values verbatim and the target formatting rules explicitly. They should not ask for a "better" recipe in general terms.

---

## 9. Prompt contract for similarity / related recipe retrieval

### Purpose

Support related recipe discovery and query interpretation without replacing deterministic archive retrieval.

### Established facts

Similarity and retrieval assistance are secondary to the archive's structured search system.

### Input contract

Two contract patterns are allowed.

#### 9.1 Query interpretation contract

Inputs:

* natural language query
* allowed taxonomy values
* optional pantry context
* `output_schema.query_interpretation_result`

Behavior:

* translate user language into structured search hints
* do not fabricate recipe records
* do not return a final ranked result set if the retrieval engine has not executed one

#### 9.2 Related-recipe explanation contract

Inputs:

* anchor recipe snapshot
* candidate related recipe summaries or IDs
* `output_schema.related_recipe_explanation_result`

Behavior:

* explain relationship signals briefly
* use structured reasons where possible
* keep commentary subordinate to the actual retrieved records

### Recommendation

For retrieval, the preferred sequence is:

1. deterministic retrieval
2. embeddings similarity where available
3. optional model explanation

Freeform generation should not be the retrieval core.

---

## 10. Prompt contract for pantry-based suggestion

### Purpose

Suggest recipes, components, or directionally relevant cooking options based on pantry inventory without making pantry AI the center of the product.

### Established facts

Pantry workflows are expansion-oriented and must remain subordinate to the archive.

### Input contract

Required input fields:

* `source_kind = pantry_snapshot`
* `record_context.pantry_items`
* optional current meal constraints
* optional cuisine or technique preferences
* `output_schema.pantry_suggestion_result`

### Required behavior rules

The pantry contract must instruct the model to:

* work from the supplied pantry snapshot only
* prefer suggestions that can be grounded in the existing archive when recipe candidates are provided
* separate direct matches from partial matches
* be explicit about missing ingredients when relevant
* avoid inventing pantry inventory not present in the input

### Output contract

The result should remain structured, for example:

* query hints for archive retrieval
* recipe candidate IDs if provided from retrieval context
* component suggestions
* missing-ingredient summary

### Recommendation

Pantry prompting should usually be paired with deterministic archive lookup rather than stand-alone generative ideation.

---

## 11. Trust and review requirements per contract

### Established facts

Trust state is always user-controlled. AI cannot approve, verify, or silently update trusted content.

### Contract requirements

#### 11.1 Normalization

* Output is a staged structured candidate.
* Raw source remains visible and permanent.
* User reviews field by field before save.

#### 11.2 Metadata suggestion

* Output is a staged suggestion set.
* Existing approved fields remain unchanged until explicit acceptance.
* Partial acceptance must be supported.

#### 11.3 Rewrite

* Output is a staged before/after proposal.
* Original values remain recoverable in the review surface.
* Accepting rewritten text does not imply verification.

#### 11.4 Similarity / retrieval

* Output influences retrieval or explanation only.
* It must not create or approve recipe data.
* Query interpretation results remain intermediate application data.

#### 11.5 Pantry suggestion

* Output is advisory.
* It must not create archive records automatically.
* It must not imply pantry certainty beyond the supplied snapshot.

### Review standard

Every contract that returns archive-facing fields must support:

* accept
* edit before accept
* reject
* partial acceptance where relevant

---

## 12. Required structured output fields per workflow

### 12.1 Recipe normalization

Required `data` fields:

* `title`: string or `null`
* `ingredients`: array
* `steps`: array
* `prep_time_minutes`: integer or `null`
* `cook_time_minutes`: integer or `null`
* `total_time_minutes`: integer or `null`
* `servings`: string or `null`
* `dish_role`: string or `null`
* `primary_cuisine`: string or `null`
* `secondary_cuisines`: array
* `technique_family`: string or `null`
* `ingredient_families`: array
* `notes`: string or `null`
* `source_credit`: string or `null`
* `ambiguities`: array

Ingredient object fields:

* `item`: string
* `quantity`: string or `null`
* `unit`: string or `null`
* `preparation`: string or `null`
* `optional`: boolean

Step object fields:

* `position`: integer
* `instruction`: string
* `time_note`: string or `null`
* `equipment_note`: string or `null`

### 12.2 Metadata suggestion

Required `data` fields:

* `dish_role`: string or `null`
* `primary_cuisine`: string or `null`
* `secondary_cuisines`: array
* `technique_family`: string or `null`
* `ingredient_families`: array
* `complexity`: string or `null`
* `notes_suggestion`: string or `null`
* `ambiguities`: array

### 12.3 Rewrite

Required `data` fields:

* `target_fields`: array
* `rewritten_title`: string or `null`
* `rewritten_ingredients`: array
* `rewritten_steps`: array
* `rewritten_notes`: string or `null`
* `change_notes`: array

### 12.4 Similarity / related retrieval

Query interpretation result fields:

* `query_text`: string
* `dish_role_hints`: array
* `cuisine_hints`: array
* `technique_hints`: array
* `ingredient_family_hints`: array
* `keyword_hints`: array
* `ambiguities`: array

Related explanation result fields:

* `anchor_recipe_id`: string
* `related_items`: array of objects

Related item object fields:

* `recipe_id`: string
* `reason_codes`: array
* `short_explanation`: string or `null`

### 12.5 Pantry suggestion

Required `data` fields:

* `pantry_summary`: string or `null`
* `query_hints`: array
* `direct_match_recipe_ids`: array
* `partial_match_recipe_ids`: array
* `component_suggestions`: array
* `missing_ingredient_summary`: array
* `ambiguities`: array

---

## 13. Validation rules

### 13.1 Parse validation

The application must reject outputs that are not valid JSON when the contract requires JSON.

### 13.2 Schema validation

The application must validate:

* required top-level keys
* required `data` keys
* scalar types
* array types
* nullability rules

### 13.3 Taxonomy validation

Single-select taxonomy fields must either:

* match an allowed value
* normalize deterministically to an allowed value
* resolve to `null`

They must not create new canonical taxonomy values silently.

### 13.4 Provenance validation

The application must reject or strip:

* invented source URLs
* invented source authors
* invented publication metadata
* trust-state assignments

### 13.5 Field sanity validation

The application should flag:

* empty ingredient items
* empty step instructions
* negative or implausible time values
* duplicate step indexes
* arrays replaced by prose blocks

### 13.6 Contract identity validation

If the output includes the wrong contract name or version, the application should treat it as invalid or at minimum degraded and re-validate cautiously.

---

## 14. Failure / malformed output handling

### Established facts

Malformed AI output must not block archive workflows.

### Handling standard

#### 14.1 Non-JSON output

Behavior:

* mark request failed
* show inline workflow error
* preserve source and user edits
* allow manual continuation

#### 14.2 Partial but usable output

Behavior:

* keep valid fields
* mark missing fields clearly
* let the user complete the record manually

#### 14.3 Wrong schema

Behavior:

* reject invalid fields
* do not coerce arbitrary prose into archive fields
* surface a clean error state or partial state depending on usable remainder

#### 14.4 Hallucinatory provenance

Behavior:

* strip or reject invented provenance fields
* log validation failure locally
* continue with non-provenance fields only if safe

#### 14.5 Empty result

Behavior:

* show `AI returned no usable content. Review source and continue manually.`
* preserve all source material

### Recommendation

The application should distinguish:

* transport failure
* parse failure
* schema failure
* taxonomy failure
* safe partial success

These should map to separate local error codes even if the UI consolidates the message.

---

## 15. Versioning strategy for prompts

### Contract versioning rule

Each prompt contract and its output schema must be versioned together.

Recommended format:

* major version for breaking schema or behavior changes
* minor version for backward-compatible prompt improvements
* patch version for wording clarifications that do not change the expected output shape

### Persistence rule

Every AI job record should store:

* `contract_name`
* `contract_version`
* `model_id`
* `workflow_type`

This makes later evaluation and regression analysis possible.

### Migration rule

Changing a prompt without changing its version is prohibited if the expected output behavior materially changes.

### Recommendation

When a contract graduates from experiment to canonical use, freeze the schema first and tune wording second.

---

## 16. Evaluation criteria for each prompt type

### 16.1 Recipe normalization

Evaluate for:

* schema compliance rate
* ingredient extraction completeness
* step ordering quality
* low hallucination rate
* taxonomy alignment accuracy
* usefulness of ambiguities field

### 16.2 Metadata suggestion

Evaluate for:

* taxonomy precision
* low over-tagging rate
* consistency across similar recipes
* usefulness to retrieval and filtering

### 16.3 Rewrite

Evaluate for:

* meaning preservation
* clarity improvement
* low factual drift
* reviewability of changes

### 16.4 Similarity / retrieval

Evaluate for:

* usefulness of structured query hints
* retrieval improvement over baseline
* low irrelevant suggestion rate
* explanation brevity and relevance

### 16.5 Pantry suggestion

Evaluate for:

* grounding in actual pantry input
* usefulness to archive retrieval
* clarity about missing ingredients
* low speculative output rate

### Evaluation rule

A prompt contract is good only if it produces outputs the application can validate and the user can review efficiently. Pleasant wording alone is not a success criterion.

---

## 17. Anti-patterns

### 17.1 Generic assistant prompts

Do not use prompts that ask the model to act as a chef, friend, editor, archivist, or concierge without a strict output contract.

### 17.2 Style-first prompting

Do not optimize for eloquence, voice, or polish when the workflow requires structured archive data.

### 17.3 Hidden schema assumptions

Do not rely on the model to remember field names or shapes without the application supplying them explicitly.

### 17.4 Prompting around validation

Prompt instructions do not replace application-side validation.

### 17.5 Trust laundering through wording

Do not use prompt language like:

* finalize
* approve
* verify
* confirm
* publish

for model-generated outputs.

### 17.6 Taxonomy sprawl

Do not ask the model to invent novel cuisines, dish roles, or technique families as part of standard output.

### 17.7 Paragraph dumps in place of fields

Do not accept prose blocks when the contract calls for arrays or named fields.

### 17.8 Contract drift without versioning

Do not materially change prompt behavior while keeping the same contract version.

### 17.9 Using prompts as product design

Prompt text must not become the place where archive rules, trust rules, or UI behavior are decided. Those belong in the application and the specs.

---

## 18. Final prompt contract standard

Every AI workflow in Sevastolink Galley Archive must be defined as a bounded prompt contract with:

* explicit input envelope
* explicit behavior rules
* explicit structured output schema
* application-side validation
* staged human review where archive-facing data is involved

The prompt is not the product logic. The prompt is one component inside a local-first archive system that preserves source evidence, suggestion boundaries, taxonomy integrity, and user authority.

If a prompt makes the model feel authoritative, obscures provenance, blurs source and approved data, or produces output the application cannot validate cleanly, the prompt is out of standard.

---

## Decisions made

1. Prompt contracts are defined as application-owned task contracts, not open-ended assistant instructions.
2. Structured JSON is the default output mode for archive-facing workflows.
3. Each workflow type has its own contract: normalization, metadata suggestion, rewrite, similarity, and pantry suggestion.
4. Input envelopes must include explicit source snapshots, allowed taxonomy values, output schema, and behavior rules.
5. Output contracts must exclude trust-state decisions and invented provenance.
6. Prompt versioning is mandatory and tied to schema versioning.
7. Validation is application-side and required for parse, schema, taxonomy, and provenance safety.

## Open questions

1. Should the `ambiguities` field be mandatory across all contracts, or only where source interpretation is central?
2. Should rewrite contracts always return `change_notes`, or should that remain optional to reduce verbosity for weaker local models?
3. For pantry suggestion, should the model return only retrieval hints in v1-style architecture, or also structured component suggestions once pantry features exist?
4. Should metadata suggestion include lightweight confidence buckets, or should confidence remain implicit and handled only through review UX?

## Deliverables created

1. `/docs/05_ai/prompt-contracts.md`

## What document should be created next

`docs/09_ops/local-deployment.md`

This document should define how the local app stack and optional LM Studio runtime are configured and run together in development and local deployment.
