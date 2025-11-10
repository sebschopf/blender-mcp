# 0010 — Policy design (extension to 0005)

But
---
Documenter les choix d'architecture pour la couche de policy (0005) : moteur d'évaluation, format de règles, points d'intégration (dispatcher, server.execute_command), comportement en cas d'indisponibilité.

Comment valider
----------------
- `openspec validate --strict` doit accepter ce changement.
- Un prototype minimal (implémentation POC) est listé dans `tasks.md`.
