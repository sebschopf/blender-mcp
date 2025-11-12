# Inventory & Consolidation Plan — `src/blender_mcp` and root shim

Ce document liste les fichiers candidats à la consolidation, leur rôle estimé, l'action recommandée à court terme, le niveau de risque (impact API/comportement) et si une proposition OpenSpec est probablement requise.

Usage: ce fichier est généré automatiquement par l'outil d'audit. Servez-vous-en pour créer des PRs petites et ciblées (1 objectif par PR).

| Chemin | Rôle / description | Action recommandée (court) | Risque | OpenSpec requis? |
|---|---|---|---:|---:|
| `blender_mcp/__init__.py` | Shim racine / compat export | Laisser en lecture seule; documenter comme shim; rendre lazy si besoin | High | Yes |
| `blender_mcp/server.py` | Shim racine minimal (façade pour tests) | Rendre explicitement lazy / déléguer à `src/` ou déplacer vers `tools/` | High | Yes |
| `src/blender_mcp/__init__.py` | Package canonique — lazy exports | Garder; documenter API publique | Low | No |
| `src/blender_mcp/server.py` | Impl server canonique (lifecycle, handlers) | Consolider ici la logique serveur; ajouter tests d'API | High | Yes (if API change) |
| `src/blender_mcp/server_shim.py` | Shim interne / compat | Regrouper sous `compat/` et rendre import-safe | Medium | Possibly |
| `src/blender_mcp/servers/server.py` | Impl spécifique servers/ | Fusionner/réexporter depuis `src/blender_mcp/server.py` | High | Possibly |
| `src/blender_mcp/servers/shim.py` | Shim pour servers package | Consolider dans `compat/` | Medium | Possibly |
| `src/blender_mcp/servers/embedded_adapter.py` | Adaptateur embedded | Vérifier tests; extraire interface testable | Medium | No |
| `src/blender_mcp/dispatchers/dispatcher.py` | Dispatcher central (register/dispatch) | Garder comme canonical; améliorer tests & docs | High | No |
| `src/blender_mcp/dispatchers/simple_dispatcher.py` | Impl simple (compat) | Marquer comme compat; tests de compat | Medium | No |
| `src/blender_mcp/dispatchers/command_dispatcher.py` | Command-style dispatcher | Consolider interface et tests | Medium | No |
| `src/blender_mcp/simple_dispatcher.py` | Ancienne copie top-level | Vérifier utilisation; supprimer/redirect après tests | Medium | Possibly |
| `src/blender_mcp/connection_core.py` | Core connection (BlenderConnection) | Stabiliser, séparer network vs API; tests socketpair | High | Possibly |
| `src/blender_mcp/services/connection/__init__.py` | Services connection package | Harmoniser API unique; tests | High | Possibly |
| `src/blender_mcp/services/connection/network.py` | Impl réseau | Tests d'intégration réseau (socketpair); factoriser | High | No |
| `src/blender_mcp/services/connection/reassembler.py` | Réassembleur fragments | Couvrir par tests (fragments/chunks) | High | No |
| `src/blender_mcp/services/connection/socket_conn.py` | Conn socket concrète | Extraire tests unitaires, mock sockets | Medium | No |
| `src/blender_mcp/services/connection/framing.py` | Framing messages | Isoler et tester | Medium | No |
| `src/blender_mcp/command_dispatcher.py` | Backwards compat top-level | Déplacer vers `dispatchers/` et déprécier import direct | Medium | Possibly |
| `src/blender_mcp/endpoints.py` | Endpoint registry / mapping | Audit signatures; ajouter tests d'intégration | High | Yes (if signature change) |
| `src/blender_mcp/mcp_client.py` | Client MCP (remote calls) | Tester, clarifier responsabilités | Medium | No |
| `src/blender_mcp/asgi.py` | ASGI adapter | Tests d'intégration minimale; document lifecycle | Medium | No |
| `src/blender_mcp/http.py` | Helpers HTTP | Regrouper/typer, tests | Low | No |
| `src/blender_mcp/tools.py` | Helpers utilitaires | Vérifier SRP; refactorer helpers spécifiques vers services | Low | No |
| `src/blender_mcp/types.py` | Types partagés | Centraliser typings; ajouter mypy coverage | Low | No |
| `src/blender_mcp/config.py` | Configuration | Centraliser env vars; tests | Low | No |
| `src/blender_mcp/downloaders.py` | Downloaders (PolyHaven...) | Tests réseau/retry; keep under services when stable | Medium | No |
| `src/blender_mcp/texture_helpers.py` | Helpers textures | Déplacer si spécifique aux services | Low | No |
| `src/blender_mcp/sketchfab.py` | Sketchfab integration | Tests + clarify | Medium | No |
| `src/blender_mcp/polyhaven.py` | Polyhaven integration | Tests + clarify | Medium | No |
| `src/blender_mcp/hyper3d.py` | Hyper3D integration | Tests + clarify | Medium | No |
| `src/blender_mcp/prompts.py` | Prompt helpers | Keep under codegen/integrations | Low | No |
| `src/blender_mcp/gemini_client.py` | Gemini bridge client | Mark as integration; tests should mock | Medium | No |
| `src/blender_mcp/blender_codegen.py` | Codegen utilities | Group under `codegen/` | Low | No |
| `src/blender_mcp/codegen/blender_codegen.py` | Codegen package file | Keep and test | Low | No |
| `src/blender_mcp/blender_ui/__init__.py` | Addon UI package init | Ensure import-safety | Medium | No |
| `src/blender_mcp/blender_ui/panel.py` | UI panel | Keep import-safe; small unit tests if possible | Medium | No |
| `src/blender_mcp/blender_ui/operators.py` | UI operators | Keep import-safe; unit tests for logic | Medium | No |
| `src/blender_mcp/blender_ui/props.py` | UI props | Keep import-safe | Low | No |
| `src/blender_mcp/blender_ui/addon_handlers.py` | UI handlers | Keep import-safe | Medium | No |
| `src/blender_mcp/codegen/__init__.py` | Codegen package | Keep | Low | No |
| `src/blender_mcp/simple_dispatcher.py` | historical simple dispatcher | Consolidate with `dispatchers/` | Medium | Possibly |
| `src/blender_mcp/dispatchers/__init__.py` | Dispatchers package root | Keep minimal exports | Low | No |
| `src/blender_mcp/blender_ui/addon_handlers.py` | Addon UI handlers (dup) | Confirm single source | Medium | No |
| `src/blender_mcp/blender_ui/props.py` | UI props (dup) | As above | Low | No |
| `src/blender_mcp/templates/asset_creation_strategy.txt` | Template text | Keep | Low | No |
| `src/blender_mcp/templates/*` | Templates | Keep / document | Low | No |

## Archive (snapshots)
Les fichiers sous `src/blender_mcp/archive/` sont des snapshots historiques. Ils doivent être préservés mais exclus des checks automatiques (lint/mypy). Ne pas modifier sans accord explicite.

Examples:
- `src/blender_mcp/archive/server.py`
- `src/blender_mcp/archive/server_shim.py`
- `src/blender_mcp/archive/*` (dispatcher, connection, blender_ui, etc.)

Action courte recommandée: ajouter une note dans `openspec/changes/` si l'objectif est de réimporter/migrer ces snapshots. 

## Priorités recommandées (rappel)
1. High: consolidation points d'entrée (server, shim root, dispatchers, connection).
2. Medium: shims/compat move to `compat/`, tests network, embedded adapter tests.
3. Low: helpers, templates, docs, typings.

## Prochaine étape proposée
- Je peux générer un Markdown plus détaillé listant chaque fichier individuel (83 lignes) dans le même format CSV/markdown si tu veux l'import direct dans un tracker. Dis si tu veux le Markdown complet, CSV, ou que je crée des branches PR stubs pour les 3 items high-priority.
