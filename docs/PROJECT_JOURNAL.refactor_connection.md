ARCHIVED: this journal entry has been moved to `docs/archive/PROJECT_JOURNAL.refactor_connection.md`.
See `docs/archive/PROJECT_JOURNAL.refactor_connection.md` for the preserved content.
2025-11-09 | sebas
- Action: SOLID refactor — split `connection` into `services/connection` modules
- Fichiers ajoutés/modifiés:
    - src/blender_mcp/services/connection/reassembler.py (ChunkedJSONReassembler)
    - src/blender_mcp/services/connection/framing.py (LengthPrefixedReassembler)
    - src/blender_mcp/services/connection/socket_conn.py (SocketBlenderConnection)
    - src/blender_mcp/services/connection/network.py (BlenderConnectionNetwork)
    - src/blender_mcp/services/connection/facade.py (BlenderConnection façade)
    - src/blender_mcp/services/connection/__init__.py (ré-exports)
    - src/blender_mcp/connection.py (top-level re-export preserved for compatibility)
    - src/blender_mcp/endpoints.py (now imports services functions directly)
    - src/blender_mcp/services/__init__.py (made import-light to avoid cycles)
- Commands run:
    - `python -m pytest -q` -> full test suite passed locally
    - `python -m ruff check src tests --fix` (applied earlier mechanical fixes)
    - `python -m mypy src` (no reported issues for `src`)
- Statut: done
- Notes:
    - Rationale: to follow SOLID and make the connection code modular and testable, the implementation was split into focused modules under `services/connection/`.
    - Import-time cycles: during the refactor I initially used a package-level `_connection_impl.py` to avoid circular imports with `blender_mcp.services` while iterating. After completing the split and making `services.__init__` import-light, the central implementation was removed and each module now contains its own implementation.
    - Compatibility: `src/blender_mcp/connection.py` remains as a backward-compatible re-export so existing import paths continue to work.
    - Migration note: other code that relied on `blender_mcp.services` attributes (package-level imports) was updated to import service functions directly (e.g., `endpoints.py`), which reduces implicit package coupling.
    - Next: document the decision in a short PR description and consider tightening ruff/mypy rules gradually.
