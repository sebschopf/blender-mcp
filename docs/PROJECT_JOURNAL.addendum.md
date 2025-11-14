ARCHIVED: this journal addendum has been moved to `docs/archive/PROJECT_JOURNAL.addendum.md`.
See `docs/archive/PROJECT_JOURNAL.addendum.md` for the preserved content.
2025-11-08 | sebas
- Action: Created draft PR for current port/refactor work
- Fichiers: branch `feature/port-refactor-2025-11-08` (many files under `src/`, tests and docs)
- Commands run:
  - `gh pr create --repo sebschopf/blender-mcp --base main --head feature/port-refactor-2025-11-08 --draft ...`
- Tests: local QC (ruff/mypy/pytest) run prior to PR creation -> pass for active code
- Statut: done (draft PR created)
- Notes: Draft PR opened at: https://github.com/sebschopf/blender-mcp/pull/1

2025-11-14 | ai-session
- Action: Corrections et intégration du bridge Gemini → MCP → Blender durant une session interactive.
- Fichiers modifiés:
  - `src/blender_mcp/asgi.py` (guard startup thread)
  - `src/blender_mcp/gemini_client.py` (prompt formatting safe replace)
  - `scripts/gemini_bridge.py` (instanciation `Dispatcher`, wiring callables, support `use_api`)
  - `docs/AI_SESSION_CHANGES.md` (nouveau, résumé et instructions)
- Commands run / notes:
  - Validation locale: `ruff`, `mypy`, `pytest` exécutés; dépendance `google-genai` installée si nécessaire.
  - Environnement: `MCP_BASE` doit être défini pour le mode HTTP (ex: `http://127.0.0.1:8000`).
- Statut: correctifs appliqués localement; à pousser/PRer en petits modules atomiques.

