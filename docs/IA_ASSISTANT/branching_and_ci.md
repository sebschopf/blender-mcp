**But**
- Centraliser les règles de branche, PR et la procédure pour vérifier que les vérifications locales sont compatibles avec celles de CI.

**Branches recommandées**
- `feature/<desc>` : nouvelles fonctionnalités (ex: `feature/transport-phase-a`).
- `chore/<desc>` : tâches infra, dépréciations, migrations non-fonctionnelles.
- `docs/<desc>` : documentation uniquement.
- `fix/<desc>` : corrections de bugs ciblées.

Conventions:
- PR atomiques: idéalement ≤ 3 fichiers de code modifiés.
- Messages de commits: Conventional Commits en français (ex: `feat(transport): add Transport protocol`).
- Labels: ajouter `phase2` pour portages/phase 2 work.

**Procédure pour exécuter les vérifications locales (PowerShell)**
```
# activer venv
& .\.venv\Scripts\Activate.ps1
# exécuter vérifs locales
$Env:PYTHONPATH='src'
ruff check src tests
mypy src --exclude "src/blender_mcp/archive/.*"
pytest -q
Remove-Item Env:PYTHONPATH
```
Notes:
- Assurez-vous d'utiliser les mêmes versions d'outils que la CI (voir `ai_session_guide.yaml` -> `versions.recommended`). Installer si nécessaire via `pip install ruff==0.12.4 mypy==1.11.0 pytest==7.4.2`.
- Si `pytest` échoue localement mais passe en CI, comparer les environnements: CI définit `PYTHONPATH='src:.'`; reproduisez-le localement (PowerShell: `setx` ou `$Env:PYTHONPATH='src:.'` pour la session). Vérifier aussi variables d'environnement requises par certains tests.

**Comparer local ↔ CI**
1. Exécuter les commandes locales et capturer la sortie dans des fichiers: `ruff_out.txt`, `mypy_out.txt`, `pytest_out.txt`.
2. Dans l'interface GitHub Actions, ouvrir le job `pytest`/`mypy`/`ruff` et télécharger les logs correspondants (ou noter erreurs).  
3. Relever différences spécifiques:
   - Versions d'outils (installer la même version localement).
   - Valeurs d'environnement (`PYTHONPATH`, flags, variables privées). Recréer les mêmes valeurs.
   - Configs (pyproject.toml, mypy.ini, pytest.ini). Vérifier qu'il n'y a pas d'ignore différent.
4. Si les différences persistent, créer un ticket `ci/inconsistency` avec les artefacts attachés et l'ID du run CI.

**Exemples de branches à créer (squelette)**
- `feature/transport-phase-a` — implémentation protocole `Transport`, tests de sélection.
- `chore/deprecations-legacy-shims` — ajouter DeprecationWarning aux modules legacy.
- `feature/services-refactor` — déplacer services racine vers `src/blender_mcp/services/` (si nécessaire, faire en étapes).
- `docs/ai_assistant_guides` — documentation pour assistants automatisés (fichiers YAML/MD).

**Checklist PR (à inclure dans description de PR)**
- [ ] Lint: `ruff check src tests` passe.
- [ ] Typage: `mypy src --exclude "src/blender_mcp/archive/.*"` passe.
- [ ] Tests: `pytest -q` passe localement.
- [ ] Changements ≤ 3 fichiers code (si fonctionnels), sinon expliquer justification.
- [ ] Si API changée: ajouter spécification sous `openspec/changes/<id>/`.
- [ ] Mettre à jour `PROJECT_JOURNAL.md` si changement d'architecture.

**Conseils pour l'assistant IA**
- Avant tout changement: relire `docs_index` listé dans `ai_session_guide.yaml`.
- Pour choisir une branche: utiliser `feature/*` pour toute nouveauté, `chore/*` pour infra.
- Toujours documenter la raison des changements dans `PROJECT_JOURNAL.md` et le corps du PR.

**Annexes**
- Fichiers clés à inspecter avant modification: `src/blender_mcp/services/registry.py`, `src/blender_mcp/dispatchers/dispatcher.py`, `src/blender_mcp/asgi.py`, `.github/workflows/ci.yml`, `pyproject.toml`.

