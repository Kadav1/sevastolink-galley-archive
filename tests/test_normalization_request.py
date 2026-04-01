from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPORT_ROOT = REPO_ROOT / "scripts" / "import"
if str(IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPORT_ROOT))

from recipe_import.models import ReferenceMatchArtifact, ReferenceMatchItem, TranslationArtifact, TranslationSegment  # noqa: E402
from recipe_import.normalization_request import build_normalization_request  # noqa: E402


def test_build_normalization_request_serializes_stage1_artifacts_and_policy() -> None:
    translation = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="1 tsp pickle brine",
        segments=[
            TranslationSegment(
                segment_id="seg_0001",
                segment_type="ingredient_line",
                source_text="1 tsk spad från relish eller pickles",
                translated_text="1 tsp pickle brine",
                uncertainty_flags=["ambiguous_ingredient"],
            )
        ],
    )
    match = ReferenceMatchArtifact(
        pipeline_stage="stage1_reference_match",
        render_profile="english_metric_strict",
        locale="en_generic",
        unit_matches=[
            ReferenceMatchItem(source_token="tsk", matched_entry_key="tsk", deterministic=True, requires_review=False),
            ReferenceMatchItem(source_token="krm", matched_entry_key="krm", deterministic=True, requires_review=False),
        ],
        term_matches=[
            ReferenceMatchItem(
                source_token="vitlökspulver",
                matched_entry_key="vitlökspulver",
                deterministic=True,
                requires_review=False,
            )
        ],
        contextual_matches=[
            ReferenceMatchItem(
                source_token="spad från relish eller pickles",
                matched_entry_key="spad från relish eller pickles",
                deterministic=False,
                requires_review=True,
            )
        ],
        drift_signals=["source_measurement_parity_changed"],
    )

    payload = build_normalization_request(
        translation=translation,
        reference_match=match,
        render_profile="english_metric_strict",
        locale="en_generic",
    )

    assert set(payload) == {
        "pipeline_stage",
        "render_profile",
        "locale",
        "stage1_translation",
        "stage1_reference_match",
        "normalization_policy",
    }
    assert payload["pipeline_stage"] == "stage2_normalization_request"
    assert payload["render_profile"] == "english_metric_strict"
    assert payload["locale"] == "en_generic"
    assert payload["stage1_translation"]["translated_text"] == "1 tsp pickle brine"
    assert payload["stage1_translation"]["segments"][0]["segment_id"] == "seg_0001"
    assert payload["stage1_translation"]["segments"][0]["uncertainty_flags"] == ["ambiguous_ingredient"]
    assert payload["stage1_reference_match"]["pipeline_stage"] == "stage1_reference_match"
    assert payload["stage1_reference_match"]["render_profile"] == "english_metric_strict"
    assert payload["stage1_reference_match"]["locale"] == "en_generic"
    assert payload["stage1_reference_match"]["drift_signals"] == ["source_measurement_parity_changed"]
    assert payload["stage1_reference_match"]["unit_matches"]
    assert {item["source_token"] for item in payload["stage1_reference_match"]["unit_matches"]} == {"tsk", "krm"}
    assert any(
        item["matched_entry_key"] == "vitlökspulver"
        for item in payload["stage1_reference_match"]["term_matches"]
    )
    assert any(
        item["matched_entry_key"] == "spad från relish eller pickles"
        and item["requires_review"] is True
        for item in payload["stage1_reference_match"]["contextual_matches"]
    )
    assert payload["normalization_policy"]["preserve_source_authority"] is True
    assert payload["normalization_policy"]["preserve_non_exact_phrases"] is True
    assert payload["normalization_policy"]["allow_contextual_micro_unit_rendering"] is False
    assert payload["normalization_policy"]["volume_to_weight_requires_match"] is True


def test_build_normalization_request_enables_micro_unit_rendering_for_hybrid_profile() -> None:
    translation = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="1 pinch salt",
        segments=[],
    )
    match = ReferenceMatchArtifact(
        pipeline_stage="stage1_reference_match",
        render_profile="english_hybrid_natural",
        locale="en_generic",
    )

    payload = build_normalization_request(
        translation=translation,
        reference_match=match,
        render_profile="english_hybrid_natural",
        locale="en_generic",
    )

    assert payload["normalization_policy"]["allow_contextual_micro_unit_rendering"] is True
