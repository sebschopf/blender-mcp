<#
PowerShell helper: run local checks and collect artifacts for comparison with CI logs.
Creates an artifacts folder `artifacts/ci_compare_<timestamp>/` and archives outputs.
#>
param(
    [switch]$ActivateVenv = $false,
    [string]$VenvPath = ".venv",
    [string]$OutputDir = "artifacts",
    [bool]$IncludePipFreeze = $true
)

# Timestamped folder
$ts = (Get-Date).ToString('yyyyMMdd_HHmmss')
$workDir = Join-Path $PSScriptRoot "$OutputDir\ci_compare_$ts"
New-Item -ItemType Directory -Path $workDir -Force | Out-Null
Write-Output "Artifacts will be written to: $workDir"

# Optional venv activation
if ($ActivateVenv -and (Test-Path "$VenvPath\Scripts\Activate.ps1")) {
    Write-Output "Activating virtualenv at $VenvPath"
    & "$VenvPath\Scripts\Activate.ps1"
}

# Replicate CI PYTHONPATH behavior (CI uses 'src:.')
if ($IsWindows) {
    $Env:PYTHONPATH = 'src;.'
} else {
    $Env:PYTHONPATH = 'src:.'
}
Write-Output "Using PYTHONPATH=$Env:PYTHONPATH"

# Run ruff
Write-Output "Running ruff..."
$ruffOut = Join-Path $workDir 'ruff_out.txt'
ruff check src tests --format=quiet *>&1 | Tee-Object -FilePath $ruffOut

# Run mypy
Write-Output "Running mypy..."
$mypyOut = Join-Path $workDir 'mypy_out.txt'
mypy src --exclude "src/blender_mcp/archive/.*" *>&1 | Tee-Object -FilePath $mypyOut

# Run pytest (capture stdout and junit xml)
Write-Output "Running pytest..."
$pytestOut = Join-Path $workDir 'pytest_out.txt'
$pytestXml = Join-Path $workDir 'pytest-report.xml'
pytest -q --junitxml=$pytestXml *>&1 | Tee-Object -FilePath $pytestOut

# Optionally capture pip freeze
if ($IncludePipFreeze) {
    Write-Output "Capturing pip freeze..."
    $freezeOut = Join-Path $workDir 'pip_freeze.txt'
    pip freeze *>&1 | Tee-Object -FilePath $freezeOut
}

# Create a zip
$zipPath = Join-Path $OutputDir "ci_compare_$ts.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path $workDir -DestinationPath $zipPath

Write-Output "Artifacts archived to: $zipPath"
Write-Output "Next steps:"
Write-Output " - Download CI logs from GitHub Actions for the relevant run (ruff/mypy/pytest job logs)."
Write-Output " - Place CI logs into a folder and diff with the files in the archive."
Write-Output " - For cross-OS parity, consider running tests inside WSL or a Linux container to replicate CI's 'src:.' PYTHONPATH behaviour."

exit 0
