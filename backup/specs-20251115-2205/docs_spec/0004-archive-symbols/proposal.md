# Proposal: 0004 - Archive symbol mapping and migration

Summary
-------

Capture and formalize the inventory and migration plan for symbols that currently live in archive top-level files (`addon.py`, `src/blender_mcp/server.py`). The goal is to ensure stepwise, testable porting or retention of those symbols while keeping the add-on import-safe.

What this change does
---------------------
- Records an authoritative inventory of archived symbols (per-symbol files under `symbols/`).
- Proposes dispositions for each symbol (keep as archive, port to `src/`, or deprecate).
- Creates explicit tasks for porting, testing and validation tied to each symbol.

Why now
--------

The ongoing refactor (session factory, embedded adapter) touches API surface and risks losing traceability for archived symbols. This proposal locks an explicit migration contract.

Acceptance criteria
-------------------
- There is a complete inventory of symbols in the archived files.
- Every symbol has an associated disposition and at least one follow-up task or reference implementation.
- Tests demonstrate that import-safety is preserved for `addon.py`.
