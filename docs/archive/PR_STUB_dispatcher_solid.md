Refactor(dispatcher): rendre le dispatcher plus SOLID (itérations 1–3)
===============================================================

Résumé
------
Cette PR regroupe trois petites itérations visant à améliorer l'adhérence
aux principes SOLID sans changer l'API publique :

1. Extraction d'une interface (ABC) `AbstractDispatcher` pour définir le
   contrat minimal (register/unregister/list_handlers/dispatch).
2. Extraction d'un `CommandAdapter` responsable de la normalisation des
   `dispatch_command` (response shaping) pour alléger les responsabilités
   de `Dispatcher`.
3. Injection de dépendances (DI) :
   - `Dispatcher` accepte une factory `executor_factory` pour le
     `dispatch_with_timeout` (testabilité)
   - ajout de `BridgeService` pour encapsuler le flow Gemini→outil et
     permettre l'injection des callables externes (gemini/mcp)

Motivation
----------
- Réduire les responsabilités de `Dispatcher` (SRP).
- Permettre l'injection de dépendances externes pour tests et politiques (DIP).
- Préparer un futur découpage (policy layer, suppression contrôlée des shims).

Fichiers principaux modifiés/ajoutés
-----------------------------------
- `src/blender_mcp/dispatchers/abc.py` — nouvelle ABC `AbstractDispatcher`.
- `src/blender_mcp/dispatchers/command_adapter.py` — `CommandAdapter` extrait.
- `src/blender_mcp/dispatchers/bridge.py` — `BridgeService` injectable.
- `src/blender_mcp/dispatchers/dispatcher.py` — `Dispatcher` hérite de l'ABC,
  délègue `dispatch_command` au `CommandAdapter` et accepte `executor_factory`.
- `tests/test_dispatcher_interface.py`, `tests/test_command_adapter.py` — nouveaux tests.

Validation locale
-----------------
- Tests ciblés exécutés localement:
  - `tests/test_dispatcher_interface.py` ✓
  - `tests/test_command_adapter.py` ✓
  - `tests/test_dispatcher_run_bridge.py` ✓
- Linter (`ruff`) exécuté et corrections appliquées ✓
- Type checking (`mypy -p blender_mcp`) ✓

Checklist (PR)
--------------
- [ ] Les tests complets passent sur CI (GitHub Actions)
- [ ] Relire les exports publics et confirmer qu'aucune API breaking n'est
      introduite sans OpenSpec (si breaking, créer `openspec/changes/<id>/`)
- [ ] Ajouter une note dans `docs/` sur les points d'extension (BridgeService,
      CommandAdapter) pour les contributeurs ultérieurs

Notes
-----
Cette PR est volontairement conservative : le comportement visible
ne change pas (les shims et noms historiques restent disponibles).
Les prochaines itérations proposeront : wiring de la couche policy dans
`CommandAdapter`, et réduction progressive des shims avec une OpenSpec si
nécessaire.
