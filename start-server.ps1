#!/usr/bin/env pwsh
<#
Start script for BlenderMCP. It activates the local venv (if found)
and launches the `blender-mcp` entry point in a background PowerShell process.

Usage: Right-click -> Run with PowerShell, or place a shortcut to this script in the Startup folder.
#>

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvActivate = Join-Path $projectRoot 'venv\Scripts\Activate.ps1'

if (Test-Path $venvActivate) {
    # Source the venv activation script in the current session
    & $venvActivate
} else {
    Write-Host "No venv detected at $venvActivate — make sure your virtualenv is activated if needed." -ForegroundColor Yellow
}

# Launch the server in a detached PowerShell process and redirect output to a log file
$logFile = Join-Path $projectRoot 'blender-mcp.log'
$psArgs = "-NoProfile -WindowStyle Hidden -Command & { cd '$projectRoot'; blender-mcp *>&1 | Out-File -FilePath '$logFile' -Encoding utf8 }"

Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList $psArgs -WindowStyle Hidden

Write-Host "BlenderMCP démarré en arrière-plan. Voir le fichier de log: $logFile"
