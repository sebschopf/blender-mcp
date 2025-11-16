# Deprecation proposal: `connection_core.py`

Id: 2025-11-14-deprecate-connection_core

Summary
-------
Propose deprecating the legacy compatibility shim `src/blender_mcp/connection_core.py` over a two-release cycle. The `services.connection` package (notably `NetworkCore` and `Transport` abstractions) is the canonical API and should be the migration target for consumers.

Motivation
----------
- `connection_core.py` duplicates logic present in `services.connection.network_core` and the new transport abstractions.
- Keeping both implementations indefinitely increases maintenance burden and risks divergence.

Proposal
--------
1. Mark `connection_core.py` as deprecated (already emits DeprecationWarning on import). Keep the shim functional for backward compatibility for two releases.
2. Add documentation and examples in `DEVELOPER_SETUP.md` and `docs/TRANSPORT_PHASE_A.md` that show how to migrate consumers to `services.connection.NetworkCore` or inject a `Transport` instance.
3. Add a follow-up OpenSpec in ~2 release cycles to remove the shim and update tests to import canonical modules.

Acceptance criteria
-------------------
- All public behaviors are preserved during the deprecation window (no regression in tests).
- Migration guide added to `docs/TRANSPORT_PHASE_A.md` and `DEVELOPER_SETUP.md`.
- A new OpenSpec entry is scheduled for removal at least 2 releases ahead.
