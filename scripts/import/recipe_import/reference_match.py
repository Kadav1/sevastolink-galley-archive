from __future__ import annotations

import re

from .models import ReferenceMatchArtifact, ReferenceMatchItem, TranslationArtifact
from .references import (
    contextual_guard_terms,
    extract_measurement_signatures,
    iter_measurement_units,
    term_lookup_ambiguities,
    term_lookup_map,
)
def _contains_phrase(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    pattern = re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", flags=re.IGNORECASE)
    return pattern.search(text) is not None


def _build_unit_matches(source_text: str) -> list[ReferenceMatchItem]:
    matches: list[ReferenceMatchItem] = []
    seen: set[tuple[str, str]] = set()

    for source_token, matched_entry_key in iter_measurement_units(source_text):
        key = (source_token, matched_entry_key)
        if key in seen:
            continue
        seen.add(key)
        matches.append(
            ReferenceMatchItem(
                source_token=source_token,
                matched_entry_key=matched_entry_key,
                deterministic=True,
            )
        )

    return matches


def _build_term_matches(source_text: str) -> list[ReferenceMatchItem]:
    matches: list[ReferenceMatchItem] = []
    seen: set[tuple[str, str]] = set()
    ambiguities = term_lookup_ambiguities()

    for source_token, matched_entry_key in term_lookup_map().items():
        if not _contains_phrase(source_text, source_token):
            continue
        key = (source_token, matched_entry_key)
        if key in seen:
            continue
        seen.add(key)
        matches.append(
            ReferenceMatchItem(
                source_token=source_token,
                matched_entry_key=matched_entry_key,
                deterministic=True,
            )
        )

    for source_token in ambiguities:
        if not _contains_phrase(source_text, source_token):
            continue
        key = (source_token, source_token)
        if key in seen:
            continue
        seen.add(key)
        matches.append(
            ReferenceMatchItem(
                source_token=source_token,
                matched_entry_key=source_token,
                deterministic=False,
                requires_review=True,
            )
        )

    return matches


def _build_contextual_matches(source_text: str) -> list[ReferenceMatchItem]:
    matches: list[ReferenceMatchItem] = []
    seen: set[str] = set()

    for entry in contextual_guard_terms():
        phrase = str(entry.get("swedish", "")).strip()
        if not phrase or phrase in seen:
            continue
        if not _contains_phrase(source_text, phrase):
            continue
        seen.add(phrase)
        matches.append(
            ReferenceMatchItem(
                source_token=phrase,
                matched_entry_key=phrase,
                deterministic=False,
                requires_review=True,
            )
        )

    return matches


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

    source_segments = [segment.source_text.strip() for segment in translation.segments if segment.source_text.strip()]
    if not source_segments:
        artifact.drift_signals.append("source_evidence_unavailable")
        return artifact

    source_text = "\n".join(source_segments)
    translated_text = translation.translated_text
    artifact.unit_matches = _build_unit_matches(source_text)
    artifact.term_matches = _build_term_matches(source_text)
    artifact.contextual_matches = _build_contextual_matches(source_text)

    source_measurements = extract_measurement_signatures(source_text)
    translated_measurements = extract_measurement_signatures(translated_text)
    if source_measurements != translated_measurements:
        artifact.drift_signals.append("source_measurement_parity_changed")

    return artifact
