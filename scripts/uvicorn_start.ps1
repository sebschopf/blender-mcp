<#
Starts the uvicorn ASGI adapter from the repository root. This script is intended to be
invoked with PowerShell -File from a new window so logs remain visible.
#>

$ErrorActionPreference = 'Stop'

# Determine repo root (parent of scripts folder)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Host "Starting uvicorn from $projectRoot"
Set-Location -LiteralPath $projectRoot

# Start uvicorn (assumes uvicorn is on PATH in the active environment)
uvicorn blender_mcp.asgi:app --host 127.0.0.1 --port 8000 --reload
