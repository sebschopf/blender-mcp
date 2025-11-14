## Retrait façade blender_codegen.py

Objectif: supprimer `blender_codegen.py` au profit de `codegen/blender_codegen.py`.

Checklist:
- [ ] Grep usages façade; migrer vers chemin canonique.
- [ ] Supprimer façade.
- [ ] Ajuster tests (ex: `test_blender_codegen.py`).
- [ ] Script parité CI OK.
- [ ] Mise à jour tracker/journal.

Critères d'acceptation:
- Plus aucun import de la façade.
- CI verte.
