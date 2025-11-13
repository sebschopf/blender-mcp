## But : instructions pour agents AI (français)

Court guide d'action pour les agents automatisés travaillant sur le dépôt `blender-mcp`.
Lis d'abord `openspec/AGENTS.md` et `openspec/project.md` avant toute modification structurelle.

## Règles rapides (à lire avant de coder)
- Toute modification de comportement/API → procedure OpenSpec: `openspec/changes/<id>/` + `openspec validate --strict`.
- Toujours valider localement lint/type/tests avant PR (voir commandes ci‑dessous).
- Préférer des commits/PR petits et thématiques (≤ 3 fichiers code hors tests/docs).
- Conventions de commit: Conventional Commits en français (`feat(x): …`, `refactor(y): …`, `chore(lint): …`, `docs: …`, `ci: …`).
- Scripts utiles: `scripts/run_tests.ps1`, `scripts/uvicorn_start.ps1`, `scripts/run_gemini_bridge.ps1`.

## Architecture — où commencer
- `addon.py` : point d'entrée Blender (doit rester minimal et import-safe). Voir `blender_mcp.blender_ui` pour l'UI réelle.
- `src/blender_mcp/` : package principal (services, downloaders, helpers, server). Pendant la refactorisation, le code actif est migré sous `src/`.
- `blender_mcp/server.py` (shim temporaire à la racine) : implémentation minimale attendue par les tests pendant le refactor.
- `docs/endpoint_mapping.md` et `docs/endpoint_mapping_detailed.md` : cartographie endpoints → modules.
- `openspec/` : vérité canonique pour les specs et le processus de proposition.

Pourquoi : le projet sépare la définition des endpoints (docs + openspec) de l'implémentation runtime dans `blender_mcp`.

## Workflows développeur (commandes explicites)
- Vérifs locales (PowerShell):

```powershell
$Env:PYTHONPATH='src'
ruff check src tests
mypy src --exclude "src/blender_mcp/archive/.*"
pytest -q
Remove-Item Env:PYTHONPATH
```

- Scripts utiles :
	- `scripts/run_tests.ps1` — wrapper PowerShell pour lancer la suite de tests.
	- `start-server.ps1` — démarre `blender-mcp` en arrière-plan (PowerShell détaché).
	- `scripts/uvicorn_start.ps1` — démarre l'adaptateur ASGI avec uvicorn (si installé). 

## Conventions propres au projet
- Spécifications: changements de comportement → `openspec/changes/<id>/` (format scénarios `#### Scenario:`).
- Dispatcher: si ordre d'import nécessaire, documenter et utiliser `# isort: skip_file` (pas de refactor structurel dans une PR de portage); tests: `tests/test_dispatcher*`.
- Services: style exceptions-first (lever `InvalidParamsError` / `ExternalServiceError` / `HandlerError`), pas de dict d'erreur; adapter formate `{status, result|message, error_code}` (voir `docs/developer/error_handling.md`).
- Registre services: enregistrer dans `src/blender_mcp/services/registry.py` et ajouter tests de découverte/dispatch.
- Tests: `test_*.py`, `tests/test_services_*.py`; mock `bpy` via `sys.modules` + `monkeypatch`.

## Intégrations et dépendances externes
- Bridge Gemini / LLM: `scripts/gemini_bridge.py`, `run_gemini_bridge.ps1`.
- Services externes tests: PolyHaven, Sketchfab, Hyper3D (`tests/test_services_*`).
- CI/Deps: voir `pyproject.toml`. CI installe `pytest`, `ruff`, `mypy`, `fastapi`, `starlette`, `httpx`, `pytest-asyncio`.

## Avant d'ouvrir une PR
1. Lint/type/tests OK localement (voir commandes plus haut); corriger les erreurs (imports, lignes longues, types).
2. Si comportement/API change: créer/mettre à jour une spec sous `openspec/changes/<id>/` et référencer dans la PR.
3. Mettre à jour la doc (journal, cartographie endpoints) si pertinent.
4. Commits petits et thématiques avec messages conventionnels; regrouper par domaine (polyhaven, sketchfab, hyper3d, textures, connection, docs, ci, lint).
5. Ouvrir la PR via `gh`: ajouter label `phase2` et milestone courant; s'assurer que la CI se déclenche (PR vers n'importe quelle branche supportée).

## Remarques finales
- Viser SOLID: extraire/refactorer hors PR de portage si impact large; documenter le plan (ex: dispatcher import order gelé temporairement).
- Tenir `docs/developer/ai_session_guide.md` et `docs/developer/error_handling.md` comme références courantes pour les décisions.

