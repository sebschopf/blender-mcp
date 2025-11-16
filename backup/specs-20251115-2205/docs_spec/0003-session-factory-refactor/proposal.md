# Proposal: 0003 - Session factory refactor

Summary
-------

Centralize HTTP session creation into a single factory module to allow injection, testing, and consistent headers (e.g., User-Agent). Migrate helper modules to accept an optional `requests.Session` parameter while preserving conservative fallback to `requests.get/post`.

What changes
------------
- Add `src/blender_mcp/http.py` exposing `get_session()` and `reset_session()`.
- Update downloaders and services to accept `session: Optional[requests.Session]` parameters.
