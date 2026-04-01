# Broad Swedish Import Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the current Swedish recipe importer so it broadly preserves structured culinary meaning across many recipes, not just single-file fixes, by adding deterministic source parsing, protected measurement handling, richer operational references, structured drift codes, and taxonomy-safe postprocessing.

**Architecture:** Keep the current staged importer shape in `scripts/import/recipe_import/`, but insert more deterministic structure before and after model calls. Stage 0 parses common Swedish recipe lines into structured evidence, stage 1 preserves semantics with protected tokens, stage 1.5 matches references and emits structured drift codes, and stage 2 normalization is followed by a controlled-vocabulary mapper before bundle emission.

**Tech Stack:** Python 3, JSON files under `data/reference/`, LM Studio OpenAI-compatible APIs, existing importer modules under `scripts/import/recipe_import/`, `pytest`, current candidate-bundle and `review_candidates.py` workflow.

---

## File Structure Map

### Existing files to modify

- `data/reference/swedish_recipe_units.json`
  Purpose: expand from alias/support data into a broader operational unit reference with parsing behavior, ambiguity policy, and protected-token metadata.
- `data/reference/swedish_recipe_terms.json`
  Purpose: expand from core terms into categorized importer data with ingredient, modifier, technique, time, and context-term behavior.
- `scripts/import/recipe_import/models.py`
  Purpose: add typed stage-0 parse artifacts, protected-token artifacts, drift-code records, and taxonomy-map records.
- `scripts/import/recipe_import/references.py`
  Purpose: load richer references, expose deterministic matching utilities, and stop relying on warning text as the primary contract.
- `scripts/import/recipe_import/reference_match.py`
  Purpose: evolve matching into a first-class stage that returns structured codes, protected-token parity, and contextual semantics.
- `scripts/import/recipe_import/normalization_request.py`
  Purpose: consume stage-0 and stage-1.5 artifacts so stage 2 gets structured evidence instead of just translated text.
- `scripts/import/recipe_import/pipeline.py`
  Purpose: orchestrate stage 0 parsing, protected-token validation, structured severity policy, taxonomy-safe postprocessing, and candidate-bundle emission.
- `scripts/import/recipe_import/transforms.py`
  Purpose: accept taxonomy-safe mappings and preserve structured source hints instead of dropping them.
- `prompts/runtime/translation/recipe-translation-v1.md`
  Purpose: tell stage 1 to preserve protected tokens and semantic structure without normalizing.
- `prompts/runtime/normalization/recipe-normalization-v1.md`
  Purpose: tell stage 2 how to use structured source evidence, protected units, and reference matches conservatively.
- `tests/test_normalize_recipes_rewrite.py`
  Purpose: keep end-to-end importer regression coverage.
- `docs/10_imports/recipe-import-workflow.md`
  Purpose: document the broader pipeline stages and review-state policy.
- `docs/10_imports/implemented-imports.md`
  Purpose: keep implementation-aware docs aligned with the new parser/matcher/mapping stages.
- `README.md`
  Purpose: refresh operator-facing importer workflow where needed.

### New files to create

- `scripts/import/recipe_import/source_parse.py`
  Purpose: deterministic Swedish source-line parser for ingredient lines, time lines, difficulty lines, method lines, and serving lines.
- `scripts/import/recipe_import/protected_tokens.py`
  Purpose: extract and compare protected quantities, units, and context-sensitive spans across source and translation.
- `scripts/import/recipe_import/severity_policy.py`
  Purpose: convert structured drift codes into warnings, review flags, and approval-blocking outcomes.
- `scripts/import/recipe_import/taxonomy_map.py`
  Purpose: map near-match stage-2 output values into allowed repo vocabulary where safe.
- `data/reference/swedish_recipe_false_friends.json`
  Purpose: store high-risk Swedish culinary terms and contextual traps that should never be treated as free translation.
