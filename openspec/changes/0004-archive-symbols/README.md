# 0004 - Archive symbol mapping and migration

Proposal: Create a precise inventory of symbols present in archived top-level files (`addon.py`, `src/blender_mcp/server.py`) and author OpenSpec proposals/tasks for each symbol. This change documents what is archived, what to port, what to deprecate, and provides a minimal, testable migration plan to keep the add-on import-safe while moving implementations under `src/blender_mcp/`.

Why: During refactor we must not lose track of legacy symbols kept in archive files. Having an explicit OpenSpec change for each symbol ensures traceability, acceptance criteria and smooth stepwise migration.

Files added in this change:
- `openspec/changes/0004-archive-symbols/symbols/*` : per-symbol proposal files

High level steps:
1. Inventory symbols in archive files and create per-symbol proposals (done in this change).
2. For each symbol: decide (port|wrap|deprecate) and add an implementation task referencing this change id.
3. Implement porting tasks in small PRs, validate with tests and mark the symbol change as completed in openspec.

Acceptance criteria:
- Each archived file has an inventory file in this change describing contained symbols.
- For every symbol a proposed disposition (port/wrap/deprecate) is recorded with test expectations and migration steps.
- The change contains clear next steps (task list) for engineering and testing.

Proposer: session-factory-refactor (automation)
