## Why

FastAPI deprecated `@app.on_event("startup")` in favor of lifespan handlers. Running ASGI tests currently emits a DeprecationWarning; this change replaces the startup handler with an explicit `lifespan` implementation.

## What changes

- Replace deprecated startup handler in `src/blender_mcp/asgi.py` with `lifespan(app)` implementation.
- Use module-level reference to `logging_utils` to make log action monkeypatchable in tests.
- Add optional CI integration job to run ASGI tests (`.github/workflows/ci.yml`).
- Add dev deps to `pyproject.toml` to support FastAPI/ASGI tests locally.

## Impact

- Non-breaking for runtime behavior. Improves test hygiene (no DeprecationWarning) and provides an opt-in CI integration job for ASGI tests.
