### Résumé
Refactor Phase 2 : ajout stratégie d'instrumentation du dispatcher (non-breaking), baseline sécurité pour `execute_blender_code` (audit logger + dry-run), dépréciations des shims legacy (warnings import), synchronisation mapping endpoints et enregistrement service `asset_creation_strategy`.

### Changements Principaux
- Dispatcher: injection options `handler_resolution_strategy`, `policy_strategy`, `instrumentation_strategy` + hooks start/success/error/adapter.
- Execute Service: audit file logger `blender_mcp_execute.log` + branche dry-run via env `BLENDER_MCP_EXECUTE_DRY_RUN`.
- Legacy: DeprecationWarning sur `simple_dispatcher.py`, `command_dispatcher.py`, `server_shim.py`, `server.py` (façade), `connection_core.py`, racine `blender_mcp/server.py`, helpers `polyhaven.py`, `sketchfab.py`, `hyper3d.py`.
- Materials: scission en package pur (`materials/spec.py`) + création Blender optionnelle (`materials/blender_create.py`) + façade de compatibilité.
- Services Registry: ajout prompt service `asset_creation_strategy` + tests mapping kwargs.
- ASGI `/tools`: option d'exposition du registre via `BLENDER_MCP_EXPOSE_REGISTRY_TOOLS`.
- Docs & Specs: specs instrumentation + timeline retrait legacy + deprecations + journal & architecture mis à jour.

### Specs Référencées
- Instrumentation Strategy: `openspec/changes/2025-11-13-dispatcher-instrumentation-strategy/spec.md`
- Deprecations warnings: `openspec/changes/2025-11-13-deprecations-legacy-shims/spec.md`
- Legacy removal timeline: `openspec/changes/2025-11-13-legacy-removal-timeline/spec.md`

### Tests
Commandes locales:
```powershell
$Env:PYTHONPATH='src'
pytest -q tests/test_dispatcher_instrumentation.py tests/test_execute_service.py tests/test_deprecations.py tests/test_dispatcher_strategies.py tests/test_prompt_service.py tests/test_services_registry_extra.py
pytest -q
Remove-Item Env:PYTHONPATH
```
Tous verts; warnings de dépréciation attendus.

### Migration
Importer désormais:
- Dispatcher: `from blender_mcp.dispatchers.dispatcher import Dispatcher`
- Services: `from blender_mcp.services.polyhaven import get_polyhaven_categories`
- Server: `from blender_mcp.servers.server import BlenderMCPServer`
- Connection: `from blender_mcp.connection import BlenderConnection`
Shims resteront deux cycles avec warnings puis seront retirés (Phase 4).

### Sécurité Execute (Phase 2)
- Audit logging minimal + dry-run.
- Phase 3 planifiée: sandbox AST/allowlist + instrumentation métriques.

### Suivi / Prochaines Étapes
1. Phase A Transport: introduire `RawSocketTransport` + `CoreTransport` (voir journal SRP).
2. Stratégie instrumentation connexion (on_connect/on_send/on_receive/on_timeout).
3. Durcissement execute (sandbox).
4. Export métriques (Prometheus/OpenTelemetry) via implémentation instrumentation.

### Validation
- Aucun breaking change API publique.
- Réponses services inchangées (`status`, `result|message`, `error_code optionnel`).
- Couverture tests étendue aux stratégies / instrumentation / prompts / dépréciations.

Merci pour la revue. Suggestions welcome.
