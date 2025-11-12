# État local du projet vs dépôt original (ahujasid/blender-mcp)

Date: 2025-11-07

But de ce document
- Fournir un état clair et méthodique du projet local par rapport à la base de référence de `ahujasid/blender-mcp` (les deux gros fichiers monolithiques `copy_server.py` et `copy_addon.py`).
- Proposer une feuille de route priorisée pour terminer la refactorisation en modules testables, typés et lintés.

Contexte rapide
- Le projet d'origine contenait un gros serveur monolithe (`copy_server.py`) et un gros addon (`copy_addon.py`) — ces deux fichiers regroupaient la logique réseau, les handlers MCP, les intégrations (PolyHaven, Sketchfab, Hyper3D), et le code Blender (bpy).
- Objectif du refactor : factoriser la logique métier dans `src/blender_mcp/` (services, tools, dispatcher, connections), garder `addon.py` et `server.py` minimalistes et import‑safe (pas d'import `bpy` à l'import-time), ajouter tests, typage et CI.

Résumé de l'état local actuel (points saillants)
- Fichiers originaux disponibles (copies) : `copy_server.py`, `copy_addon.py` — conservés comme référence.
- Package modulaire en `src/blender_mcp/` avec :
  - `tools.py` (wrappers / handlers côté addon) — tests unitaires ciblés ajoutés.
  - `integrations.py`, `services/*` (logique réseau pour PolyHaven/Sketchfab/Hyper3D) — beaucoup de code déjà porté.
  - `prompts.py`, `templates/` — présents.
  - `tests/` : plusieurs tests ajoutés (ex. `tests/test_tools.py`) ; tests ciblés pour handlers critiques ont été ajoutés et passent localement.
- `src/blender_mcp/server.py` était corrompu par des fragments collés ; il a été remplacé temporairement par une implémentation minimale et import‑safe qui expose les symboles utilisés par les tests (`_process_bbox`, `BlenderMCPServer` minimal). Ceci a débloqué la collecte pytest.
- Un shim `blender_mcp/server.py` au niveau racine existait précédemment pour débloquer l'import — il a été nettoyé; le `src` est maintenant la source d'import principale.
- CI : un workflow initial `.github/workflows/ci.yml` existe mais doit être validé/finalisé.

