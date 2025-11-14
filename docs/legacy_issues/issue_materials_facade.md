## Retrait façade materials.py

Objectif: retirer `materials.py` (façade) au profit du package `materials/`.

Checklist:
- [ ] Grep usages `from blender_mcp.materials import` hors package; migrer vers `blender_mcp.materials` (package).
- [ ] Supprimer fichier façade.
- [ ] Adapter tests si nécessaire.
- [ ] Script parité CI OK.
- [ ] Mise à jour tracker/journal.

Critères d'acceptation:
- Aucun import du fichier supprimé.
- CI verte.