- `tests/test_source_parse.py`
  Purpose: fixture coverage for broad Swedish source parsing behavior.
- `tests/test_protected_tokens.py`
  Purpose: fixture coverage for unit and quantity preservation.
- `tests/test_taxonomy_map.py`
  Purpose: fixture coverage for controlled-vocabulary mapping.
- `tests/fixtures/import/swedish/`
  Purpose: broad Swedish source fixtures across units, powder/spice distinctions, brine/liquid terms, time phrases, and mixed-language content.

### Files that should remain stable

- `scripts/import/review_candidates.py`
  Purpose: continue consuming emitted candidate bundles without requiring a new review tool.
- `prompts/schemas/recipe-normalization-output.schema.json`
  Purpose: keep final normalization output shape stable in the first hardening pass.

---

### Task 1: Add Stage-0 Swedish Source Parsing

**Files:**
- Create: `scripts/import/recipe_import/source_parse.py`
- Modify: `scripts/import/recipe_import/models.py`
- Test: `tests/test_source_parse.py`

- [ ] **Step 1: Write the failing parser tests for broad Swedish line extraction**

```python
from recipe_import.source_parse import parse_source_text


def test_parse_source_text_extracts_common_recipe_fields() -> None:
    parsed = parse_source_text(
        "Recipe title\n"
        "Difficulty: Enkel\n"
        "Ingredients: 1 dl majonnäs, 1 tsk lökpulver.\n"
        "Preparation time: 10 min + vila\n"
        "Cooking process: Rörs kall\n"
        "Serves: 2 burgare\n"
    )

    assert parsed.title_lines == ["Recipe title"]
    assert parsed.difficulty_lines == ["Difficulty: Enkel"]
    assert parsed.ingredient_lines == ["1 dl majonnäs", "1 tsk lökpulver"]
    assert parsed.time_lines == ["Preparation time: 10 min + vila"]
    assert parsed.method_lines == ["Cooking process:"]
    assert parsed.instruction_lines == ["Rörs kall"]
    assert parsed.serving_lines == ["Serves: 2 burgare"]


def test_parse_source_text_handles_swedish_headings_multiline_sections_and_decimal_commas() -> None:
    parsed = parse_source_text(
        "Recepttitel\n"
        "Svårighetsgrad: Enkel\n"
        "Ingredienser:\n"
        "1,5 dl mjölk, 2 ägg\n"
        "1 nypa salt\n"
        "Tillagning:\n"
        "Vispa ihop\n"
        "Stek i panna\n"
        "Ger: 2 burgare\n"
    )

    assert parsed.title_lines == ["Recepttitel"]
    assert parsed.difficulty_lines == ["Svårighetsgrad: Enkel"]
    assert parsed.ingredient_lines == ["1,5 dl mjölk", "2 ägg", "1 nypa salt"]
    assert parsed.method_lines == ["Tillagning:"]
    assert parsed.instruction_lines == ["Vispa ihop", "Stek i panna"]
    assert parsed.serving_lines == ["Ger: 2 burgare"]
```

- [ ] **Step 2: Run the focused parser tests to verify they fail**

Run: `python3 -m pytest tests/test_source_parse.py -q`
Expected: FAIL with `ModuleNotFoundError` or missing parser behavior.

- [ ] **Step 3: Add minimal typed models for parsed source evidence**

```python
@dataclass
class ParsedSource:
    title_lines: list[str] = field(default_factory=list)
    ingredient_lines: list[str] = field(default_factory=list)
    instruction_lines: list[str] = field(default_factory=list)
    note_lines: list[str] = field(default_factory=list)
    time_lines: list[str] = field(default_factory=list)
    difficulty_lines: list[str] = field(default_factory=list)
    method_lines: list[str] = field(default_factory=list)
    serving_lines: list[str] = field(default_factory=list)
```

- [ ] **Step 4: Implement the minimal deterministic parser**

