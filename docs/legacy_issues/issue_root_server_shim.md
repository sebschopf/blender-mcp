## Retrait shim serveur racine

Objectif: enlever `blender_mcp/server.py` dans la racine du repo (double shim) pour converger.

Checklist:
- [ ] Identifier tests utilisant le shim racine; mettre à jour vers implémentation canonique.
- [ ] Supprimer fichier racine.
- [ ] Confirmer que le shim `src/blender_mcp/server.py` reste (ou planifier retrait ultérieur).
- [ ] Script parité CI OK.
- [ ] Mise à jour README/architecture si chemins changent.
- [ ] Tracker/journal mis à jour.

Critères d'acceptation:
- Aucun import du shim racine restant.
- CI verte.
