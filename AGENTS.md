<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

---

# Guide d'exécution pour agents (synthèse opératoire)

Ce dépôt applique une conduite « senior lead dev » orientée petits incréments, CI stricte et documentation vivante. Pour le contexte complet, lis d'abord `docs/developer/ai_session_guide.md`.

Objectif courant (terrain)
- Phase 2: registre de services et portage d'endpoints vers `src/blender_mcp/services/*` avec exceptions canoniques et tests dédiés.
- CI: ruff + mypy + pytest (Python 3.11/3.12) doivent être verts avant PR.

Conventions de travail
- Taille des PR: petite surface (≤ 3 fichiers code hors tests/docs) par thème.
- Commits: Conventional Commits en français, p.ex. `feat(polyhaven): …`, `refactor(connection): …`, `chore(lint): …`, `docs: …`, `ci: …`.
- Lint/Type: `ruff check` et `mypy` obligatoires localement avant PR; corriger import order/unused/long lines; privilégier directives localisées si l'ordre d'import est intentionnel (ex: `# isort: skip_file`).
- Tests: `pytest -q` avec `PYTHONPATH=src` localement; la CI utilise `PYTHONPATH='src:.'`.
- Spécifications: tout changement de comportement/API passe par `openspec/changes/<id>/` avec validation.

Checklist avant commit
1) Exécuter localement:
	- `ruff check src tests`
	- `mypy src --exclude "src/blender_mcp/archive/.*"`
	- `$Env:PYTHONPATH='src'; pytest -q`
2) Mettre à jour docs si nécessaire (`docs/PROJECT_JOURNAL.md`, `docs/endpoint_mapping_detailed.md`).
3) Ajouter/mettre à jour les specs si surface publique affectée (`openspec/changes/<id>/`).

PR et CI
- Branching: `feature/<objectif-court>`.
- Labels: utiliser `phase2` pour les portages de services; milestones alignés avec la roadmap.
- CI PR: s'exécute sur toutes les bases de PR (workflow `CI`). Matrice 3.11/3.12; jobs ruff, mypy, pytest doivent être success.

Décisions spécifiques projet
- Dispatcher: si l'ordre d'import est nécessaire, documenter et geler via `# isort: skip_file` (aucun changement runtime). Prévoir un refactor SOLID ultérieur, pas dans une PR de portage.
- Services: exceptions-first (ne jamais retourner de dict d'erreur). Les adapters formatent `{status, result|message, error_code}`. Voir `docs/developer/error_handling.md`.
- Registre: enregistrer toute nouvelle fonction service dans `services/registry.py` et ajouter les tests de découverte/dispatch associés.

Pense-bête Windows/PowerShell
```powershell
$Env:PYTHONPATH='src'; ruff check .; mypy src --exclude "src/blender_mcp/archive/.*"; pytest -q
Remove-Item Env:PYTHONPATH
```

Rappels
- Préférer des changements petits, testés, réversibles; documenter le « pourquoi » dans la PR.
- Quand c'est ambigu (plan, changements d'API, sécurité), ouvrir/mettre à jour une spec OpenSpec avant de coder.