```python
INGREDIENT_SPLIT_PATTERN = re.compile(r"(?<!\d),(?!\d)")


def parse_source_text(source_text: str) -> ParsedSource:
    parsed = ParsedSource()
    active_section: str | None = None
    seen_structured_heading = False
    for raw_line in source_text.splitlines():
        line = raw_line.strip()
        if not line:
            active_section = None
            continue
        lowered = line.casefold()
        if lowered.startswith("difficulty:"):
            seen_structured_heading = True
            parsed.difficulty_lines.append(line)
            active_section = None
        elif lowered.startswith("ingredients:"):
            seen_structured_heading = True
            payload = line.split(":", 1)[1]
            parsed.ingredient_lines.extend(part.strip() for part in INGREDIENT_SPLIT_PATTERN.split(payload) if part.strip())
            active_section = "ingredients"
        elif lowered.startswith("preparation time:") or lowered.startswith("cooking time:"):
            seen_structured_heading = True
            parsed.time_lines.append(line)
            active_section = None
        elif lowered.startswith("cooking process:") or lowered.startswith("cooking method:"):
            seen_structured_heading = True
            heading, _, payload = line.partition(":")
            parsed.method_lines.append(f"{heading}:")
            if payload.strip():
                parsed.instruction_lines.append(payload.strip())
            active_section = "instructions"
        elif lowered.startswith("serves:"):
            seen_structured_heading = True
            parsed.serving_lines.append(line)
            active_section = None
        elif active_section == "ingredients":
            parsed.ingredient_lines.extend(part.strip() for part in INGREDIENT_SPLIT_PATTERN.split(line) if part.strip())
        elif active_section == "instructions":
            parsed.instruction_lines.append(line)
        else:
            if seen_structured_heading:
                parsed.note_lines.append(line)
            else:
                parsed.title_lines.append(line)
    return parsed
```

- [ ] **Step 5: Run the parser tests and verify they pass**

Run: `python3 -m pytest tests/test_source_parse.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/import/recipe_import/source_parse.py \
  scripts/import/recipe_import/models.py \
  tests/test_source_parse.py
git commit -m "import: add stage-0 Swedish source parser"
```

---

### Task 2: Protect Quantities and Units Before Translation Drift

**Files:**
- Create: `scripts/import/recipe_import/protected_tokens.py`
- Modify: `data/reference/swedish_recipe_units.json`
- Modify: `scripts/import/recipe_import/models.py`
- Test: `tests/test_protected_tokens.py`

- [ ] **Step 1: Write the failing protected-token tests**

```python
from recipe_import.protected_tokens import extract_protected_tokens, compare_protected_tokens


def test_extract_protected_tokens_keeps_swedish_measurements() -> None:
    tokens = extract_protected_tokens("1 tsk spad från relish eller pickles\n1 dl majonnäs\n1 nypa salt")
    assert [token.normalized_unit for token in tokens] == ["tsk", "dl", "nypa"]


def test_compare_protected_tokens_flags_measurement_drift() -> None:
    source_tokens = extract_protected_tokens("1 tsk salt")
    translated_tokens = extract_protected_tokens("1 tbsp salt")
    drift = compare_protected_tokens(source_tokens, translated_tokens)
    assert "measurement_drift" in [code.code for code in drift]
```

- [ ] **Step 2: Run the protected-token tests to verify they fail**

Run: `python3 -m pytest tests/test_protected_tokens.py -q`
Expected: FAIL with missing module or drift comparison.

- [ ] **Step 3: Expand the units reference with behavior fields**

```json
{
  "canonical_units": {
    "tsk": {
      "aliases": ["tsk", "tesked", "teskedar", "tsp", "teaspoon", "teaspoons"],
      "category": "volume_spoon",
      "protected": true,
      "allow_naturalized_render": false,
      "ambiguity_policy": "review_on_change"
    }
  }
}
```

- [ ] **Step 4: Add typed protected-token models**

