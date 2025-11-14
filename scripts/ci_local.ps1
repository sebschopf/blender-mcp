<#
Reproduce GitHub Actions CI steps locally on Windows PowerShell.

Usage: .\scripts\ci_local.ps1

This script will:
- activate an existing virtualenv in `.venv` or `venv` if present
- set `PYTHONPATH` to include `src` and the repository root
- install the pinned tools used in CI (ruff, mypy) and test deps
- run `ruff`, `mypy`, then `pytest` to mirror the CI job order
#>

if (Test-Path -Path ".venv/Scripts/Activate.ps1") {
    Write-Host "Activating .venv..."
    . "./.venv/Scripts/Activate.ps1"
} elseif (Test-Path -Path "venv/Scripts/Activate.ps1") {
    Write-Host "Activating venv..."
    . "./venv/Scripts/Activate.ps1"
} else {
    Write-Host "No virtualenv found at .venv or venv. Proceeding without activation."
}

Write-Host "Setting PYTHONPATH for this session (Windows separator ';')"
$Env:PYTHONPATH = 'src;.'

Write-Host "Updating pip and installing pinned tooling (ruff, mypy) and test deps"
python -m pip install --upgrade pip
pip install ruff==0.12.4 mypy==1.11.0 types-requests types-urllib3 --disable-pip-version-check

Write-Host "Running ruff (lint)"
ruff check --exclude "src/blender_mcp/archive/**" src tests

Write-Host "Running mypy (typecheck)"
mypy src --exclude "src/blender_mcp/archive/.*"

Write-Host "Installing pytest and runtime/test dependencies"
pip install pytest==7.4.2 requests fastapi starlette httpx pytest-asyncio --disable-pip-version-check

Write-Host "Running pytest"
pytest -q --junitxml=pytest-report.xml

Write-Host "Cleaning PYTHONPATH environment variable"
Remove-Item Env:\PYTHONPATH -ErrorAction SilentlyContinue

Write-Host "Done."
