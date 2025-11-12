## MODIFIED Requirements

### Requirement: ASGI startup lifecycle uses lifespan handlers
The ASGI adapter MUST use FastAPI lifespan handlers instead of the deprecated `@app.on_event("startup")` decorator.

- Any usage of `@app.on_event("startup")` MUST be replaced with an explicit `lifespan(app: FastAPI)` implementation that starts and stops the MCP thread.

#### Scenario: Running ASGI tests locally
Given a developer with the repository and dev dependencies installed
When they run `pytest tests/test_asgi_tools.py`
Then the tests run without emitting `DeprecationWarning` about `on_event("startup")` and the ASGI adapter starts/stops via lifespan
