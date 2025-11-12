# Inventory Full — src/blender_mcp (détail)

Ce document contient la liste complète des fichiers trouvés sous `src/blender_mcp` et du shim racine `blender_mcp/`, avec une recommandation rapide pour consolidation, un indicateur de risque, et s'il faut préparer une proposition OpenSpec.

Format: Path | Rôle estimé | Recommandation courte | Risque | OpenSpec

| Path | Rôle estimé | Recommandation courte | Risque | OpenSpec |
|---|---|---|---:|---:|
| `blender_mcp/__init__.py` | Shim racine / compat | Documenter comme shim; rendre lazy si besoin | High | Yes |
| `blender_mcp/server.py` | Shim racine minimal (façade pour tests) | Rendre explicitement lazy / déléguer à `src/` ou déplacer vers `tools/` | High | Yes |
| `src/blender_mcp/__init__.py` | Package canonique — lazy exports | Garder; clarifier API publique dans docs | Low | No |
| `src/blender_mcp/server.py` | Impl serveur canonique (lifecycle, handlers) | Consolider ici; ajouter tests d'API et lifecycle | High | Yes (if API change) |
| `src/blender_mcp/server_shim.py` | Shim interne / compat | Regrouper sous `compat/` et rendre import-safe | Medium | Possibly |
| `src/blender_mcp/servers/__init__.py` | Package servers | Clarifier exports; minimal init | Low | No |
| `src/blender_mcp/servers/shim.py` | Shim pour servers package | Consolider dans `compat/` et rendre import-safe | Medium | Possibly |
| `src/blender_mcp/servers/server.py` | Impl servers spécifique | Fusionner/réexporter depuis `src/blender_mcp/server.py` | High | Possibly |
| `src/blender_mcp/servers/embedded_adapter.py` | Adaptateur embedded | Ajouter tests; extraire interface testable | Medium | No |
| `src/blender_mcp/server.py` | (duplicate path entry) | See canonical server note above | High | Possibly |
| `src/blender_mcp/server_shim.py` | (duplicate) | See shim entry above | Medium | Possibly |
| `src/blender_mcp/types.py` | Types partagés | Centraliser et enrichir typings, mypy coverage | Low | No |
| `src/blender_mcp/tools.py` | Helpers utilitaires | Auditer SRP; déplacer helpers spécifiques vers services | Low | No |
| `src/blender_mcp/texture_helpers.py` | Helpers textures | Déplacer si exclusivement utilisé par services | Low | No |
| `src/blender_mcp/sketchfab.py` | Sketchfab integration | Tests d'intégration mockés; document | Medium | No |
| `src/blender_mcp/simple_dispatcher.py` | Ancienne copie top-level | Unifier avec `dispatchers/` ou garder comme compat | Medium | Possibly |
| `src/blender_mcp/prompts.py` | Prompt helpers | Garder; tests unitaires | Low | No |
| `src/blender_mcp/primitive.py` | Primitive helpers | Keep small, add tests | Low | No |
| `src/blender_mcp/polyhaven.py` | PolyHaven integration | Tests, retry logic, document | Medium | No |
| `src/blender_mcp/node_helpers.py` | Node helpers | Audit for SRP; add types | Low | No |
| `src/blender_mcp/mcp_client.py` | Client MCP (remote calls) | Clarify responsibilities; add unit tests | Medium | No |
| `src/blender_mcp/materials.py` | Materials helpers | Add tests; move to services/templates if needed | Low | No |
| `src/blender_mcp/integrations.py` | Integration helpers | Split by integration; add tests | Medium | No |
| `src/blender_mcp/hyper3d.py` | Hyper3D integration | Tests + doc; treat as integration module | Medium | No |
| `src/blender_mcp/http.py` | HTTP helpers | Keep; add typing and tests | Low | No |
| `src/blender_mcp/gemini_client.py` | Gemini bridge client | Mark as external integration; mock in tests | Medium | No |
| `src/blender_mcp/endpoints.py` | Endpoint registry / mapping | Audit signatures; add integration tests | High | Yes (if signature changes) |
| `src/blender_mcp/downloaders.py` | Downloaders (PolyHaven etc.) | Tests network/retry; keep under services when stable | Medium | No |
| `src/blender_mcp/connection_core.py` | Core connection (BlenderConnection) | Stabilize; separate network vs API; add socket tests | High | Possibly |
| `src/blender_mcp/config.py` | Configuration | Centralize env vars; add tests | Low | No |
| `src/blender_mcp/command_dispatcher.py` | Top-level command dispatcher | Move to `dispatchers/` and deprecate old imports | Medium | Possibly |
| `src/blender_mcp/blender_codegen.py` | Codegen utilities | Keep under `codegen/`; add tests | Low | No |
| `src/blender_mcp/asgi.py` | ASGI adapter | Add integration tests; document lifecycle | Medium | No |
| `src/blender_mcp/codegen/__init__.py` | Codegen package init | Keep | Low | No |
| `src/blender_mcp/codegen/blender_codegen.py` | Codegen implementation | Keep and test | Low | No |
| `src/blender_mcp/dispatchers/command_dispatcher.py` | Dispatcher (command style) | Consolidate interface; add tests | Medium | No |
| `src/blender_mcp/dispatchers/dispatcher.py` | Dispatcher core | Keep canonical; add docs and tests | High | No |
| `src/blender_mcp/dispatchers/simple_dispatcher.py` | Simple dispatcher (compat) | Keep as compat; add tests | Medium | No |
| `src/blender_mcp/archive/simple_dispatcher.py` | Archive snapshot | Preserve in archive; exclude from lint/type | Low | No |
| `src/blender_mcp/archive/server_shim.py` | Archive snapshot shim | Preserve; do not modify | Low | No |
| `src/blender_mcp/archive/server.py` | Archive server snapshot | Preserve; do not modify | Low | No |
| `src/blender_mcp/blender_ui/addon_handlers.py` | Addon UI handlers | Ensure import-safety; add light tests | Medium | No |
| `src/blender_mcp/archive/embedded_server_adapter.py` | Archive embedded adapter | Keep snapshot only | Low | No |
| `src/blender_mcp/archive/dispatcher.py` | Archive dispatcher | Snapshot; preserve | Low | No |
| `src/blender_mcp/archive/connection.py` | Archive connection snapshot | Preserve only; excluded | Low | No |
| `src/blender_mcp/archive/command_dispatcher.py` | Archive command dispatcher | Preserve | Low | No |
| `src/blender_mcp/archive/blender_ui.py` | Archive blender_ui snapshot | Preserve | Low | No |
| `src/blender_mcp/archive/addon_handlers.py` | Archive addon handlers | Preserve | Low | No |
| `src/blender_mcp/blender_ui/__init__.py` | Addon UI package init | Keep import-safe | Low | No |
| `src/blender_mcp/blender_ui/props.py` | UI props | Keep import-safe | Low | No |
| `src/blender_mcp/blender_ui/panel.py` | UI panel | Keep import-safe; unit tests for logic | Medium | No |
| `src/blender_mcp/blender_ui/operators.py` | UI operators | Keep import-safe; unit tests | Medium | No |
| `src/blender_mcp/templates/asset_creation_strategy.txt` | Template text | Keep | Low | No |
| `src/blender_mcp/services/__init__.py` | Services package init | Keep; ensure exports correct | Low | No |
| `src/blender_mcp/services/utils.py` | Services utilities | Audit SRP; add types | Low | No |
| `src/blender_mcp/services/types.py` | Service-specific types | Centralize typings; mypy tests | Low | No |
| `src/blender_mcp/services/textures.py` | Textures service | Tests + SRP | Medium | No |
| `src/blender_mcp/services/sketchfab.py` | Sketchfab service | Tests + docs | Medium | No |
| `src/blender_mcp/services/screenshots.py` | Screenshots aggregator | Confirm duplicates; add tests | Medium | No |
| `src/blender_mcp/services/screenshot.py` | Screenshot service | Add tests; import-safe | Medium | No |
| `src/blender_mcp/services/scene.py` | Scene service | Add unit tests; mock bpy | High | Possibly |
| `src/blender_mcp/services/registry.py` | Service registry | Add tests; ensure thread-safety | High | No |
| `src/blender_mcp/services/polyhaven.py` | Polyhaven service | Tests network; retries | Medium | No |
| `src/blender_mcp/services/object.py` | Object service | Tests; mock bpy | High | Possibly |
| `src/blender_mcp/services/hyper3d.py` | Hyper3D service | Tests + doc | Medium | No |
| `src/blender_mcp/services/execute.py` | Execute service (runs code) | Security note: document and limit; tests | High | Yes (if interface changes) |
| `src/blender_mcp/services/templates/__init__.py` | Templates package | Keep | Low | No |
| `src/blender_mcp/services/connection/__init__.py` | Services connection root | Harmonize API; tests | High | Possibly |
| `src/blender_mcp/services/connection/socket_conn.py` | Socket connection impl | Add socket tests; mock network | Medium | No |
| `src/blender_mcp/services/connection/reassembler.py` | Reassembler fragments | Add chunk tests; ensure correctness | High | No |
| `src/blender_mcp/services/connection/network_core.py` | Network core implementation | Add integration tests; separate concerns | High | No |
| `src/blender_mcp/services/connection/network.py` | Network glue | Add tests; refactor as needed | High | No |
| `src/blender_mcp/services/connection/framing.py` | Framing logic | Unit tests | Medium | No |
| `src/blender_mcp/services/connection/facade.py` | Connection facade | Provide stable API; tests | High | Possibly |
| `src/blender_mcp/services/templates/node_helpers.py` | Template helpers | Keep | Low | No |
| `src/blender_mcp/services/templates/materials.py` | Template materials | Keep | Low | No |
| `src/blender_mcp/services/servers/__init__.py` | Services servers package | Keep; clarify exports | Low | No |
| `src/blender_mcp/services/addon/__init__.py` | Addon services package | Keep separated from server-only services | Low | No |
| `src/blender_mcp/services/addon/textures.py` | Addon textures service | Keep import-safe | Low | No |
| `src/blender_mcp/services/addon/screenshots.py` | Addon screenshots service | Keep import-safe | Low | No |
| `src/blender_mcp/services/addon/scene.py` | Addon scene helpers | Keep import-safe | Low | No |
| `src/blender_mcp/services/addon/polyhaven.py` | Addon polyhaven helpers | Keep import-safe | Low | No |
| `src/blender_mcp/services/addon/objects.py` | Addon objects helpers | Keep import-safe | Low | No |
| `src/blender_mcp/services/addon/execution.py` | Addon execution helpers | Keep import-safe; tests | Low | No |
| `src/blender_mcp/services/addon/constants.py` | Addon constants | Keep | Low | No |
