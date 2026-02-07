"""RedNote data adapters."""

from .base import RedNoteAdapter
from .mock import MockAdapter

__all__ = ["MockAdapter", "RedNoteAdapter"]

# PlaywrightAdapter is optional — only available with [browser] extra
try:
    from .playwright import PlaywrightAdapter  # noqa: F401

    __all__.append("PlaywrightAdapter")
except ImportError:
    pass
