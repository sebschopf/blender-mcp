Developer setup (Windows PowerShell)
=================================

Quick steps to create a virtual environment and run the test suite locally on Windows PowerShell.

1. Create & activate venv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Upgrade pip and install dev dependencies (minimal)

```powershell
python -m pip install --upgrade pip
python -m pip install -U pytest ruff mypy types-requests requests
# if you use poetry, prefer: poetry install --with dev
```

3. Run tests

```powershell
# ensure package root is discoverable by tests
$env:PYTHONPATH = 'src'; python -m pytest -q
```

Note: Dans CI (GitHub Actions) `PYTHONPATH` est défini en `src:.` pour garantir que le repo root est accessible pendant les tests. Localement, `$env:PYTHONPATH = 'src'` reste la pratique recommandée.

4. Install pre-commit hooks (recommended)

```powershell
python -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Notes
-----
- The project supports running tests without Blender because modules touching `bpy` use lazy imports.
- To allow the dangerous `execute_blender_code` endpoint to actually run code inside Blender, set the environment variable `BLENDER_MCP_ALLOW_EXECUTE=1` inside a Blender session (be cautious). You can enable a dry-run mode with `BLENDER_MCP_EXECUTE_DRY_RUN=1` which will log but not execute code.
