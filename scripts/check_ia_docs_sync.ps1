<#
Check IA docs synchronization script

Usage:
  .\scripts\check_ia_docs_sync.ps1 -BaseRef 'origin/main' -HeadRef 'HEAD'

This script fails (exit code 1) when code or tests touching services/endpoints
are modified in the diff between BaseRef..HeadRef but no files under
`docs/IA_ASSISTANT/` are updated. It emits both a human-friendly message and
a machine-readable JSON blob at `artifacts/ia_docs_sync.json` when failing.
#>

param(
    [string]$BaseRef = 'origin/main',
    [string]$HeadRef = 'HEAD',
    [string]$OutputDir = 'artifacts'
)

function Write-JsonToFile($obj, $path) {
    $json = $obj | ConvertTo-Json -Depth 6
    $dir = Split-Path $path -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $json | Out-File -FilePath $path -Encoding utf8
}

# Ensure we have the refs available (best-effort)
try {
    & git fetch origin $BaseRef --depth=1 2>$null | Out-Null
} catch {
    # ignore fetch errors; git diff may still work in some CI contexts
}

$diffFiles = & git diff --name-only $BaseRef..$HeadRef
if ($LASTEXITCODE -ne 0) {
    Write-Output "Failed to run git diff between $BaseRef and $HeadRef";
    exit 2
}

$changed = $diffFiles -split "\r?\n" | Where-Object { $_ -ne '' }

# Patterns we consider important to document
$importantPatterns = @(
    '^src/blender_mcp/services/',
    '^src/blender_mcp/endpoints.py$',
    '^src/blender_mcp/asgi.py$',
    '^src/blender_mcp/dispatchers/',
    '^tests/'
)

$iaDocsPrefix = 'docs/IA_ASSISTANT/'

$importantChanged = @()
foreach ($f in $changed) {
    foreach ($p in $importantPatterns) {
        if ($f -match $p) { $importantChanged += $f; break }
    }
}

$iaDocsChanged = $changed | Where-Object { $_ -like "$iaDocsPrefix*" }

if ($importantChanged.Count -gt 0 -and $iaDocsChanged.Count -eq 0) {
    $msg = @()
    $msg += "IA Docs Sync Check: MISSING documentation updates"
    $msg += "Found important changed files that should be reflected under docs/IA_ASSISTANT/:"
    foreach ($c in $importantChanged) { $msg += " - $c" }
    $msg += "No files under 'docs/IA_ASSISTANT/' were modified in this diff."
    $msg += "Action: Update one or more of: services_index.yaml, services_metadata.yaml, endpoints.yaml, tests_index.yaml, pr_template_for_ai.md"
    $msg += "Suggestion: include an explicit note in the PR body indicating which IA file(s) were updated."

    $human = $msg -join "`n"
    Write-Output $human

    $out = [PSCustomObject]@{
        status = 'fail'
        reason = 'important_changes_without_ia_docs_update'
        important_changed = $importantChanged
        ia_docs_changed = @()
        suggestions = @("Update docs/IA_ASSISTANT/services_index.yaml","Update docs/IA_ASSISTANT/services_metadata.yaml","Update docs/IA_ASSISTANT/endpoints.yaml","Update docs/IA_ASSISTANT/tests_index.yaml")
    }

    if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }
    $artifactPath = Join-Path $OutputDir 'ia_docs_sync.json'
    Write-JsonToFile $out $artifactPath
    Write-Output "Wrote machine-readable report to: $artifactPath"

    # Attempt to run content validator (if Python and validator script available)
    if (Test-Path './scripts/validate_ia_yaml.py') {
        Write-Output "Running IA YAML validator..."
        $py = Get-Command python -ErrorAction SilentlyContinue
        if (-not $py) { Write-Output "python not found in PATH; skipping content validation."; exit 1 }
        $ret = & python ./scripts/validate_ia_yaml.py
        if ($LASTEXITCODE -ne 0) {
            Write-Output "Content validation failed (see output above)."
            exit 1
        }
    }

    exit 1
} else {
    Write-Output "IA Docs Sync Check: OK"
    $out = [PSCustomObject]@{
        status = 'ok'
        important_changed = $importantChanged
        ia_docs_changed = $iaDocsChanged
    }
    $artifactPath = Join-Path $OutputDir 'ia_docs_sync.json'
    Write-JsonToFile $out $artifactPath
    # Also run content validator if available; fail if validation fails
    if (Test-Path './scripts/validate_ia_yaml.py') {
        Write-Output "Running IA YAML validator..."
        $py = Get-Command python -ErrorAction SilentlyContinue
        if (-not $py) { Write-Output "python not found in PATH; skipping content validation."; exit 2 }
        & python ./scripts/validate_ia_yaml.py
        if ($LASTEXITCODE -ne 0) {
            Write-Output "IA YAML validation failed. See validator output above.";
            exit 1
        }
    }
    exit 0
}
