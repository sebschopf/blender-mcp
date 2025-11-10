# 0004 - Archive symbols: spec

Scope
-----

This spec enumerates the expected behaviours for archived symbols and the compatibility guarantees during refactor operations.

Expected behaviours
-------------------

1. `addon.py` remains importable in non-Blender environments and continues to expose `bl_info`, `register`, `unregister`, and the `BlenderMCPServer` wrapper.
2. Any functional code is implemented under `src/blender_mcp/` and `addon.py` only contains lazy wrappers and metadata.
3. For each archived symbol, there is:
   - a documented disposition (keep/port/deprecate)
   - tests that validate behaviour (import-safety or API compatibility)

Compatibility contract
---------------------

- When porting a symbol, the new implementation must pass existing unit tests and a compatibility shim must be provided for one release cycle if the public API changes.

Validation
----------

- Unit tests in `tests/` cover wrappers and any compatibility shims.
- `openspec validate` must accept the `0004` change directory format and show no missing spec files.
