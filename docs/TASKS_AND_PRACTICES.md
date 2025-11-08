# Checklist, bonnes pratiques et contrôles SOLID

But
----
Ce document centralise :
- une liste de tâches actionnable et priorisée pour terminer le portage et la stabilisation du projet ;
- des bonnes pratiques à appliquer pour chaque tâche (tests, typage, import paresseux, sécurité) ;
- une checklist de conformité au principe SOLID adaptée au code Python et au projet ;
- un processus de journalisation des étapes et de validation avant commit.

Organisation des tâches
----------------------
Les tâches sont regroupées par domaine : architecture, endpoints, tests, CI, packaging, documentation.

Important : chaque tâche doit être accompagnée d'un petit test unitaire (ou d'un test d'intégration léger) et d'une entrée de journal décrivant les fichiers modifiés et la commande pour reproduire les tests.

Liste de tâches principale (à cocher au fur et à mesure)
----------------------------------------------------

- [x] Finaliser le workflow CI (GitHub Actions)
  - Objectif : exécuter `pytest`, `ruff` et `mypy` sur PRs.
  - Bonnes pratiques : utiliser une matrice Python (3.11+), cache pip, exécuter tests unitaires en parallèle si possible.
  - Tests : vérifier que `pytest -q` passe localement avant push.

- [x] Affiner la configuration typing/lint
  - Ajouter `pyproject.toml` / `mypy.ini` / `.ruff.toml` si manquant.
  - Rendre `mypy` strictité progressive (commencer par `--disallow-untyped-calls` désactivé, puis activer par module).

- [ ] Porter restants endpoints (par lots de 3)
  - Prioriser par fréquence d'utilisation (voir `docs/endpoint_mapping.md`).
  - Pour chaque endpoint :
    - créer un service dans `src/blender_mcp/services/` (import paresseux `bpy` si nécessaire),
    - ajouter tests unitaires (mock `bpy` / mock réseau),
    - ajouter entrée dans `endpoints.register_builtin_endpoints` et test d'intégration léger.

- [ ] Ajouter wrappers MCP import-safe
  - Pour chaque service porté, écrire un wrapper minimal décoré par `@mcp.tool` (ou `@mcp.prompt`) qui appelle le dispatcher.
  - Wrapper = adaptateur de params + conversion d'erreurs en réponse JSON.

- [ ] Tests d'intégration réseau
  - Utiliser `socketpair` ou fake-socket pour tester `BlenderConnectionNetwork` send/recv et la ré-assemblage.
  - Cas testés : fragments, plusieurs messages, timeout, reconnect.

- [ ] Audit SOLID et refactor mineur
  - Exécuter la checklist SOLID (voir ci-dessous) sur les modules modifiés ; corriger violations simples.

- [ ] Documentation / mapping final
  - Mettre à jour `docs/endpoint_mapping_detailed.md` et `README.md` pour refléter les endpoints portés et leur contrat.

- [ ] Packaging / release readiness

### État de la factorisation (résumé)

