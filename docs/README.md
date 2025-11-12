# Documentation index — blender-mcp

This README provides a concise map of the project's documentation and the archive policy.

Canonical docs (top-level)
- `docs/TASKS_AND_PRACTICES.md` — Roadmap and small-PR rules (read first).
- `docs/endpoint_mapping_detailed.md` — Canonical endpoint mapping and portage status.
- `docs/architecture.md` — High-level architecture and module responsibilities.
- `docs/project_state_vs_ahujasid.md` — Progress notes vs original reference implementation.

Developer docs
- `docs/developer/` — developer-focused guides (error handling, injection patterns).

Archive
- Old/noisy documents have been moved to `docs/archive/` to reduce clutter. See that folder for:
  - historical inventories, PR stubs, adenda and generated mapping files.

Pointer stubs
 - Some top-level files were replaced with small pointer stubs that redirect readers to `docs/archive/` (non-destructive). If you maintain a file and want it restored to top-level, create a small PR referencing the archive entry.

How to contribute docs changes
1. Edit or add markdown under `docs/` for canonical docs.
2. For behavior/contract changes, add an OpenSpec proposal under `openspec/changes/<id>/`.
3. Update `docs/PROJECT_JOURNAL.md` with a short entry describing the change.

Quick reproduction
Use PowerShell (Windows) when reproducing tests locally:

```powershell
$env:PYTHONPATH = 'src'
python -m pytest -q
Remove-Item Env:\PYTHONPATH
```

Archive policy
- Files in `docs/archive/` are read-only reference material and may be re-used when drafting PRs. If you want a file restored to the top-level docs, open a PR and reference this README.
