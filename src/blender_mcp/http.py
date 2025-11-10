"""Small HTTP session factory for shared configuration.

Provides a single place to configure request sessions (headers, retries,
proxies, timeouts). Services should accept an optional `session` parameter
and use `get_session()` when None.
"""
from __future__ import annotations

from typing import Optional

import requests

_global_session: Optional[requests.Session] = None


def get_session() -> requests.Session:
    """Return a shared requests.Session instance, creating it on first use."""
    global _global_session
    if _global_session is None:
        s = requests.Session()
        # sensible defaults
        s.headers.update({"User-Agent": "blender-mcp"})
        _global_session = s
    return _global_session


def reset_session() -> None:
    """Reset the global session (for tests)."""
    global _global_session
    if _global_session is not None:
        try:
            _global_session.close()
        except Exception:
            pass
    _global_session = None


__all__ = ["get_session", "reset_session"]