```python
@dataclass
class ProtectedToken:
    source_text: str
    quantity_text: str
    normalized_quantity: str
    unit_text: str
    normalized_unit: str
    line_role: str


@dataclass
class DriftCode:
    code: str
    severity: str
    message: str
```

- [ ] **Step 5: Implement minimal extraction and parity comparison**

```python
MEASUREMENT_PATTERN = re.compile(r"(?P<quantity>[0-9]+(?:[.,][0-9]+)?|[0-9]+/[0-9]+)\s*(?P<unit>[A-Za-zåäöÅÄÖ]+)")


def extract_protected_tokens(text: str) -> list[ProtectedToken]:
    tokens: list[ProtectedToken] = []
    for line in text.splitlines():
        match = MEASUREMENT_PATTERN.search(line)
        if not match:
            continue
        normalized_unit = normalize_reference_unit(match.group("unit"))
        if not normalized_unit:
            continue
        tokens.append(
            ProtectedToken(
                source_text=line.strip(),
                quantity_text=match.group("quantity"),
                normalized_quantity=match.group("quantity").replace(",", "."),
                unit_text=match.group("unit"),
                normalized_unit=normalized_unit,
                line_role="unknown",
            )
        )
    return tokens


def compare_protected_tokens(source: list[ProtectedToken], translated: list[ProtectedToken]) -> list[DriftCode]:
    drift: list[DriftCode] = []
    for source_token, translated_token in zip(source, translated):
        if source_token.normalized_unit != translated_token.normalized_unit:
            drift.append(DriftCode("measurement_drift", "review_flag", "Protected measurement unit changed."))
    return drift
```

- [ ] **Step 6: Run the protected-token tests and verify they pass**

Run: `python3 -m pytest tests/test_protected_tokens.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add data/reference/swedish_recipe_units.json \
  scripts/import/recipe_import/models.py \
  scripts/import/recipe_import/protected_tokens.py \
  tests/test_protected_tokens.py
git commit -m "import: protect Swedish quantity and unit tokens"
```

---

### Task 3: Expand the Operational Swedish Lexicon

**Files:**
- Modify: `data/reference/swedish_recipe_terms.json`
- Create: `data/reference/swedish_recipe_false_friends.json`
- Modify: `scripts/import/recipe_import/references.py`
- Test: `tests/test_reference_match.py`

- [ ] **Step 1: Write the failing lexicon behavior tests**

```python
from recipe_import.references import preferred_semantic_targets_for_term


def test_preferred_semantic_targets_for_context_term_are_explicit() -> None:
    targets = preferred_semantic_targets_for_term("spad från relish eller pickles")
    assert "pickle brine" in targets
    assert "juice from relish or pickles" in targets


def test_false_friend_terms_are_loaded() -> None:
    targets = preferred_semantic_targets_for_term("vitlökspulver")
    assert "garlic powder" in targets
```

- [ ] **Step 2: Run the reference-match tests to verify they fail**

Run: `python3 -m pytest tests/test_reference_match.py -q`
Expected: FAIL with missing explicit term behavior or false-friend data.

- [ ] **Step 3: Expand `swedish_recipe_terms.json` into categorized importer data**

```json
{
  "terms": {
    "vitlökspulver": {
      "category": "ingredient",
      "preferred_english": ["garlic powder"],
      "allow_naturalized_render": false,
      "drift_policy": "review_on_semantic_change"
    },
    "rörs kall": {
      "category": "technique_phrase",
      "preferred_english": ["mixed cold", "stirred cold"],
      "allow_naturalized_render": false,
      "drift_policy": "review_on_loss"
    }
  }
}
```

- [ ] **Step 4: Add a dedicated false-friends reference**

```json
{
  "false_friends": {
    "vitlökspulver": {
      "never_map_to": ["onion powder"],
      "reason": "garlic vs onion semantic substitution"
    },
    "lökpulver": {
      "never_map_to": ["garlic powder"],
      "reason": "onion vs garlic semantic substitution"
    }
  }
}
```

