"""Small HTTP session factory for shared configuration.

Provides a single place to configure request sessions (headers, retries,
proxies, timeouts). Services should accept an optional `session` parameter
and use `get_session()` when None.
"""

from __future__ import annotations

from typing import Optional

import requests

# To keep tests that monkeypatch `requests.get`/`requests.post` working, we
# provide a lightweight session-proxy that stores headers but delegates the
# actual network calls to the top-level `requests` functions. This preserves
# both the ability to configure shared headers and the ability for tests to
# monkeypatch `requests.get` / `requests.post`.


class _SessionProxy:
    def __init__(self) -> None:
        # session-like headers mapping; callers may update/merge with this
        self.headers: dict[str, str] = {}

    def get(self, url: str, **kwargs):
        headers = dict(self.headers)
        hdrs = kwargs.pop("headers", None)
        if hdrs:
            headers.update(hdrs)
        return requests.get(url, headers=headers, **kwargs)

    def post(self, url: str, **kwargs):
        headers = dict(self.headers)
        hdrs = kwargs.pop("headers", None)
        if hdrs:
            headers.update(hdrs)
        return requests.post(url, headers=headers, **kwargs)

    def close(self) -> None:
        # No-op for the proxy
        return None


_global_session: Optional[_SessionProxy] = None


def get_session() -> _SessionProxy:
    """Return a shared session-like proxy instance (creates on first use).

    The proxy stores headers and delegates network calls to `requests.get`/`post`
    which allows tests that patch `requests` to intercept calls.
    """
    global _global_session
    if _global_session is None:
        s = _SessionProxy()
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
