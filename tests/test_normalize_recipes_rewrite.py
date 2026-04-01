from __future__ import annotations

import json
import sys
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPORT_ROOT = REPO_ROOT / "scripts" / "import"
if str(IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPORT_ROOT))
if str(IMPORT_ROOT.parent.parent / "apps" / "api") not in sys.path:
    sys.path.insert(0, str(IMPORT_ROOT.parent.parent / "apps" / "api"))

from recipe_import.constants import ARTIFACT_TYPE, SCHEMA_VERSION  # noqa: E402
from recipe_import.discovery import resolve_file_selection  # noqa: E402
from recipe_import.models import (  # noqa: E402
    FileResult,
    ImporterFailure,
    TranslationArtifact,
    TranslationSegment,
)
from recipe_import.normalization_request import build_normalization_request  # noqa: E402
from recipe_import.pipeline import DEFAULT_LOCALE, DEFAULT_RENDER_PROFILE  # noqa: E402
from recipe_import.reference_match import build_reference_match  # noqa: E402
from recipe_import.pipeline import (  # noqa: E402
    assess_translation_quality,
    build_bundle,
    detect_source_language,
    main,
    preprocessed_output_path,
    preprocess_file,
    process_file,
)
from recipe_import.references import collect_preprocessing_guardrails  # noqa: E402
from recipe_import.reporting import build_report_path, build_run_label, create_report, finalize_report, write_report  # noqa: E402
from recipe_import.transport import load_schema, run_preprocessing_contract, validate_preprocessing_payload  # noqa: E402
from recipe_import.transforms import normalize_unit  # noqa: E402
from review_candidates import candidate_files, candidate_update_from_bundle  # noqa: E402


def normalization_payload(*, title: str = "Test Recipe") -> dict[str, object]:
    return {
        "source_language": "sv",
        "output_language": "en",
        "title": title,
        "short_description": "Short description",
        "dish_role": "Main",
        "primary_cuisine": "Swedish",
        "secondary_cuisines": [],
        "technique_family": "Boil",
        "ingredient_families": ["Dairy"],
        "complexity": "Basic",
        "time_class": "15–30 min",
        "service_format": "Single Plate",
        "season": "All Year",
        "mood_tags": [],
        "storage_profile": [],
        "dietary_flags": [],
        "sector": None,
        "class": None,
        "heat_window": None,
        "provision_tags": [],
        "servings": 2,
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "total_time_minutes": 25,
        "yield_text": None,
        "ingredients": [
            {
                "amount": "2",
                "unit": "tbsp",
                "item": "butter",
                "note": None,
                "optional": False,
                "group": None,
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "instruction": "Melt the butter.",
                "time_note": None,
                "heat_note": None,
                "equipment_note": None,
            }
        ],
        "recipe_notes": None,
        "service_notes": None,
        "source_type": "markdown_file",
        "source_url": None,
        "raw_source_text": "Smor recept",
        "uncertainty_notes": [],
        "confidence_summary": "High confidence.",
    }


def test_resolve_file_selection_supports_repeated_files_and_directory(tmp_path: Path) -> None:
    recipe_one = tmp_path / "one.md"
    recipe_two = tmp_path / "two.txt"
    ignored = tmp_path / "README.md"
    recipe_one.write_text("one", encoding="utf-8")
    recipe_two.write_text("two", encoding="utf-8")
    ignored.write_text("ignore", encoding="utf-8")

    args = Namespace(
        input_dir=tmp_path,
        input_files=[recipe_one, recipe_two, recipe_one],
    )

    selection = resolve_file_selection(args)

    assert selection.source_paths == [recipe_one, recipe_two]


def test_resolve_file_selection_rejects_explicit_file_outside_directory(tmp_path: Path) -> None:
    inside = tmp_path / "inside.md"
    inside.write_text("inside", encoding="utf-8")
    outside_dir = tmp_path.parent / "outside-import-test"
    outside_dir.mkdir(exist_ok=True)
    outside = outside_dir / "outside.md"
    outside.write_text("outside", encoding="utf-8")

    args = Namespace(
        input_dir=tmp_path,
        input_files=[inside, outside],
    )

    try:
        resolve_file_selection(args)
    except ImporterFailure as exc:
        assert exc.stage == "discover"
        assert "outside input directory" in exc.message
    else:
        raise AssertionError("Expected ImporterFailure for mixed input roots")


