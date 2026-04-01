from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import ReferenceMatchArtifact, TranslationArtifact


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
