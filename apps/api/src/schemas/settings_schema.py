"""
Settings domain schemas.

Persisted product preferences — not operator/runtime config.
ai_enabled is read-only: it reflects the LM_STUDIO_ENABLED env flag,
not a value the user can change through the API.
"""
from typing import Literal

from pydantic import BaseModel

# ── Allowed values ─────────────────────────────────────────────────────────────

VerificationStateDefault = Literal["Draft", "Unverified"]
LibrarySortDefault = Literal[
    "updated_at_desc",
    "created_at_desc",
    "title_asc",
    "title_desc",
]

# ── Response ───────────────────────────────────────────────────────────────────


class SettingsOut(BaseModel):
    """Current settings values. ai_enabled is read-only (from .env)."""

    default_verification_state: VerificationStateDefault
    library_default_sort: LibrarySortDefault
    ai_enabled: bool  # read-only — mirrors LM_STUDIO_ENABLED

    model_config = {"from_attributes": True}


# ── Request ────────────────────────────────────────────────────────────────────


class SettingsUpdate(BaseModel):
    """Partial settings update. Only persisted preferences are writable."""

    default_verification_state: VerificationStateDefault | None = None
    library_default_sort: LibrarySortDefault | None = None