def test_build_bundle_keeps_compatibility_and_supports_external_prompt_paths(tmp_path: Path) -> None:
    source_path = tmp_path / "recipes" / "sample.md"
    source_path.parent.mkdir(parents=True)
    source_path.write_text("recipe", encoding="utf-8")

    external_prompt = tmp_path / "external-prompt.md"
    external_schema = tmp_path / "external-schema.json"
    external_prompt.write_text("prompt", encoding="utf-8")
    external_schema.write_text("{}", encoding="utf-8")

    preprocessing_payload = {
        "source_language": "sv",
        "output_language": "en",
        "translated_text": "preprocessed english text",
        "segments": [
            {
                "segment_id": "seg_0001",
                "segment_type": "ingredient_line",
                "source_text": "1 tsk spad från relish eller pickles",
                "translated_text": "1 tsp pickle brine",
                "uncertainty_flags": ["ambiguous_ingredient"],
            }
        ],
    }

    bundle = build_bundle(
        source_path=source_path,
        relative_source_path=Path("sample.md"),
        source_text="raw source text",
        normalized_input_text="preprocessed english text",
        source_type="markdown_file",
        source_url=None,
        model="test-model",
        prompt_path=external_prompt,
        schema_path=external_schema,
        raw_payload=normalization_payload(),
        raw_payload_json=json.dumps(normalization_payload(), ensure_ascii=True),
        preprocessing_applied=True,
        preprocessing_input_path=None,
        preprocessing_payload_json=json.dumps(preprocessing_payload, ensure_ascii=True),
        preprocessing_prompt_path=REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md",
        preprocessing_schema_path=REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json",
        initial_warnings=["Preprocessing changed or dropped source measurements: 5 ml."],
        initial_review_flags=[
            "Review preprocessing: source measurement parity changed between Swedish source and normalized input text."
        ],
    )

    bundle_dict = bundle.to_dict()

    assert bundle_dict["artifact_type"] == ARTIFACT_TYPE
    assert bundle_dict["schema_version"] == SCHEMA_VERSION
    assert bundle_dict["candidate"]["candidate_status"] == "pending"
    assert bundle_dict["candidate"]["approval_required"] is True
    assert bundle_dict["candidate"]["candidate_extras"]["secondary_cuisines"] == []
    assert bundle_dict["candidate"]["candidate_extras"]["ingredient_families"] == ["Dairy"]
    assert bundle_dict["candidate"]["candidate_extras"]["service_format"] == "Single Plate"
    assert bundle_dict["candidate"]["candidate_extras"]["confidence_summary"] == "High confidence."
    assert bundle_dict["candidate"]["candidate_extras"]["uncertainty_notes"] == []
    assert bundle_dict["source"]["normalized_input_text"] == "preprocessed english text"
    assert bundle_dict["source"]["source_type"] == "markdown_file"
    assert bundle_dict["source"]["relative_source_path"] == "sample.md"
    assert bundle_dict["ai_metadata"]["prompt_path"] == str(external_prompt.resolve())
    assert bundle_dict["ai_metadata"]["schema_path"] == str(external_schema.resolve())
    assert bundle_dict["ai_metadata"]["preprocessing_applied"] is True
    assert bundle_dict["ai_metadata"]["preprocessing_input_path"] is None
    assert bundle_dict["ai_metadata"]["preprocessing_prompt_path"] == "prompts/runtime/translation/recipe-translation-v1.md"
    assert bundle_dict["ai_metadata"]["preprocessing_schema_path"] == "prompts/schemas/recipe-translation-output.schema.json"
    assert bundle_dict["ai_metadata"]["preprocessing_payload_json"] == json.dumps(preprocessing_payload, ensure_ascii=True)
    assert bundle_dict["review_flags"] == [
        "Review preprocessing: source measurement parity changed between Swedish source and normalized input text."
    ]
    assert bundle_dict["warnings"] == ["Preprocessing changed or dropped source measurements: 5 ml."]

    candidate = candidate_update_from_bundle(bundle_dict)
    assert candidate.title == "Test Recipe"
    assert candidate.ingredients[0].unit == "ml"


def test_process_file_emits_bundle_with_repo_relative_metadata(tmp_path: Path, monkeypatch) -> None:
    source_path = tmp_path / "raw" / "recipe.md"
    source_path.parent.mkdir(parents=True)
    source_path.write_text("rå text", encoding="utf-8")
    output_dir = tmp_path / "parsed"

    payload = normalization_payload(title="Pipeline Recipe")

    def fake_run_preprocessing_contract(**_: object):
        preprocess_payload = {
            "source_language": "sv",
            "output_language": "en",
            "translated_text": "english source text",
        }
        return preprocess_payload, json.dumps(preprocess_payload, ensure_ascii=True)

    def fake_run_json_contract(**_: object):
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.pipeline.run_preprocessing_contract", fake_run_preprocessing_contract)
    monkeypatch.setattr("recipe_import.pipeline.run_json_contract", fake_run_json_contract)

    output_path, bundle = process_file(
        input_root=source_path.parent,
        source_path=source_path,
        output_dir=output_dir,
        base_url="http://localhost:1234/v1",
        model="test-model",
        prompt_path=REPO_ROOT / "prompts/runtime/normalization/recipe-normalization-v1.md",
        schema_path=REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json",
        preprocessing_prompt_path=REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md",
        preprocessing_schema_path=REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json",
        system_prompt="prompt",
        schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json"),
        preprocessing_system_prompt="preprocess prompt",
        preprocessing_schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"),
        overwrite=False,
        temperature=0.0,
        timeout_seconds=30,
    )

    assert output_path.exists()
    emitted = json.loads(output_path.read_text(encoding="utf-8"))
    assert emitted["candidate"]["candidate_update"]["title"] == "Pipeline Recipe"
    assert emitted["source"]["relative_source_path"] == "recipe.md"
    assert emitted["source"]["normalized_input_text"] == "english source text"
    assert emitted["ai_metadata"]["prompt_path"] == "prompts/runtime/normalization/recipe-normalization-v1.md"
    assert emitted["ai_metadata"]["preprocessing_applied"] is True
    assert bundle.review_flags == []


