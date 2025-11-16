# Spec: Legacy Module Removal Timeline

Status: proposed
Date: 2025-11-13
Author: automation
Scope: Deprecated compatibility façades and root helper modules
Phase: 2 (warnings), Phase: 3 (prep), Phase: 4 (removal)

## Summary
Define a formal schedule for removing legacy/shim modules now emitting `DeprecationWarning` at import: dispatcher shims, server shims, root helpers (`polyhaven.py`, `sketchfab.py`, `hyper3d.py`), `connection_core.py` façade, and root `server.py`. Ensures consumers have two release cycles to migrate to canonical paths under `blender_mcp.dispatchers.*`, `blender_mcp.services.*`, and `blender_mcp.servers.*`.

## Motivation
Refactors introduced canonical modules while retaining legacy import paths. Continued coexistence risks divergence and increases maintenance overhead. A documented timeline provides predictability and communicates stable targets for downstream code.

## Inventory (Deprecated Modules)
| Module | Replacement | Warning Added | Notes |
|--------|-------------|---------------|-------|
| `simple_dispatcher.py` | `dispatchers/dispatcher.py` | Phase 2 | Pure façade re-export |
| `command_dispatcher.py` (root) | `dispatchers/dispatcher.py` | Phase 2 | Legacy naming only |
| `server_shim.py` | `servers/shim.py` | Phase 2 | Transition server entry |
| `blender_mcp/server.py` (repo root) | `src/blender_mcp/servers/server.py` | Phase 2 | Test-only shim |
| `connection_core.py` | `services/connection/network_core.py` + `connection.py` | Phase 2 | High‑risk consumers (socket) |
| `polyhaven.py` | `services/polyhaven.py` | Phase 2 | Root helper now warns |
| `sketchfab.py` | `services/sketchfab.py` | Phase 2 | Root helper now warns |
| `hyper3d.py` | `services/hyper3d.py` | Phase 2 | Root helper now warns |

## Removal Timeline
- Phase 2 (Current): Import-time `DeprecationWarning`. CI tolerates warnings.
- Phase 3 (Next minor release): Log an additional INFO message directing migration; update docs to remove legacy examples. Tests begin importing canonical modules; legacy modules still present.
- Phase 4 (Second subsequent release): Remove legacy files from repository. Any import raises `ModuleNotFoundError`. Changelog highlights removal. Major version bump NOT required if semantic versioning treats these as internal (document classification as public vs internal now).

## Public vs Internal Classification
Treat dispatcher façade modules as public until removal; root helpers (`polyhaven.py`, etc.) classified as internal compatibility only. Policy: only canonical service paths (`blender_mcp.services.*`) will be considered stable after Phase 3.

## Migration Guidance
Consumers should:
1. Replace `from blender_mcp.simple_dispatcher import Dispatcher` with `from blender_mcp.dispatchers.dispatcher import Dispatcher`.
2. Replace root service imports (`blender_mcp.polyhaven`) with `blender_mcp.services.polyhaven`.
3. Stop using `connection_core` directly; use `from blender_mcp.connection import BlenderConnection`.
4. Adjust server imports to `from blender_mcp.servers.server import start_server` (example).

## Risks & Mitigations
- Hidden third-party scripts relying on legacy names: warnings provide early signal; Phase 3 adds explicit doc banner.
- Accidental partial removal: tracked via checklist in PROJECT_JOURNAL.md and CI test ensuring absence/presence as appropriate.
- Divergent behavior before removal: forbid functional changes inside legacy modules (no new logic, only warnings) — enforced by code review.

## Acceptance Scenarios
#### Scenario: Phase 3 doc banner present
When opening `docs/developer/ai_session_guide.md` during Phase 3
Then a section lists removed future paths and instructs migration.

#### Scenario: Phase 4 import fails
When importing `blender_mcp.simple_dispatcher` after Phase 4
Then `ModuleNotFoundError` is raised.

#### Scenario: Legacy modules unchanged
Throughout Phases 2-3, the legacy modules contain only re-exports and warning code; no functional divergence from canonical modules.

## Tasks
- [ ] Update docs with Phase 3 migration banner.
- [ ] Add CI test ensuring each legacy module emits `DeprecationWarning` (existing tests partly cover).
- [ ] Phase 3: add INFO log on import (optional) & update endpoint mapping removing legacy references.
- [ ] Phase 4: delete legacy files + update tests & changelog.

## Rollout & Validation
Track tasks in issue #27. Close after Phase 4 removal. Each release: verify warnings still emitted until deletion; ensure changelog entries present.

## Changelog Impact
Phase 2: deprecation notice (done). Phase 4: explicit removal notice with migration steps. No version policy breach given prior warning cycles.

