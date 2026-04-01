# Semantics-First Swedish Import Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve the current Swedish recipe importer from a two-stage text handoff into a semantics-first pipeline with enriched stage-1 translation output, explicit reference matching, policy-driven stage-2 request assembly, and stronger review-state handling without breaking candidate-bundle compatibility.

**Architecture:** Keep the current CLI importer shape and candidate-bundle output model, but insert two new internal layers: enriched stage-1 translation artifacts and a deterministic reference-match object consumed by stage 2. Preserve backward compatibility by keeping `translated_text` required in stage 1, keeping the final normalization output schema unchanged at first, and reusing the existing warnings / `review_flags` model for approval safety.

**Tech Stack:** Python 3, JSON Schema, LM Studio OpenAI-compatible APIs, `pytest`, existing importer modules under `scripts/import/recipe_import/`, reference assets under `data/reference/`.

---

## File Structure Map

### Existing files to modify

- `prompts/schemas/recipe-translation-output.schema.json`
  Purpose: expand stage-1 output to support segmented semantic evidence while preserving `translated_text`.
- `prompts/runtime/translation/recipe-translation-v1.md`
  Purpose: instruct the preprocessing model to emit enriched stage-1 output without doing archive normalization.
- `scripts/import/recipe_import/transport.py`
  Purpose: validate enriched stage-1 output and keep `translategemma` transport compatibility.
- `scripts/import/recipe_import/models.py`
  Purpose: add typed containers for stage-1 translation artifacts and stage-1.5 reference-match artifacts.
- `scripts/import/recipe_import/pipeline.py`
  Purpose: orchestrate enriched stage 1, reference matching, explicit stage-2 request construction, and weak-stage-1 fallback behavior.
- `scripts/import/recipe_import/references.py`
  Purpose: keep existing guardrails and expose reusable matching helpers for the new reference-match stage.
- `tests/test_normalize_recipes_rewrite.py`
  Purpose: regression coverage for enriched translation output, reference matching, request assembly, review-state escalation, and fallback behavior.
- `docs/10_imports/recipe-import-workflow.md`
  Purpose: document the new staged importer behavior.
- `docs/10_imports/implemented-imports.md`
  Purpose: keep implementation-aware docs aligned with the new importer structure.
- `README.md`
  Purpose: refresh the operator-facing workflow summary.

### New files to create

- `scripts/import/recipe_import/reference_match.py`
  Purpose: construct deterministic stage-1.5 reference-match artifacts from enriched stage-1 output plus the active Swedish reference files.
- `scripts/import/recipe_import/normalization_request.py`
  Purpose: assemble explicit stage-2 normalization requests with render policy and locale.
- `tests/test_reference_match.py`
  Purpose: focused tests for unit, term, and contextual reference matching.
- `tests/test_normalization_request.py`
  Purpose: focused tests for stage-2 request assembly.

### Files that should remain stable

- `scripts/import/review_candidates.py`
  Purpose: continue consuming candidate bundles as-is.
- `prompts/schemas/recipe-normalization-output.schema.json`
  Purpose: keep final normalized output shape stable in the first implementation pass.

---

### Task 1: Enrich Stage-1 Translation Output Without Breaking Compatibility

**Files:**
- Modify: `prompts/schemas/recipe-translation-output.schema.json`
- Modify: `prompts/runtime/translation/recipe-translation-v1.md`
- Modify: `scripts/import/recipe_import/transport.py`
- Modify: `scripts/import/recipe_import/models.py`
- Test: `tests/test_normalize_recipes_rewrite.py`

- [ ] **Step 1: Write the failing schema-validation tests for enriched stage-1 output**

