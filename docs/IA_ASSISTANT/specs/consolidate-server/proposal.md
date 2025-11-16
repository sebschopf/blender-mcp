# OpenSpec Change: consolidate-server

Titre: Consolider serveur sous `src/blender_mcp` et clarifier shims

Auteur: <à remplir>
Date: <YYYY-MM-DD>

## Contexte
Actuellement le projet contient plusieurs points d'entrée et shims liés au serveur (`blender_mcp/server.py` au root, `src/blender_mcp/server.py`, `src/blender_mcp/servers/*`). Ceci provoque de l'ambiguïté lors des imports et des runs locaux.

## Proposition
1. Désigner `src/blender_mcp/server.py` comme code d'autorité pour le server.
2. Convertir le shim racine `blender_mcp/server.py` en un module de compatibilité léger qui délègue paresseusement vers `src` si disponible.
3. Documenter le changement et proposer une fenêtre de compatibilité de N jours avant suppression du shim racine.

## Impact
- Risque de breaking change pour les consommateurs qui importent `blender_mcp.server` depuis la racine.
- Tests et scripts devront utiliser `PYTHONPATH=src`.

## Rollback
Revenir à l'état actuel: rétablir `blender_mcp/server.py` original depuis la branche `backup/baseline-...`.

## Scénarios d'acceptation
- `pytest` passe localement
- `ruff`/`mypy` passent
- Les imports historiques restent compatibles via shim