Ce que faisait `copy_server.py` (liste non exhaustive des responsabilités)
- Définition d'une classe `BlenderConnection` robuste (connect/disconnect/send_command/receive_full_response avec reassembly de chunks).
- Gestion d'un objet global `_blender_connection` et d'une variable `_polyhaven_enabled`.
- Déclaration de nombreux endpoints MCP via `@mcp.tool()` et quelques `@mcp.prompt()` (exemples : `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `execute_blender_code`, `get_polyhaven_status`, `search_polyhaven_assets`, `download_polyhaven_asset`, `set_texture`, `get_hyper3d_status`, `create_rodin_job`, `import_generated_asset`, `search_sketchfab_models`, `download_sketchfab_model`, etc.).
- `server_lifespan` (asynccontextmanager) qui teste la connexion au démarrage et nettoie à l'arrêt.
- Fonction `main()` qui fait `mcp.run()`.
- Beaucoup de logique métier inline (gestion des fichiers temporaires, téléchargements, parsing JSON, création de matériaux Blender, import GLB, etc.).

Comparaison synthétique : ce qui EST déjà modularisé
- Services réseau (PolyHaven, Sketchfab, Hyper3D) : partiellement portés dans `src/blender_mcp/services/`.
- Handlers → `tools.py` et `integrations.py` : wrappers et facades commencent à exister.
- Tests unitaires : tests ciblés pour certains handlers (p.ex. `tests/test_tools.py`) ont été ajoutés.
- Documentation : `docs/endpoint_mapping_detailed.md` existe (mapping des endpoints et état de portage).

Comparaison synthétique : ce qui MANQUE / reste à faire
1. Recréer l'ensemble des endpoints MCP déclarés dans `copy_server.py` sous forme modulaire :
   - Décider du « landing module » (services.* pour logique réseau, tools.* pour wrappers côté addon) et porter endpoint par endpoint.
2. Implémenter la `BlenderConnection` testable dans `src/blender_mcp/connection.py` avec la logique de reassembly/chunking et tests unitaires.
3. Réimplémenter ou exposer un `dispatcher`/`command_registry` (register/list_handlers/dispatch) dans `src/blender_mcp/dispatcher.py` ou `command_dispatcher.py` et intégrer dans `BlenderMCPServer` pour :
   - enregistrement paresseux des handlers,
   - fallback echo,
   - possibilité de lister et d'appeler des handlers depuis tests.
4. Rendre `src/blender_mcp/server.py` la façade minimale qui :
   - expose `mcp` si disponible (FastMCP),
   - enregistre handlers au démarrage si mcp présent,
   - reste import‑safe (pas de bpy à l'import).
5. Porter toutes les intégrations métier (set_texture, download_* etc.) dans `services/` et écrire tests réseau simulés (vcr/requests-mock ou fixtures pytest + monkeypatch).
6. Ajouter plus de tests unitaires (handlers, dispatcher, connection) et tests d'intégration légers.
7. Linter/Typecheck : exécuter `ruff` et `mypy`, corriger violations et configurer en CI.

Priorités proposées (court terme → long terme)
1. Stabiliser le package : garantir que `src/blender_mcp` s'importe proprement (PASS).
2. Implémenter un `dispatcher` léger + adapter `BlenderMCPServer.execute_command` pour utiliser le dispatcher (permettra d'avoir l'echo et `list_handlers`). (PRIORITAIRE)
3. Extraire/implémenter `BlenderConnection` robuste et tests unitaires (PRIORITAIRE)
4. Porter les endpoints critiques avec tests unitaires :
   - `get_scene_info`, `execute_blender_code`, `get_viewport_screenshot` (haut)
   - `get_polyhaven_status`, `get_sketchfab_status`, `get_hyper3d_status` (moyen)
5. Finaliser mapping complet des endpoints et planifier portage (moyen)
6. Lint, mypy, CI — faire passer les quality gates (long)

Checklist technique (actions concrètes & fichiers ciblés)
- src/blender_mcp/connection.py  ← implémenter BlenderConnection (reassembly/chunks)
- src/blender_mcp/dispatcher.py  ← registry, register_default_handlers(), list_handlers(), dispatch()
- src/blender_mcp/server.py      ← façade minimale : expose mcp (si dispon.), registre lifecycle et points d'extension
- src/blender_mcp/tools.py       ← wrappers testables vers services
- src/blender_mcp/services/*     ← héberger logique réseau/imports testables
- tests/test_dispatcher.py       ← tests de wiring dispatcher ↔ services
- tests/test_services_*          ← tests unitaires et réseau simulé

Commandes utiles pour reproduire l'état local et valider
```
$env:PYTHONPATH = "src;."; pytest -q
# ou lancer seulement les tests serveur
$env:PYTHONPATH = "src;."; pytest tests/test_server.py -q
```

Petite « contract » pour les endpoints portés (2-3 bullets)
- Input : dictionnaire JSON -> {"type"|"tool": str, "params": dict}
- Output : dict JSON-serializable contenant au minimum {"status": "ok"|"error", ...}
- Error modes : connexion refusée (raises/converted en {"status":"error"}), params invalides (ValueError -> {"status":"error", "message":...}).

Risques / edge-cases
- Importer prématurément `bpy` en import-time cassera CI — respecter l'import paresseux.
- Handlers qui font du I/O réseau doivent être testés avec mocks/fake servers.
- Portage partiel peut créer des doublons ou comportements divergents : garder `copy_server.py` pour référence, mais porter endpoint par endpoint et valider via tests.

Proposition immédiate (ce que je propose de faire maintenant si tu veux)
1. Générer automatiquement la liste complète des endpoints dans `copy_server.py` et produire un tableau MD avec statut (ported/pending) — utile pour prioriser. (option A)
2. Implémenter maintenant le `dispatcher` léger et compléter `BlenderMCPServer` pour qu'il fournisse les fonctionnalités attendues par les tests (`list_handlers`, fallback echo). (option B)
3. Lancer ruff/mypy et produire le rapport d'erreurs prioritaires (option C).

Choix recommandé : commencer par (A) puis (B). Le mapping (A) nous donne une checklist exacte et B permet de rétablir le contrat fonctionnel minimal.

---

Si tu confirmes, je lance (A) : j'extrais tous les `@mcp.tool`/`@mcp.prompt` depuis `copy_server.py` et produis `docs/endpoint_mapping_detailed.md` (ou mets à jour le fichier existant) avec statut et module cible recommandé. Ensuite on pourra décider du portage prioritaire.