- [ ] **Step 5: Implement minimal lookup helpers**

```python
def preferred_semantic_targets_for_term(term: str) -> list[str]:
    entry = TERM_REFERENCE.get(term.casefold())
    if not entry:
        return []
    return list(entry.get("preferred_english", []))


def forbidden_semantic_targets_for_term(term: str) -> list[str]:
    entry = FALSE_FRIEND_REFERENCE.get(term.casefold())
    if not entry:
        return []
    return list(entry.get("never_map_to", []))
```

- [ ] **Step 6: Run the reference tests and verify they pass**

Run: `python3 -m pytest tests/test_reference_match.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add data/reference/swedish_recipe_terms.json \
  data/reference/swedish_recipe_false_friends.json \
  scripts/import/recipe_import/references.py \
  tests/test_reference_match.py
git commit -m "import: expand Swedish operational lexicon"
```

---

### Task 4: Replace Warning-Text Heuristics With Structured Drift Codes

**Files:**
- Create: `scripts/import/recipe_import/severity_policy.py`
- Modify: `scripts/import/recipe_import/reference_match.py`
- Modify: `scripts/import/recipe_import/pipeline.py`
- Test: `tests/test_reference_match.py`
- Test: `tests/test_normalize_recipes_rewrite.py`

- [ ] **Step 1: Write the failing drift-code tests**

```python
from recipe_import.reference_match import build_reference_match
from recipe_import.pipeline import assess_translation_quality


def test_reference_match_emits_structured_measurement_drift_code(preprocessing_artifact) -> None:
    match = build_reference_match(
        translation=preprocessing_artifact,
        render_profile="english_metric_strict",
        locale="en-SE",
    )
    assert "measurement_drift" in [code.code for code in match.drift_codes]


def test_assess_translation_quality_uses_drift_codes_not_warning_strings(preprocessing_artifact) -> None:
    match = build_reference_match(
        translation=preprocessing_artifact,
        render_profile="english_metric_strict",
        locale="en-SE",
    )
    warnings, flags = assess_translation_quality(translation=preprocessing_artifact, reference_match=match)
    assert any("measurement parity" in flag.lower() for flag in flags)
```

- [ ] **Step 2: Run the focused importer tests to verify they fail**

Run: `python3 -m pytest tests/test_reference_match.py tests/test_normalize_recipes_rewrite.py -q`
Expected: FAIL because `drift_codes` and severity policy do not exist yet.

- [ ] **Step 3: Add typed drift-code and severity-policy structures**

```python
@dataclass
class ReferenceMatch:
    matched_terms: list[str] = field(default_factory=list)
    protected_tokens: list[ProtectedToken] = field(default_factory=list)
    drift_codes: list[DriftCode] = field(default_factory=list)
```

```python
SEVERITY_POLICY = {
    "measurement_drift": "review_flag",
    "contextual_liquid_drift": "review_flag",
    "false_friend_drift": "review_flag",
    "taxonomy_near_match": "warning",
    "multiple_ingredient_split_risk": "review_flag",
}
```

- [ ] **Step 4: Emit structured drift codes from reference matching**

```python
if source_token.normalized_unit != translated_token.normalized_unit:
    drift_codes.append(
        DriftCode(
            code="measurement_drift",
            severity="review_flag",
            message="Protected measurement unit changed between source and translation.",
        )
    )
```

- [ ] **Step 5: Convert drift codes into warnings and review flags**

```python
def evaluate_drift_codes(drift_codes: list[DriftCode]) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    review_flags: list[str] = []
    for code in drift_codes:
        if code.severity == "warning":
            warnings.append(code.message)
        elif code.severity == "review_flag":
            review_flags.append(code.message)
    return warnings, review_flags
```

- [ ] **Step 6: Run the focused tests and verify they pass**

