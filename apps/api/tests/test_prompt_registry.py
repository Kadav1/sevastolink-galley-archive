"""
Tests for the shared-prompts registry and loader.

Verifies:
  - All registered contracts are importable and well-formed
  - All registered file paths exist on disk
  - loader.load_prompt_text() returns a non-empty string for each contract
  - loader.load_schema() returns a non-empty dict for contracts with schemas
  - loader.build_response_format() produces a valid response_format payload
  - get_contract() raises KeyError for unknown families/versions
"""

import pytest

from shared_prompts import all_contracts, get_contract, loader
from shared_prompts.contracts import PromptContract


# ── Registry completeness ─────────────────────────────────────────────────────

EXPECTED_FAMILIES = {"normalization", "translation", "evaluation", "metadata", "rewrite", "pantry", "similarity"}


def test_all_expected_families_registered():
    registered = {c.family for c in all_contracts()}
    assert registered == EXPECTED_FAMILIES


def test_all_contracts_have_version_1():
    for contract in all_contracts():
        assert contract.version == "1", f"{contract.family} has unexpected version {contract.version!r}"


# ── Asset existence ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("contract", all_contracts(), ids=lambda c: f"{c.family}_v{c.version}")
def test_prompt_file_exists(contract: PromptContract):
    missing = loader.missing_assets(contract)
    assert missing == [], f"Missing files for {contract}: {missing}"


# ── Prompt text loading ───────────────────────────────────────────────────────

@pytest.mark.parametrize("contract", all_contracts(), ids=lambda c: f"{c.family}_v{c.version}")
def test_load_prompt_text_nonempty(contract: PromptContract):
    text = loader.load_prompt_text(contract)
    assert isinstance(text, str)
    assert len(text) > 50, f"Prompt text for {contract} is suspiciously short ({len(text)} chars)"


# ── Schema loading ────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "contract",
    [c for c in all_contracts() if c.schema_path is not None],
    ids=lambda c: f"{c.family}_v{c.version}",
)
def test_load_schema_is_dict(contract: PromptContract):
    schema = loader.load_schema(contract)
    assert isinstance(schema, dict)
    assert len(schema) > 0


@pytest.mark.parametrize(
    "contract",
    [c for c in all_contracts() if c.schema_path is not None],
    ids=lambda c: f"{c.family}_v{c.version}",
)
def test_build_response_format_shape(contract: PromptContract):
    fmt = loader.build_response_format(contract)
    assert fmt["type"] == "json_schema"
    js = fmt["json_schema"]
    assert "name" in js
    assert js["name"] == f"{contract.family}_output_v{contract.version}"
    assert "strict" in js
    assert "schema" in js and isinstance(js["schema"], dict)


# ── get_contract() error handling ─────────────────────────────────────────────

def test_get_contract_unknown_family():
    with pytest.raises(KeyError, match="[Nn]o prompt family"):
        get_contract("nonexistent_family")


def test_get_contract_unknown_version():
    with pytest.raises(KeyError):
        get_contract("normalization", "999")


def test_get_contract_default_version():
    contract = get_contract("normalization")
    assert contract.family == "normalization"
    assert contract.version == "1"


# ── PromptContract invariants ─────────────────────────────────────────────────

def test_contract_key_property():
    contract = get_contract("normalization")
    assert contract.key == ("normalization", "1")


def test_contract_is_frozen():
    contract = get_contract("normalization")
    with pytest.raises((AttributeError, TypeError)):
        contract.family = "mutated"  # type: ignore[misc]
