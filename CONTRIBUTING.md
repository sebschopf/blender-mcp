# Contributing / Developer guide

This project uses Poetry for dependency management and the following developer tools:

- ruff (linter / auto-fixer)
- mypy (type checking)
- black (formatter)
- isort (import sorter)
- pre-commit (git hooks)

Quick start (local dev environment)

1. Install Poetry (if not already):

```powershell
python -m pip install --upgrade pip
pip install poetry
```

2. Install project dependencies (recommended to run inside your project venv):

```powershell
poetry config virtualenvs.create false --local
poetry install
```

3. Install pre-commit hooks:

```powershell
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Useful commands

```powershell
# Lint / auto-fix with ruff
python -m ruff check . --fix

# Format
python -m isort .
python -m black .

# Type checks
python -m mypy src --ignore-missing-imports

# Tests
python -m pytest -q
```

CI

A GitHub Actions workflow is provided in `.github/workflows/ci.yml` which runs ruff, mypy, black/isort checks and pytest on push/PR.

Thank you for contributing — keep things small, well-typed and covered by tests.
