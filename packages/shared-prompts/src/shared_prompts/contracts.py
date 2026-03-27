"""
PromptContract — canonical shape for a runtime AI prompt entry.

A contract associates a prompt family + version with the concrete file
paths for the instruction text and the expected structured output schema.
It is a stable, named reference — service code should ask the registry for
a contract rather than building paths inline.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PromptContract:
    """Resolved file locations for one versioned prompt contract."""

    family: str
    """Prompt family identifier, e.g. 'normalization', 'metadata'."""

    version: str
    """Version string, e.g. '1'. Increments when the prompt breaks backwards compatibility."""

    prompt_path: Path
    """Absolute path to the runtime prompt .md file."""

    schema_path: Path | None
    """
    Absolute path to the JSON schema for structured output validation,
    or None if this contract does not produce structured JSON output.
    """

    @property
    def key(self) -> tuple[str, str]:
        return (self.family, self.version)

    def __repr__(self) -> str:
        return f"PromptContract({self.family!r}, v{self.version})"
