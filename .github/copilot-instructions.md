## But : instructions pour agents AI (français)

Court guide d'action pour les agents automatisés travaillant sur le dépôt `blender-mcp`.
Lis d'abord `openspec/AGENTS.md` et `openspec/project.md` avant toute modification structurelle.

## Règles rapides (à lire avant de coder)
- Pour toute modification qui change le comportement ou l'API, suis la procédure OpenSpec : scafolder sous `openspec/changes/<change-id>/` et valide avec `openspec validate --strict`.
- Exécute les tests localement avant d'ouvrir une PR. Les tests sont sous `tests/` et utilisent `pytest` (voir `pytest.ini`).
- Les scripts d'aide et exemples PowerShell sont dans `scripts/` (ex. `run_tests.ps1`, `uvicorn_start.ps1`, `run_gemini_bridge.ps1`). Utilise-les pour reproduire les workflows CI localement.

## Architecture — où commencer
- `addon.py` : point d'entrée Blender (doit rester minimal et import-safe). Voir `blender_mcp.blender_ui` pour l'UI réelle.
- `src/blender_mcp/` : package principal (services, downloaders, helpers, server). Pendant la refactorisation, le code actif est migré sous `src/`.
- `blender_mcp/server.py` (shim temporaire à la racine) : implémentation minimale attendue par les tests pendant le refactor.
- `docs/endpoint_mapping.md` et `docs/endpoint_mapping_detailed.md` : cartographie endpoints → modules.
- `openspec/` : vérité canonique pour les specs et le processus de proposition.

Pourquoi : le projet sépare la définition des endpoints (docs + openspec) de l'implémentation runtime dans `blender_mcp`.

## Workflows développeur (commandes explicites)
- Exécution rapide des tests (PowerShell) :

```powershell
$env:PYTHONPATH = 'src'; python -m pytest -q
```

- Scripts utiles :
	- `scripts/run_tests.ps1` — wrapper PowerShell pour lancer la suite de tests.
	- `start-server.ps1` — démarre `blender-mcp` en arrière-plan (PowerShell détaché).
	- `scripts/uvicorn_start.ps1` — démarre l'adaptateur ASGI avec uvicorn (si installé). 

## Conventions propres au projet
- Modifications de comportement → créer une proposition sous `openspec/changes/<id>/` (voir `openspec/AGENTS.md`).
- Format des scénarios dans les specs : utilisez `#### Scenario:` pour chaque scénario d'acceptation.
- Pattern dispatcher : regarder `src/blender_mcp/dispatcher.py` et `tests/test_dispatcher*` pour voir comment les handlers sont enregistrés et testés.
- Tests : les modules de test suivent `test_*.py` et `tests/test_services_*.py` pour les services ; mocks de `bpy` via `sys.modules` + `monkeypatch`.

## Intégrations et dépendances externes
- Bridge Gemini / LLM : `scripts/gemini_bridge.py` et `run_gemini_bridge.ps1`.
- Services externes utilisés dans les tests : PolyHaven, Sketchfab, Hyper3D (voir `tests/test_services_*`).
- Manifest des dépendances : `pyproject.toml` (Poetry). Les dépendances de dev incluent `pytest`, `ruff`, `mypy`, `black`, `isort`.

## Avant d'ouvrir une PR
1. Relire `openspec/AGENTS.md` si la PR change un comportement/API.
2. Exécuter `python -m pytest -q` (avec `PYTHONPATH=src`) et corriger les tests cassés.
	- Note: la CI GitHub Actions utilise `PYTHONPATH: 'src:.'` pour inclure aussi le répertoire racine du dépôt pendant les runs (séparateur `:` sur Linux). Les développeurs peuvent continuer à utiliser `PYTHONPATH=src` localement.
3. Ajouter/modifier les deltas sous `openspec/changes/<id>/` si nécessaire.
4. Documenter les fichiers modifiés dans la proposition/PR (ex. `blender_mcp/server.py:ligne`).

## Remarques finales
- Préfère des changements petits, testés et réversibles. Le projet vise une refactorisation stricte (SOLID, rigueur académique) — évite les hacks non documentés.
- Si tu veux, je peux ajouter un mini-exemple montrant comment enregistrer un nouvel endpoint dans `src/blender_mcp/server.py` et un test minimal associé.

