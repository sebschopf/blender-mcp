
# Tasks & Practices — Roadmap claire et exécutable

Ce document est une feuille de route actionnable pour terminer le portage, rendre le code plus SOLID, et maintenir la compatibilité pendant la migration.

## Objectifs principaux
- Standardiser la gestion d'erreurs (exceptions canoniques dans `src/blender_mcp/errors.py`).
- Porter les endpoints vers `src/blender_mcp/services/` par petits lots (tests + façades compatibles).
- Introduire des interfaces légères (Protocols/ABCs) là où c'est utile pour faciliter les tests et l'injection de dépendances.

### Quick rules
- Package canonique : `src/blender_mcp/` (les shims à la racine sont rétrocompatibles).
- Pour les développeurs : utilisez `PYTHONPATH=src` (PowerShell : `$env:PYTHONPATH = 'src'`) quand vous exécutez des tests ou ouvrez une PR.
	- Note CI : la pipeline GitHub Actions (ubuntu) définit `PYTHONPATH: 'src:.'` pour s'assurer que le repo root est aussi trouvable pendant les tests. Les deux approches sont valides ; préférez `src` localement pour la cohérence des exemples.

### Reproduire localement (PowerShell)
```powershell
$env:PYTHONPATH = 'src'
python -m pytest -q
Remove-Item Env:\PYTHONPATH
```

## Environnement de développement (parité CI)

Pour éviter les écarts entre les runs locaux et CI, suivez ces recommandations pour installer un environnement local qui reflète la pipeline GitHub Actions :

- Python : la CI exécute une matrice sur 3.11 et 3.12. Pour reproduire le run principal, utilisez Python 3.11.
- Outils & versions pinned (installés par le workflow CI) :
	- ruff==0.12.4
	- mypy==1.11.0
	- pytest==7.4.2
	- types-requests, types-urllib3
	- requests
	- fastapi, starlette, httpx, pytest-asyncio (pour les tests ASGI)

Commandes rapides (PowerShell) pour créer un venv et installer les versions CI-pinned :

```powershell
# Crée et active un virtualenv (doit utiliser Python 3.11 si tu veux la parité exacte)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Met à jour pip et installe les outils pinés exactement comme en CI
python -m pip install --upgrade pip
pip install ruff==0.12.4 mypy==1.11.0 pytest==7.4.2 types-requests types-urllib3 requests fastapi==0.95 starlette==0.28 httpx==0.24 pytest-asyncio==0.21

# Positionner PYTHONPATH pour la session PowerShell (séparateur Windows = ;)
$Env:PYTHONPATH = 'src;.'

# Lancer la suite (mêmes étapes que CI)
ruff check --exclude "src/blender_mcp/archive/**" src tests
mypy src --exclude "src/blender_mcp/archive/.*"
pytest -q --junitxml=pytest-report.xml
```

Notes et conseils:
- Si vous utilisez Poetry, préférez `poetry install --with dev` pour reproduire la résolution exacte des dépendances définies dans `pyproject.toml`.
- Vérifiez les versions locales utiles :
	- `python --version`
	- `ruff --version`
	- `mypy --version`
	- `pytest --version`
- CI sets PYTHONPATH to `src:.` (colon on Linux) in the workflow matrix jobs; locally use `'src'` or `'src;.'` on Windows as shown.

Si tu veux, je peux ajouter un script `scripts/verify_local_ci.ps1` qui exécute ces étapes automatiquement dans un venv et vérifie les versions (je peux le committer dans le repo).
### Structure du document
- Roadmap priorisée (tâches + pourquoi/quoi/comment)
- Template par-endpoint (copiable dans PR/ticket)
- Checklist PR et validation
- Checklist SOLID & procédure d'audit
- Journalisation et documentation
- Machine-readable tasks (YAML) pour automatiser priorisation

----

## Roadmap priorisée (bref)

1. High priority
	- `get_viewport_screenshot`, `execute_blender_code`, `get_scene_info`, `get_object_info`
	- Pourquoi : utilisés par l'UI et bridge, impact élevé.

2. Medium priority
	- Integrations I/O : PolyHaven, Sketchfab, Hyper3D

3. Low priority
	- Helpers, debug endpoints, internal tools

----

## Template de tâche / ticket / PR (par endpoint)

Copiez-coller ce template dans la description du ticket/PR.

