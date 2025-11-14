<!-- OpenSpec: Legacy Retirement Schedule -->

# Spécification: Calendrier de Retrait des Modules Legacy
Date: 2025-11-14
Phase: 2 (préparation retrait) / projection Phases 3–5
Auteur: automation

## Contexte
Le projet contient encore plusieurs shims / modules legacy conservés pour la compatibilité pendant la migration vers la structure canonique `src/blender_mcp/`. Certains émettent déjà un `DeprecationWarning`. Cette spec formalise un calendrier de retrait sur deux cycles (non-breaking initialement) et décrit les scénarios de compatibilité et de transition.

Modules legacy ciblés:
- `connection_core.py`
- `simple_dispatcher.py` (racine) & `command_dispatcher.py` (racine)
- `server_shim.py` & `servers/shim.py`
- Services racine: `polyhaven.py`, `sketchfab.py`, `hyper3d.py`
- `blender_codegen.py` (racine)

## Objectifs
1. Documenter les étapes (avertir, stabiliser, retirer) sans rupture non planifiée.
2. Réduire la surface de maintenance en éliminant duplications après migration complète.
3. Garantir que toute suppression est précédée d'au moins deux cycles de release avec warning explicite et mention CHANGELOG.

## Non Objectifs
- Modifier immédiatement les signatures publiques des services portés.
- Introduire une rupture dans `send_command` ou dans le schema de réponse.

## Calendrier Proposé (Cycles = releases mineures du projet)
| Module | État actuel | Cycle N (courant) | Cycle N+1 | Cycle N+2 | Action finale |
|--------|-------------|-------------------|-----------|-----------|---------------|
| Services racine (`polyhaven.py`, `sketchfab.py`, `hyper3d.py`) | DeprecationWarning | Warning + doc | Warning + CHANGELOG rappel | Retrait (suppression fichiers) | Supprimer et ajouter mapping vers services.* dans notes de migration |
| `simple_dispatcher.py`, `command_dispatcher.py` (racine) | DeprecationWarning partiel | Uniformiser warning | Doc + tests de compat explicites | Retrait | Rediriger import → dispatcher.py via stub si besoin |
| `connection_core.py` | DeprecationWarning | Warning + pointer vers `services.connection.*` | Maintien warning | Retrait (Phase 4) | Adapter doc pour nouvelle connexion uniquement |
| `server_shim.py`, `servers/shim.py` | DeprecationWarning (partiel) | Uniformiser warning & doc | Maintien warning | Retrait | Consolidation unique `servers/server.py` |
| `blender_codegen.py` racine | DeprecationWarning | Warning + doc | Maintien warning | Retrait (Phase 5) | Utiliser seulement `codegen/blender_codegen.py` |

## Critères Avant Retrait
- Tous les imports internes migrés vers la nouvelle localisation (`services.*`, `dispatchers.*`, `servers.*`).
- Tests ne référencent plus les chemins legacy (sauf tests de dépréciation explicites).
- CHANGELOG contient deux entrées successives mentionnant le futur retrait.
- Aucun appel externe documenté restant (audit rapide / communication release notes).

## Scénarios

#### Scenario: Import d'un module legacy pendant phase d'avertissement
Given un code utilisateur importe `blender_mcp.connection_core`
When le module est chargé
Then un `DeprecationWarning` est émis avec un message clair recommandant `blender_mcp.services.connection.network_core`.
And aucune rupture fonctionnelle n'a lieu.

#### Scenario: Tentative d'import après retrait (post Cycle N+2)
Given le même code utilisateur n'a pas été mis à jour
When l'import est tenté
Then l'import échoue avec `ModuleNotFoundError`
And les notes de migration (CHANGELOG + docs/migration.md si ajouté) indiquent la nouvelle cible.

#### Scenario: Outil d'audit interne exécuté avant le retrait
Given l'audit inspecte l'arbre `src/`
When il détecte une référence aux modules legacy hors tests de dépréciation
Then il signale une violation et propose la correction.

#### Scenario: Release note Cycle N+1
Given une release mineure est publiée
When les release notes sont générées
Then elles listent chaque module legacy avec un rappel "Retrait dans le prochain cycle".

#### Scenario: Maintien compat services racine
Given `polyhaven.py` (racine) émet un warning
When un service `search_polyhaven_assets` est invoqué via l'ancien chemin
Then le comportement est identique à la version canonique sous `services.polyhaven`.

## Risques & Mitigations
- Risque: Utilisateurs retardent la mise à jour et subissent un `ModuleNotFoundError` au retrait.
  - Mitigation: Doubler le canal (DeprecationWarning + release notes + journal + spec).
- Risque: Oubli d'une référence interne résiduelle.
  - Mitigation: Script d'audit (optionnel) avant suppression finale.

## Actions à Implémenter (Cycle N)
1. Vérifier présence uniforme des warnings aux imports (ajouter si manquant).
2. Ajouter entrée journale `PROJECT_JOURNAL.md` pour adoption du calendrier.
3. Ajouter label `legacy-removal` aux issues/PR liées.
4. Préparer snippet release note (template).

## Actions (Cycle N+1)
1. Audit des références internes.
2. Release notes rappel retrait imminent.
3. Ajout tests assurant que warnings persistent.

## Actions (Cycle N+2)
1. Supprimer fichiers legacy.
2. Mettre à jour CHANGELOG (section Breaking Changes).
3. Ajouter documentation de migration (si non existante) listant remplacements.

## Implémentation Technique Minimale
- AUCUN changement runtime immédiat.
- Fichier spec ajouté sous `openspec/changes/`.
- Suivi via labels GitHub: `legacy-removal`, `deprecation`.

## Validation
- Cette spec est non-breaking à l'introduction.
- Toute suppression déclenchera une nouvelle spec si surface publique additionnelle impactée.

## Notes
- Conserver les tests de dépréciation jusqu'à la suppression (ensuite retirer ou adapter).
- Penser à mettre à jour `INVENTORY_CONSOLIDATION.md` après retrait effectif.

---
Fin de spec.