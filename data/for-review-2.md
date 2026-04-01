# Proposal 2: Target Staged Contract For Translation, Reference Matching, And Normalization

## Purpose

This document defines a target contract for the next revision of the Swedish translation and normalization workflow.

It is a future-state design that should be implemented incrementally from the current importer, not treated as already live.

---

## Current implementation boundary

Today the importer effectively does this:

1. stage 1: Swedish source becomes English preprocessing text
2. stage 2: English preprocessing text becomes normalized archive candidate data

That is a good foundation, but the current stage-1 contract is too thin and the stage-2 request is too implicit.

The target state below keeps the same broad shape while making the handoff explicit.

---

## Proposed staged flow

### Stage 0: Raw source evidence

Input:

* raw Swedish source file

Output:

* immutable source text
* source path
* source-language guess

Authority:

* this remains the truth layer

### Stage 1: Semantic translation

Input:

* raw Swedish source text
* translation prompt
* translation policy

Output:

* faithful English translation text
* segment-level translation objects
* uncertainty markers produced by the translation stage

Responsibility:

* preserve meaning
* preserve quantities and ordering
* preserve structure
* do not normalize into archive taxonomy

### Stage 1.5: Reference matching

Input:

* stage-1 translation output
* Swedish unit reference
* Swedish term reference
* render policy

Output:

* matched units
* matched ingredients and modifiers
* contextual term matches
* drift signals
* suggested normalization hints

Responsibility:

* deterministic matching where possible
* contextual guardrails where deterministic matching is not possible
* no archive mutation yet

### Stage 2: Archive normalization

Input:

* stage-1 translation output
* stage-1.5 matched references
* render policy
* archive schema contract

Output:

* normalized archive candidate payload
* warnings
* review flags

Responsibility:

* map semantics into archive fields
* choose canonical archive rendering
* preserve uncertainty as review behavior

---

## Proposed contracts

## 1. Stage-1 translation output

The current translation contract only returns:

* `source_language`
* `output_language`
* `translated_text`

The next revision should extend that into a richer but still bounded object:

```json
{
  "pipeline_stage": "stage1_translation",
  "source_language": "sv",
  "output_language": "en",
  "source_text": "...",
  "translated_text": "...",
  "segments": [
    {
      "segment_id": "seg_0001",
      "segment_type": "title | ingredient_line | instruction_line | note | other",
      "source_text": "...",
      "translated_text": "...",
      "uncertainty_flags": [
        "unknown_token",
        "ambiguous_ingredient",
        "ambiguous_modifier",
        "unresolved_unit",
        "ocr_noise"
      ]
    }
  ]
}
```

Key rule:

* segmenting is for semantic traceability, not for changing source meaning

Compatibility rule:

* `translated_text` remains required
* `segments` should be introduced as optional first
* once the importer, tests, and prompts are stable, `segments` can become required in a later schema revision

## 2. Stage-1.5 reference match output

This is the missing contract in the current importer.

It should look something like:

```json
{
  "pipeline_stage": "stage1_reference_match",
  "render_profile": "english_metric_strict | english_hybrid_natural | english_us",
  "locale": "en_generic | en_us | en_uk",
  "unit_matches": [
    {
      "source_token": "tsk",
      "canonical_unit": "tsk",
      "matched_entry_key": "tsk",
      "deterministic": true
    }
  ],
  "term_matches": [
    {
      "source_token": "vitlökspulver",
      "matched_entry_key": "vitlökspulver",
      "deterministic": true
    }
  ],
  "contextual_matches": [
    {
      "source_phrase": "spad från relish eller pickles",
      "matched_entry_key": "spad från relish eller pickles",
      "requires_review": true
    }
  ],
  "drift_signals": [
    "source_measurement_parity_changed"
  ]
}
```

Key rule:

* this stage prepares evidence for normalization; it does not yet emit candidate fields

## 3. Stage-2 normalization request

The normalization stage should explicitly consume both prior stages:

```json
{
  "pipeline_stage": "stage2_normalization_request",
  "render_profile": "english_metric_strict",
  "locale": "en_generic",
  "stage1_translation": { "...": "..." },
  "stage1_reference_match": { "...": "..." },
  "normalization_policy": {
    "preserve_source_authority": true,
    "preserve_non_exact_phrases": true,
    "allow_contextual_micro_unit_rendering": false,
    "volume_to_weight_requires_match": true
  }
}
```

Key rule:

* archive rendering policy must be explicit at request time

## 4. Stage-2 normalization output

This should remain compatible with the existing candidate-bundle workflow.

That means the final output still maps cleanly into:

* candidate update
* candidate extras
* warnings
* review flags

The point of the staged revision is not to discard the current archive schema.
It is to improve the semantic input quality before that schema is populated.

---

## Reference asset model

The current repository already has two active reference files:

* `data/reference/swedish_recipe_units.json`
* `data/reference/swedish_recipe_terms.json`

The target state should still preserve those as the source of truth.

If the reference system expands, it should do so by decomposition from those files, not by introducing an unrelated parallel package.

Recommended structure:

* keep `swedish_recipe_units.json` as the unit authority
* keep `swedish_recipe_terms.json` as the broad term authority
* optionally split generated or derived subsets later:
  * `ingredients_sv_to_en.json`
  * `modifiers_sv_to_en.json`
  * `translation_rules.json`

Important rule:

* the derived files should be generated from the main reference set or clearly documented as canonical replacements
* they should not silently become a second truth system