```
[ ] Porter l'endpoint: <nom_du_endpoint>
  Pourquoi :
	 - (ex. testabilité, corriger bug X, standardiser erreurs)
  Où :
	 - Cible implémentation : `src/blender_mcp/services/<nom_du_service>.py`
	 - Façade rétrocompatible (si besoin) : `src/blender_mcp/services/__init__.py` ou top-level shim
  Contrat / Spec :
	 - Entrée : params: dict | None (JSON serializable)
	 - Sortie : JSON-serializable dict (success) OR raise `BlenderMCPError` (see `errors.py`)
	 - Adapter mapping exception -> `error_code` dans l'adapter (ASGI/dispatcher)
  Comment (checklist technique) :
	 - [ ] Écrire un spec court dans `openspec/changes/<id>/` si le contrat change publiquement
	 - [ ] Implémenter service (lazy import `bpy`)
	 - [ ] Ajouter tests unitaires : happy-path, error-path (absence de `bpy` / invalid params)
	 - [ ] Ajouter tests d'intégration légers (dispatcher / wrapper `@mcp.tool`)
	 - [ ] Ajouter entrée `docs/PROJECT_JOURNAL.md`
	 - [ ] Ouvrir PR petite (<3 fichiers modifiés) avec la commande pour reproduire tests
```

Checklist PR (must pass before merge)
- Tests unitaires passés localement
- `mypy` et `ruff` exécutés sur fichiers modifiés
- Entrée dans `docs/PROJECT_JOURNAL.md`
- Si contrat public change → ajouter proposition OpenSpec sous `openspec/changes/<id>/`

----

## Checklist SOLID adaptée (rapide contrôle)

- SRP (Single Responsibility)
  - Le module/fonction fait-il une seule chose ? Si non, extraire.

- OCP (Open/Closed)
  - Peut-on ajouter un handler sans modifier le core ? Utiliser `Dispatcher.register()`.

- LSP (Liskov Substitution)
  - Les implémentations interchangeables respectent la même API.

- ISP (Interface Segregation)
  - Préférer petites interfaces/coeurs testables.

- DIP (Dependency Inversion)
  - Dépendre d'abstractions (Protocols) ; injecter factories/connexions pour tests.

Procédure d'audit SOLID (par fichier modifié)
1. Ajouter entrée courte dans `docs/PROJECT_JOURNAL.md` (SRP/OCP/DIP quick status)
2. Corriger violations simples (< ~10 lignes)
3. Documenter décisions pour changements plus vastes

----

## Journalisation — modèle d'entrée (obligatoire pour chaque PR)

Format (copier) :

```
YYYY-MM-DD | auteur
- Action: porter <endpoint>
- Fichiers: list...
- Tests: commande utilisée -> verdict
- Statut: done/partial/blocker
- Notes: décisions d'architecture, open questions
```

----

## Documentation & CI notes

- Ajoutez/tenez à jour : `docs/endpoint_mapping_detailed.md`, `docs/PROJECT_JOURNAL.md`, `docs/SECURITY.md`.
- CI must run with `PYTHONPATH=src`. Add FastAPI to dev deps if you want ASGI tests to run in CI.

----

## Machine-readable tasks (YAML)

Copiable pour automation / génération d'issues. Modifiez les statuts selon besoin.

```yaml
tasks:
  - id: 1
	 title: porter_object_get_object_info
	 priority: high
	 target: src/blender_mcp/services/object.py
	 status: in-progress
	 why: "Testability + UI usage"
  - id: 2
	 title: porter_execute_blender_code
	 priority: high
	 target: src/blender_mcp/services/execute.py
	 status: todo
  - id: 3
	 title: porter_get_viewport_screenshot
	 priority: high
	 target: src/blender_mcp/services/screenshot.py
	 status: todo
  - id: 10
	 title: implement_dispatcher
	 priority: critical
	 target: src/blender_mcp/dispatcher.py
	 status: todo
  - id: 11
	 title: implement_connection_reassembler
	 priority: critical
	 target: src/blender_mcp/connection.py
	 status: todo
```

----

## Commandes utiles (PowerShell)

Run tests (entire suite):
```powershell
$env:PYTHONPATH = 'src'
python -m pytest -q
Remove-Item Env:\PYTHONPATH
```

Run specific tests:
```powershell
$env:PYTHONPATH = 'src'
python -m pytest tests/test_services_object.py -q
Remove-Item Env:\PYTHONPATH
```

Lint & typecheck:
```powershell
python -m ruff check src tests
python -m mypy src --ignore-missing-imports
```

----

## Toutes les étapes détaillées (checklist granulaire)

Ci‑dessous une checklist exhaustive et ordonnée par priorité/phase. Chaque ligne doit être traitée dans une PR indépendante quand possible (1-3 fichiers modifiés). Pour chaque étape, ajouter une entrée dans `docs/PROJECT_JOURNAL.md` et joindre la commande pour reproduire les tests.

