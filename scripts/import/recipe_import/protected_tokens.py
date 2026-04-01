from __future__ import annotations

import re

from .models import DriftCode, ProtectedToken
from .references import load_unit_reference


MEASUREMENT_PATTERN = re.compile(
    r"(?P<quantity>[0-9]+(?:[.,][0-9]+)?|[0-9]+/[0-9]+)\s*(?P<unit>[A-Za-zÅÄÖåäö]+)",
)


def _normalized_unit_map() -> dict[str, str]:
    reference = load_unit_reference()
    canonical_units = reference.get("canonical_units")
    normalized: dict[str, str] = {}

    if isinstance(canonical_units, dict):
        for canonical_unit, metadata in canonical_units.items():
            canonical_key = str(canonical_unit).strip().casefold()
            if not canonical_key or not isinstance(metadata, dict):
                continue
            if metadata.get("protected", True) is False:
                continue
            normalized[canonical_key] = canonical_key
            aliases = metadata.get("aliases", [])
            if isinstance(aliases, list):
                for alias in aliases:
                    alias_key = str(alias).strip().casefold()
                    if alias_key:
                        normalized[alias_key] = canonical_key

    return normalized


def normalize_reference_unit(unit_text: str) -> str | None:
    cleaned = unit_text.strip().casefold()
    if not cleaned:
        return None
    return _normalized_unit_map().get(cleaned)


def extract_protected_tokens(text: str) -> list[ProtectedToken]:
    tokens: list[ProtectedToken] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = MEASUREMENT_PATTERN.search(line)
        if match is None:
            continue
        normalized_unit = normalize_reference_unit(match.group("unit"))
        if normalized_unit is None:
            continue
        quantity_text = match.group("quantity")
        tokens.append(
            ProtectedToken(
                source_text=line,
                quantity_text=quantity_text,
                normalized_quantity=quantity_text.replace(",", "."),
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
            drift.append(
                DriftCode(
                    code="measurement_drift",
                    severity="review_flag",
                    message="Protected measurement unit changed.",
                )
            )
    return drift
