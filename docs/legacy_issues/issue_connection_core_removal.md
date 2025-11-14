## Audit final & retrait connection_core.py

Objectif: supprimer `connection_core.py` après stabilisation couche transport.

Checklist:
- [ ] Grep étendu « connection_core » (code, docs, scripts, tests) → références uniquement historiques.
- [ ] Vérifier tests transport (fragmentation, timeout, DI) verts.
- [ ] Supprimer fichier + adapter exports (`__init__.py`).
- [ ] Script parité CI OK.
- [ ] Mise à jour tracker/journal + CHANGELOG (entrée retrait effectif).

Critères d'acceptation:
- Aucun import runtime vers module supprimé.
- CI verte.
