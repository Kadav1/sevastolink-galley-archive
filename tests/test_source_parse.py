from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPORT_ROOT = REPO_ROOT / "scripts" / "import"
if str(IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPORT_ROOT))

from recipe_import.source_parse import parse_source_text  # noqa: E402


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


def test_parse_source_text_recognizes_swedish_headings() -> None:
    parsed = parse_source_text(
        "Recepttitel\n"
        "Svårighetsgrad: Enkel\n"
        "Ingredienser: 1 dl majonnäs, 1,5 dl mjölk, 2 ägg\n"
        "Tillagningstid: 10 min + vila\n"
        "Tillagning:\n"
        "Vispa ihop\n"
        "Stek i panna\n"
        "Ger: 2 burgare\n"
    )

    assert parsed.title_lines == ["Recepttitel"]
    assert parsed.difficulty_lines == ["Svårighetsgrad: Enkel"]
    assert parsed.ingredient_lines == ["1 dl majonnäs", "1,5 dl mjölk", "2 ägg"]
    assert parsed.time_lines == ["Tillagningstid: 10 min + vila"]
    assert parsed.method_lines == ["Tillagning:"]
    assert parsed.instruction_lines == ["Vispa ihop", "Stek i panna"]
    assert parsed.serving_lines == ["Ger: 2 burgare"]


def test_parse_source_text_handles_multiline_ingredient_sections() -> None:
    parsed = parse_source_text(
        "Ingredienser:\n"
        "1,5 dl mjölk, 2 ägg.\n"
        "1 nypa salt;\n"
        "Gör så här:\n"
        "Vispa ihop\n"
        "Stek i panna\n"
    )

    assert parsed.title_lines == []
    assert parsed.ingredient_lines == ["1,5 dl mjölk", "2 ägg", "1 nypa salt"]
    assert parsed.method_lines == ["Gör så här:"]
    assert parsed.instruction_lines == ["Vispa ihop", "Stek i panna"]


def test_parse_source_text_handles_multiline_instruction_sections() -> None:
    parsed = parse_source_text(
        "Directions:\n"
        "Fold together the sauce.\n"
        "Stir in the onions.\n"
    )

    assert parsed.method_lines == ["Directions:"]
    assert parsed.instruction_lines == ["Fold together the sauce.", "Stir in the onions."]


def test_parse_source_text_keeps_descriptive_commas_with_ingredient_fragment() -> None:
    parsed = parse_source_text(
        "Ingredients: 1 tomato, chopped, 2 eggs\n"
    )

    assert parsed.ingredient_lines == ["1 tomato, chopped", "2 eggs"]


def test_parse_source_text_keeps_sections_across_blank_lines() -> None:
    parsed = parse_source_text(
        "Ingredienser:\n"
        "1 dl mjölk\n"
        "\n"
        "2 ägg\n"
        "\n"
        "Gör så här:\n"
        "Vispa ihop\n"
        "\n"
        "Stek i panna\n"
    )

    assert parsed.ingredient_lines == ["1 dl mjölk", "2 ägg"]
    assert parsed.method_lines == ["Gör så här:"]
    assert parsed.instruction_lines == ["Vispa ihop", "Stek i panna"]