Ce qui a déjà été factorisé / stabilisé :
- `src/blender_mcp/services/` : plusieurs endpoints et helpers ont été extraits en services testables (ex. `object.py`, `scene.py`, `execute.py`, `screenshot.py`).
- `src/blender_mcp/tools.py` et `src/blender_mcp/integrations.py` : wrappers et façades progressives pour certains handlers.
- Tests unitaires : nombreux tests ajoutés (mock `bpy`, tests d'intégration légers) — la suite locale passe.
- Journalisation : `docs/PROJECT_JOURNAL.md` reprend les étapes et les vérifications.
- CI minimal : `.github/workflows/ci.yml` présent et exécute `ruff`, `mypy` et `pytest` (workflow itératif, permissif pour l'instant).

Ce qui reste à factoriser / porter :
- `BlenderConnection` (réassembly/chunking, gestion socket) : doit devenir `src/blender_mcp/connection.py` et recevoir des tests simulant fragments et reconnect.
- `dispatcher` / `command_registry` : implémenter un dispatcher léger (register/list/dispatch) dans `src/blender_mcp/dispatcher.py` et relier `BlenderMCPServer`.
- Endpoints restants listés dans `docs/endpoint_mapping_detailed.md` : porter par lots, en commençant par `get_viewport_screenshot`, `execute_blender_code`, `get_scene_info` puis intégrations (PolyHaven/Sketchfab/Hyper3D).
- `src/blender_mcp/server.py` : consolider la façade minimale, retirer duplications et exposer lifecycle testable.
- Wrappers MCP (`@mcp.tool` / `@mcp.prompt`) : créer adaptateurs import-safe pour chaque service porté.
- Packaging / release readiness : `pyproject.toml` final, `CHANGELOG.md`, test `pip install .` dans un venv propre.

### Étapes ajoutées (petits jalons)
- [ ] Implémenter `src/blender_mcp/dispatcher.py` (register/list/dispatch) + tests unitaires (prioritaire)
- [ ] Implémenter `src/blender_mcp/connection.py` (BlenderConnection testable, reassembly) + tests de chunks (prioritaire)
- [ ] Préparer une branche PR contenant les changements en cours et le journal (pour revue)
- [ ] Mettre à jour CI : exiger PYTHONPATH correct dans workflow, ajouter matrix Python 3.11+, et retirer `|| true` une fois la base propre
- [ ] Ajouter tests d'intégration réseau (socketpair / fake socket) pour la connection

### Statut global et recommandations
- Statut actuel : progression forte sur la modularisation des services et des tests. Quality gates (ruff/mypy/pytest) passent pour le code actif.
- Risques immédiats : rester vigilant à ne pas re-modifier les archives (docs/archive) ; veiller à ce que CI utilise le même PYTHONPATH que les runs locaux.
- Recommandation : prioriser l'implémentation du dispatcher et de la connection (jalons prioritaires) puis porter les endpoints critiques par lots de 3, en journalisant chaque lot.

---
  - Mettre à jour `pyproject.toml`, créer `CHANGELOG.md`, tester `pip install .` dans un venv propre.


Bonnes pratiques (règles concrètes)
----------------------------------

- Import paresseux : ne jamais importer `bpy` au module-level.
  - Toujours :
    ```py
    import importlib

    try:
        bpy = importlib.import_module('bpy')
    except Exception:
        # handle absence in CI/tests
    ```

- Tests : chaque nouveau service ou endpoint doit avoir :
  - 1 test unitaire happy-path ;
  - 1 test d'erreur (paramètres invalides / exception / absence de bpy) ;
  - pour le code réseau, un test simulant chunks partiels.

- Typage : annoter les fonctions publiques et utiliser types simples (Dict[str, Any]) pour payloads JSON.

- Logging : utiliser `logging.getLogger(__name__)` et logger exceptions via `logger.exception()`.

- Sécurité : pour `execute_blender_code`, documenter clairement qu'il exécute du Python arbitraire et protéger l'usage (UI confirmation, taille max du code, ou usage réservé à opérateurs). Documenter dans `docs/SECURITY.md`.


Checklist SOLID adaptée
-----------------------
Pour chaque module / classe, vérifier :

- Single Responsibility (SRP)
  - Chaque module/fonction a-t-il une responsabilité unique ?
  - Si une fonction réalise I/O réseau + parsing + logique métier, extraire le parsing et la logique métier dans `services/` et laisser la couche réseau appeler ces services.

- Open/Closed (OCP)
  - Peut-on ajouter un nouveau service/endpoint sans modifier du code existant ?
  - Utiliser `Dispatcher.register()` pour ajouter des handlers dynamiquement.

- Liskov Substitution (LSP)
  - Pour les objets interchangeables (p.ex. wrappers de connection), s'assurer qu'ils respectent la même API et lèvent des exceptions cohérentes.

- Interface Segregation (ISP)
  - Favoriser petites interfaces (ex : `BlenderConnectionNetwork.send_command()` / `receive_full_response()` plutôt que un monolithe avec dizaines de méthodes inutilisées).

- Dependency Inversion (DIP)
  - Dépendre d'abstractions (Dispatcher / services) plutôt que d'implémentations concrètes ; injecter la dépendance quand nécessaire pour faciliter les tests.

Procédure d'audit SOLID
----------------------
1. Pour chaque fichier modifié, ajouter une courte entrée dans `docs/PROJECT_JOURNAL.md` indiquant le contrôle SOLID rapide (SRP, OCP, DIP). Exemple :

   - fichier: `src/blender_mcp/connection.py` — SRP OK (réassembleur + network wrapper séparés), DIP partiellement (le network wrapper crée un socket internement) — recommandation : injecter le socket factory pour tests réels si besoin.

2. Corriger immédiatement les violations simples (facteur 2-3 lignes) et documenter les décisions pour les violations plus vastes.


Organisation de la documentation (tri et clarté)
-----------------------------------------------

Structure recommandée du dossier `docs/` :

- `docs/PROJECT_JOURNAL.md` — journal des étapes (obligatoire, format ci‑dessous).
- `docs/TASKS_AND_PRACTICES.md` — ce fichier (règles & checklist).
- `docs/endpoint_mapping_detailed.md` — mapping endpoint + statut (porté/pending) et référence à `copy_server.py`.
- `docs/SECURITY.md` — risques et garde-fous (exécution de code, upload/download).
- `docs/CONTRIBUTING.md` — guide pour contributeurs (tests, style, commit messages, PR template).

Chaque document doit commencer par : objectif, public cible, commande(s) utiles pour tester (ex : `pytest -q tests/test_x.py`).


Journalisation : `docs/PROJECT_JOURNAL.md` (modèle)
-------------------------------------------------
Chaque entrée doit contenir :

- Date (ISO)
- Auteur
- Action (fichiers modifiés, nouveau fichier)
- Tests exécutés (commande + résultat)
- Résultat / statut (done/partial/blocker)
- Notes / décisions (ex : raisons d'un choix d'architecture)

Exemple d'entrée :

```
2025-11-08 | sebas
- Action: Ajout services execute/scene/screenshot, dispatcher et connection reassembler
- Fichiers: src/blender_mcp/services/execute.py, ...
- Tests: pytest -q tests/test_services_execute.py -> 3 passed
- Statut: done
- Notes: Import paresseux de bpy, wrapper compatibility pour BlenderConnection
```


Validation avant commit
-----------------------
Avant d'ouvrir une PR, vérifier :

1. Tous les tests unitaires passent localement.
2. Les nouveaux fichiers sont documentés (docstring + tests + note dans le journal).
3. `pyproject.toml` / tooling minimal présent (ou justifié dans le journal si pas encore configuré).


Annexes
-------
- Commandes utiles de debug :
  - `python -m pytest tests/test_services_execute.py -q`
  - `ruff check src tests`
  - `mypy src --ignore-missing-imports`

---
Fin du document.
