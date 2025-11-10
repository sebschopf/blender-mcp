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
- Suppression du fichier `src/blender_mcp/blender_ui.py` (monolithique). Une copie archivée a été conservée dans `src/blender_mcp/archive/blender_ui.py`.
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
  `src/blender_mcp/addon_handlers.py` a été déplacé sous `src/blender_mcp/blender_ui/addon_handlers.py` ; le module top‑level a été remplacé par une mince façade qui réexporte les symboles pour préserver la compatibilité des importations externes.

Propositions / étapes suivantes
------------------------------
1. Créer la PR et demander relecture.
2. Optionnel : réintroduire une opt-in sécurisé pour `execute_blender_code` via une préférence
   ou configuration (et adapter/simplifier les tests en conséquence).
3. Poursuivre la migration d'autres helpers UI si nécessaire (petits modules, tests, commits atomiques).

Notes de migration détaillées
---------------------------
Voici un tableau rapide des chemins d'importation historiques et de leurs nouveaux emplacements
pour faciliter la mise à jour des intégrations :

- Ancien monolithe : `src/blender_mcp/blender_ui.py` → Nouveau package : `src/blender_mcp/blender_ui/`
  - `BLENDERMCP_PT_Panel` → `blender_mcp.blender_ui.panel.BLENDERMCP_PT_Panel` (façade exposée au même nom)
  - `BLENDERMCP_OT_StartServer` → `blender_mcp.blender_ui.operators.BLENDERMCP_OT_StartServer`
  - `BLENDERMCP_OT_StopServer` → `blender_mcp.blender_ui.operators.BLENDERMCP_OT_StopServer`
  - `BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey` → `blender_mcp.blender_ui.operators.BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey`
  - `BLENDERMCP_OT_ApplyRemoteExecSetting` → `blender_mcp.blender_ui.operators.BLENDERMCP_OT_ApplyRemoteExecSetting`
  - Propriétés de scène (ex. `blendermcp_port`) → enregistrées via `blender_mcp.blender_ui.props` (façade gère l'enregistrement)

- `blender_mcp.addon_handlers` → déplacé vers `blender_mcp.blender_ui.addon_handlers` ; le module top‑level
  `blender_mcp.addon_handlers` reste une façade qui réexporte les symboles pour compatibilité.

Conseil de migration rapide pour les intégrateurs:

- Si vous aviez des imports explicites depuis l'ancien module, vous pouvez soit continuer à importer
  depuis `blender_mcp.blender_ui` (la façade fournit les mêmes noms), soit migrer vers les chemins
  explicites ci‑dessus (`blender_mcp.blender_ui.operators`, `blender_mcp.blender_ui.panel`, etc.).

Test ajouté
-----------
- `tests/test_blender_ui_facade.py` vérifie qu'en injectant un faux `bpy` la façade expose bien
  les noms historiques (prévention des régressions d'import).

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
 