def test_process_file_accepts_relative_source_paths_when_input_root_is_absolute(tmp_path: Path, monkeypatch) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    source_path = raw_dir / "recipe.md"
    source_path.write_text("rå text", encoding="utf-8")
    output_dir = tmp_path / "parsed"

    payload = normalization_payload(title="Relative Path Recipe")

    def fake_run_preprocessing_contract(**_: object):
        preprocess_payload = {
            "source_language": "sv",
            "output_language": "en",
            "translated_text": "english source text",
        }
        return preprocess_payload, json.dumps(preprocess_payload, ensure_ascii=True)

    def fake_run_json_contract(**_: object):
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("recipe_import.pipeline.run_preprocessing_contract", fake_run_preprocessing_contract)
    monkeypatch.setattr("recipe_import.pipeline.run_json_contract", fake_run_json_contract)

    output_path, bundle = process_file(
        input_root=raw_dir.resolve(),
        source_path=Path("raw/recipe.md"),
        output_dir=output_dir,
        base_url="http://localhost:1234/v1",
        model="test-model",
        prompt_path=REPO_ROOT / "prompts/runtime/normalization/recipe-normalization-v1.md",
        schema_path=REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json",
        preprocessing_prompt_path=REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md",
        preprocessing_schema_path=REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json",
        system_prompt="prompt",
        schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json"),
        preprocessing_system_prompt="preprocess prompt",
        preprocessing_schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"),
        overwrite=False,
        temperature=0.0,
        timeout_seconds=30,
    )

    assert output_path.exists()
    emitted = json.loads(output_path.read_text(encoding="utf-8"))
    assert emitted["source"]["relative_source_path"] == "recipe.md"
    assert bundle.candidate.candidate_update.title == "Relative Path Recipe"


def test_assess_translation_quality_raises_when_stage1_translation_is_empty() -> None:
    translation = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="   ",
        segments=[],
    )
    reference_match = build_reference_match(
        translation=TranslationArtifact(
            source_language="sv",
            output_language="en",
            translated_text="1 tsp salt",
            segments=[
                TranslationSegment(
                    segment_id="seg_0001",
                    segment_type="ingredient_line",
                    source_text="1 tsk salt",
                    translated_text="1 tsp salt",
                    uncertainty_flags=[],
                )
            ],
        ),
        render_profile=DEFAULT_RENDER_PROFILE,
        locale=DEFAULT_LOCALE,
    )

    with pytest.raises(ImporterFailure) as excinfo:
        assess_translation_quality(translation=translation, reference_match=reference_match)

    assert excinfo.value.stage == "preprocess"


def test_process_file_fails_when_saved_preprocessed_input_is_empty(tmp_path: Path) -> None:
    source_path = tmp_path / "recipe.md"
    source_path.write_text("rå text", encoding="utf-8")
    output_dir = tmp_path / "parsed"

    with pytest.raises(ImporterFailure) as excinfo:
        process_file(
            input_root=source_path.parent,
            source_path=source_path,
            output_dir=output_dir,
            base_url="http://localhost:1234/v1",
            model="test-model",
            prompt_path=REPO_ROOT / "prompts/runtime/normalization/recipe-normalization-v1.md",
            schema_path=REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json",
            preprocessing_prompt_path=REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md",
            preprocessing_schema_path=REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json",
            system_prompt="prompt",
            schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json"),
            preprocessing_system_prompt="preprocess prompt",
            preprocessing_schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"),
            overwrite=False,
            temperature=0.0,
            timeout_seconds=30,
            preprocessed_input_text="   ",
            preprocessing_artifact_path=tmp_path / "recipe.preprocessed.txt",
        )

    assert excinfo.value.stage == "preprocess_input"


