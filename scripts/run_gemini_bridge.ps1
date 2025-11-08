<#
Interactive wrapper to run the gemini_bridge.
It asks for your Gemini API key (session-only), lets you choose the gemini-cli command, then prompts for a user request and calls the Python bridge.

Usage:
  Right from PowerShell in the repo root:
    & .\scripts\run_gemini_bridge.ps1

This script does NOT persist your key to disk. It only sets it for the current session.
#>

Param()

Write-Host "=== Gemini -> MCP bridge runner ===`n"

$key = Read-Host -Prompt "Entrez votre clé Gemini (sera utilisée pour cette session)" -AsSecureString
# Convert secure string to plain text for gemini-cli usage
$ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($key)
$plainKey = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)

$env:GEMINI_API_KEY = $plainKey

Write-Host "Clé Gemini définie pour la session.`n"

$defaultCmd = "gemini chat --model=gemini-pro --api-key $env:GEMINI_API_KEY"
Write-Host "Commande gemini par défaut : $defaultCmd"
$cmdInput = Read-Host -Prompt "(optionnel) Modifier la commande gemini (laisser vide pour défaut)"
if (![string]::IsNullOrWhiteSpace($cmdInput)) {
    $env:GEMINI_CMD = $cmdInput
} else {
    $env:GEMINI_CMD = $defaultCmd
}

Write-Host "MCP endpoint (par défaut http://127.0.0.1:8000)"
$mcpBase = Read-Host -Prompt "Entrer MCP_BASE ou laisser vide" -ErrorAction SilentlyContinue
if (![string]::IsNullOrWhiteSpace($mcpBase)) { $env:MCP_BASE = $mcpBase }

# Ask for session defaults: verbose, save .blend, engraving mode, photoreal
$bridgeFlags = @()
$v = Read-Host -Prompt "Afficher le code généré (verbose)? (y/N)"
if ($v -match '^[Yy]') { $bridgeFlags += '--verbose' }
$s = Read-Host -Prompt "Sauvegarder automatiquement le .blend dans ./output ? (y/N)"
if ($s -match '^[Yy]') { $bridgeFlags += '--save' }
$p = Read-Host -Prompt "Mode photoréal (améliore matériaux/bevels)? (y/N)"
if ($p -match '^[Yy]') { $bridgeFlags += '--photoreal' }
$engr = Read-Host -Prompt "Mode gravure par défaut (geometry / visual) [geometry]"
if (-not [string]::IsNullOrWhiteSpace($engr)) { $bridgeFlags += "--engraving=$engr" }

Write-Host "Options session pour le bridge: $($bridgeFlags -join ' ')`n"

while ($true) {
    $userReq = Read-Host -Prompt "Tapez la requête utilisateur pour Gemini (ou 'quit' pour sortir, 'help' pour tuto)"
    if ($userReq -eq 'quit') { break }
    if ($userReq -eq 'help' -or $userReq -eq '?') {
        Write-Host "`n---- Aide: commandes et exemples ----"
        Write-Host "Exemples de requêtes (français):"
        Write-Host "  fais-moi un dé à 10 faces en ruby avec marquages dorés"
        Write-Host "  crée une sphère et applique un matériau métallique"
        Write-Host "Options de session: --verbose (affiche le code), --save (sauvegarde .blend), --photoreal, --engraving=geometry|visual"
        Write-Host "Vous pouvez relancer le bridge avec d'autres options en quittant et relançant ce script."
        Write-Host "-------------------------------------`n"
        continue
    }
    Write-Host "Appel de Gemini..."
    # If a GEMINI_API_KEY is present in this session, prefer API mode unless user explicitly chose CLI.
    if ($env:GEMINI_API_KEY -and -not ($bridgeFlags -contains '--use-api')) {
        $bridgeFlags += '--use-api'
    }

    $args = $bridgeFlags + @($userReq)
    python .\scripts\gemini_bridge.py $args
    Write-Host "--- demande suivante ---`n"
}

Write-Host "Terminé. La clé reste active pour cette session PowerShell seulement."
