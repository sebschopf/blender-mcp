# Contexte du projet

## Objectif
Blender-MCP connecte Blender au Model Context Protocol (MCP) pour permettre à des agents LLM / outils externes de piloter Blender, télécharger des assets et orchestrer des workflows 3D. Le dépôt vise une base testable, importable hors-Blender (CI, tests) et un addon Blender léger qui déléguera la logique métier au package `blender_mcp`.

## Stack technique
- Langage : Python 3.10+ (mypy et configurations ciblent py310)
- Gestion des dépendances : Poetry (`pyproject.toml`)
- Tests : pytest (voir `pytest.ini`) ; mocks et monkeypatch pour remplacer `bpy` en CI
- Lint/format : ruff, black, isort (configurés dans `pyproject.toml`)
- Runtime/serveur : package `mcp` (avec extras `cli`), adaptateur ASGI possible (uvicorn/fastapi) pour l'exposition HTTP
- Outils PowerShell : scripts utilitaires fournis (`scripts/*.ps1`, `start-server.ps1`) — le dépôt privilégie des exemples PowerShell pour Windows.

## Conventions du projet
- Spec-first : toute modification comportementale ou API doit passer par `openspec/changes/<change-id>/` (proposal, tasks, delta specs) et être validée avec `openspec validate --strict`.
- Minimalisme pour l'addon : `addon.py` DOIT rester léger et import-safe ; UI et opérateurs lives sont lazy-importés depuis `blender_mcp.blender_ui`.
- Dispatcher / services : la logique métier est organisée en services (ex. `src/blender_mcp/services/*`) ; le dispatcher centralise l'enregistrement et l'exécution des handlers.
- Nom des tests : suivre `test_*.py` et `test_services_*` pour coherent mapping service → tests.
- Style : respecter `black`/`isort`/`ruff` et les règles déclarées dans `pyproject.toml` (line-length, exclude pour `docs/archive/**`).

## Patterns d'architecture
- Séparation claire :
	- surface d'intégration (Blender addon) : `addon.py` (minimal)
	- runtime / serveur : `src/blender_mcp/server.py` (implémentation réelle) ou shim temporaire en racine pour tests
	- services purs (pure functions / testables) : `services/*`, `materials.py`, `node_helpers.py`, `texture_helpers.py`
- Lazy imports de `bpy` : tous les helpers qui touchent `bpy` doivent être importables paresseusement et testables sans Blender (mocks de `bpy` via `sys.modules`).
- Dispatcher pattern : central registry + façades testables ; ré-exporter les APIs stables pour minimiser l'impact des refactors (voir `simple_dispatcher` façade).
- Tests isolés : préférer tests unitaires purs pour la logique métier et tests d'intégration simulées/mocking pour le pont réseau/Blender.

## Stratégie de tests
- Exécution locale :

```powershell
$env:PYTHONPATH = 'src'; python -m pytest -q
```

- Tests CI : la pipeline exécute `ruff`, `mypy` et `pytest`. Pendant la refactorisation, certains checks peuvent être permissifs mais l'objectif est d'arriver à strict.
- `bpy` est mocké dans les tests via `sys.modules` et `monkeypatch` ; les tests valident les chemins d'erreur et succès (helpers défensifs).
- Couverture cible : tests unitaires pour services + un ou deux tests d'intégration pour le dispatcher/serveur.

## Workflow Git / PR
- Branching : feature branches (ex. `feature/port-refactor-2025-11-08`) → PR draft pour validation initiale.
- PRs qui modifient comportement/API : inclure ou référencer une proposition OpenSpec (`openspec/changes/<id>/`).
- Checklist PR : tests locaux passés, linter/typing fixes appliqués, spec deltas ajoutés si nécessaire, `PROJECT_JOURNAL.md` mis à jour pour étapes importantes.

## Contexte métier / domaine
- Objectif primaire : automatiser l'import, la génération et la modification d'assets Blender depuis un contrôleur externe (LLM / MCP).
- Cas d'usage courant : télécharger une texture/asset PolyHaven, appliquer un matériau, inspecter la scène, exécuter un script dans Blender via MCP.

## Contraintes importantes
- Code importable hors-Blender : ne pas importer `bpy` au module-level.
- Respect strict de SOLID/bonne conception : le projet vise une refactorisation académique et stricte (petits composants, single responsibility, interfaces testables).
- Backwards-compatibility : pendant la migration, préférer façades/ré-exports pour conserver les points d'entrée publics et réduire les PR breaking.
- CI Windows-first examples : les scripts PowerShell sont privilégiés pour la reproductibilité locale.

## Dépendances externes clés
- `mcp` (protocol implementation) — dépendance runtime
- `requests` — téléchargements API (PolyHaven, Sketchfab)
- `uvicorn` / `fastapi` (optionnel) — adaptateur ASGI pour exposition HTTP
- Outils dev : `mypy`, `ruff`, `black`, `isort`, `pytest` (dev group in `pyproject.toml`)

## État actuel de la refactorisation (synthèse)
- Progression : refactorisation majeure en cours — beaucoup de code a été déplacé dans `src/blender_mcp/` et de nombreux tests unitaires ont été ajoutés.
- Position actuelle :
	- `addon.py` est volontairement minimal (shim) et doit être réduit encore pour ne faire que l'enregistrement UI et lazy-imports.
	- Le `server` a un shim en racine pour permettre aux tests de tourner pendant que l'implémentation du package est migrée.
	- Tentative de mise à jour de `polyhaven.py` en cours ; probablement incomplète — vérifier `tests/test_services_polyhaven.py` et le module `src/blender_mcp/downloaders.py`/`services/polyhaven`.
	- CI : workflows ajoutés (`.github/workflows/ci.yml`) et améliorés ; les jobs utilisent matriciels Python, artifact names fixés pour éviter 409.

## Contrat minimal pour les contributions
- Inputs : modifications dans `src/` ou `openspec/changes/` ; PRs petites et atomiques.
- Outputs attendus : tests unitaires + fixtures, modifications `openspec` si comportement changé, mise à jour de `PROJECT_JOURNAL.md`.
- Modes d'échec : tests cassés, imports non-safe de `bpy`, régressions API non documentées.

## Cas d'usage / Edge cases à vérifier
- Importation hors-Blender (import-safe) — tests doivent couvrir l'absence de `bpy`.
- Connexions socket au Blender addon — gestion des timeouts et échecs de connexion (server shim utilise socket par défaut).
- Téléchargements externes — timeout/retry et mocking en tests pour éviter dépendance réseau.

## Prochaines étapes recommandées
1. Stabiliser `src/blender_mcp/server.py` et retirer le shim racine quand le package fonctionne.
2. Reprendre `polyhaven` : exécuter les tests ciblés et corriger les imports/contrats.
3. Resserer mypy/ruff progressivement (retirer `|| true` en CI) une fois les erreurs corrigées.
4. Ajouter un exemple concret de PR + `openspec/changes/<id>/` pour montrer le workflow complet (scaffold + validate).

## Où creuser en priorité
- `docs/endpoint_mapping.md` + `blender_mcp/server.py` pour brancher de nouveaux endpoints.
- `tests/test_services_*` pour exemples de tests et mocks de `bpy`.
- `docs/PROJECT_JOURNAL.md` pour l'historique et décisions de conception.
