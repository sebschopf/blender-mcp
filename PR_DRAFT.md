PR draft: Clean up addon, make google-genai optional, add import test
===================================================================

Branch (local): feature/refactor-addon-minimal

Commit summary (single commit):
- Reduce `addon.py` to a minimal import-safe shim delegating UI registration to `blender_mcp.blender_ui`.
- Add `tests/test_addon_import.py` to ensure `addon.py` is importable without Blender (`bpy`).
- Make `google-genai` optional: dynamic import in `src/blender_mcp/gemini_client.py` with a clear RuntimeError if absent.
- Install and use `types-requests` in dev dependencies to satisfy `mypy` for `requests`.
- Add audit notes (`AUDIT.md`) and small README contributor notes about optional deps and lazy imports.

PR body (suggested):
This PR cleans up the Blender addon entrypoint and improves the project's
testability and typing by:

- Replacing the large inline Blender-only logic in `addon.py` with a thin shim
  that lazily imports the real UI implementation in `blender_mcp.blender_ui`.
- Making the google-genai dependency optional (dynamic import). If not
  installed, `call_gemini_api` raises a clear RuntimeError explaining how to
  install it. This prevents forcing the SDK on all contributors and CI runs.
- Adding `tests/test_addon_import.py` which ensures `addon.py` is importable
  outside Blender (important for CI and local tests).
- Adding `AUDIT.md` with a summary of the refactor decisions and security
  notes.
- Installing `types-requests` as dev-dependency (already present in
  `pyproject.toml`) and verifying `mypy` passes locally.

Why:
- Keep the add-on import-safe so modules can be imported in CI without Blender.
- Make optional integrations clearly opt-in.
- Improve developer experience for contributors and CI.

Checklist before merge:
- [ ] Confirm CI passes on GitHub Actions (pytest, ruff, mypy)
- [ ] Decide whether to squash commits or keep atomic commits
- [ ] Optionally add an integration test for google-genai (requires SDK + key)

Suggested Git commands (PowerShell)
```powershell
# create branch from main
git checkout -b feature/refactor-addon-minimal

# stage changes
git add -A

git commit -m "chore: minimize addon.py, make google-genai optional, add import test + audit"

# push to your fork/remote
# if you have write access to origin and want to push there:
# git push origin feature/refactor-addon-minimal

# if you prefer to push to your fork (example remote name 'fork'):
# git remote add fork https://github.com/<your-username>/blender-mcp.git
# git push fork feature/refactor-addon-minimal
```

Notes for maintainers
- This PR intentionally avoids adding google-genai to mandatory deps. If
  maintainers prefer to make it first-class, we can split the integration
  into `blender_mcp/integrations/genai.py` and add documentation to the README.

---

(You can copy-paste this content into the PR description when opening the PR.)