1) Environnement & CI
	- [x] Vérifier et standardiser `PYTHONPATH=src` dans tous les workflows CI.
	- [x] Ajouter FastAPI (et ses dépendances: starlette, pydantic, httpx/tests reqs) en dépendance de développement si on veut exécuter les tests ASGI en CI.
	- [x] Ajouter jobs CI pour `ruff`, `mypy`, `pytest` (matrix Python 3.11+).
	- [x] Ajouter un job optionnel `integration` qui installe FastAPI et exécute `tests/test_asgi_tools.py`.

	### Déclencher le job `integration` manuellement via la CLI GitHub

	Si vous avez besoin d'exécuter le job `integration` (job optionnel qui installe FastAPI et exécute les tests ASGI) depuis la ligne de commande, vous pouvez utiliser la CLI `gh` pour re-runner ou déclencher un workflow dispatch. Deux approches utiles :

	- Re-run d'un workflow existant (par exemple après avoir poussé un commit) :

	  1. Listez les runs récents pour la branche courante :

		  ```pwsh
		  gh run list --branch feature/port-refactor-2025-11-08 --limit 10
		  ```

	  2. Identifiez l'ID du run que vous voulez relancer (colonne "ID"), puis relancez uniquement le job `integration` :

		  ```pwsh
		  gh run rerun <run-id> --job integration
		  ```

	  Note: `gh run rerun --job` relance un job spécifique dans un run existant si le workflow et la plateforme le supportent.

	- Déclenchement via `workflow_dispatch` (si le workflow expose un événement `workflow_dispatch` avec des inputs) :

	  1. Vérifiez que le workflow est déclarée avec `workflow_dispatch` dans `.github/workflows/ci.yml`.

	  2. Déclenchez le workflow manuellement en fournissant la branche cible :

		  ```pwsh
		  gh workflow run ci.yml --ref feature/port-refactor-2025-11-08
		  ```

	  3. Si le workflow accepte des inputs (par ex. `run_integration: true`), vous pouvez les fournir ainsi :

		  ```pwsh
		  gh workflow run ci.yml --ref feature/port-refactor-2025-11-08 --field run_integration=true
		  ```

	Conseils pratiques :
	- Assurez-vous d'avoir la CLI `gh` installée et authentifiée (`gh auth login`).
	- Travaillez depuis la branche que vous voulez tester (la commande `--ref` accepte un nom de branche ou un sha). 
	- Les permissions du token utilisé par `gh` doivent permettre d'exécuter et relancer des workflows (repo:workflow scope).

	Si vous voulez, j'ajoute aussi un petit script PowerShell `scripts/run_integration_workflow.ps1` qui encapsule ces commandes et fait les vérifications basiques (présence de `gh`, login, choix du run ou dispatch).
	- [ ] Documenter la commande exacte reproduisant la CI localement dans `DEVELOPER_SETUP.md`.

Note: pour exécuter localement le job d'intégration (ASGI) qui est optionnel en CI, voici les commandes PowerShell recommandées :

```powershell
# Crée et active un virtualenv (utiliser Python 3.11 pour parité)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Met à jour pip et installe les dépendances d'intégration
python -m pip install --upgrade pip
pip install fastapi==0.95 starlette==0.28 httpx==0.24 pytest-asyncio==0.21

# Positionner PYTHONPATH puis exécuter uniquement le test ASGI
$Env:PYTHONPATH = 'src;.'
pytest -q tests/test_asgi_tools.py -q
Remove-Item Env:\PYTHONPATH
```

2) Core infra (peu risqué, prioritaire)
	- [ ] Finaliser `src/blender_mcp/errors.py` (liste exhaustive d'erreurs et TypedDicts) — vérifier exports.
	- [ ] Finaliser `src/blender_mcp/types.py` (DispatcherResult, ToolCommand, ToolInfo) et publier les contrats internes.
	- [ ] Ajouter `src/blender_mcp/logging_utils.py` si absent et l'utiliser uniformément pour l'audit.
	- [ ] Ajouter tests unitaires pour les helpers (types, error shaping).

3) Dispatcher (critical)
	- [ ] Implémenter `src/blender_mcp/dispatcher.py` (register/list/dispatch) minimal :
			- register(name, handler)
			- list_handlers() -> list[str]
			- dispatch(name, params) -> DispatcherResult or raise HandlerNotFoundError
			- map exceptions -> canonical BlenderMCPError where appropriate
	- [ ] Ajouter tests unitaires : registration, dispatch happy/error, concurrency basic.
	- [ ] Mettre à jour les tests existants pour consommer l'API dispatcher.

