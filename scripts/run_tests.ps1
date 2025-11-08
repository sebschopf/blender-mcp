# Run tests with PYTHONPATH=src and active virtualenv if present
# Usage: .\scripts\run_tests.ps1

# If a venv exists in ./venv, activate it (PowerShell)
if (Test-Path -Path "venv/Scripts/Activate.ps1") {
    Write-Host "Activating venv..."
    . "venv/Scripts/Activate.ps1"
}

$env:PYTHONPATH = "src"
Write-Host "Running pytest with PYTHONPATH=$env:PYTHONPATH"
python -m pytest -q