def test_process_file_escalates_measurement_drift_as_translation_quality_review_flag(
    tmp_path: Path, monkeypatch
) -> None:
    source_path = tmp_path / "recipe.md"
    source_path.write_text("1 tsk salt", encoding="utf-8")
    output_dir = tmp_path / "parsed"

    payload = normalization_payload(title="Pipeline Recipe")

    def fake_run_preprocessing_contract(**_: object):
        preprocess_payload = {
            "source_language": "sv",
            "output_language": "en",
            "translated_text": "1 tbsp salt",
            "segments": [
                {
                    "segment_id": "seg_0001",
                    "segment_type": "ingredient_line",
                    "source_text": "1 tsk salt",
                    "translated_text": "1 tbsp salt",
                    "uncertainty_flags": [],
                }
            ],
        }
        return preprocess_payload, json.dumps(preprocess_payload, ensure_ascii=True)

    def fake_run_json_contract(**_: object):
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.pipeline.run_preprocessing_contract", fake_run_preprocessing_contract)
    monkeypatch.setattr("recipe_import.pipeline.run_json_contract", fake_run_json_contract)

    _, bundle = process_file(
        input_root=source_path.parent,
        source_path=source_path,
        output_dir=output_dir,
        base_url="http://localhost:1234/v1",
        model="test-model",
        prompt_path=REPO_ROOT / "prompts/runtime/normalization/recipe-normalization-v1.md",
        schema_path=REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json",
        preprocessing_prompt_path=REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md",
        preprocessing_schema_path=REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json",
        system_prompt="prompt",
        schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json"),
        preprocessing_system_prompt="preprocess prompt",
        preprocessing_schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"),
        overwrite=False,
        temperature=0.0,
        timeout_seconds=30,
    )

    assert "Review preprocessing: source measurement parity changed between Swedish source and normalized input text." in bundle.review_flags
    assert bundle.review_flags.count(
        "Review preprocessing: source measurement parity changed between Swedish source and normalized input text."
    ) == 1
    assert not any("translation quality review required due to measurement drift" in flag.lower() for flag in bundle.review_flags)


def test_process_file_does_not_escalate_single_contextual_semantic_risk_as_generic_translation_quality_flag(
    tmp_path: Path, monkeypatch
) -> None:
    source_path = tmp_path / "recipe.md"
    source_path.write_text("vitlökspulver", encoding="utf-8")
    output_dir = tmp_path / "parsed"

    payload = normalization_payload(title="Pipeline Recipe")

    def fake_run_preprocessing_contract(**_: object):
        preprocess_payload = {
            "source_language": "sv",
            "output_language": "en",
            "translated_text": "onion powder",
            "segments": [
                {
                    "segment_id": "seg_0001",
                    "segment_type": "ingredient_line",
                    "source_text": "vitlökspulver",
                    "translated_text": "onion powder",
                    "uncertainty_flags": [],
                },
            ],
        }
        return preprocess_payload, json.dumps(preprocess_payload, ensure_ascii=True)

    def fake_run_json_contract(**_: object):
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.pipeline.run_preprocessing_contract", fake_run_preprocessing_contract)
    monkeypatch.setattr("recipe_import.pipeline.run_json_contract", fake_run_json_contract)

    _, bundle = process_file(
        input_root=source_path.parent,
        source_path=source_path,
        output_dir=output_dir,
        base_url="http://localhost:1234/v1",
        model="test-model",
        prompt_path=REPO_ROOT / "prompts/runtime/normalization/recipe-normalization-v1.md",
        schema_path=REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json",
        preprocessing_prompt_path=REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md",
        preprocessing_schema_path=REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json",
        system_prompt="prompt",
        schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json"),
        preprocessing_system_prompt="preprocess prompt",
        preprocessing_schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"),
        overwrite=False,
        temperature=0.0,
        timeout_seconds=30,
    )

    assert any("drifted 'vitlökspulver'" in warning.lower() for warning in bundle.warnings)
    assert not any("multiple contextual-term risks" in flag.lower() for flag in bundle.review_flags)


def test_process_file_keeps_measurement_drift_to_one_review_flag(tmp_path: Path, monkeypatch) -> None:
    source_path = tmp_path / "recipe.md"
    source_path.write_text("1 tsk salt", encoding="utf-8")
    output_dir = tmp_path / "parsed"

    payload = normalization_payload(title="Pipeline Recipe")

    def fake_run_json_contract(**_: object):
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.pipeline.run_json_contract", fake_run_json_contract)

    _, bundle = process_file(
        input_root=source_path.parent,
        source_path=source_path,
        output_dir=output_dir,
        base_url="http://localhost:1234/v1",
        model="test-model",
        prompt_path=REPO_ROOT / "prompts/runtime/normalization/recipe-normalization-v1.md",
        schema_path=REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json",
        preprocessing_prompt_path=REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md",
        preprocessing_schema_path=REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json",
        system_prompt="prompt",
        schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json"),
        preprocessing_system_prompt="preprocess prompt",
        preprocessing_schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"),
        overwrite=False,
        temperature=0.0,
        timeout_seconds=30,
        preprocessed_input_text="1 tbsp salt",
        preprocessing_artifact_path=tmp_path / "recipe.preprocessed.txt",
    )

    measurement_flag = "Review preprocessing: source measurement parity changed between Swedish source and normalized input text."
    assert bundle.review_flags.count(measurement_flag) == 1
    assert not any("translation quality review required due to measurement drift" in flag.lower() for flag in bundle.review_flags)


def test_detect_source_language_marks_swedish_recipe_text() -> None:
    source_text = "Ingredients: 1 dl majonnäs, 1 msk gurkrelish, 1 tsk lökpulver."

    assert detect_source_language(source_text) == "sv"