```python
def test_validate_preprocessing_payload_accepts_segmented_output() -> None:
    schema = {
        "type": "object",
        "required": ["source_language", "output_language", "translated_text"],
    }
    payload = {
        "source_language": "sv",
        "output_language": "en",
        "translated_text": "1 tsp pickle brine",
        "segments": [
            {
                "segment_id": "seg_0001",
                "segment_type": "ingredient_line",
                "source_text": "1 tsk spad från relish eller pickles",
                "translated_text": "1 tsp pickle brine",
                "uncertainty_flags": [],
            }
        ],
    }

    assert validate_preprocessing_payload(payload, schema) == []


def test_validate_preprocessing_payload_rejects_bad_segment_shape() -> None:
    schema = {
        "type": "object",
        "required": ["source_language", "output_language", "translated_text"],
    }
    payload = {
        "source_language": "sv",
        "output_language": "en",
        "translated_text": "english",
        "segments": [{"segment_type": "ingredient_line"}],
    }

    errors = validate_preprocessing_payload(payload, schema)
    assert any("segment" in error.lower() for error in errors)
```

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python3 -m pytest tests/test_normalize_recipes_rewrite.py -q`
Expected: FAIL with missing validation support for `segments` and segment-field shape checks.

- [ ] **Step 3: Expand the stage-1 schema to allow segmented semantic evidence**

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "source_language": { "type": "string" },
    "output_language": { "type": "string", "const": "en" },
    "translated_text": { "type": "string", "minLength": 1 },
    "segments": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "segment_id",
          "segment_type",
          "source_text",
          "translated_text",
          "uncertainty_flags"
        ],
        "properties": {
          "segment_id": { "type": "string", "pattern": "^seg_[0-9]{4,}$" },
          "segment_type": {
            "type": "string",
            "enum": ["title", "ingredient_line", "instruction_line", "note", "other"]
          },
          "source_text": { "type": "string", "minLength": 1 },
          "translated_text": { "type": "string", "minLength": 1 },
          "uncertainty_flags": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": [
                "unknown_token",
                "ambiguous_ingredient",
                "ambiguous_modifier",
                "unresolved_unit",
                "ocr_noise"
              ]
            },
            "uniqueItems": true
          }
        }
      }
    }
  },
  "required": ["source_language", "output_language", "translated_text"]
}
```

- [ ] **Step 4: Update the translation prompt so stage 1 preserves semantics and does not normalize**

```text
<rules>
- Detect the source language conservatively and return it in `source_language`.
- Always return `output_language` as "en".
- Return the full English rendering in `translated_text`.
- Optionally return `segments` when you can separate title lines, ingredient lines, instruction lines, notes, or other lines confidently.
- Preserve quantities, units, timing, headings, and ordering.
- Do not normalize archive taxonomy.
- Do not infer missing quantities.
- Do not collapse contextual liquids into ingredient identities.
- Use `uncertainty_flags` when a segment is semantically ambiguous.
</rules>
```

- [ ] **Step 5: Add typed models and validation support for segmented stage-1 output**

```python
@dataclass
class TranslationSegment:
    segment_id: str
    segment_type: str
    source_text: str
    translated_text: str
    uncertainty_flags: list[str]


@dataclass
class TranslationArtifact:
    source_language: str
    output_language: str
    translated_text: str
    segments: list[TranslationSegment] = field(default_factory=list)
```

```python
def validate_preprocessing_payload(payload: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ...
    segments = payload.get("segments")
    if segments is not None:
        if not isinstance(segments, list):
            errors.append("Preprocessing field segments must be an array when present.")
        else:
            for index, segment in enumerate(segments, start=1):
                if not isinstance(segment, dict):
                    errors.append(f"Preprocessing segment {index} is not an object.")
                    continue
                for key in ("segment_id", "segment_type", "source_text", "translated_text", "uncertainty_flags"):
                    if key not in segment:
                        errors.append(f"Preprocessing segment {index} missing field: {key}")
    return errors
```

- [ ] **Step 6: Run the tests and verify they pass**

Run: `python3 -m pytest tests/test_normalize_recipes_rewrite.py -q`
Expected: PASS for the new stage-1 tests and all existing importer rewrite tests.

- [ ] **Step 7: Commit**

```bash
git add prompts/schemas/recipe-translation-output.schema.json \
  prompts/runtime/translation/recipe-translation-v1.md \
  scripts/import/recipe_import/transport.py \
  scripts/import/recipe_import/models.py \
  tests/test_normalize_recipes_rewrite.py
git commit -m "import: enrich stage-1 translation output"
```

---

### Task 2: Add Deterministic Stage-1.5 Reference Matching

**Files:**
- Create: `scripts/import/recipe_import/reference_match.py`
- Modify: `scripts/import/recipe_import/references.py`
- Modify: `scripts/import/recipe_import/models.py`
- Test: `tests/test_reference_match.py`

