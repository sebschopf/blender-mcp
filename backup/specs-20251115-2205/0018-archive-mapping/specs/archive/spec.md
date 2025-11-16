# Archive mapping delta spec

## ADDED Requirements

### Requirement: Archive mapping document

A document `docs/archive_symbol_mapping.md` MUST be produced listing archived symbols and their canonical implementation locations under `src/blender_mcp`, and must recommend a disposition for each (keep shim, move+shim, or remove).

#### Scenario: Mapping exists

- Given the repository contains legacy symbols in the top-level `blender_mcp` shim and canonical implementations under `src/blender_mcp`
- When `docs/archive_symbol_mapping.md` is produced
- Then each archived symbol appears with a recommended disposition and at least one rationale sentence explaining the choice.
