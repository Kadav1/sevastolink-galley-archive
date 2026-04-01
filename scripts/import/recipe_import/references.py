from __future__ import annotations

import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

from .constants import SWEDISH_RECIPE_TERMS_PATH, SWEDISH_RECIPE_UNITS_PATH


@lru_cache(maxsize=1)
def load_unit_reference() -> dict[str, Any]:
    with SWEDISH_RECIPE_UNITS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def load_term_reference() -> dict[str, Any]:
    with SWEDISH_RECIPE_TERMS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def unit_alias_map() -> dict[str, str]:
    reference = load_unit_reference()
    aliases: dict[str, str] = {}

    for group_name in ("volume_units", "weight_units", "count_units", "package_units"):
        for entry in reference.get(group_name, []):
            canonical = str(entry.get("canonical", "")).strip().lower()
            if not canonical:
                continue
            aliases[canonical] = canonical
            for alias in entry.get("aliases", []):
                cleaned = str(alias).strip().lower()
                if cleaned:
                    aliases[cleaned] = canonical

    for alias, canonical in reference.get("normalization_aliases", {}).items():
        cleaned_alias = str(alias).strip().lower()
        cleaned_canonical = str(canonical).strip().lower()
        if cleaned_alias and cleaned_canonical:
            aliases[cleaned_alias] = cleaned_canonical

    return aliases


@lru_cache(maxsize=1)
def verified_unit_set() -> set[str]:
    return {str(value).strip().lower() for value in load_unit_reference().get("verification_buckets", {}).get("verified_units", [])}


@lru_cache(maxsize=1)
def unit_canonical_map() -> dict[str, str]:
    reference = load_unit_reference()
    canonical_map: dict[str, str] = {}

    for group_name in ("volume_units", "weight_units", "count_units", "package_units", "time_units", "temperature_units"):
        for entry in reference.get(group_name, []):
            canonical = str(entry.get("canonical", "")).strip().lower()
            if not canonical:
                continue
            canonical_map[canonical] = canonical
            for alias in entry.get("aliases", []):
                cleaned = str(alias).strip().lower()
                if cleaned:
                    canonical_map.setdefault(cleaned, canonical)

    for alias, canonical in reference.get("normalization_aliases", {}).items():
        cleaned_alias = str(alias).strip().lower()
        cleaned_canonical = str(canonical).strip().lower()
        if cleaned_alias and cleaned_canonical and cleaned_alias not in canonical_map:
            canonical_map[cleaned_alias] = cleaned_canonical

    return canonical_map


@lru_cache(maxsize=1)
def contextual_guard_terms() -> list[dict[str, Any]]:
    return list(load_term_reference().get("contextual_guard_terms", []))


@lru_cache(maxsize=1)
def false_friend_risks() -> list[dict[str, Any]]:
    return list(load_term_reference().get("false_friend_risks", []))


@lru_cache(maxsize=1)
def _term_lookup_index() -> dict[str, set[str]]:
    reference = load_term_reference()
    index: dict[str, set[str]] = {}

    for entry in reference.get("ingredient_terms", []):
        canonical = str(entry.get("swedish", "")).strip().casefold()
        if not canonical:
            continue
        tokens = {canonical}
        tokens.update(str(alias).strip().casefold() for alias in entry.get("aliases", []))
        for token in tokens:
            if token:
                index.setdefault(token, set()).add(canonical)

    return index


@lru_cache(maxsize=1)
def term_lookup_map() -> dict[str, str]:
    return {
        token: next(iter(canonicals))
        for token, canonicals in _term_lookup_index().items()
        if len(canonicals) == 1
    }


@lru_cache(maxsize=1)
def term_lookup_keys() -> set[str]:
    reference = load_term_reference()
    keys: set[str] = set()
    for entry in reference.get("ingredient_terms", []):
        swedish = str(entry.get("swedish", "")).strip().casefold()
        if swedish:
            keys.add(swedish)
    return keys


@lru_cache(maxsize=1)
def term_lookup_ambiguities() -> set[str]:
    return {token for token, canonicals in _term_lookup_index().items() if len(canonicals) > 1}


@lru_cache(maxsize=1)
def iter_measurement_units(text: str) -> tuple[tuple[str, str], ...]:
    matches: list[tuple[str, str]] = []
    for match in _measurement_pattern().finditer(text):
        canonical = _canonical_unit(match.group("unit"))
        if canonical is None:
            continue
        matches.append((match.group("unit").strip().lower(), canonical))
    return tuple(matches)


@lru_cache(maxsize=1)
def _measurement_pattern() -> re.Pattern[str]:
    alias_tokens = sorted(unit_alias_map().keys(), key=len, reverse=True)
    escaped = "|".join(re.escape(token) for token in alias_tokens)
    return re.compile(
        rf"(?<!\w)(?P<amount>\d+(?:[.,]\d+)?|\d+\s+\d+/\d+|\d+/\d+)\s*(?P<unit>{escaped})(?!\w)",
        flags=re.IGNORECASE,
    )


def _parse_amount(value: str) -> float | None:
    cleaned = value.strip().replace(",", ".")
    if not cleaned:
        return None
    if " " in cleaned and "/" in cleaned:
        whole, fraction = cleaned.split(" ", 1)
        try:
            numerator, denominator = fraction.split("/", 1)
            return float(whole) + (float(numerator) / float(denominator))
        except ValueError:
            return None
    if "/" in cleaned:
        try:
            numerator, denominator = cleaned.split("/", 1)
            return float(numerator) / float(denominator)
        except ValueError:
            return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _canonical_unit(token: str) -> str | None:
    candidate = unit_canonical_map().get(token.strip().lower())
    if candidate is None:
        return None

    seen: set[str] = set()
    while candidate not in seen:
        seen.add(candidate)
        next_candidate = unit_canonical_map().get(candidate)
        if next_candidate is None or next_candidate == candidate:
            return candidate
        candidate = next_candidate

    return candidate