---

## Render policy

The next revision should define render policy explicitly.

Recommended render profiles:

### `english_metric_strict`

Use when archive safety is primary.

Rules:

* preserve metric structure
* preserve spoon units where they are standard and stable
* prefer deterministic rendering over natural-language smoothing

### `english_hybrid_natural`

Use when readability is important but drift risk must still be controlled.

Rules:

* allow limited natural-English rendering
* keep source measurement meaning stable
* use contextual micro-unit rendering only when backed by policy and ingredient class

### `english_us`

Use only when the output explicitly targets US customary rendering.

Rules:

* conversions must be policy-driven
* never convert merely because the model “felt like it”

## Render-policy matrix

The revised pipeline should define concrete behavior per mode.

| Behavior | `english_metric_strict` | `english_hybrid_natural` | `english_us` |
| --- | --- | --- | --- |
| `dl` rendering | convert to `ml` | convert to `ml` | may convert to cups only when explicitly allowed |
| `msk` rendering | preserve as `tbsp` | preserve as `tbsp` | preserve as `tbsp` |
| `tsk` rendering | preserve as `tsp` | preserve as `tsp` | preserve as `tsp` |
| `krm` rendering | preserve exact metric meaning, typically `1 ml` | may become `a pinch` or `1/4 tsp` only if ingredient/context policy allows | may become `1/4 tsp` only if policy allows |
| locale-sensitive dairy terms like `vispgrädde` | prefer safe generic or archive-default rendering | allow locale-sensitive rendering | allow locale-sensitive US rendering |
| non-exact phrases like `efter smak` | preserve non-exactness literally | preserve non-exactness naturally | preserve non-exactness naturally |
| qualitative usage like `till stekning` | do not invent exact amount | do not invent exact amount | do not invent exact amount |
| volume-to-weight conversion | forbidden unless exact ingredient match policy permits it | forbidden unless exact ingredient match policy permits it | forbidden unless exact ingredient match policy permits it |
| archive vocabulary decisions | stage 2 only | stage 2 only | stage 2 only |

Hard rule:

* render policy belongs to stage 2
* stage 1 may support that policy, but must not silently apply archive-facing normalization decisions on its own

## Canonical reference ownership

The reference system needs one declared truth source.

Canonical source in the current repo:

* `data/reference/swedish_recipe_units.json`
* `data/reference/swedish_recipe_terms.json`

Rule:

* any future `ingredients_sv_to_en.json`, `modifiers_sv_to_en.json`, or `translation_rules.json` must either be:
  * generated from the two canonical files, or
  * explicitly declared as the new canonical source with a migration that retires or rewrites the current files

Do not allow both systems to evolve in parallel.

---

## Review-state mapping

The staged contract should define what happens when semantics are uncertain.

Recommended mapping:

* deterministic unit mismatch -> warning + review flag
* contextual term mismatch -> review flag
* unresolved ingredient identity -> review flag
* archive vocabulary mismatch -> warning + review flag
* source evidence conflict -> approval should remain blocked unless explicitly overridden

## Weak stage-1 fallback behavior

The target contract should define what happens when translation quality is clearly insufficient.

Recommended fallback rules:

* if stage 1 returns structurally valid output but semantic drift is detected, continue and emit a candidate with strong `review_flags`
* if stage 1 is semantically weak on contextual terms or measurement parity, approval should remain blocked by default
* if stage 1 returns empty or unusable translation content, skip normalization and emit a failed run result
* if stage 1 uncertainty is widespread but not catastrophic, emit the candidate and attach an explicit “translation quality review required” flag

This keeps the pipeline useful without pretending weak translation is safe.

## Worked example: `Burgarsås`

Example source fragment:

```text
1 tsk spad från relish eller pickles
1 krm vitlökspulver
1 krm lökpulver
10 min + vila
Rörs kall
```

Target interpretation through the revised pipeline:

### Stage 1

Should preserve something close to:

```json
{
  "translated_text": "1 tsp juice from relish or pickles\n1 ml garlic powder\n1 ml onion powder\n10 min + rest\nmixed cold",
  "segments": [
    {
      "segment_type": "ingredient_line",
      "source_text": "1 tsk spad från relish eller pickles",
      "translated_text": "1 tsp juice from relish or pickles",
      "uncertainty_flags": []
    }
  ]
}
```

### Stage 1.5

Should match:

* `tsk` -> deterministic spoon unit
* `spad från relish eller pickles` -> contextual liquid term requiring semantic verification
* `vitlökspulver` -> garlic powder
* `lökpulver` -> onion powder
* `10 min + vila` -> active time plus rest requirement
* `rörs kall` -> no-heat preparation semantics

### Stage 2

Should normalize into archive output while preserving review behavior:

* no silent `tsk -> tbsp` drift
* no collapse of `spad` into relish itself
* no swap between garlic powder and onion powder
* no loss of rest/no-heat semantics

### If drift still occurs

Expected importer behavior:

* warning for measurement parity change
* review flag for contextual liquid drift
* review flag for powder identity drift
* review flag for lost no-heat or rest semantics
* approval remains blocked unless explicitly overridden

---

## Recommended implementation order

The cleanest order is:

1. enrich the stage-1 translation payload
2. add the stage-1.5 reference-matching object
3. make stage-2 consume explicit policy and reference matches
4. keep final candidate output backward-compatible

This gives the importer a stronger semantic spine without forcing an abrupt redesign of the candidate bundle model.
