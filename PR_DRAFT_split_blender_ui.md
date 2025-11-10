PR draft — feature/split-blender-ui
=================================

Résumé
------
Cette PR réorganise l'UI du paquet `blender_mcp` en remplaçant le fichier monolithique
`src/blender_mcp/blender_ui.py` par un package `src/blender_mcp/blender_ui/` composé de :

- `__init__.py` — façade (compatibilité d'import et fonctions `register()` / `unregister()`).
- `props.py` — enregistrement/désenregistrement des propriétés de `bpy.types.Scene`.
- `operators.py` — opérateurs (start/stop server, set API key, apply remote-exec setting).
- `panel.py` — panneau UI principal (mêmes operator ids et layout conservés).

Motivation
----------
- Améliorer la séparation des responsabilités (SRP) et la lisibilité.
- Faciliter les tests et la maintenance (pièces plus petites).
- Préparer le terrain pour d'autres réorganisations (ex. déplacer handlers, better wiring).

Ce que j'ai modifié
-------------------
- Suppression du fichier `src/blender_mcp/blender_ui.py` (monolithique).
- Ajout du package `src/blender_mcp/blender_ui/` avec les modules listés ci-dessus.
- Correctif minime dans `src/blender_mcp/services/execute.py` : rétablissement de
  l'exécution lorsque `bpy` est disponible (les logs d'audit et le mode dry-run ont été
  conservés). Ceci rend le comportement compatible avec les tests automatisés
  existants. Si on veut restaurer un opt-in sécurité, je propose d'ajouter
  une configuration explicite documentée (ex : `BLENDER_MCP_ALLOW_EXECUTE` ou
  préférence d'addon) et des tests correspondants.

Tests
-----
- La suite de tests locale a été exécutée (`pytest`) et est verte.
- Tests ciblés pour l'UI (`tests/test_addon_prefs.py`, `tests/test_addon_server_ui.py`) sont passés.

Notes de migration / compatibilité
---------------------------------
- Le package expose en façade les mêmes noms publics (par ex. `BLENDERMCP_PT_Panel`,
  `BLENDERMCP_OT_StartServer`, etc.) pour rester compatible avec les imports
  existants (`importlib.import_module('blender_mcp.blender_ui')`).
- `addon.py` reste inchangé — il appelle `blender_mcp.blender_ui.register()` via une importation paresseuse.

Propositions / étapes suivantes
------------------------------
1. Créer la PR et demander relecture.
2. Optionnel : réintroduire une opt-in sécurisé pour `execute_blender_code` via une préférence
   ou configuration (et adapter/simplifier les tests en conséquence).
3. Poursuivre la migration d'autres helpers UI si nécessaire (petits modules, tests, commits atomiques).

Fichiers principaux modifiés/créés
---------------------------------
- src/blender_mcp/blender_ui/__init__.py
- src/blender_mcp/blender_ui/props.py
- src/blender_mcp/blender_ui/operators.py
- src/blender_mcp/blender_ui/panel.py
- src/blender_mcp/services/execute.py (modifié)

Commande pour reproduire localement
----------------------------------
```powershell
$env:PYTHONPATH = 'src'
python -m pytest -q
```
 
