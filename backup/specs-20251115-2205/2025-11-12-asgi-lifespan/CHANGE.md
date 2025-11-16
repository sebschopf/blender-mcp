# Change: 2025-11-12-asgi-lifespan

Date: 2025-11-12
Author: automated-agent / maintainer

Summary
-------
Replace deprecated FastAPI startup handler usage with the Lifespan handler and add an optional CI integration job to run ASGI tests.

Motivation
----------
- FastAPI deprecates `@app.on_event("startup")` in favor of lifespan handlers. Tests trigger DeprecationWarning and CI should be warning-free.
- Provide a reproducible, opt-in integration job to run ASGI tests (FastAPI/Starlette) without slowing down standard PR checks.

Files changed
-------------
- `src/blender_mcp/asgi.py` — use `lifespan` handler and remove deprecated `@app.on_event("startup")` usage. Also use module reference to `logging_utils` to allow monkeypatching in tests.
- `.github/workflows/ci.yml` — add optional `integration` job and document `PYTHONPATH` guidance; job installs FastAPI+test deps and runs `tests/test_asgi_tools.py` when manually triggered.
- `pyproject.toml` — add dev dependencies for FastAPI and ASGI testing (fastapi, starlette, httpx, pytest-asyncio).

Breaking change
---------------
This is non-breaking for runtime behavior. It removes a deprecated startup hook and replaces it with the lifespan handler. No user-facing API change.

Acceptance criteria
-------------------
1. Unit and ASGI tests pass locally when dev deps are installed:

```powershell
$env:PYTHONPATH = 'src'
python -m pip install --upgrade pip
python -m pip install fastapi starlette httpx pytest-asyncio uvicorn
python -m pytest tests/test_asgi_tools.py -q
Remove-Item Env:\PYTHONPATH
```

2. The PR includes a clear description and references this openspec change directory.
3. FastAPI DeprecationWarning for `on_event("startup")` no longer appears when running ASGI tests.
4. CI `integration` job can be manually dispatched and produces an artifact `pytest-integration-report.xml`.

Scenarios (short)
-----------------
- Scenario: Running ASGI tests locally
  - Given a dev environment with the listed dev deps
  - When running `pytest tests/test_asgi_tools.py`
  - Then tests succeed and no DeprecationWarning about `on_event("startup")` is emitted

- Scenario: Running integration job in CI
  - Given the workflow is manually dispatched
  - When the integration job runs
  - Then the job completes and uploads `pytest-integration-report.xml` as an artifact

Validation
----------
- Run `openspec validate --strict` (if available) in repo root to validate spec format.
- Ensure the PR body references this change id `2025-11-12-asgi-lifespan`.

Notes
-----
If future changes to the lifespan handler are made, update this change to include the rationale and test outcomes.
