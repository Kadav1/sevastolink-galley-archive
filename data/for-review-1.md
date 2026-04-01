# Proposal 1: Rationale For A Semantics-First Swedish Import Pipeline

## Purpose

This document explains why the current Swedish recipe importer should evolve from:

* raw Swedish source
* optional English preprocessing text
* direct normalization into the archive schema

into a more explicit semantics-first pipeline.

This is a proposal for revising the current translation and normalization workflow. It is not a description of the live implementation.

---

## Current baseline

The current importer already has two stages:

1. preprocessing / translation into English
2. normalization into the archive candidate bundle

That baseline is implemented today in:

* `scripts/import/recipe_import/pipeline.py`
* `scripts/import/recipe_import/transport.py`
* `prompts/runtime/translation/recipe-translation-v1.md`
* `prompts/schemas/recipe-translation-output.schema.json`
* `prompts/runtime/normalization/recipe-normalization-v1.md`
* `prompts/schemas/recipe-normalization-output.schema.json`

The importer also now uses Swedish reference assets and preprocessing guardrails to detect drift before candidate emission.

What is still missing is a richer semantic handoff between translation and normalization.

---

## Problem statement

The current pipeline is structurally correct, but it still lets too much meaning collapse between stages.

Typical failure classes:

* Swedish kitchen units change value or rendering during translation
* contextual liquid terms like `spad` become the ingredient itself instead of the liquid from it
* ingredient identity drifts, for example `vitlökspulver` and `lökpulver`
* rest or no-heat meaning is expressed in prose but not strongly represented for normalization
* natural-English rendering and archive-safe preservation are not clearly separated responsibilities

The core issue is not lack of translation alone. It is that semantic interpretation, reference matching, and final archive rendering are still too tightly coupled.

---

## Why semantics-first is the right direction

### 1. Swedish remains the authority layer

The raw Swedish source should remain the evidence layer.

That means:

* source quantities stay authoritative
* source terminology stays authoritative
* uncertainty should be attached to the translation or normalization result, not silently resolved away

### 2. Translation and normalization have different jobs

The translation stage should produce a faithful English representation of the Swedish source.

The normalization stage should then decide:

* archive-facing field values
* canonical ingredient names
* archive-safe unit rendering
* vocabulary mapping into the existing candidate schema

When those jobs blur together, the system becomes harder to debug and harder to trust.

### 2.5 Translation must not normalize

This boundary should be explicit in the revised pipeline.

Stage 1 may:

* translate Swedish into clear English
* preserve structure and sequence
* preserve quantities, units, timing, and headings
* attach uncertainty markers

Stage 1 must not:

* resolve archive taxonomy
* infer missing quantities
* rewrite contextual liquids into ingredient identities
* choose final archive-facing canonical ingredient names
* decide approval safety on its own

That work belongs downstream, where reference matches and archive policy are available.

### 3. Semantic references should be active inputs

Reference files should not just exist as lookups.

They should actively shape the pipeline by helping with:

* unit alias resolution
* contextual ingredient interpretation
* ambiguity handling
* review-flag generation
* render-policy enforcement

### 4. Natural English is not the same as archive English

Some English rendering choices are more readable, but less safe.

Examples:

* `krm` might be rendered as `a pinch` in natural English
* `dl` might become `200 ml`
* `vispgrädde` might become `cream`, `whipping cream`, or `heavy cream`

Those can be valid choices, but only if the pipeline makes clear:

* which stage made the choice
* which source meaning it was based on
* whether the choice is deterministic or contextual

### 5. Uncertainty should become review behavior

Semantic uncertainty should not stop at “interesting note.”

It should map into importer actions:

* keep as warning only
* raise `review_flags`
* block approval without explicit override

That aligns semantic interpretation with the archive’s trust model.

---

## What the next revision should achieve

The next revision should preserve the current two-stage importer, but make the handoff between stages explicit.

Target outcomes:

* translation returns structured semantic evidence, not just one large text field
* normalization consumes both translated text and matched semantic references
* semantic references become first-class runtime inputs
* uncertainty becomes structured importer behavior
* archive rendering policy is explicit instead of implicit

---

## Design principles

The future pipeline should follow these principles:

1. Swedish source is the truth layer.
2. Translation must preserve semantics before style.
3. Normalization may render, but must not erase provenance.
4. Reference files should drive deterministic behavior wherever possible.
5. Contextual ambiguity should become review state, not silent mutation.
6. Natural English output is allowed only when the pipeline can still justify it against the source.
7. Translation must preserve semantics before archive rendering.

---

## Recommended outcome

The best direction is not a total rewrite.

It is a staged revision of the existing importer:

1. enrich stage-1 translation output
2. add a reference-matching handoff before normalization
3. make normalization consume both semantic evidence and render policy
4. map semantic uncertainty into warnings, review flags, and approval safety

This keeps the current importer shape, but makes it much more trustworthy on Swedish recipe material.