def _unit_metric_value(unit_reference: dict[str, Any], canonical_unit: str, amount: float) -> tuple[str, float] | None:
    for entry in unit_reference.get("volume_units", []):
        if entry.get("canonical") == canonical_unit:
            metric = entry.get("metric_equivalent_ml")
            if metric is not None:
                return ("ml", round(float(metric) * amount, 3))
    for entry in unit_reference.get("weight_units", []):
        if entry.get("canonical") == canonical_unit:
            metric = entry.get("metric_equivalent_g")
            if metric is not None:
                return ("g", round(float(metric) * amount, 3))
    return None


def extract_measurement_signatures(text: str) -> Counter[str]:
    reference = load_unit_reference()
    signatures: Counter[str] = Counter()

    for match in _measurement_pattern().finditer(text):
        canonical = _canonical_unit(match.group("unit"))
        amount = _parse_amount(match.group("amount"))
        if canonical is None or amount is None:
            continue

        metric_value = _unit_metric_value(reference, canonical, amount)
        if metric_value is not None:
            metric_unit, metric_amount = metric_value
            signatures[f"{metric_amount:g} {metric_unit}"] += 1
        else:
            signatures[f"{amount:g} {canonical}"] += 1

    return signatures


def collect_preprocessing_guardrails(*, source_text: str, normalized_input_text: str, source_language: str) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    review_flags: list[str] = []

    if source_language != "sv":
        return warnings, review_flags

    source_measurements = extract_measurement_signatures(source_text)
    normalized_measurements = extract_measurement_signatures(normalized_input_text)
    missing_or_changed = sorted((source_measurements - normalized_measurements).elements())
    introduced_or_changed = sorted((normalized_measurements - source_measurements).elements())

    if missing_or_changed:
        warnings.append(
            "Preprocessing changed or dropped source measurements: "
            + ", ".join(missing_or_changed[:6])
            + ("." if len(missing_or_changed) <= 6 else ", ...")
        )
        review_flags.append("Review preprocessing: source measurement parity changed between Swedish source and normalized input text.")
    if introduced_or_changed:
        warnings.append(
            "Preprocessing introduced measurement values not present in the source: "
            + ", ".join(introduced_or_changed[:6])
            + ("." if len(introduced_or_changed) <= 6 else ", ...")
        )

    source_lower = source_text.casefold()
    normalized_lower = normalized_input_text.casefold()
    for entry in contextual_guard_terms():
        swedish = str(entry.get("swedish", "")).strip()
        if not swedish or swedish.casefold() not in source_lower:
            continue
        preferred = str(entry.get("preferred_english", "")).strip()
        review_flags.append(f"Review preprocessing: contextual term {swedish!r} is present and requires semantic verification.")

        if swedish == "spad från relish eller pickles":
            if not any(token in normalized_lower for token in ("brine", "juice", "liquid")):
                warnings.append("Preprocessing may have lost the liquid/brine meaning for 'spad från relish eller pickles'.")
            if "relish itself" in " ".join(entry.get("must_not_become", [])) and "relish" in normalized_lower and "brine" not in normalized_lower and "juice" not in normalized_lower:
                warnings.append("Preprocessing may have collapsed pickle brine into relish rather than liquid from relish/pickles.")
        elif swedish == "vitlökspulver":
            if "onion powder" in normalized_lower or "white onion powder" in normalized_lower:
                warnings.append("Preprocessing drifted 'vitlökspulver' toward onion powder semantics.")
        elif swedish == "lökpulver":
            if "garlic powder" in normalized_lower or "white onion powder" in normalized_lower:
                warnings.append("Preprocessing drifted 'lökpulver' away from onion powder semantics.")
        elif swedish == "rörs kall":
            if not any(token in normalized_lower for token in ("mixed cold", "stirred cold", "cold", "no heat")):
                warnings.append("Preprocessing may have lost the no-heat meaning of 'rörs kall'.")
        elif swedish == "10 min + vila":
            if not any(token in normalized_lower for token in ("rest", "chill", "refrigerate")):
                warnings.append("Preprocessing may have dropped the rest/chill requirement from '10 min + vila'.")

        if preferred and preferred.casefold() not in normalized_lower:
            warnings.append(f"Preprocessing did not preserve the preferred semantic target for {swedish!r}: {preferred}.")

    for entry in false_friend_risks():
        term = str(entry.get("term", "")).strip()
        risk = str(entry.get("risk", "")).strip()
        if term and term.casefold() in source_lower:
            warnings.append(f"Source contains context-sensitive Swedish term {term!r}: {risk}")
            review_flags.append(f"Review preprocessing: context-sensitive Swedish term {term!r} appears in the source.")

    deduped_warnings: list[str] = []
    seen_warnings: set[str] = set()
    for warning in warnings:
        if warning not in seen_warnings:
            seen_warnings.add(warning)
            deduped_warnings.append(warning)

    deduped_review_flags: list[str] = []
    seen_flags: set[str] = set()
    for flag in review_flags:
        if flag not in seen_flags:
            seen_flags.add(flag)
            deduped_review_flags.append(flag)

    return deduped_warnings, deduped_review_flags
