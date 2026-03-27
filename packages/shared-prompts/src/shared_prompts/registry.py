"""
Runtime prompt registry.

Maps (family, version) → PromptContract with resolved absolute paths.

All entries here are RUNTIME prompts (used by the running application).
Build prompts (used to generate code and specs during development) live
under prompts/build/ and are NOT registered here.

Canonical prompt families:
  normalization   — extract structured recipe fields from raw source text
  translation     — translate raw recipe source text into archive-facing English
  evaluation      — review a normalization result for quality and completeness
  metadata        — suggest taxonomy and classification fields for an existing recipe
  rewrite         — rephrase or improve recipe method text in archive style
  pantry          — suggest pantry / ingredient family labels
  similarity      — identify similar recipes within the archive

Versioning:
  - Version is a simple integer string ("1", "2", …).
  - Increment when the prompt instruction changes in a backwards-incompatible way
    (different output schema, removed/added required fields, changed taxonomy).
  - Minor wording fixes that preserve the output contract do not require a version bump.
  - The DEFAULT_VERSION for each family is the current stable version.
"""

from __future__ import annotations

from pathlib import Path

from .contracts import PromptContract

# ── Path roots ────────────────────────────────────────────────────────────────

# This file lives at: packages/shared-prompts/src/shared_prompts/registry.py
# parents[4] is the repository root.
_REPO_ROOT = Path(__file__).resolve().parents[4]
_PROMPTS_ROOT = _REPO_ROOT / "prompts"
_RUNTIME_ROOT = _PROMPTS_ROOT / "runtime"
_SCHEMAS_ROOT = _PROMPTS_ROOT / "schemas"


# ── Registry ──────────────────────────────────────────────────────────────────

REGISTRY: dict[tuple[str, str], PromptContract] = {

    ("normalization", "1"): PromptContract(
        family="normalization",
        version="1",
        prompt_path=_RUNTIME_ROOT / "normalization" / "recipe-normalization-v1.md",
        schema_path=_SCHEMAS_ROOT / "recipe-normalization-output.schema.json",
    ),

    ("translation", "1"): PromptContract(
        family="translation",
        version="1",
        prompt_path=_RUNTIME_ROOT / "translation" / "recipe-translation-v1.md",
        schema_path=_SCHEMAS_ROOT / "recipe-translation-output.schema.json",
    ),

    ("evaluation", "1"): PromptContract(
        family="evaluation",
        version="1",
        prompt_path=_RUNTIME_ROOT / "evaluation" / "normalization-review-v1.md",
        schema_path=_SCHEMAS_ROOT / "normalization-review-output.schema.json",
    ),

    ("metadata", "1"): PromptContract(
        family="metadata",
        version="1",
        prompt_path=_RUNTIME_ROOT / "metadata" / "metadata-suggestion-v1.md",
        schema_path=_SCHEMAS_ROOT / "metadata-suggestion-output.schema.json",
    ),

    ("rewrite", "1"): PromptContract(
        family="rewrite",
        version="1",
        prompt_path=_RUNTIME_ROOT / "rewrite" / "archive-rewrite-v1.md",
        schema_path=_SCHEMAS_ROOT / "archive-rewrite-output.schema.json",
    ),

    ("pantry", "1"): PromptContract(
        family="pantry",
        version="1",
        prompt_path=_RUNTIME_ROOT / "pantry" / "pantry-suggestion-v1.md",
        schema_path=_SCHEMAS_ROOT / "pantry-suggestion-output.schema.json",
    ),

    ("similarity", "1"): PromptContract(
        family="similarity",
        version="1",
        prompt_path=_RUNTIME_ROOT / "similarity" / "similar-recipes-v1.md",
        schema_path=_SCHEMAS_ROOT / "similar-recipes-output.schema.json",
    ),
}

# Default (current stable) version for each family.
DEFAULT_VERSION: dict[str, str] = {
    "normalization": "1",
    "translation":   "1",
    "evaluation":    "1",
    "metadata":      "1",
    "rewrite":       "1",
    "pantry":        "1",
    "similarity":    "1",
}


# ── Lookup ────────────────────────────────────────────────────────────────────

def get_contract(family: str, version: str | None = None) -> PromptContract:
    """
    Return the PromptContract for the given family and version.

    If version is omitted, the current default version is used.
    Raises KeyError if the (family, version) pair is not in the registry.
    """
    resolved_version = version if version is not None else DEFAULT_VERSION.get(family)
    if resolved_version is None:
        raise KeyError(f"No prompt family registered: {family!r}")
    key = (family, resolved_version)
    if key not in REGISTRY:
        raise KeyError(
            f"No prompt contract registered for {family!r} version {resolved_version!r}. "
            f"Available: {sorted(REGISTRY.keys())}"
        )
    return REGISTRY[key]


def all_contracts() -> list[PromptContract]:
    """Return all registered prompt contracts."""
    return list(REGISTRY.values())
