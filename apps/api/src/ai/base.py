"""Shared base types for AI module error handling."""


class AiError:
    """Plain base class for AI module errors.

    Not a dataclass — keeping it plain allows frozen subclasses to inherit
    ``__str__`` without the frozen/unfrozen inheritance restriction.
    Subclasses are frozen dataclasses that define their own ``kind`` and
    ``message`` fields.
    """

    def __str__(self) -> str:
        kind = getattr(self, "kind", "unknown")
        kind_str = kind.value if hasattr(kind, "value") else str(kind)
        return f"{type(self).__name__}({kind_str}): {getattr(self, 'message', '')}"
