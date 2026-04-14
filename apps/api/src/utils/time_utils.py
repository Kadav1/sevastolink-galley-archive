from datetime import datetime, timezone

_UTC = timezone.utc


def now_utc() -> str:
    """Return current UTC timestamp as ISO-8601 string (seconds precision)."""
    return datetime.now(_UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