- [ ] **Step 1: Write the failing reference-match tests**

```python
def test_build_reference_match_detects_units_and_contextual_terms() -> None:
    artifact = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="1 tbsp relish\n1 tsp onion powder",
        segments=[
            TranslationSegment(
                segment_id="seg_0001",
                segment_type="ingredient_line",
                source_text="1 tsk spad från relish eller pickles",
                translated_text="1 tbsp relish",
                uncertainty_flags=[],
            ),
            TranslationSegment(
                segment_id="seg_0002",
                segment_type="ingredient_line",
                source_text="1 krm vitlökspulver",
                translated_text="1 tsp onion powder",
                uncertainty_flags=[],
            ),
        ],
    )

    match = build_reference_match(
        translation=artifact,
        render_profile="english_metric_strict",
        locale="en_generic",
    )

    assert "source_measurement_parity_changed" in match.drift_signals
    assert any(item.matched_entry_key == "spad från relish eller pickles" for item in match.contextual_matches)
    assert any(item.matched_entry_key == "vitlökspulver" for item in match.term_matches)
```

- [ ] **Step 2: Run the new test file to verify it fails**

Run: `python3 -m pytest tests/test_reference_match.py -q`
Expected: FAIL because `reference_match.py` and typed match models do not exist yet.

- [ ] **Step 3: Add typed match models**

```python
@dataclass
class ReferenceMatchItem:
    source_token: str
    matched_entry_key: str
    deterministic: bool
    requires_review: bool = False


@dataclass
class ReferenceMatchArtifact:
    pipeline_stage: str
    render_profile: str
    locale: str
    unit_matches: list[ReferenceMatchItem] = field(default_factory=list)
    term_matches: list[ReferenceMatchItem] = field(default_factory=list)
    contextual_matches: list[ReferenceMatchItem] = field(default_factory=list)
    drift_signals: list[str] = field(default_factory=list)
```

- [ ] **Step 4: Create the reference-match module with deterministic helpers**

```python
def build_reference_match(
    *,
    translation: TranslationArtifact,
    render_profile: str,
    locale: str,
) -> ReferenceMatchArtifact:
    artifact = ReferenceMatchArtifact(
        pipeline_stage="stage1_reference_match",
        render_profile=render_profile,
        locale=locale,
    )

    source_text = "\n".join(segment.source_text for segment in translation.segments) or translation.translated_text
    translated_text = translation.translated_text

    source_measurements = extract_measurement_signatures(source_text)
    translated_measurements = extract_measurement_signatures(translated_text)
    if source_measurements != translated_measurements:
        artifact.drift_signals.append("source_measurement_parity_changed")

    for entry in contextual_guard_terms():
        phrase = entry["swedish"]
        if phrase.casefold() in source_text.casefold():
            artifact.contextual_matches.append(
                ReferenceMatchItem(
                    source_token=phrase,
                    matched_entry_key=phrase,
                    deterministic=False,
                    requires_review=True,
                )
            )

    return artifact
```

- [ ] **Step 5: Expose any missing reusable helpers from `references.py`**

```python
@lru_cache(maxsize=1)
def term_lookup_keys() -> set[str]:
    reference = load_term_reference()
    keys: set[str] = set()
    for item in reference.get("ingredient_terms", []):
        swedish = str(item.get("swedish", "")).strip().casefold()
        if swedish:
            keys.add(swedish)
    return keys
```

- [ ] **Step 6: Run the focused tests and then the full importer test suite**

Run: `python3 -m pytest tests/test_reference_match.py -q`
Expected: PASS

Run: `python3 -m pytest tests/test_normalize_recipes_rewrite.py tests/test_reference_match.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/import/recipe_import/reference_match.py \
  scripts/import/recipe_import/references.py \
  scripts/import/recipe_import/models.py \
  tests/test_reference_match.py
git commit -m "import: add stage-1.5 reference matching"
```

---

### Task 3: Build an Explicit Stage-2 Normalization Request

**Files:**
- Create: `scripts/import/recipe_import/normalization_request.py`
- Modify: `scripts/import/recipe_import/pipeline.py`
- Modify: `scripts/import/recipe_import/models.py`
- Test: `tests/test_normalization_request.py`

