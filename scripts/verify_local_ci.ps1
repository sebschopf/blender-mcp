Param(
    [switch]$Verbose
)

$ErrorActionPreference = 'Stop'
Write-Host "== Local CI Parity Checks ==" -ForegroundColor Cyan

if ($Verbose) { Write-Host "Ruff (lint)" -ForegroundColor DarkGray }
ruff check src tests

Write-Host "-- Ruff OK --" -ForegroundColor Green

if ($Verbose) { Write-Host "MyPy (types)" -ForegroundColor DarkGray }
mypy src --exclude "src/blender_mcp/archive/.*"
Write-Host "-- MyPy OK --" -ForegroundColor Green

if ($Verbose) { Write-Host "Pytest (suite)" -ForegroundColor DarkGray }
$Env:PYTHONPATH = 'src'
try {
    pytest -q
    Write-Host "-- Pytest OK --" -ForegroundColor Green
} finally {
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
}

Write-Host "All local CI parity checks passed." -ForegroundColor Cyan

exit 0