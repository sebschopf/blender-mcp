<#
Prompt the user for the GEMINI API key securely and optionally save it as a User environment variable.

Usage:
  pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\set_gemini_key.ps1

This script reads a secure string (masked input) and, if the user agrees,
stores it in the User environment so shortcuts and new shells can access it.

Security note: Storing an API key in a User environment variable is convenient but
will make the key available to any process running as the user. Consider using
platform-specific secret storage for higher security.
#>

$ErrorActionPreference = 'Stop'

function Convert-SecureStringToPlainText([System.Security.SecureString] $secStr) {
    if (-not $secStr) { return $null }
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secStr)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    } finally {
        if ($bstr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
    }
}

Write-Host "This script will prompt you to enter your Gemini API key (input is masked)."
Write-Host "It will NOT print the key. You can choose whether to save it to your User environment."

$secure = Read-Host -Prompt 'Enter GEMINI_API_KEY' -AsSecureString
if (-not $secure) {
    Write-Host "No key entered. Aborting." -ForegroundColor Yellow
    exit 1
}

$plain = Convert-SecureStringToPlainText $secure

Write-Host "Key read. Do you want to save it as a User environment variable so new shells and shortcuts can access it? (y/N)"
$resp = Read-Host -Prompt 'Save as User environment variable?'
if ($resp -match '^[Yy]') {
    try {
        [Environment]::SetEnvironmentVariable('GEMINI_API_KEY',$plain,'User')
        Write-Host "Saved GEMINI_API_KEY as a User environment variable. Restart your terminals or log out/in for it to take effect." -ForegroundColor Green
    } catch {
        Write-Warning "Could not set environment variable: $_"
    }
} else {
    Write-Host "Key not saved. It is available for this session only (export below)." -ForegroundColor Yellow
    Write-Host "To set it for the current session use (PowerShell):`n`$env:GEMINI_API_KEY = 'your_key_here'"
}

Write-Host "Done. Keep your key secret. If you want to remove it later, run:`n[Environment]::SetEnvironmentVariable('GEMINI_API_KEY',$null,'User')" -ForegroundColor Cyan
