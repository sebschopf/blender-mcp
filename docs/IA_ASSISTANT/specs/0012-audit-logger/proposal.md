# 0012 - Audit logger & request-id POC

Résumé
-------
Ajouter un changement qui introduit un POC `audit.py` fournissant un append-only JSONL audit sink et la génération/propagation d'un `request_id` pour chaque commande exécutée.

Type
----
NEW SPEC: POC d'implémentation (audit + instrumentation minimale).
