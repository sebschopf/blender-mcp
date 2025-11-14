# Legacy Tracker

Ce document liste les modules legacy/shims de compatibilité encore présents dans le dépôt, leur statut de dépréciation, la cible de retrait (cycle) et la source de remplacement. Il complète la spec OpenSpec `openspec/changes/2025-11-14-legacy-retirement-schedule/spec.md`.

Format cycle: N = cycle courant, N+1 = prochain cycle de release, N+2 = retrait possible (suppression) après période de grâce et audit.

| Module / Fichier | Statut actuel | Remplacement / Source canonique | Cible retrait | Notes |
|------------------|--------------|---------------------------------|---------------|-------|
| `src/blender_mcp/connection_core.py` | Déprécié (DeprecationWarning à l'import) | `src/blender_mcp/services/connection/*` (`NetworkCore`, transports) | N+2 | Utilisé via `CoreTransport` pour compat; migrer appels vers couche services. |
| `src/blender_mcp/simple_dispatcher.py` | Façade minimale (ré-export) | `src/blender_mcp/dispatcher.py` | N+2 | Aucun nouveau code; surveiller utilisations externes. |
| `src/blender_mcp/command_dispatcher.py` | Façade minimale (ré-export) | `src/blender_mcp/dispatcher.py` | N+2 | Identique à simple_dispatcher. |
| `src/blender_mcp/server.py` | Shim temporaire | `src/blender_mcp/services/connection/facade.py` + transport | N+2 | Maintenu pour chemins d'import historiques/tests. |
| `blender_mcp/server.py` (racine) | Shim racine | `src/blender_mcp/server.py` (déjà shim) | N+2 | Double shim; retrait après nettoyage usages CI/tests. |
| `src/blender_mcp/materials.py` | Façade de compatibilité | `src/blender_mcp/materials/__init__.py` (package) | N+2 | Avertissement déjà en place; vérifier absence d'import direct dans outils tiers. |
| `src/blender_mcp/blender_codegen.py` | Façade de compatibilité | `src/blender_mcp/codegen/blender_codegen.py` | N+2 | Fallback import; retirer une fois migrations complètes. |
| `src/blender_mcp/archive/*` | Archivé / ignoré lint | Implémentations canoniques actives | N/A | Conserver pour historique uniquement. |

## Processus de retrait
1. Audit références internes (`grep` + outils de recherche) pour confirmer absence d'usage runtime hors tests.
2. Ajout entrée CHANGELOG annonçant retrait au cycle suivant (N+1 → retrait en N+2).
3. Suppression + mise à jour des imports dans tests (ou suppression des tests legacy).
4. Vérification CI (ruff/mypy/pytest) verte post-suppression.
5. Mise à jour `docs/endpoint_mapping_detailed.md` et journal.

## Contrôles à effectuer avant suppression (checklist)
- [ ] Plus aucune importation directe dans `scripts/` (ex: `scripts/gemini_bridge.py`).
- [ ] Plus aucune importation dans `addon.py` (hors shims nécessaires temporairement).
- [ ] Tests de dépréciation (`tests/test_deprecations.py`) ajustés ou supprimés.
- [ ] Aucun warning critique restant dans CI après retrait.
- [ ] Documentation mise à jour (README section Legacy, architecture, journal).

## État actuel (mise à jour 2025-11-14)
- Tous les modules listés émettent un DeprecationWarning ou sont des ré-exportations triviales.
- Le transport abstrait est en place; prochaine phase: réduction des usages de `connection_core`.
- Ouverture d'issues GitHub recommandée (manuelle) pour chaque élément : utiliser labels `legacy-removal`, `deprecation`, `phase2`.

## Référence
- Spec calendrier: `openspec/changes/2025-11-14-legacy-retirement-schedule/spec.md`
- Journal: `docs/PROJECT_JOURNAL.md`
