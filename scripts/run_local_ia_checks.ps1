# Convenience script to run IA doc generation, validation and consistency test locally (PowerShell)
# Usage: .\scripts\run_local_ia_checks.ps1

param(
    [string]$OutputDraft = 'docs/IA_ASSISTANT/services_metadata_full_draft.yaml'
)

# Activate venv if exists (best-effort)
if (Test-Path '.venv\Scripts\Activate.ps1') {
    Write-Output 'Activating .venv...'
    & .\.venv\Scripts\Activate.ps1
}

Write-Output 'Generating draft metadata...'
python .\scripts\generate_services_metadata.py -o $OutputDraft
if ($LASTEXITCODE -ne 0) { Write-Error 'Generator failed'; exit $LASTEXITCODE }

Write-Output 'Validating IA YAML files...'
python .\scripts\validate_ia_yaml.py
if ($LASTEXITCODE -ne 0) { Write-Error 'YAML validation failed'; exit $LASTEXITCODE }

Write-Output 'Running IA docs consistency test...'
$Env:PYTHONPATH='src'
pytest -q tests/test_ia_docs_consistency.py
if ($LASTEXITCODE -ne 0) { Write-Error 'Consistency test failed'; exit $LASTEXITCODE }

Write-Output 'All IA checks passed locally.'
exit 0
