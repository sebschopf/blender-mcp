# Extract the last Gemini execute_blender_code suggestion from ../log.txt
# Then prompt the user: "Envoyer la requete a blender ? (y/n)" and POST it to the ASGI endpoint if confirmed.

$logPath = Join-Path $PSScriptRoot "..\log.txt"
if (-not (Test-Path $logPath)) {
    Write-Error "Log file not found at $logPath. Please provide a file containing the Gemini suggestion or run this script from the repo/scripts folder."
    exit 1
}

$raw = Get-Content -Raw -Path $logPath -ErrorAction Stop

# Try to find the last occurrence of: Gemini suggested: execute_blender_code {'code': '...'}
$pattern = "Gemini suggested:\s*execute_blender_code\s*\{\s*'code'\s*:\s*'(?<code>.*?)'\s*\}" 
$match = [regex]::Matches($raw, $pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline) | Select-Object -Last 1

if ($null -eq $match) {
    Write-Host "Aucune suggestion 'execute_blender_code' trouvée dans $logPath." -ForegroundColor Yellow
    $file = Read-Host "Si vous avez un fichier contenant le code Python à envoyer, entrez son chemin (ou appuyez sur Entrée pour quitter)"
    if (-not $file) { exit 0 }
    if (-not (Test-Path $file)) { Write-Error "Fichier introuvable: $file"; exit 1 }
    $code = Get-Content -Raw -Path $file -ErrorAction Stop
} else {
    $codeEscaped = $match.Groups['code'].Value
    # Unescape common escape sequences coming from the log: \n, \' etc.
    $code = $codeEscaped -replace "\\n", "`n" -replace "\\r", "`r" -replace "\\t", "`t" -replace "\\'", "'" -replace '\\"', '"'
}

Write-Host "--- Extrait code (premières 400 caractères) ---" -ForegroundColor Cyan
Write-Host ($code.Substring(0, [Math]::Min(400, $code.Length)))
if ($code.Length -gt 400) { Write-Host "... (truncated)" }

$answer = Read-Host "Envoyer la requête à Blender ? (y/n)"
if ($answer.ToLower() -ne 'y') { Write-Host "Annulé par l'utilisateur." -ForegroundColor Yellow; exit 0 }

# Build payload and send
$payload = @{ params = @{ code = $code } } | ConvertTo-Json -Depth 10
$uri = 'http://127.0.0.1:8000/tools/execute_blender_code'

Write-Host "Envoi vers $uri ..." -ForegroundColor Green
try {
    $resp = Invoke-RestMethod -Uri $uri -Method Post -Body $payload -ContentType 'application/json' -ErrorAction Stop
    Write-Host "Réponse reçue:" -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 6 | Write-Host
} catch {
    Write-Error "Erreur lors de l'envoi: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        try { $_.Exception.Response.GetResponseStream() | Get-Content -Raw | Write-Host } catch { }
    }
    exit 1
}

Write-Host "Terminé." -ForegroundColor Green