- [ ] **Step 1: Write the failing stage-2 request assembly tests**

```python
def test_build_normalization_request_includes_translation_match_and_policy() -> None:
    translation = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="1 tsp pickle brine",
        segments=[],
    )
    match = ReferenceMatchArtifact(
        pipeline_stage="stage1_reference_match",
        render_profile="english_metric_strict",
        locale="en_generic",
        drift_signals=["source_measurement_parity_changed"],
    )

    payload = build_normalization_request(
        translation=translation,
        reference_match=match,
        render_profile="english_metric_strict",
        locale="en_generic",
    )

    assert payload["pipeline_stage"] == "stage2_normalization_request"
    assert payload["stage1_translation"]["translated_text"] == "1 tsp pickle brine"
    assert payload["stage1_reference_match"]["drift_signals"] == ["source_measurement_parity_changed"]
    assert payload["normalization_policy"]["preserve_source_authority"] is True
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m pytest tests/test_normalization_request.py -q`
Expected: FAIL because the request-builder module does not exist yet.

- [ ] **Step 3: Create the normalization request builder**

```python
def build_normalization_request(
    *,
    translation: TranslationArtifact,
    reference_match: ReferenceMatchArtifact,
    render_profile: str,
    locale: str,
) -> dict[str, Any]:
    return {
        "pipeline_stage": "stage2_normalization_request",
        "render_profile": render_profile,
        "locale": locale,
        "stage1_translation": asdict(translation),
        "stage1_reference_match": asdict(reference_match),
        "normalization_policy": {
            "preserve_source_authority": True,
            "preserve_non_exact_phrases": True,
            "allow_contextual_micro_unit_rendering": render_profile == "english_hybrid_natural",
            "volume_to_weight_requires_match": True,
        },
    }
```

- [ ] **Step 4: Route normalization request construction through the pipeline**

```python
translation_artifact = build_translation_artifact(preprocessing_payload, normalized_input_text, source_language)
reference_match = build_reference_match(
    translation=translation_artifact,
    render_profile="english_metric_strict",
    locale="en_generic",
)
normalization_request = build_normalization_request(
    translation=translation_artifact,
    reference_match=reference_match,
    render_profile="english_metric_strict",
    locale="en_generic",
)
user_prompt = json.dumps(normalization_request, ensure_ascii=True, indent=2)
```

- [ ] **Step 5: Keep backward-compatible source capture in the candidate bundle**

```python
source=SourceInfo(
    ...,
    raw_source_text=source_text,
    normalized_input_text=translation_artifact.translated_text,
)
```

- [ ] **Step 6: Run the new request-builder tests and the full suite**

Run: `python3 -m pytest tests/test_normalization_request.py -q`
Expected: PASS

Run: `python3 -m pytest tests/test_normalize_recipes_rewrite.py tests/test_reference_match.py tests/test_normalization_request.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/import/recipe_import/normalization_request.py \
  scripts/import/recipe_import/pipeline.py \
  scripts/import/recipe_import/models.py \
  tests/test_normalization_request.py
git commit -m "import: add explicit stage-2 normalization request"
```

---

### Task 4: Formalize Review-State Severity And Weak-Stage-1 Handling

**Files:**
- Modify: `scripts/import/recipe_import/pipeline.py`
- Modify: `scripts/import/recipe_import/models.py`
- Modify: `scripts/import/recipe_import/references.py`
- Modify: `tests/test_normalize_recipes_rewrite.py`

- [ ] **Step 1: Write failing tests for unusable stage-1 output and review escalation**