Run: `python3 -m pytest tests/test_reference_match.py tests/test_normalize_recipes_rewrite.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/import/recipe_import/severity_policy.py \
  scripts/import/recipe_import/reference_match.py \
  scripts/import/recipe_import/pipeline.py \
  tests/test_reference_match.py \
  tests/test_normalize_recipes_rewrite.py
git commit -m "import: replace warning text heuristics with drift codes"
```

---

### Task 5: Add Controlled Vocabulary Mapping After Stage 2

**Files:**
- Create: `scripts/import/recipe_import/taxonomy_map.py`
- Modify: `scripts/import/recipe_import/transforms.py`
- Modify: `scripts/import/recipe_import/pipeline.py`
- Test: `tests/test_taxonomy_map.py`
- Test: `tests/test_normalize_recipes_rewrite.py`

- [ ] **Step 1: Write the failing taxonomy-map tests**

```python
from recipe_import.taxonomy_map import map_taxonomy_value


def test_map_taxonomy_value_maps_safe_near_match() -> None:
    result = map_taxonomy_value(field_name="complexity", raw_value="easy")
    assert result.mapped_value == "Basic"
    assert result.requires_review is False


def test_map_taxonomy_value_leaves_unknown_values_unmapped() -> None:
    result = map_taxonomy_value(field_name="technique_family", raw_value="molecular vapor")
    assert result.mapped_value is None
    assert result.requires_review is True
```

- [ ] **Step 2: Run the taxonomy-map tests to verify they fail**

Run: `python3 -m pytest tests/test_taxonomy_map.py -q`
Expected: FAIL with missing module.

- [ ] **Step 3: Add minimal taxonomy-map behavior**

```python
SAFE_TAXONOMY_MAP = {
    "complexity": {
        "easy": "Basic",
    },
    "time_class": {
        "short": "15–30 min",
    },
}
```

```python
def map_taxonomy_value(*, field_name: str, raw_value: str | None) -> TaxonomyMapResult:
    if raw_value is None:
        return TaxonomyMapResult(mapped_value=None, requires_review=False, warning=None)
    normalized = raw_value.strip().casefold()
    mapped = SAFE_TAXONOMY_MAP.get(field_name, {}).get(normalized)
    if mapped:
        return TaxonomyMapResult(mapped_value=mapped, requires_review=False, warning=None)
    return TaxonomyMapResult(
        mapped_value=None,
        requires_review=True,
        warning=f"{field_name} value '{raw_value}' not in allowed vocabulary",
    )
```

- [ ] **Step 4: Apply mapping before bundle emission**

```python
for field_name in ("technique_family", "complexity", "time_class"):
    mapping = map_taxonomy_value(field_name=field_name, raw_value=payload.get(field_name))
    if mapping.mapped_value is not None:
        payload[field_name] = mapping.mapped_value
```

- [ ] **Step 5: Run the focused tests and verify they pass**

Run: `python3 -m pytest tests/test_taxonomy_map.py tests/test_normalize_recipes_rewrite.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/import/recipe_import/taxonomy_map.py \
  scripts/import/recipe_import/transforms.py \
  scripts/import/recipe_import/pipeline.py \
  tests/test_taxonomy_map.py \
  tests/test_normalize_recipes_rewrite.py
git commit -m "import: map safe taxonomy near-matches"
```

---

### Task 6: Feed Parsed Source and Protected Tokens Into Stage 2

**Files:**
- Modify: `scripts/import/recipe_import/normalization_request.py`
- Modify: `scripts/import/recipe_import/pipeline.py`
- Modify: `prompts/runtime/normalization/recipe-normalization-v1.md`
- Test: `tests/test_normalization_request.py`
- Test: `tests/test_normalize_recipes_rewrite.py`

- [ ] **Step 1: Write the failing request-assembly tests**

