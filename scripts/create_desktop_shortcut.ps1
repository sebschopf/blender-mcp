<#
Create a Desktop shortcut (.lnk) and a .bat launcher that execute
`scripts/desktop_start.ps1` with PowerShell. This avoids the "Open with" dialog
when double-clicking the .ps1 file.

Run this script once from PowerShell (recommended):

pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\create_desktop_shortcut.ps1

It will create two files on your Desktop:
- "Blender MCP.lnk" → starts PowerShell with the proper args and keeps the window open
- "Start Blender MCP.bat" → Windows double-clickable batch file that launches the same command

If you prefer, you can manually create the shortcut instead of running this script.
#>

$ErrorActionPreference = 'Stop'

$scriptPath = $MyInvocation.MyCommand.Path
# projectRoot should be the repository root (parent of the scripts folder)
$projectRoot = Split-Path -Parent $scriptPath
$projectRoot = Split-Path -Parent $projectRoot

Write-Host "Project root: $projectRoot"

$desktop = [Environment]::GetFolderPath('Desktop')

# Target command: PowerShell executable
$pwshPath = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
if (-not (Test-Path $pwshPath)) {
    # fallback to pwsh if available
    $pwshCmd = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($pwshCmd) { $pwshPath = $pwshCmd.Source }
}

if (-not (Test-Path $pwshPath)) {
    Write-Error "Could not find PowerShell executable (pwsh or powershell.exe). Aborting."
    exit 1
}

$targetScript = Join-Path $projectRoot 'scripts\desktop_start.ps1'
if (-not (Test-Path $targetScript)) {
    Write-Host "Expected $targetScript to exist. Make sure you have scripts/desktop_start.ps1 in the repo." -ForegroundColor Red
    exit 1
}

$arguments = "-ExecutionPolicy Bypass -NoProfile -NoExit -File `"$targetScript`""

Write-Host "Creating shortcut on Desktop: $desktop"

try {
    $wsh = New-Object -ComObject WScript.Shell
    $lnkPath = Join-Path $desktop 'Blender MCP.lnk'
    $shortcut = $wsh.CreateShortcut($lnkPath)
    $shortcut.TargetPath = $pwshPath
    $shortcut.Arguments = $arguments
    $shortcut.WorkingDirectory = $projectRoot
    # Optionally use a repo icon if present
    $iconCandidate = Join-Path $projectRoot 'assets\icon.ico'
    if (Test-Path $iconCandidate) { $shortcut.IconLocation = $iconCandidate }
    $shortcut.Save()
    Write-Host "Created shortcut: $lnkPath"
} catch {
    Write-Warning "Could not create .lnk shortcut: $_"
}

# Also create a .bat launcher as a fallback (double-clickable)
try {
    $batPath = Join-Path $desktop 'Start Blender MCP.bat'
    $batContent = @(
        "@echo off",
        "REM Launcher for Blender MCP",
        ""
        """$pwshPath"" -ExecutionPolicy Bypass -NoProfile -NoExit -File ""$targetScript"""
    ) -join "`r`n"
    Set-Content -Path $batPath -Value $batContent -Encoding ASCII
    Write-Host "Created batch launcher: $batPath"
} catch {
    Write-Warning "Could not create .bat file: $_"
}

    # Optionally set a sensible default model name for Gemini API in the user's environment
    $existingModel = [Environment]::GetEnvironmentVariable('GEMINI_MODEL','User')
    if (-not $existingModel) {
        try {
            [Environment]::SetEnvironmentVariable('GEMINI_MODEL','gemini-2.5-flash','User')
            Write-Host "Set user environment variable GEMINI_MODEL=gemini-2.5-flash"
        } catch {
            Write-Warning "Could not set GEMINI_MODEL environment variable: $_"
        }
    } else {
        Write-Host "GEMINI_MODEL already set for user: $existingModel (left unchanged)"
    }

    Write-Host "Done. Double-click the shortcut or the .bat on your Desktop to start the MCP stack." -ForegroundColor Green
