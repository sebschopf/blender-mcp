"""Shared constants used by addon service modules.

Keep minimal runtime cost; these are simple constants used for network calls
and feature flags.
"""

from __future__ import annotations

import requests

# Minimal required constants (kept local to avoid circular imports)
REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "blender-mcp"})

RODIN_FREE_TRIAL_KEY = "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez"

__all__ = ["REQ_HEADERS", "RODIN_FREE_TRIAL_KEY"]
