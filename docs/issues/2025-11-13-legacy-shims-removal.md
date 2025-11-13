# Issue Proposal: Retrait des shims legacy (N+2)

## Résumé
Planifier et exécuter le retrait des modules shim legacy après deux cycles de release, suivant l’ajout de DeprecationWarning à l’import (2025-11-13).

## Contexte
Voir la spec OpenSpec: `openspec/changes/2025-11-13-deprecations-legacy-shims/spec.md`.
Les shims concernés émettent désormais un avertissement de dépréciation mais restent fonctionnels.

## Portée
Modules à retirer au cycle N+2:
- `src/blender_mcp/simple_dispatcher.py`
- `src/blender_mcp/command_dispatcher.py`
- `src/blender_mcp/server_shim.py`
- `src/blender_mcp/server.py` (façade)
- `src/blender_mcp/connection_core.py`
- `blender_mcp/server.py` (shim racine)

## Plan
1. Cycle N/N+1: conserver les shims avec DeprecationWarning; documenter et tracer usages.
2. Cycle N+2: supprimer les fichiers listés; mettre à jour les imports dans tests et docs.
3. Vérifier CI: lint, mypy, pytest verts.

## Critères d’acceptation
- Tous les imports legacy supprimés du code et des tests.
- CI verte en 3.11/3.12.
- `CHANGELOG.md` mentionne la suppression et les chemins de migration.
- `docs/developer/ai_session_guide.md` mis à jour (section dépréciation).

## Risques
- Tests ou scripts externes qui consomment les chemins legacy.
  - Mitigation: communiquer en amont via CHANGELOG et PR, fournir mapping des chemins.

## Commandes utiles
```powershell
$Env:PYTHONPATH='src'
ruff check src tests
mypy src --exclude "src/blender_mcp/archive/.*"
pytest -q
Remove-Item Env:PYTHONPATH
```

## Liens
- Spec: `openspec/changes/2025-11-13-deprecations-legacy-shims/spec.md`
- Journal: `docs/PROJECT_JOURNAL.md` (entrée 2025-11-13)
