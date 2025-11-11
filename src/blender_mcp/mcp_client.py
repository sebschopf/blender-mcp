"""Small MCP HTTP client wrapper used by the bridge.

Provides a single function `call_mcp_tool` that POSTs to the MCP server and
returns parsed JSON. Keeps a single place to add auth, retries, timeouts.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import requests

from .http import get_session


def call_mcp_tool(tool: str, params: dict[str, Any] | None, session: Optional[requests.sessions.Session] = None) -> Any:
    """Call an MCP tool over HTTP and return parsed JSON.

    Accepts an optional requests.Session-like object. If omitted, a shared
    session from `get_session()` will be used.
    """
    MCP_BASE = os.environ.get("MCP_BASE", "http://127.0.0.1:8000")
    sess = session if session is not None else get_session()
    resp = sess.post(f"{MCP_BASE}/tools/{tool}", json={"params": params}, timeout=60)
    resp.raise_for_status()
    return resp.json()
