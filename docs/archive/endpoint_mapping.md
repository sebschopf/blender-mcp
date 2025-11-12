# Mapping des endpoints — `copy_server.py` → `src/blender_mcp`

Ce document liste les endpoints trouvés dans `copy_server.py`, leur état dans
`src/blender_mcp/` et la recommandation pour leur placement/traitement.

Format : Endpoint | Présent dans package | Fichier destination | Notes / action recommandée

- get_scene_info | oui | `src/blender_mcp/tools.py` | Garder, ajouter test (mock send_command)
- get_object_info | oui | `src/blender_mcp/tools.py` | Garder, ajouter test
- get_viewport_screenshot | oui | `src/blender_mcp/tools.py` | Garder, ajouter test qui écrit un fichier temporaire
- execute_blender_code | oui | `src/blender_mcp/tools.py` | Garder, ajouter test
- get_polyhaven_categories | oui | `src/blender_mcp/integrations.py` | Server-first, fallback to addon. OK
- search_polyhaven_assets | oui | `src/blender_mcp/integrations.py` | OK
- download_polyhaven_asset | oui | `src/blender_mcp/integrations.py` | OK
- set_texture | oui | `src/blender_mcp/integrations.py` | OK
- get_polyhaven_status | oui | `src/blender_mcp/integrations.py` | OK
- get_hyper3d_status | oui | `src/blender_mcp/integrations.py` | OK
- get_sketchfab_status | oui | `src/blender_mcp/integrations.py` | OK
- search_sketchfab_models | oui | `src/blender_mcp/integrations.py` | OK
- download_sketchfab_model | oui | `src/blender_mcp/integrations.py` | OK
- generate_hyper3d_model_via_text | oui | `src/blender_mcp/integrations.py` | OK
- generate_hyper3d_model_via_images | oui | `src/blender_mcp/integrations.py` | OK
- poll_rodin_job_status | oui | `src/blender_mcp/integrations.py` | OK
- import_generated_asset | oui | `src/blender_mcp/integrations.py` | OK
- asset_creation_strategy (prompt) | non | `copy_server.py` only | Recommander : extraire vers `src/blender_mcp/templates/asset_creation_strategy.txt` et wrapper `@mcp.prompt()`
- services registry (polyhaven/sketchfab handlers) | oui | `src/blender_mcp/services/registry.py` | OK
- get_blender_connection / BlenderConnection / lifecycle | partiellement | `src/blender_mcp/server.py` | `server.py` contient actuellement du contenu dupliqué/mangé — proposer nettoyage contrôlé et consolidation de `BlenderConnection` testable

Résumé des actions recommandées:
1. Nettoyer `src/blender_mcp/server.py` et y placer une implémentation testable de `BlenderConnection` et `get_blender_connection` (lazy, import-safe pour `bpy`).
2. Extraire le prompt `asset_creation_strategy` vers `src/blender_mcp/templates/asset_creation_strategy.txt` et ajouter un petit wrapper qui lit ce fichier.
3. Ajouter des tests unitaires ciblés pour `get_scene_info`, `execute_blender_code`, `get_viewport_screenshot`.

Fichier généré automatiquement par l'agent de portage — révisez avant de porter en production.
## Mapping des endpoints — archived copy

This is an archived copy of the endpoint mapping. The active mapping remains in `docs/endpoint_mapping_detailed.md`.

Content snapshot preserved for reference.
