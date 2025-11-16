# 0002 - Addon preference: allow_ui_start_server

Résumé
------
Ajoute une préférence d'add-on pour contrôler si l'UI peut démarrer un serveur MCP externe.

Motivation
----------
Actuellement, le panneau UI expose un bouton "Connect to MCP server" qui peut lancer un processus externe via l'adapter embarqué. Pour des raisons de sécurité et de contrôle utilisateur (notamment dans des environnements multi-utilisateurs ou CI/téléassistance), nous voulons rendre ce comportement désactivable depuis les Préférences de l'add-on.

Comportement
-----------
- Nouvelle préférence booléenne `allow_ui_start_server` (par défaut: true).
- L'opérateur `BLENDERMCP_OT_StartServer` vérifie cette préférence avant de lancer l'adapter. S'il est `False`, l'opérateur renvoie `CANCELLED` et enregistre un message d'erreur.

Fichiers modifiés
-----------------
- `src/blender_mcp/blender_ui.py` : nouvelle classe `BLENDERMCP_AddonPreferences`, enregistrement, lecture dans l'opérateur Start.

Tests
-----
- `tests/test_addon_prefs.py` : test unitaire vérifiant que l'opérateur `BLENDERMCP_OT_StartServer` respecte la préférence (autorisé / interdit).

Migration & validation OpenSpec
------------------------------
- Ce changement est non-breaking pour l'API publique des services; c'est une amélioration UX/API d'addon.
- Ajoutez ce dossier `openspec/changes/0002-addon-preferences` à la PR et exécutez :

```
# depuis la racine du repo
openspec validate --strict
```

Notes
-----
- L'implémentation défensive permet d'importer le module hors de Blender (tests) même si `bpy.types.AddonPreferences` n'est pas disponible.
- Aucun comportement serveur additionnel n'est introduit.
