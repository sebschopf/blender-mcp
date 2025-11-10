## ADDED Requirements

### Requirement: Archive symbol inventory and dispositions
The project SHALL maintain an authoritative inventory of exported symbols present in archived top-level files (such as `addon.py` and `src/blender_mcp/server.py`) and SHALL record, per-symbol, a disposition (keep/port/deprecate) and associated tasks.

#### Scenario: Inventory created
- **WHEN** the change is proposed
- **THEN** a `specs/archive/spec.md` file exists listing the requirement and at least one example scenario validating import-safety and disposition documentation