```python
from recipe_import.normalization_request import build_normalization_request


def test_build_normalization_request_includes_parsed_source_and_protected_tokens(preprocessing_artifact) -> None:
    request = build_normalization_request(
        translation=preprocessing_artifact,
        reference_match=reference_match,
        parsed_source=parsed_source,
        render_profile="english_metric_strict",
        locale="en-SE",
    )
    assert request["stage0_source_parse"]["ingredient_lines"]
    assert request["stage1_reference_match"]["protected_tokens"]
```

- [ ] **Step 2: Run the request-assembly tests to verify they fail**

Run: `python3 -m pytest tests/test_normalization_request.py -q`
Expected: FAIL because `parsed_source` and `protected_tokens` are not part of the request.

- [ ] **Step 3: Extend the request builder**

```python
def build_normalization_request(
    *,
    translation: TranslationArtifact,
    reference_match: ReferenceMatch,
    parsed_source: ParsedSource,
    render_profile: str,
    locale: str,
) -> dict[str, Any]:
    return {
        "pipeline_stage": "stage2_normalization_request",
        "stage0_source_parse": parsed_source.to_dict(),
        "stage1_translation": translation.to_dict(),
        "stage1_reference_match": reference_match.to_dict(),
        "render_profile": render_profile,
        "locale": locale,
    }
```

- [ ] **Step 4: Update the normalization prompt to treat protected tokens as immutable**

```text
<stage2_rules>
- Use `stage0_source_parse` and `stage1_reference_match` as grounding evidence.
- Preserve protected quantities and units unless the structured evidence explicitly marks a safe conversion.
- Do not rewrite contextual-liquid terms into ingredient identities unless the translated segment already resolved them clearly.
- Prefer explicit source evidence over stylistic naturalization.
</stage2_rules>
```

- [ ] **Step 5: Run the focused tests and verify they pass**

Run: `python3 -m pytest tests/test_normalization_request.py tests/test_normalize_recipes_rewrite.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/import/recipe_import/normalization_request.py \
  scripts/import/recipe_import/pipeline.py \
  prompts/runtime/normalization/recipe-normalization-v1.md \
  tests/test_normalization_request.py \
  tests/test_normalize_recipes_rewrite.py
git commit -m "import: ground stage 2 in parsed source evidence"
```

---

### Task 7: Build Broad Swedish Fixture Coverage

**Files:**
- Create: `tests/fixtures/import/swedish/units-and-fractions.md`
- Create: `tests/fixtures/import/swedish/powders-and-spices.md`
- Create: `tests/fixtures/import/swedish/brines-and-context-liquids.md`
- Create: `tests/fixtures/import/swedish/times-and-rest.md`
- Create: `tests/fixtures/import/swedish/mixed-language-notes.md`
- Modify: `tests/test_normalize_recipes_rewrite.py`
- Modify: `tests/test_source_parse.py`
- Modify: `tests/test_protected_tokens.py`

- [ ] **Step 1: Write fixture-driven tests for behavior families**

```python
@pytest.mark.parametrize(
    "fixture_name,expected_unit",
    [
        ("units-and-fractions.md", "tsk"),
        ("powders-and-spices.md", "tsk"),
    ],
)
def test_source_fixtures_preserve_expected_units(fixture_name: str, expected_unit: str) -> None:
    source_text = (FIXTURE_ROOT / fixture_name).read_text(encoding="utf-8")
    tokens = extract_protected_tokens(source_text)
    assert any(token.normalized_unit == expected_unit for token in tokens)
```

- [ ] **Step 2: Run the fixture tests to verify they fail**

Run: `python3 -m pytest tests/test_source_parse.py tests/test_protected_tokens.py tests/test_normalize_recipes_rewrite.py -q`
Expected: FAIL until the fixtures exist and broad parser behavior is wired in.

- [ ] **Step 3: Add broad Swedish source fixtures**

```text
Ingredients: 1 tsk dijonsenap, 1/2 msk vitvinsvinäger, 2 dl grädde.
Preparation time: 15 min + vila
Cooking process: Rörs kall
```

