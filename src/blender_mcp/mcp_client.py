"""Small MCP HTTP client wrapper used by the bridge.

Provides a single function `call_mcp_tool` that POSTs to the MCP server and
returns parsed JSON. Keeps a single place to add auth, retries, timeouts.
"""

from __future__ import annotations

import os
from typing import Any, Optional, cast

import requests

import blender_mcp.http as _http


def call_mcp_tool(tool: str, params: dict[str, Any] | None, session: Optional[requests.sessions.Session] = None) -> Any:
    """Call an MCP tool over HTTP and return parsed JSON.

    Accepts an optional requests.Session-like object. If omitted, a shared
    session from `get_session()` will be used.
    """
    MCP_BASE = os.environ.get("MCP_BASE", "http://127.0.0.1:8000")
    sess = session if session is not None else cast("requests.sessions.Session", get_session())
    resp = sess.post(f"{MCP_BASE}/tools/{tool}", json={"params": params}, timeout=60)
    resp.raise_for_status()
    return resp.json()


def get_session() -> Any:
    """Compatibility shim exposed for tests: returns the shared session.

    Tests sometimes monkeypatch `blender_mcp.mcp_client.get_session`. Expose a
    function that delegates to the real factory so those monkeypatches continue
    to work.
    """
    return _http.get_session()
