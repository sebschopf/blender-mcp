**PR Template — AI / Assistant-Friendly**

But
- Fournir un squelette de PR et une checklist que les assistants IA (Copilot/GPT) peuvent remplir automatiquement.
- Forcer la mise à jour des fichiers machine‑readables (`docs/IA_ASSISTANT/*`) quand les services/endpoints/tests sont modifiés.

Utilisation
- Copier ce template dans le corps de la PR. Laisser les sections remplies par l'IA ou l'auteur humain.

**Titre**: `feat(<scope>): courte description` ou `chore(<scope>): ...` (Conventional Commits FR)

**Description**:
- **Contexte**: Résumé (1-2 lignes) du changement.
- **Changements**: Liste concise des fichiers modifiés et du but.
- **Impact**: API publique modifiée ? (oui/non). Si oui -> ajouter un spec sous `openspec/changes/<id>/`.

**Checklist (obligatoire)**
- [ ] **Lint**: `ruff check src tests` passe localement.
- [ ] **Typing**: `mypy src --exclude "src/blender_mcp/archive/.*"` passe localement.
- [ ] **Tests**: `pytest -q` passe localement.
- [ ] **Files changed**: ≤ 3 fichiers de code (si plus, expliquer la raison ci‑dessous).
- [ ] **Docs IA**: si vous modifiez services/endpoints/tests, mettez à jour **au moins** un des fichiers sous `docs/IA_ASSISTANT/` (par ex. `services_index.yaml`, `services_metadata.yaml`, `endpoints.yaml`, `tests_index.yaml`).
- [ ] **PROJECT_JOURNAL**: Mettre à jour `docs/PROJECT_JOURNAL.md` si le changement est architectural.
- [ ] **Openspec**: Si modification d'API → créer une spec `openspec/changes/<id>/` et lier ici.

**Détails complémentaires (à remplir automatiquement par l'IA si possible)**
- **Fichiers modifiés (liste)**:
  - 
- **Raison technique**:
  - 
- **Tests exécutés (commandes + sorties attachées)**:
  - `ruff`: (résumé)
  - `mypy`: (résumé)
  - `pytest`: (résumé)

**Notes sécurité / exécution de code**
- Si la PR affecte `execute_blender_code` ou tout service qui exécute du code, ajouter une section `Security` précisant la politique d'exécution (sandbox, dry_run, allowlist AST, etc.).

**Labels recommandés**
- `phase2` (portage / migration), `ci` (changements CI), `docs` (docs only), `chore`.

**Comment l'IA doit utiliser ce template (règles)**
- Avant d'ouvrir la PR, **exécuter localement** les commandes listées dans `docs/IA_ASSISTANT/ai_session_guide.yaml` (PowerShell) et joindre les artefacts (`ruff_out.txt`, `mypy_out.txt`, `pytest_out.txt`) au PR si des erreurs sont présentes.
- Si la PR change un service/endpoint/test, **mettre à jour** les fichiers `docs/IA_ASSISTANT/services_index.yaml`, `services_metadata.yaml`, `endpoints.yaml`, `tests_index.yaml` selon l'étendue du changement.
- Si l'IA ne connaît pas l'ID openspec requis pour un changement d'API, inclure le fichier `openspec/changes/<id>/spec.md` en draft et demander revue humaine.

---

Remarques finales
- Les mainteneurs peuvent refuser une PR automatisée si les YAML `docs/IA_ASSISTANT/*` ne sont pas tenus à jour. La règle vise à garder l'IA autonome et la documentation synchronisée.
