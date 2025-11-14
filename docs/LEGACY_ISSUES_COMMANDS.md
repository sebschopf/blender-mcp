# Commandes `gh` pour création des issues legacy

Utiliser `gh issue create` après authentification (`gh auth login`). Adapter les descriptions si besoin.

```powershell
# 1 Dispatcher shims
gh issue create --title "Retrait façades dispatcher (simple_dispatcher.py, command_dispatcher.py)" `
  --body-file docs/ISSUES_LEGACY_DRAFTS.md `
  --label "legacy-removal,deprecation,phase2" --label connection

# 2 Root services
gh issue create --title "Retrait services racine (polyhaven/sketchfab/hyper3d)" `
  --body-file docs/ISSUES_LEGACY_DRAFTS.md `
  --label "legacy-removal,deprecation,phase2" --label services

# 3 Materials facade
gh issue create --title "Retrait façade materials.py" `
  --body-file docs/ISSUES_LEGACY_DRAFTS.md `
  --label "legacy-removal,deprecation,phase2"

# 4 Blender codegen facade
gh issue create --title "Retrait façade blender_codegen.py" `
  --body-file docs/ISSUES_LEGACY_DRAFTS.md `
  --label "legacy-removal,deprecation,phase2"

# 5 Root server shim
gh issue create --title "Retrait shim serveur racine" `
  --body-file docs/ISSUES_LEGACY_DRAFTS.md `
  --label "legacy-removal,deprecation,phase2" --label connection

# 6 Connection core removal audit
gh issue create --title "Audit final & retrait connection_core.py" `
  --body-file docs/ISSUES_LEGACY_DRAFTS.md `
  --label "legacy-removal,deprecation,phase2" --label connection
```

Note: `--body-file` injecte tout le contenu; pour un corps spécifique, créer des fichiers extraits ou utiliser un heredoc (`--body "..."`).

Astuce: Pour consigner les numéros une fois créés, mettre à jour `docs/LEGACY_WITHDRAWAL_PLAN.md` (tableau synthèse).
