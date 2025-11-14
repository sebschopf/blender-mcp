## Retrait façades dispatcher (simple_dispatcher.py, command_dispatcher.py)

Objectif: supprimer les ré-export legacy pour centraliser sur `dispatchers/`.

Contexte:
- Fichiers: `src/blender_mcp/simple_dispatcher.py`, `src/blender_mcp/command_dispatcher.py`.
- DeprecationWarning à l'import.
- Aucune logique métier; pure compat.

Checklist:
- [ ] Grep usages internes et remplacer par imports directs (`from blender_mcp.dispatchers import Dispatcher`).
- [ ] Adapter/retirer tests warnings si présents.
- [ ] Mise à jour CHANGELOG (déjà section Deprecation & Planned Removals).
- [ ] Script parité CI OK après suppression.
- [ ] Mettre à jour `LEGACY_TRACKER.md` + Journal.

Critères d'acceptation:
- Plus aucun import des deux façades dans code actif/tests.
- CI verte (ruff, mypy, pytest).
