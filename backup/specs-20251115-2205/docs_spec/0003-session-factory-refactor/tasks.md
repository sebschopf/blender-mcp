# 0003 Tasks

1. Implement `src/blender_mcp/http.py` with `get_session()` and `reset_session()`.
2. Migrate modules (`downloaders.py`, `polyhaven.py`, `sketchfab.py`, `hyper3d.py`) to accept `session: Optional[requests.Session]` and forward to `session.get/post` when provided.
3. Add unit tests that pass a fake `requests.Session` to targeted helpers and verify the injected path is used.