```python
def test_process_file_fails_when_stage1_translation_is_empty(tmp_path: Path, monkeypatch) -> None:
    source_path = tmp_path / "recipe.md"
    source_path.write_text("rå text", encoding="utf-8")

    def fake_run_preprocessing_contract(**_: object):
        return {"source_language": "sv", "output_language": "en", "translated_text": ""}, ""

    monkeypatch.setattr("recipe_import.pipeline.run_preprocessing_contract", fake_run_preprocessing_contract)

    with pytest.raises(ImporterFailure) as excinfo:
        process_file(...)

    assert excinfo.value.stage == "preprocess"


def test_process_file_escalates_translation_quality_review_flag(tmp_path: Path, monkeypatch) -> None:
    ...
    assert any("translation quality review required" in flag.lower() for flag in bundle.review_flags)
```

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python3 -m pytest tests/test_normalize_recipes_rewrite.py -q`
Expected: FAIL because weak-stage-1 escalation is not yet formalized.

- [ ] **Step 3: Add an explicit weak-stage-1 assessment helper**

```python
def assess_translation_quality(
    *,
    translation: TranslationArtifact,
    reference_match: ReferenceMatchArtifact,
) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    review_flags: list[str] = []

    if not translation.translated_text.strip():
        raise ImporterFailure("preprocess", "Preprocessing returned empty translated_text.")

    if "source_measurement_parity_changed" in reference_match.drift_signals:
        review_flags.append("Review preprocessing: translation quality review required due to measurement drift.")
    if len(reference_match.contextual_matches) >= 2:
        review_flags.append("Review preprocessing: translation quality review required due to multiple contextual-term risks.")
    return warnings, review_flags
```

- [ ] **Step 4: Merge severity assessment into the current warnings / `review_flags` flow**

```python
reference_warnings, reference_review_flags = collect_preprocessing_guardrails(...)
quality_warnings, quality_review_flags = assess_translation_quality(
    translation=translation_artifact,
    reference_match=reference_match,
)
reference_warnings.extend(quality_warnings)
reference_review_flags.extend(quality_review_flags)
```

- [ ] **Step 5: Run the importer tests again**

Run: `python3 -m pytest tests/test_normalize_recipes_rewrite.py tests/test_reference_match.py tests/test_normalization_request.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/import/recipe_import/pipeline.py \
  scripts/import/recipe_import/models.py \
  scripts/import/recipe_import/references.py \
  tests/test_normalize_recipes_rewrite.py
git commit -m "import: formalize stage-1 fallback and review severity"
```

---

### Task 5: Preserve Candidate-Bundle Compatibility And Add End-To-End Swedish Fixture Coverage

**Files:**
- Modify: `tests/test_normalize_recipes_rewrite.py`
- Modify: `tests/test_reference_match.py`
- Modify: `tests/test_normalization_request.py`
- Test: existing importer entrypoint and live LM Studio verification

- [ ] **Step 1: Add a compatibility test that stage-2 still emits existing candidate fields**

```python
def test_build_bundle_remains_candidate_compatible_with_enriched_pipeline() -> None:
    bundle = build_bundle(
        ...,
        raw_payload=normalization_payload(title="Burgarsås"),
        initial_warnings=["Preprocessing changed or dropped source measurements: 5 ml."],
        initial_review_flags=["Review preprocessing: source measurement parity changed between Swedish source and normalized input text."],
    )

    data = bundle.to_dict()
    assert data["candidate"]["candidate_update"]["title"] == "Burgarsås"
    assert "review_flags" in data
    assert "warnings" in data
```

- [ ] **Step 2: Add a Swedish fixture regression based on `Burgarsås` semantics**

```python
def test_reference_match_burgarsas_semantics() -> None:
    translation = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="1 tbsp relish\n1 tsp onion powder\nMix together.",
        segments=[
            TranslationSegment(
                segment_id="seg_0001",
                segment_type="ingredient_line",
                source_text="1 tsk spad från relish eller pickles",
                translated_text="1 tbsp relish",
                uncertainty_flags=[],
            ),
            TranslationSegment(
                segment_id="seg_0002",
                segment_type="ingredient_line",
                source_text="1 krm vitlökspulver",
                translated_text="1 tsp onion powder",
                uncertainty_flags=[],
            ),
        ],
    )
    match = build_reference_match(translation=translation, render_profile="english_metric_strict", locale="en_generic")
    assert "source_measurement_parity_changed" in match.drift_signals
