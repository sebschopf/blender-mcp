Developer setup (Windows PowerShell)
=================================

Quick steps to create a virtual environment and run the test suite locally on Windows PowerShell.

1. Create & activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Upgrade pip and install minimal development dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -U pytest ruff mypy types-requests requests
# If you use Poetry, prefer: poetry install --with dev
```

3. Run tests

```powershell
# Ensure the package root is discoverable by tests
$env:PYTHONPATH = 'src'; python -m pytest -q
```

Note: In CI (GitHub Actions) `PYTHONPATH` is set to `src:.` to ensure the repository root is available during tests. Locally, `$env:PYTHONPATH = 'src'` is the recommended practice.

Alternatively, to run the exact same steps as GitHub Actions (ruff, mypy, pytest with pinned tool versions), use the provided helper script:

```powershell
.\scripts\ci_local.ps1
```

## Reproduce the CI environment locally (PowerShell)

To reproduce the GitHub Actions pipeline environment as closely as possible on Windows PowerShell (virtual environment, pinned tool versions, and running the same steps `ruff`, `mypy`, `pytest`), follow these commands.

Note: CI runs a matrix on Python 3.11 and 3.12; for parity use Python 3.11 locally.

```pwsh
# 1) Create and activate a virtualenv (use Python 3.11 for exact parity)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Update pip and install the pinned tools used in CI
python -m pip install --upgrade pip
pip install ruff==0.12.4 mypy==1.11.0 pytest==7.4.2 types-requests types-urllib3 requests

# 3) (Optional) install ASGI integration dependencies if you want to run the optional "integration" job locally
pip install fastapi==0.95 starlette==0.28 httpx==0.24 pytest-asyncio==0.21

# 4) Set PYTHONPATH for the PowerShell session (Windows separator = ;)
$Env:PYTHONPATH = 'src;.'

# 5) Run the checks in the same order as CI
ruff check --exclude "src/blender_mcp/archive/**" src tests
mypy src --exclude "src/blender_mcp/archive/.*"
pytest -q --junitxml=pytest-report.xml

# 6) Clean up the environment variable when finished
Remove-Item Env:\PYTHONPATH

# Additional notes:
# - If you use Poetry: `poetry install --with dev` will reproduce dependency resolution defined in `pyproject.toml`.
# - Verify local versions if needed: `python --version`, `ruff --version`, `mypy --version`, `pytest --version`.
```

## Running the optional ASGI integration test (local)

If you want to reproduce the optional ASGI integration job locally (the job that runs `tests/test_asgi_tools.py` in CI), use these PowerShell commands (prefer Python 3.11 for parity):

```powershell
# Create and activate the virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install ASGI test dependencies
python -m pip install --upgrade pip
pip install fastapi==0.95 starlette==0.28 httpx==0.24 pytest-asyncio==0.21

# Run the ASGI tests
$Env:PYTHONPATH = 'src;.'
pytest -q tests/test_asgi_tools.py -q
Remove-Item Env:\PYTHONPATH
```

4. Install pre-commit hooks (recommended)

```powershell
python -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Notes
-----
- The project supports running tests without Blender because modules that touch `bpy` use lazy imports.
- To allow the dangerous `execute_blender_code` endpoint to actually run code inside Blender, set the environment variable `BLENDER_MCP_ALLOW_EXECUTE=1` inside a Blender session (use with caution). You can enable a dry-run mode with `BLENDER_MCP_EXECUTE_DRY_RUN=1` which will log but not execute code.
