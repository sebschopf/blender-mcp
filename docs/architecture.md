# Architecture canonique de blender-mcp

Ce document décrit l'architecture canonique proposée pour le projet.
L'objectif est de séparer clairement le code qui dépend de Blender (API `bpy`) du code métier testable hors Blender, d'avoir des contrats de service stables et des conventions d'import claires afin de faciliter la maintenance et les migrations.

## Principes

- Service-facing vs Addon (Blender-side)
  - services/* : modules canoniques orientés service (API interne). Ils valident les paramètres d'entrée, délèguent aux implémentations Blender si nécessaire, et normalisent les réponses dans des schémas JSON-like.
  - services/addon/* : implémentations Blender-only. Ces modules peuvent importer `bpy` (lazy import) et effectuer les opérations réelles dans Blender. Ils doivent rester simples et réutilisables.

- Lazy import de `bpy` : tout import de `bpy` doit être fait à l'intérieur de fonctions (lazy) afin que l'importation statique du package ne nécessite pas Blender. Cela permet d'exécuter les tests et d'analyser le code hors Blender.

- Façade de compatibilité : `blender_mcp/addon_handlers.py` continue d'exposer l'API publique historique mais délègue vers `services.addon`. Cela permet une migration progressive.

- TypedDicts et schéma de réponse : définir des types partagés (`services/types.py`) pour standardiser les réponses des services et améliorer le typage mypy.

## Packages / arborescence canonique proposée

- `src/blender_mcp/services/`
  - Modules service-facing (ex: `scene.py`, `object.py`, `screenshot.py`, `textures.py`, `polyhaven.py`, `execute.py`, `model.py`...)
  - Ils n'importent pas `bpy` au niveau module.

- `src/blender_mcp/services/addon/`
  - Implémentations Blender-side (ex: `scene.py`, `objects.py`, `screenshots.py`, `textures.py`, `polyhaven.py`, `execution.py`, `constants.py`).
  - Ces fonctions importent `bpy` à l'intérieur d'appels et renvoient des dicts riches ou `{"error": ...}` en cas de problème.

- `src/blender_mcp/services/servers/`
  - Code serveur / transport qui orchestre la réception des messages (sockets / ASGI wrappers / dispatch). Aucun `bpy` ici. Doit appeler les services canoniques.

- `src/blender_mcp/services/templates/`
  - Générateurs de templates, matériaux, spécifications de nœuds (`materials.py`, `node_helpers.py`). Ce code est purement logique et testable hors Blender.

- `src/blender_mcp/services/types.py`
  - TypedDicts et types partagés (GenericResponse, SceneResponse, ObjectResponse, MaterialSpec, etc.).

- `src/blender_mcp/addon_handlers.py`
  - Façade de compatibilité qui ré-exporte des helpers de `services.addon`.

## Contrats de service (exemples)

- Convention générale : chaque service retourne un dictionnaire JSON-serializable avec au moins une clé `status` valant `"success"` ou `"error"`.

Success example:

```json
{"status": "success", "result": {...}}
```

Error example:

```json
{"status": "error", "message": "Blender (bpy) not available"}
```

- Les services peuvent exposer plus de champs (e.g. `scene_name`, `objects`), mais la présence de `status` est requise pour standardiser le parsing côté client.

## Conventions d'import

- Les services doivent importer leurs implémentations addon via import relatif :

```py
from .addon import scene as addon_scene
```

- Le code qui ne dépend pas de Blender (tests, runners, CI) importe uniquement les modules `services.*`.

## Tests

- Ecrire des tests unitaires pour chaque service qui couvrent :
  - comportement quand `bpy` est absent (monkeypatch `sys.modules['bpy']`),
  - comportement quand `bpy` retourne un résultat valide (fake minimal),
  - validation des paramètres erronés.

- Ajouter des tests d'intégration simulés qui montent un dispatcher/connection factice et vérifient l'appel bout-à-bout.

## Migration & checklist

1. Ajouter `services/types.py` et `services/addon/` package.
2. Déplacer les implémentations Blender existantes sous `services/addon/`.
3. Pour chaque service, créer le wrapper service-facing qui appelle `services.addon`.
4. Mettre à jour `addon_handlers.py` pour ré-exporter les symboles publics.
5. Lancer ruff/mypy/pytest et corriger.
6. Mettre à jour documentation et créer PRs atomiques.

## Commandes utiles

```powershell
# tests
python -m pytest -q
# linter
ruff check src
# typage
mypy --show-error-codes src
# format
black --line-length 88 src
```

## Règles de sécurité

- Ne jamais exécuter du code arbitraire renvoyé par un tiers sans sandboxing.
- Préférer des appels paramétrés (create_model(params)) plutôt que l'exécution de scripts texte.

----