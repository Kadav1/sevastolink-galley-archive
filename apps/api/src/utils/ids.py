"""
ULID generator — stdlib only.

ULID spec: 48-bit millisecond timestamp + 80-bit random = 128 bits
Encoded as 26 Crockford base32 characters (uppercase, no I/L/O/U).
"""

import os
import time

_ENCODING = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid() -> str:
    """Return a new ULID string (26 uppercase chars, lexicographically sortable)."""
    ms = int(time.time() * 1000)
    random_bytes = int.from_bytes(os.urandom(10), "big")

    chars: list[str] = []

    # 10 chars of timestamp (48 bits)
    t = ms
    for _ in range(10):
        chars.append(_ENCODING[t & 0x1F])
        t >>= 5
    chars[0:10] = chars[9::-1]  # reverse so most-significant first

    # 16 chars of randomness (80 bits)
    r = random_bytes
    for _ in range(16):
        chars.append(_ENCODING[r & 0x1F])
        r >>= 5

    return "".join(chars)


def is_ulid(value: str) -> bool:
    """Return True if value looks like a ULID (26 chars, all Crockford base32)."""
    if len(value) != 26:
        return False
    return all(c in _ENCODING for c in value.upper())
