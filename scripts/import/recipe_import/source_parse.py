from __future__ import annotations

import re

from recipe_import.models import ParsedSource


_DIFFICULTY_PREFIXES = ("difficulty:", "svårighetsgrad:", "svårighet:")
_INGREDIENT_PREFIXES = ("ingredients:", "ingredienser:", "ingrediens:")
_TIME_PREFIXES = ("preparation time:", "cooking time:", "tillagningstid:", "tid:", "förberedelsetid:")
_METHOD_PREFIXES = (
    "cooking process:",
    "cooking method:",
    "tillagning:",
    "gör så här:",
    "instruktioner:",
    "instructions:",
    "directions:",
)
_SERVING_PREFIXES = ("serves:", "yield:", "ger:", "portioner:", "serverar:")
_INGREDIENT_SPLIT_PATTERN = re.compile(r"(?<!\d),(?!\d)")
_NEW_INGREDIENT_FRAGMENT_PATTERN = re.compile(r"^\s*(?:\d+/\d+|\d+|[¼½¾])")


def _matches_heading(line: str, prefixes: tuple[str, ...]) -> bool:
    lowered = line.casefold()
    return any(lowered.startswith(prefix) for prefix in prefixes)


def _split_heading_payload(line: str) -> tuple[str, str]:
    heading, separator, payload = line.partition(":")
    if not separator:
        return line, ""
    return heading + separator, payload.strip()


def _split_ingredient_items(payload: str) -> list[str]:
    parts = _INGREDIENT_SPLIT_PATTERN.split(payload)
    items: list[str] = []
    current_item = ""

    for part in parts:
        stripped_part = part.strip()
        if not stripped_part:
            continue

        if not current_item:
            current_item = stripped_part
            continue

        if _NEW_INGREDIENT_FRAGMENT_PATTERN.match(stripped_part):
            items.append(current_item.rstrip(" .;"))
            current_item = stripped_part
        else:
            current_item = f"{current_item}, {stripped_part}"

    if current_item:
        items.append(current_item.rstrip(" .;"))

    return items


def parse_source_text(source_text: str) -> ParsedSource:
    parsed = ParsedSource()
    active_section: str | None = None
    seen_structured_heading = False

    for raw_line in source_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if _matches_heading(line, _DIFFICULTY_PREFIXES):
            seen_structured_heading = True
            parsed.difficulty_lines.append(line)
            active_section = None
        elif _matches_heading(line, _INGREDIENT_PREFIXES):
            seen_structured_heading = True
            _, payload = _split_heading_payload(line)
            if payload:
                parsed.ingredient_lines.extend(_split_ingredient_items(payload))
            active_section = "ingredients"
        elif _matches_heading(line, _TIME_PREFIXES):
            seen_structured_heading = True
            parsed.time_lines.append(line)
            active_section = None
        elif _matches_heading(line, _METHOD_PREFIXES):
            seen_structured_heading = True
            heading, payload = _split_heading_payload(line)
            parsed.method_lines.append(heading)
            if payload:
                parsed.instruction_lines.append(payload)
            active_section = "instructions"
        elif _matches_heading(line, _SERVING_PREFIXES):
            seen_structured_heading = True
            parsed.serving_lines.append(line)
            active_section = None
        elif active_section == "ingredients":
            parsed.ingredient_lines.extend(_split_ingredient_items(line))
        elif active_section == "instructions":
            parsed.instruction_lines.append(line)
        else:
            if seen_structured_heading:
                parsed.note_lines.append(line)
            else:
                parsed.title_lines.append(line)
    return parsed