```text
Ingredients: 1 tsk vitlökspulver, 1 tsk lökpulver, 1 tsk paprikapulver.
```

- [ ] **Step 4: Run the fixture tests and verify they pass**

Run: `python3 -m pytest tests/test_source_parse.py tests/test_protected_tokens.py tests/test_normalize_recipes_rewrite.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/import/swedish \
  tests/test_source_parse.py \
  tests/test_protected_tokens.py \
  tests/test_normalize_recipes_rewrite.py
git commit -m "import: add broad Swedish importer fixtures"
```

---

### Task 8: Align Docs With the Hardened Pipeline

**Files:**
- Modify: `README.md`
- Modify: `docs/10_imports/recipe-import-workflow.md`
- Modify: `docs/10_imports/implemented-imports.md`

- [ ] **Step 1: Write the failing documentation assertions as a manual checklist**

```text
- README must mention that Swedish imports use deterministic source parsing and protected measurement handling.
- recipe-import-workflow.md must describe stage 0, protected-token validation, structured drift codes, and taxonomy mapping.
- implemented-imports.md must describe what is actually implemented today, not target-state ideas.
```

- [ ] **Step 2: Verify the current docs are incomplete**

Run: `rg -n "stage 0|protected token|taxonomy mapping|drift code" README.md docs/10_imports/recipe-import-workflow.md docs/10_imports/implemented-imports.md`
Expected: missing or partial coverage.

- [ ] **Step 3: Update the docs**

```markdown
1. Stage 0 parses common Swedish recipe lines into structured source evidence.
2. Protected quantities and units are validated before normalization.
3. Reference matching emits structured drift codes that drive warnings and review flags.
4. Safe taxonomy near-matches are mapped before bundle emission; unresolved values remain reviewable.
```

- [ ] **Step 4: Run the checklist and deterministic verification**

Run: `python3 -m pytest tests/test_normalize_recipes_rewrite.py tests/test_source_parse.py tests/test_protected_tokens.py tests/test_reference_match.py tests/test_normalization_request.py tests/test_taxonomy_map.py -q`
Expected: PASS

Run: `python3 -m py_compile scripts/import/normalize_recipes.py scripts/import/review_candidates.py scripts/import/recipe_import/*.py tests/test_normalize_recipes_rewrite.py tests/test_source_parse.py tests/test_protected_tokens.py tests/test_reference_match.py tests/test_normalization_request.py tests/test_taxonomy_map.py`
Expected: no output

- [ ] **Step 5: Commit**

```bash
git add README.md \
  docs/10_imports/recipe-import-workflow.md \
  docs/10_imports/implemented-imports.md
git commit -m "docs: describe hardened Swedish import pipeline"
```

---

## Self-Review

- Spec coverage:
  - deterministic Swedish source parsing: Task 1
  - quantity and unit preservation: Task 2
  - broader operational lexicon: Task 3
  - structured drift codes and severity policy: Task 4
  - controlled vocabulary mapping: Task 5
  - stage-2 grounding on structured evidence: Task 6
  - broad behavior-family tests: Task 7
  - implementation-aware docs: Task 8
- Placeholder scan:
  - no `TODO`, `TBD`, or “similar to previous task” shortcuts remain
  - each task includes files, tests, implementation snippets, verification commands, and commit steps
- Type consistency:
  - `ParsedSource`, `ProtectedToken`, `DriftCode`, `ReferenceMatch`, and taxonomy mapping are introduced once and reused consistently

## Notes

- This plan intentionally keeps `review_candidates.py` and the final normalization output schema stable in the first hardening pass.
- The current two canonical reference files remain canonical. New reference files such as `swedish_recipe_false_friends.json` are additive, not replacements.
- The first implementation pass should not attempt OCR, RAG, or a new approval UI. Those are follow-up projects.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-03-30-broad-swedish-import-hardening.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
