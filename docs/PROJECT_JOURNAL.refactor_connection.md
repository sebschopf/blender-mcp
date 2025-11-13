ARCHIVED: this journal entry has been moved to `docs/archive/PROJECT_JOURNAL.refactor_connection.md`.
See `docs/archive/PROJECT_JOURNAL.refactor_connection.md` for the preserved content.

2025-11-13 | automation
- Action: SRP assessment follow-up (connection package)
- Current modules & responsibilities:
    - `network_core.py`: orchestrates transport selection (core vs raw socket), send/receive, JSON reassembly (newline-delimited). Combines concerns: strategy selection + framing + retry/timeout logging.
    - `network.py` (façade): thin wrapper preserving historical API.
    - `socket_conn.py`: length-prefixed framing send/receive, buffering multiple messages.
    - `reassembler.py`: newline-delimited JSON extraction.
    - `framing.py`: length-prefixed frame parsing.
    - `facade.py`: tri-mode wrapper (socket / network / reassembler) multiplexing disparate responsibilities.
- SRP Findings:
    1. `facade.BlenderConnection` mixes three interfaces (socket, network client, incremental reassembler) — candidates for separate classes to reduce type branching.
    2. `NetworkCore` holds both connection strategy (core vs socket) and message framing & receive loop logic. A smaller `ConnectionStrategy` abstraction could isolate selection from framing.
    3. Framing and reassembly are already separated (`framing.py`, `reassembler.py`) — good; they can be injected instead of hard-coded inside `socket_conn.py` / `network_core.py` to improve test substitution.
    4. Error handling (logging + exception raising) lives inline; could move to a lightweight decorator or instrumentation strategy (reuse pattern from dispatcher) to keep `NetworkCore` focused on orchestration only.
- Proposed incremental refactor (non-breaking plan):
    - Phase A: introduce explicit classes `RawSocketTransport` (connect/close/send/recv) and `CoreTransport` (wrapper around legacy core class) with a `Transport` Protocol.
    - Phase B: split `NetworkCore` into `TransportSelector` (choose implementation) and `ResponseReceiver` (loop with `ChunkedJSONReassembler`). Keep façade delegating to a composed instance.
    - Phase C: decompose `BlenderConnection` façade into three explicit public classes (`SocketConnection`, `NetworkClient`, `JsonReassembler`) and retain `BlenderConnection` as a thin compatibility shim emitting DeprecationWarning.
    - Phase D: add optional `ConnectionInstrumentationStrategy` mirroring dispatcher instrumentation (callbacks: on_connect, on_send, on_receive, on_disconnect, on_timeout).
- Migration considerations:
    - Tests rely on existing import paths and behavior; new classes can be introduced alongside current ones without removal at first.
    - Avoid changing return shapes (still raw dict or raised exceptions) — any normalization must be spec’d.
    - Deprecation warnings for `BlenderConnection` can follow same 2-cycle schedule defined in legacy removal spec.
- Risks & mitigation:
    - Over-fragmentation: ensure each extracted class has a single clear responsibility and minimal public surface.
    - Test churn: add targeted tests for new classes before altering existing ones; keep old tests until shim removal phase.
- Next step suggestion: implement Phase A transport protocol (minimal PR: add `transport.py` + refactor `NetworkCore` usage).
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
