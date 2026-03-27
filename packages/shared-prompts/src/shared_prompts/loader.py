"""
Prompt and schema loading utilities.

Functions here work with PromptContract objects from the registry.
They do not hardcode file paths — callers obtain a contract via
`get_contract()` and pass it here.
"""

from __future__ import annotations

import json
from typing import Any

from .contracts import PromptContract


# ── Prompt text ───────────────────────────────────────────────────────────────

def load_prompt_text(contract: PromptContract) -> str:
    """
    Load and return the instruction text from a runtime prompt .md file.

    Runtime prompts are Markdown documents that contain the system instruction
    inside a fenced ```text … ``` block. If no such block is found, the entire
    file content is returned (trimmed).

    Raises FileNotFoundError if the prompt file does not exist.
    """
    text = contract.prompt_path.read_text(encoding="utf-8")

    start_marker = "```text"
    start = text.find(start_marker)
    if start == -1:
        # No fenced block — return full file trimmed
        return text.strip()

    # Move past the opening fence to the start of the content
    content_start = text.find("\n", start)
    if content_start == -1:
        return text.strip()

    # Find the closing fence
    content_end = text.find("```", content_start + 1)
    if content_end == -1:
        return text[content_start:].strip()

    return text[content_start:content_end].strip()


# ── Schema loading ────────────────────────────────────────────────────────────

def load_schema(contract: PromptContract) -> dict[str, Any]:
    """
    Load and return the JSON schema dict for a contract's structured output.

    Raises ValueError if the contract has no schema_path.
    Raises FileNotFoundError if the schema file does not exist.
    Raises json.JSONDecodeError if the schema file is not valid JSON.
    """
    if contract.schema_path is None:
        raise ValueError(
            f"Contract {contract.family!r} v{contract.version} has no associated schema. "
            "Check the registry entry."
        )
    return json.loads(contract.schema_path.read_text(encoding="utf-8"))


def build_response_format(contract: PromptContract, strict: bool = True) -> dict[str, Any]:
    """
    Build an OpenAI-compatible response_format dict for JSON schema enforcement.

    The returned dict is suitable for passing directly to
    LMStudioClient.chat_completion(response_format=...).

    Raises ValueError if the contract has no schema.
    """
    schema = load_schema(contract)
    schema_name = f"{contract.family}_output_v{contract.version}"
    return {
        "type": "json_schema",
        "json_schema": {
            "name": schema_name,
            "strict": strict,
            "schema": schema,
        },
    }


# ── Asset validation ──────────────────────────────────────────────────────────

def missing_assets(contract: PromptContract) -> list[str]:
    """
    Return a list of file paths that are registered but do not exist on disk.

    An empty list means all assets are present and loadable.
    """
    absent: list[str] = []
    if not contract.prompt_path.exists():
        absent.append(str(contract.prompt_path))
    if contract.schema_path is not None and not contract.schema_path.exists():
        absent.append(str(contract.schema_path))
    return absent
