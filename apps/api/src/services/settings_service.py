"""
Settings service.

Reads and writes well-known setting keys from the key-value settings table.
Returns typed defaults when a key is absent — no row is required upfront.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.models.settings import SettingEntry

# ── Well-known keys ────────────────────────────────────────────────────────────

KEY_DEFAULT_VERIFICATION_STATE = "default_verification_state"
KEY_LIBRARY_DEFAULT_SORT = "library_default_sort"

# ── Defaults ───────────────────────────────────────────────────────────────────

DEFAULTS: dict[str, str] = {
    KEY_DEFAULT_VERIFICATION_STATE: "Draft",
    KEY_LIBRARY_DEFAULT_SORT: "updated_at_desc",
}


# ── Internal helpers ───────────────────────────────────────────────────────────

def _get(db: Session, key: str) -> str:
    row = db.get(SettingEntry, key)
    return row.value if (row and row.value is not None) else DEFAULTS[key]


def _set(db: Session, key: str, value: str) -> None:
    row = db.get(SettingEntry, key)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    if row is None:
        db.add(SettingEntry(key=key, value=value, updated_at=now))
    else:
        row.value = value
        row.updated_at = now


# ── Public interface ───────────────────────────────────────────────────────────

def get_all(db: Session) -> dict[str, str]:
    """Return all persisted settings with defaults applied for missing keys."""
    return {
        KEY_DEFAULT_VERIFICATION_STATE: _get(db, KEY_DEFAULT_VERIFICATION_STATE),
        KEY_LIBRARY_DEFAULT_SORT: _get(db, KEY_LIBRARY_DEFAULT_SORT),
    }


def update(db: Session, updates: dict[str, str]) -> dict[str, str]:
    """Upsert one or more settings. Returns the full settings dict after update."""
    for key, value in updates.items():
        if key in DEFAULTS:
            _set(db, key, value)
    db.flush()
    return get_all(db)