4) Connection / Reassembly (critical)
	- [ ] Extraire `BlenderConnection` en `src/blender_mcp/connection.py` avec API testable : connect/disconnect/send_command/receive_full_response.
	- [ ] Implémenter fonction de réassemblage (reassembler) qui accepte fragments et retourne message complet.
	- [ ] Écrire tests simulant fragments (socketpair / fake socket) : multiple messages / partial / timeout / reconnect.
	- [ ] Ajouter injection de socket factory pour tests.

5) Services — portage par lots (détaillé)
	- Règles valides pour chaque endpoint porté :
		 - service dans `src/blender_mcp/services/<name>.py`
		 - lazy import `bpy` (importlib) ; sur absence lever `ExternalServiceError`
		 - lève `InvalidParamsError` pour params invalides
		 - lève `HandlerError` si l'implémentation appelle addon qui lève
		 - tests: happy + error (no bpy) + boundary cases

	- Liste d'implémentations prioritaires (chaque sous-étape = PR) :
	  - [ ] `get_object_info` (exemple PR) — tests unitaires & `object_location*` tests.
	  - [ ] `execute_blender_code` — sécuriser, tests, doc sécurité.
	  - [ ] `get_viewport_screenshot` — tests visuels/fake + performance.
	  - [ ] `get_scene_info` — tests et mapping.
	  - [ ] `get_scene_materials`, `get_node_helpers` (batch)
	  - [ ] autres endpoints listés dans `docs/endpoint_mapping_detailed.md` par priorité.

6) Wrappers MCP / mcp.tool decorators
	- [ ] Pour chaque service porté, écrire un wrapper `@mcp.tool()` qui :
		 - prend `params` JSON, appelle le service, capture exceptions et renvoie DispatcherResult dict (status/result/message/error_code)
		 - teste wrapper via TestClient / dispatcher unit tests
	- [ ] Garder les façades top-level (`src/blender_mcp/services/__init__.py`) ré-exportant les services pour compatibilité.

7) Adapters (ASGI / CLI)
	- [ ] Stabiliser `src/blender_mcp/asgi.py` :
		 - lifespan startup/shutdown robuste
		 - mapping exceptions -> (HTTP status, error_code) et JSONResponse
		 - audit log on success/error
	- [ ] Ajouter tests ASGI (TestClient) pour tous les cas d'erreur canonique.
	- [ ] Créer/valider un adapter CLI si nécessaire (pour debug/manual invocation).

8) Integrations réseau (I/O heavy)
	- [ ] Isoler les helpers réseau (downloaders, polyhaven, sketchfab, hyper3d) dans `src/blender_mcp/integrations/`.
	- [ ] S'assurer que ces fonctions lèvent `ExternalServiceError` sur échec réseau.
	- [ ] Tests unitaires mockant `requests` / sessions ; tests d'intégration optionnels contre des endpoints stubs.

9) Tests & qualité
	- [ ] Augmenter la couverture sur services portés (happy + error + edge cases).
	- [ ] Créer tests d'intégration réseau pour `BlenderConnection` reassembly.
	- [ ] Linter (`ruff`) & typecheck (`mypy`) vert pour fichiers modifiés.

10) Documentation & OpenSpec
	- [ ] Mettre à jour `docs/endpoint_mapping_detailed.md` après chaque lot.
	- [ ] Pour tout changement de contrat public (payload ou `error_code`), créer `openspec/changes/<id>/` avec spec et scénarios d'acceptation, puis `openspec validate --strict`.
	- [ ] Tenir `docs/PROJECT_JOURNAL.md` à jour (format prescrit).

11) Packaging & release
	- [ ] Finaliser `pyproject.toml` (versions, extras [dev] incl FastAPI), verrouiller dépendances si nécessaire.
	- [ ] Test `pip install .` in clean venv and run smoke tests.
	- [ ] Rédiger `CHANGELOG.md` pour le lot de modifications.

12) PR process & merge guard
	- PR size limit : 1 concept (max 3 files) per PR.
	- Always include:
		 - Tests that demonstrate behavior.
		 - `docs/PROJECT_JOURNAL.md` entry.
		 - Commands to reproduce tests locally.
	- Require: successful `pytest`, `mypy` (for modified files), `ruff` in CI.

13) Post-merge / follow-ups
	- [ ] Remove façade shims only after all callers/tests have migrated.
	- [ ] Run scheduled pass to convert remaining tests that expect dict-style errors to raising exceptions.
	- [ ] Periodic audit (monthly) of SOLID checklist for modules modified since last audit.
