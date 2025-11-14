## Retrait services racine (polyhaven/sketchfab/hyper3d)

Objectif: enlever modules racine legacy au profit des services exceptions-first.

Contexte:
- Fichiers: `src/blender_mcp/polyhaven.py`, `src/blender_mcp/sketchfab.py`, `src/blender_mcp/hyper3d.py`.
- DeprecationWarning à l'import; endpoints portés.

Checklist:
- [ ] Confirmer portage complet endpoints (voir `endpoint_mapping_detailed.md`).
- [ ] Mettre à jour tests pour utiliser `services.*` exclusivement.
- [ ] Supprimer modules + ajuster imports résiduels.
- [ ] Script parité CI OK.
- [ ] Mise à jour tracker + journal.

Critères d'acceptation:
- Plus aucune importation racine dans code/tests (hors archives).
- CI verte.
