from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPORT_ROOT = REPO_ROOT / "scripts" / "import"
if str(IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPORT_ROOT))

from recipe_import.protected_tokens import compare_protected_tokens, extract_protected_tokens  # noqa: E402


def test_extract_protected_tokens_keeps_swedish_measurements() -> None:
    tokens = extract_protected_tokens("1 tsk spad från relish eller pickles\n1 dl majonnäs\n1 nypa salt")

    assert [token.normalized_unit for token in tokens] == ["tsk", "dl", "nypa"]


def test_compare_protected_tokens_flags_measurement_drift() -> None:
    source_tokens = extract_protected_tokens("1 tsk salt")
    translated_tokens = extract_protected_tokens("1 tbsp salt")

    drift = compare_protected_tokens(source_tokens, translated_tokens)

    assert "measurement_drift" in [code.code for code in drift]