```

- [ ] **Step 3: Run all local tests**

Run: `python3 -m pytest tests/test_normalize_recipes_rewrite.py tests/test_reference_match.py tests/test_normalization_request.py -q`
Expected: PASS

- [ ] **Step 4: Run compile verification**

Run: `python3 -m py_compile scripts/import/normalize_recipes.py scripts/import/recipe_import/*.py tests/test_normalize_recipes_rewrite.py tests/test_reference_match.py tests/test_normalization_request.py`
Expected: no output

- [ ] **Step 5: Run a realistic single-file importer flow**

Run:

```bash
python3 scripts/import/normalize_recipes.py \
  /tmp/semantics-preprocessed \
  --file data/imports/raw/recipes/Burgarsås.md \
  --model translategemma-4b-it \
  --base-url http://192.168.1.91:1234/v1 \
  --preprocess-only \
  --overwrite \
  --report-dir /tmp/semantics-reports-pre
```

Expected: `/tmp/semantics-preprocessed/Burgarsås.preprocessed.txt` is created.

Run:

```bash
python3 scripts/import/normalize_recipes.py \
  /tmp/semantics-output \
  --file data/imports/raw/recipes/Burgarsås.md \
  --model qwen2.5-7b-instruct \
  --base-url http://192.168.1.91:1234/v1 \
  --use-preprocessed-dir /tmp/semantics-preprocessed \
  --overwrite \
  --report-dir /tmp/semantics-reports
```

Expected: emitted candidate bundle includes semantic warnings and `review_flags` rather than silently trusting preprocessing drift.

- [ ] **Step 6: Commit**

```bash
git add tests/test_normalize_recipes_rewrite.py \
  tests/test_reference_match.py \
  tests/test_normalization_request.py
git commit -m "test: add semantic pipeline regression coverage"
```

---

### Task 6: Rewrite Implementation-Aware Documentation To Match The New Pipeline

**Files:**
- Modify: `README.md`
- Modify: `docs/10_imports/recipe-import-workflow.md`
- Modify: `docs/10_imports/implemented-imports.md`
- Modify: `docs/05_ai/implemented-ai.md`

- [ ] **Step 1: Add failing doc-drift checks via targeted review notes in the plan**

```text
Expected drift to remove:
- translation stage described as text-only
- missing stage-1.5 reference matching
- missing explicit render policy and fallback semantics
```

- [ ] **Step 2: Rewrite the README import summary**

```md
Swedish-source imports now run through:

1. stage-1 translation / preprocessing
2. stage-1.5 reference matching against active Swedish reference assets
3. stage-2 normalization into candidate bundles

The final candidate format remains backward-compatible with the existing review workflow.
```

- [ ] **Step 3: Rewrite the implementation-aware import docs**

```md
Current implemented behavior now includes:

* enriched stage-1 translation artifacts with backward-compatible `translated_text`
* deterministic stage-1.5 reference matching
* explicit stage-2 normalization request assembly
* stronger weak-stage-1 fallback and review-state escalation
```

- [ ] **Step 4: Review docs for contradiction against current code**

Run: `rg -n "translated_text|reference matching|stage-1.5|render policy|review_flags" README.md docs/10_imports docs/05_ai/implemented-ai.md`
Expected: updated wording appears in the implementation-aware docs and no stale text-only-stage claims remain.

- [ ] **Step 5: Commit**

```bash
git add README.md \
  docs/10_imports/recipe-import-workflow.md \
  docs/10_imports/implemented-imports.md \
  docs/05_ai/implemented-ai.md
git commit -m "docs: align importer docs with semantic pipeline"
```

---

## Self-Review

### Spec coverage

- Proposal 1 rationale is covered by Tasks 1-4.
- Proposal 2 staged contract is covered by Tasks 1-4.
- Proposal 2 render policy and canonical reference ownership are covered by Tasks 2-4 and Task 6 documentation updates.
- Proposal 2 weak-stage-1 fallback is covered by Task 4.
- Proposal 2 worked `Burgarsås` example is covered by Task 5.
- Proposal 3 migration path is reflected in the task order.

### Placeholder scan

- No `TODO`, `TBD`, or “implement later” placeholders remain.
- All code-touching tasks include concrete code or payload shapes.
- All test steps include exact commands.

### Type consistency

- Stage-1 models use `TranslationArtifact` and `TranslationSegment`.
- Stage-1.5 uses `ReferenceMatchArtifact` and `ReferenceMatchItem`.
- Stage-2 request assembly consistently refers to `build_normalization_request()`.

---

Plan complete and saved to `docs/superpowers/plans/2026-03-30-semantics-first-swedish-import-pipeline.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