def test_preprocessed_output_path_uses_parallel_relative_layout(tmp_path: Path) -> None:
    input_root = tmp_path / "raw"
    source_path = input_root / "nested" / "recipe.md"
    preprocessed_dir = tmp_path / "preprocessed"

    assert preprocessed_output_path(
        source_path=source_path,
        input_root=input_root,
        output_dir=preprocessed_dir,
    ) == preprocessed_dir / "nested" / "recipe.preprocessed.txt"


def test_preprocess_file_writes_saved_intermediate_text(tmp_path: Path, monkeypatch) -> None:
    input_root = tmp_path / "raw"
    source_path = input_root / "recipe.md"
    output_dir = tmp_path / "preprocessed"
    input_root.mkdir()
    source_path.write_text("rå text", encoding="utf-8")

    def fake_run_preprocessing_contract(**_: object):
        preprocess_payload = {
            "source_language": "sv",
            "output_language": "en",
            "translated_text": "english source text",
        }
        return preprocess_payload, json.dumps(preprocess_payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.pipeline.run_preprocessing_contract", fake_run_preprocessing_contract)

    output_path, preprocessed_text = preprocess_file(
        input_root=input_root,
        source_path=source_path,
        output_dir=output_dir,
        base_url="http://localhost:1234/v1",
        model="test-model",
        preprocessing_system_prompt="preprocess prompt",
        preprocessing_schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"),
        timeout_seconds=30,
        temperature=0.0,
        overwrite=False,
    )

    assert output_path.exists()
    assert output_path.name == "recipe.preprocessed.txt"
    assert output_path.read_text(encoding="utf-8") == "english source text\n"
    assert preprocessed_text == "english source text"


def test_run_preprocessing_contract_uses_translategemma_completion_prompt(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_completion_raw_text(*, base_url: str, payload: dict[str, object], timeout_seconds: int) -> str:
        captured["base_url"] = base_url
        captured["payload"] = payload
        captured["timeout_seconds"] = timeout_seconds
        return "english source text"

    monkeypatch.setattr("recipe_import.transport.lmstudio_completion_raw_text", fake_completion_raw_text)

    payload, raw_text = run_preprocessing_contract(
        base_url="http://localhost:1234/v1",
        model="translategemma-4b-it",
        system_prompt="ignored",
        user_prompt="ignored",
        source_text="rå text",
        source_lang_code="sv",
        response_format={"type": "json_schema"},
        temperature=0.0,
        timeout_seconds=30,
    )

    assert json.loads(raw_text) == {
        "source_language": "sv",
        "output_language": "en",
        "translated_text": "english source text",
    }
    assert isinstance(payload, TranslationArtifact)
    assert payload.source_language == "sv"
    assert payload.output_language == "en"
    assert payload.translated_text == "english source text"
    assert captured["payload"]["model"] == "translategemma-4b-it"
    assert captured["payload"]["temperature"] == 0.0
    assert captured["payload"]["stream"] is False
    assert captured["payload"]["prompt"].startswith("<bos><start_of_turn>user\nYou are a professional Swedish (sv) to English (en) translator.")
    assert "rå text" in captured["payload"]["prompt"]


def test_run_preprocessing_contract_labels_non_json_content_as_preprocess_failure(monkeypatch) -> None:
    def fake_chat_raw_content(**_: object) -> str:
        return "plain text instead of json"

    monkeypatch.setattr("recipe_import.transport.lmstudio_chat_raw_content", fake_chat_raw_content)

    with pytest.raises(ImporterFailure) as excinfo:
        run_preprocessing_contract(
            base_url="http://localhost:1234/v1",
            model="test-model",
            system_prompt="ignored",
            user_prompt="ignored",
            source_text="rå text",
            source_lang_code="sv",
            response_format={"type": "json_schema"},
            temperature=0.0,
            timeout_seconds=30,
        )

    assert excinfo.value.stage == "preprocess"
    assert "non-json" in excinfo.value.message.lower()


def test_candidate_files_discovers_nested_candidate_bundles(tmp_path: Path) -> None:
    top_level = tmp_path / "top-level.candidate.json"
    nested = tmp_path / "nested" / "recipe.candidate.json"
    ignored = tmp_path / "nested" / "notes.json"
    nested.parent.mkdir(parents=True)
    top_level.write_text("{}", encoding="utf-8")
    nested.write_text("{}", encoding="utf-8")
    ignored.write_text("{}", encoding="utf-8")

    assert candidate_files(tmp_path) == [nested, top_level]


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


def test_validate_preprocessing_payload_rejects_wrong_segments_type() -> None:
    schema = {
        "type": "object",
        "required": ["source_language", "output_language", "translated_text"],
    }
    payload = {
        "source_language": "sv",
        "output_language": "en",
        "translated_text": "english",
        "segments": "not-an-array",
    }

    errors = validate_preprocessing_payload(payload, schema)
    assert any("segments" in error.lower() and "array" in error.lower() for error in errors)


def test_validate_preprocessing_payload_rejects_invalid_uncertainty_flags() -> None:
    schema = {
        "type": "object",
        "required": ["source_language", "output_language", "translated_text"],
    }
    payload = {
        "source_language": "sv",
        "output_language": "en",
        "translated_text": "english",
        "segments": [
            {
                "segment_id": "seg_bad",
                "segment_type": "ingredient_line",
                "source_text": "1 tsk spad från relish eller pickles",
                "translated_text": "1 tsp pickle brine",
                "uncertainty_flags": ["not-a-real-flag"],
            }
        ],
    }

    errors = validate_preprocessing_payload(payload, schema)
    assert any("segment_id" in error.lower() for error in errors)
    assert any("uncertainty" in error.lower() for error in errors)


def test_validate_preprocessing_payload_rejects_additional_root_property() -> None:
    schema = {
        "type": "object",
        "required": ["source_language", "output_language", "translated_text"],
    }
    payload = {
        "source_language": "sv",
        "output_language": "en",
        "translated_text": "english",
        "unexpected": "value",
    }

    errors = validate_preprocessing_payload(payload, schema)
    assert any("additional property" in error.lower() for error in errors)


def test_validate_preprocessing_payload_rejects_additional_segment_property() -> None:
    schema = {
        "type": "object",
        "required": ["source_language", "output_language", "translated_text"],
    }
    payload = {
        "source_language": "sv",
        "output_language": "en",
        "translated_text": "english",
        "segments": [
            {
                "segment_id": "seg_0001",
                "segment_type": "ingredient_line",
                "source_text": "1 tsk spad från relish eller pickles",
                "translated_text": "1 tsp pickle brine",
                "uncertainty_flags": [],
                "extra_field": "not-allowed",
            }
        ],
    }

    errors = validate_preprocessing_payload(payload, schema)
    assert any("additional property" in error.lower() for error in errors)


def test_run_preprocessing_contract_rejects_invalid_segment_shape(monkeypatch) -> None:
    def fake_run_json_contract(**_: object):
        payload = {
            "source_language": "sv",
            "output_language": "en",
            "translated_text": "english",
            "segments": [{"segment_type": "ingredient_line"}],
        }
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.transport.run_json_contract", fake_run_json_contract)

    try:
        run_preprocessing_contract(
            base_url="http://localhost:1234/v1",
            model="test-model",
            system_prompt="ignored",
            user_prompt="ignored",
            source_text="rå text",
            source_lang_code="sv",
            response_format={"type": "json_schema"},
            temperature=0.0,
            timeout_seconds=30,
        )
    except ImporterFailure as exc:
        assert exc.stage == "preprocess"
        assert "missing field" in exc.message.lower()
    else:
        raise AssertionError("Expected ImporterFailure for malformed segment payload")


def test_run_preprocessing_contract_rejects_wrong_segments_type(monkeypatch) -> None:
    def fake_run_json_contract(**_: object):
        payload = {
            "source_language": "sv",
            "output_language": "en",
            "translated_text": "english",
            "segments": "not-an-array",
        }
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.transport.run_json_contract", fake_run_json_contract)

    try:
        run_preprocessing_contract(
            base_url="http://localhost:1234/v1",
            model="test-model",
            system_prompt="ignored",
            user_prompt="ignored",
            source_text="rå text",
            source_lang_code="sv",
            response_format={"type": "json_schema"},
            temperature=0.0,
            timeout_seconds=30,
        )
    except ImporterFailure as exc:
        assert exc.stage == "preprocess"
        assert "segments" in exc.message.lower()
    else:
        raise AssertionError("Expected ImporterFailure for wrong segments type")


def test_run_preprocessing_contract_rejects_invalid_uncertainty_flags(monkeypatch) -> None:
    def fake_run_json_contract(**_: object):
        payload = {
            "source_language": "sv",
            "output_language": "en",
            "translated_text": "english",
            "segments": [
                {
                    "segment_id": "seg_0001",
                    "segment_type": "ingredient_line",
                    "source_text": "1 tsk spad från relish eller pickles",
                    "translated_text": "1 tsp pickle brine",
                    "uncertainty_flags": ["not-a-real-flag"],
                }
            ],
        }
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.transport.run_json_contract", fake_run_json_contract)

    try:
        run_preprocessing_contract(
            base_url="http://localhost:1234/v1",
            model="test-model",
            system_prompt="ignored",
            user_prompt="ignored",
            source_text="rå text",
            source_lang_code="sv",
            response_format={"type": "json_schema"},
            temperature=0.0,
            timeout_seconds=30,
        )
    except ImporterFailure as exc:
        assert exc.stage == "preprocess"
        assert "uncertainty" in exc.message.lower()
    else:
        raise AssertionError("Expected ImporterFailure for invalid uncertainty flags")


def test_collect_preprocessing_guardrails_flags_measurement_and_context_drift() -> None:
    warnings, review_flags = collect_preprocessing_guardrails(
        source_text="1 tsk spad från relish eller pickles\n1 tsk vitlökspulver\n10 min + vila\nRörs kall.",
        normalized_input_text="1 tbsp relish\n1 tsp onion powder\nMix together.",
        source_language="sv",
    )

    assert any("measurement parity changed" in flag for flag in review_flags)
    assert any("spad från relish eller pickles" in flag for flag in review_flags)
    assert any("vitlökspulver" in flag for flag in review_flags)
    assert any("changed or dropped source measurements" in warning for warning in warnings)
    assert any("liquid/brine meaning" in warning for warning in warnings)
    assert any("drifted 'vitlökspulver'" in warning for warning in warnings)


def test_normalize_unit_uses_reference_aliases() -> None:
    assert normalize_unit("teskedar") == "tsk"
    assert normalize_unit("matsked") == "msk"
    assert normalize_unit("teaspoons") == "tsp"
    assert normalize_unit("pounds") == "lb"


def test_process_file_uses_saved_preprocessed_input_when_provided(tmp_path: Path, monkeypatch) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    source_path = raw_dir / "recipe.md"
    source_path.write_text("rå text", encoding="utf-8")
    output_dir = tmp_path / "parsed"

    payload = normalization_payload(title="Saved Preprocessed Recipe")
    captured_prompt: dict[str, str] = {}

    def fake_run_json_contract(**kwargs: object):
        captured_prompt["user_prompt"] = kwargs["user_prompt"]
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.pipeline.run_json_contract", fake_run_json_contract)

    output_path, bundle = process_file(
        input_root=raw_dir,
        source_path=source_path,
        output_dir=output_dir,
        base_url="http://localhost:1234/v1",
        model="test-model",
        prompt_path=REPO_ROOT / "prompts/runtime/normalization/recipe-normalization-v1.md",
        schema_path=REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json",
        preprocessing_prompt_path=REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md",
        preprocessing_schema_path=REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json",
        system_prompt="prompt",
        schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json"),
        preprocessing_system_prompt="preprocess prompt",
        preprocessing_schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"),
        overwrite=False,
        temperature=0.0,
        timeout_seconds=30,
        preprocessed_input_text="english source text from disk",
        preprocessing_artifact_path=tmp_path / "preprocessed" / "recipe.preprocessed.txt",
    )

    assert output_path.exists()
    user_prompt = json.loads(captured_prompt["user_prompt"])
    assert user_prompt["pipeline_stage"] == "stage2_normalization_request"
    assert user_prompt["stage1_translation"]["translated_text"] == "english source text from disk"
    assert user_prompt["stage1_translation"]["segments"][0]["source_text"] == "rå text"
    assert user_prompt["stage1_translation"]["segments"][0]["translated_text"] == "english source text from disk"
    assert bundle.source.normalized_input_text == "english source text from disk"
    assert bundle.ai_metadata.preprocessing_applied is True
    assert bundle.ai_metadata.preprocessing_input_path == str((tmp_path / "preprocessed" / "recipe.preprocessed.txt").resolve())


def test_process_file_carries_reference_guardrails_into_bundle(tmp_path: Path, monkeypatch) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    source_path = raw_dir / "recipe.md"
    source_path.write_text("1 tsk spad från relish eller pickles", encoding="utf-8")
    output_dir = tmp_path / "parsed"

    payload = normalization_payload(title="Guarded Recipe")

    def fake_run_json_contract(**_: object):
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.pipeline.run_json_contract", fake_run_json_contract)

    output_path, bundle = process_file(
        input_root=raw_dir,
        source_path=source_path,
        output_dir=output_dir,
        base_url="http://localhost:1234/v1",
        model="test-model",
        prompt_path=REPO_ROOT / "prompts/runtime/normalization/recipe-normalization-v1.md",
        schema_path=REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json",
        preprocessing_prompt_path=REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md",
        preprocessing_schema_path=REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json",
        system_prompt="prompt",
        schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json"),
        preprocessing_system_prompt="preprocess prompt",
        preprocessing_schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"),
        overwrite=False,
        temperature=0.0,
        timeout_seconds=30,
        preprocessed_input_text="1 tbsp relish",
        preprocessing_artifact_path=tmp_path / "preprocessed" / "recipe.preprocessed.txt",
    )

    assert output_path.exists()
    assert any("changed or dropped source measurements" in warning for warning in bundle.warnings)
    assert any("measurement parity changed" in flag for flag in bundle.review_flags)


def test_process_file_builds_stage2_normalization_request_from_stage1_artifacts(tmp_path: Path, monkeypatch) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    source_path = raw_dir / "recipe.md"
    source_path.write_text("rå text", encoding="utf-8")
    output_dir = tmp_path / "parsed"

    payload = normalization_payload(title="Stage 2 Request Recipe")
    captured: dict[str, object] = {}

    preprocessing_artifact = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="english source text",
        segments=[
            TranslationSegment(
                segment_id="seg_0001",
                segment_type="ingredient_line",
                source_text="1 tsk spad från relish eller pickles",
                translated_text="1 tsp pickle brine",
                uncertainty_flags=[],
            )
        ],
    )

    def fake_run_preprocessing_contract(**_: object):
        return preprocessing_artifact, json.dumps(preprocessing_artifact.to_dict(), ensure_ascii=True)

    def fake_run_json_contract(**kwargs: object):
        captured["user_prompt"] = kwargs["user_prompt"]
        return payload, json.dumps(payload, ensure_ascii=True)

    monkeypatch.setattr("recipe_import.pipeline.run_preprocessing_contract", fake_run_preprocessing_contract)
    monkeypatch.setattr("recipe_import.pipeline.run_json_contract", fake_run_json_contract)

    output_path, bundle = process_file(
        input_root=raw_dir,
        source_path=source_path,
        output_dir=output_dir,
        base_url="http://localhost:1234/v1",
        model="test-model",
        prompt_path=REPO_ROOT / "prompts/runtime/normalization/recipe-normalization-v1.md",
        schema_path=REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json",
        preprocessing_prompt_path=REPO_ROOT / "prompts/runtime/translation/recipe-translation-v1.md",
        preprocessing_schema_path=REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json",
        system_prompt="prompt",
        schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-normalization-output.schema.json"),
        preprocessing_system_prompt="preprocess prompt",
        preprocessing_schema=load_schema(REPO_ROOT / "prompts/schemas/recipe-translation-output.schema.json"),
        overwrite=False,
        temperature=0.0,
        timeout_seconds=30,
    )

    assert output_path.exists()
    assert bundle.source.raw_source_text == "rå text"
    assert bundle.source.normalized_input_text == "english source text"

    expected_reference_match = build_reference_match(
        translation=preprocessing_artifact,
        render_profile=DEFAULT_RENDER_PROFILE,
        locale=DEFAULT_LOCALE,
    )
    expected_request = build_normalization_request(
        translation=preprocessing_artifact,
        reference_match=expected_reference_match,
        render_profile=DEFAULT_RENDER_PROFILE,
        locale=DEFAULT_LOCALE,
    )
    assert json.loads(captured["user_prompt"]) == expected_request
    assert expected_request["stage1_translation"]["segments"][0]["source_text"] == "1 tsk spad från relish eller pickles"


def test_report_generation_writes_json_summary(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"
    run_label = build_run_label()
    report_path = build_report_path(report_dir, run_label)
    report = create_report(
        output_dir=tmp_path / "out",
        report_path=report_path,
        selected_sources=[tmp_path / "one.md", tmp_path / "two.md"],
        run_label=run_label,
        started_at="2026-03-28T17:00:00+00:00",
    )
    report.results.append(
        FileResult(
            source_path=str(tmp_path / "one.md"),
            status="success",
            stage="emit_bundle",
            output_path=str(tmp_path / "out" / "one.candidate.json"),
            warning_count=2,
            review_flag_count=1,
            duration_ms=15,
        )
    )
    report.results.append(
        FileResult(
            source_path=str(tmp_path / "two.md"),
            status="failure",
            stage="normalize",
            error="schema mismatch",
            duration_ms=20,
        )
    )
    report.completed_at = "2026-03-28T17:00:05+00:00"
    finalize_report(report)
    write_report(report)

    emitted = json.loads(report_path.read_text(encoding="utf-8"))
    assert emitted["status"] == "partial_failure"
    assert emitted["summary"]["successful_files"] == 1
    assert emitted["summary"]["failed_files"] == 1
    assert emitted["summary"]["total_warnings"] == 2


def test_main_supports_explicit_file_only_runs(tmp_path: Path, monkeypatch) -> None:
    source_path = tmp_path / "recipe.md"
    source_path.write_text("recipe text", encoding="utf-8")
    prompt_path = tmp_path / "prompt.md"
    schema_path = tmp_path / "schema.json"
    prompt_path.write_text("prompt", encoding="utf-8")
    schema_path.write_text("{}", encoding="utf-8")
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "reports"

    args = Namespace(
        input_dir=None,
        input_files=[source_path],
        output_dir=output_dir,
        model="test-model",
        base_url="http://localhost:1234/v1",
        prompt_path=prompt_path,
        schema_path=schema_path,
        report_dir=report_dir,
        preprocess_only=False,
        use_preprocessed_dir=None,
        overwrite=False,
        temperature=0.0,
        timeout_seconds=30,
    )

    monkeypatch.setattr("recipe_import.pipeline.parse_args", lambda: args)
    monkeypatch.setattr("recipe_import.pipeline.load_prompt_instructions", lambda _: "prompt")
    monkeypatch.setattr("recipe_import.pipeline.load_schema", lambda _: {})

    def fake_process_file(**_: object):
        output_path = output_dir / "recipe.candidate.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("{}", encoding="utf-8")
        return output_path, SimpleNamespace(warnings=[], review_flags=[])

    monkeypatch.setattr("recipe_import.pipeline.process_file", fake_process_file)

    exit_code = main()

    assert exit_code == 0
    reports = list(report_dir.glob("recipe-normalization-run-*.json"))
    assert len(reports) == 1
