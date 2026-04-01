from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPORT_ROOT = REPO_ROOT / "scripts" / "import"
if str(IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPORT_ROOT))

from recipe_import.models import TranslationArtifact, TranslationSegment  # noqa: E402
from recipe_import.reference_match import build_reference_match  # noqa: E402
from recipe_import.references import extract_measurement_signatures, term_lookup_ambiguities, term_lookup_keys  # noqa: E402


def test_build_reference_match_detects_drift_and_reference_matches() -> None:
    translation = TranslationArtifact(
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
        translation=translation,
        render_profile="english_metric_strict",
        locale="en_generic",
    )

    assert match.pipeline_stage == "stage1_reference_match"
    assert match.render_profile == "english_metric_strict"
    assert match.locale == "en_generic"
    assert "source_measurement_parity_changed" in match.drift_signals
    assert any(item.matched_entry_key == "spad från relish eller pickles" for item in match.contextual_matches)
    assert any(item.matched_entry_key == "vitlökspulver" for item in match.term_matches)
    assert any(item.source_token == "tsk" for item in match.unit_matches)
    assert any(item.source_token == "krm" for item in match.unit_matches)


def test_build_reference_match_burgarsas_semantics_preserve_measurement_drift() -> None:
    translation = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="1 tbsp relish\n1 tsp garlic powder\n1 tsp onion powder\nMix together.",
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
                translated_text="1 tsp garlic powder",
                uncertainty_flags=[],
            ),
        ],
    )

    match = build_reference_match(
        translation=translation,
        render_profile="english_metric_strict",
        locale="en_generic",
    )

    assert match.pipeline_stage == "stage1_reference_match"
    assert "source_measurement_parity_changed" in match.drift_signals
    assert len(match.unit_matches) == 2
    assert any(item.source_token == "tsk" for item in match.unit_matches)
    assert any(item.source_token == "krm" for item in match.unit_matches)
    assert match.term_matches
    assert any(item.matched_entry_key == "vitlökspulver" for item in match.term_matches)
    assert match.contextual_matches
    assert any(
        item.matched_entry_key == "spad från relish eller pickles"
        and item.deterministic is False
        and item.requires_review is True
        for item in match.contextual_matches
    )


def test_term_lookup_keys_exposes_active_ingredient_terms() -> None:
    lookup_keys = term_lookup_keys()

    assert "vitlökspulver" in lookup_keys
    assert "spad från relish eller pickles" not in lookup_keys


def test_term_lookup_ambiguities_marks_colliding_aliases() -> None:
    ambiguities = term_lookup_ambiguities()

    assert "paprika" in ambiguities


def test_build_reference_match_marks_ambiguous_term_matches_non_deterministic() -> None:
    translation = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="paprika",
        segments=[
            TranslationSegment(
                segment_id="seg_0001",
                segment_type="ingredient_line",
                source_text="paprika",
                translated_text="paprika",
                uncertainty_flags=[],
            )
        ],
    )

    match = build_reference_match(
        translation=translation,
        render_profile="english_metric_strict",
        locale="en_generic",
    )

    paprika_matches = [item for item in match.term_matches if item.source_token == "paprika"]
    assert paprika_matches
    assert all(not item.deterministic for item in paprika_matches)
    assert all(item.requires_review for item in paprika_matches)


def test_build_reference_match_collapses_spoon_parity_for_spelled_out_english_units() -> None:
    translation = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="1 teaspoon salt\n2 tablespoons sugar",
        segments=[
            TranslationSegment(
                segment_id="seg_0001",
                segment_type="ingredient_line",
                source_text="1 tsk salt",
                translated_text="1 teaspoon salt",
                uncertainty_flags=[],
            ),
            TranslationSegment(
                segment_id="seg_0002",
                segment_type="ingredient_line",
                source_text="2 msk sugar",
                translated_text="2 tablespoons sugar",
                uncertainty_flags=[],
            ),
        ],
    )

    match = build_reference_match(
        translation=translation,
        render_profile="english_metric_strict",
        locale="en_generic",
    )

    assert "source_measurement_parity_changed" not in match.drift_signals


def test_build_reference_match_signals_no_source_evidence_using_existing_shape() -> None:
    translation = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="1 teaspoon garlic powder and paprika",
        segments=[],
    )

    match = build_reference_match(
        translation=translation,
        render_profile="english_metric_strict",
        locale="en_generic",
    )

    assert "source_evidence_unavailable" in match.drift_signals
    assert match.unit_matches == []
    assert match.term_matches == []
    assert match.contextual_matches == []
    assert "source_evidence_available" not in match.to_dict()


def test_extract_measurement_signatures_stabilizes_nypa_and_pinch() -> None:
    assert extract_measurement_signatures("1 nypa salt") == extract_measurement_signatures("1 pinch salt")


def test_build_reference_match_stabilizes_nypa_unit_matches() -> None:
    translation = TranslationArtifact(
        source_language="sv",
        output_language="en",
        translated_text="1 pinch salt",
        segments=[
            TranslationSegment(
                segment_id="seg_0001",
                segment_type="ingredient_line",
                source_text="1 nypa salt",
                translated_text="1 pinch salt",
                uncertainty_flags=[],
            )
        ],
    )

    match = build_reference_match(
        translation=translation,
        render_profile="english_metric_strict",
        locale="en_generic",
    )

    assert match.unit_matches
    assert match.unit_matches[0].source_token == "nypa"
    assert match.unit_matches[0].matched_entry_key == "nypa"
    assert "source_measurement_parity_changed" not in match.drift_signals
