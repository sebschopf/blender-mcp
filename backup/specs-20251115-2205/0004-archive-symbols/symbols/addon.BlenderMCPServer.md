# Symbol: `BlenderMCPServer` (addon.py — lazy wrapper)

Location: `addon.py` (archive) — wrapper delegates to `blender_mcp.server.BlenderMCPServer`.

Current status:
- `BlenderMCPServer` in `addon.py` is a lazy wrapper that imports the real implementation on instantiation and delegates attribute access.

Proposal:
- Keep this wrapper in `addon.py` to preserve import-safety. Create a spec describing the canonical implementation location (`src/blender_mcp/server.py`) and a migration plan to ensure the real server implements the public API used by the wrapper.

Acceptance criteria:
- Wrapper raises a clear RuntimeError when the real implementation is not available (current behaviour).
- The real server implementation provides the public methods used by clients and has unit tests (see `tests/test_server.py`).

Tasks:
- Add an OpenSpec task to record the mapping: `addon.BlenderMCPServer -> src/blender_mcp/server.BlenderMCPServer` and link tests that validate API compatibility.
