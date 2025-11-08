<#
Launcher script to start the Blender MCP stack from a single click.

What it does:
- activates the project's venv if present
- starts the MCP server in background (via start-server.ps1)
- opens a visible PowerShell window running uvicorn (ASGI adapter)
- opens a visible PowerShell window running the interactive Gemini bridge

Usage:
- Create a Windows shortcut on your Desktop that runs PowerShell with this file, for example:
  Target: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
  Arguments: -NoExit -File "C:\Users\sebas\Documents\MCP_Outils\blender-mcp\scripts\desktop_start.ps1"

Notes:
- This script assumes the repo layout hasn't changed and that `venv` is at the project root.
- Keep Blender running and the addon enabled before using the bridge.
#>

$ErrorActionPreference = 'Stop'

$scriptPath = $MyInvocation.MyCommand.Path
# projectRoot should be repository root (parent of scripts)
$projectRoot = Split-Path -Parent $scriptPath
$projectRoot = Split-Path -Parent $projectRoot

Write-Host "Project root:" $projectRoot

# Activate venv if found
$venvActivate = Join-Path $projectRoot 'venv\Scripts\Activate.ps1'
if (Test-Path $venvActivate) {
    Write-Host "Activating venv..."
    & $venvActivate
} else {
  # Avoid non-ASCII em-dash and long interpolated string which can confuse some PowerShell parsers.
  Write-Host "No venv activation script found at" $venvActivate -ForegroundColor Yellow
  Write-Host "Continuing without venv." -ForegroundColor Yellow
}

Write-Host "Starting MCP server (detached)..."
# use the existing start-server.ps1 which detaches blender-mcp
$pwshPath = (Get-Command pwsh).Source
$startServerPath = Join-Path $projectRoot 'start-server.ps1'
Start-Process -FilePath $pwshPath -ArgumentList "-NoProfile","-WindowStyle","Hidden","-File",$startServerPath

Start-Sleep -Seconds 1

Write-Host "Starting uvicorn adapter in a new window..."
$uvicornScript = Join-Path $projectRoot 'scripts\uvicorn_start.ps1'
Start-Process -FilePath $pwshPath -ArgumentList "-NoProfile","-NoExit","-File",$uvicornScript -WindowStyle Normal

Start-Sleep -Seconds 1

Write-Host "Starting interactive Gemini bridge in a new window..."
$bridgeScript = Join-Path $projectRoot 'scripts\run_gemini_bridge.ps1'
Start-Process -FilePath $pwshPath -ArgumentList "-NoProfile","-NoExit","-File",$bridgeScript -WindowStyle Normal

Write-Host "All windows started." -ForegroundColor Green
Write-Host "If Blender is running with the addon enabled, you can now type requests in the Gemini bridge window." -ForegroundColor Green
