# Plan détaillé de retrait des shims legacy

Ce plan opérationnel complète `docs/LEGACY_TRACKER.md` et la spec OpenSpec `openspec/changes/2025-11-14-legacy-retirement-schedule/spec.md`.

## Objectifs
1. Réduire progressivement la surface legacy sans rupture de compatibilité prématurée.
2. Garantir une fenêtre de migration (N → N+2) claire pour utilisateurs externes.
3. Préserver la stabilité CI (lint/type/tests) à chaque étape.

## Cycles
- Cycle N (actuel): Annonce (DeprecationWarning), documentation, issues créées.
- Cycle N+1: Préparation retraits (remplacement imports internes, CHANGELOG annonçant suppressions N+2, adaptation tests).
- Cycle N+2: Suppressions physiques; validation finale; publication release de retrait.

## Séquence recommandée
Ordre choisi pour minimiser risque de régression (shims moins couplés d'abord):
1. Façades dispatcher (`simple_dispatcher.py`, `command_dispatcher.py`).
2. Services racine (`polyhaven.py`, `sketchfab.py`, `hyper3d.py`, etc.).
3. Façades matériaux/codegen (`materials.py`, `blender_codegen.py`).
4. Double shim serveur (racine + src) — consolidation.
5. `connection_core.py` (dernier: dépend au transport pleinement stabilisé).

## Conditions pré-retrait (toutes étapes)
- Script parité CI (`scripts/verify_local_ci.ps1`) vert.
- Aucun import externe nouvellement introduit pointant vers le shim ciblé.
- CHANGELOG contient entrée « Retrait planifié <nom shim> au cycle N+2 ». (ajout en N+1 au plus tard).
- Documentation (README + tracker) mise à jour pour l'étape.

## Risques & Mitigations
| Risque | Impact | Mitigation |
|--------|--------|------------|
| Suppression trop tôt d'un shim utilisé externement | Rupture d'intégration | Préavis via CHANGELOG + DeprecationWarning sur 2 cycles |
| Régression tests après suppression | CI rouge / blocage merge | Branches feature isolées + script parité CI avant PR |
| Oubli d'import interne résiduel | Erreur runtime tardive | Grep ciblé + revue PR stricte (≤3 fichiers modifiés) |
| Mélange modifications structurelles multiples | Difficulté review | Micro-PRs thématiques séquencées |

## Branching & PR conventions
- Nom de branche: `feature/retire-<nom-shim>`.
- Taille PR: ≤3 fichiers code modifiés (hors docs/tests) + mise à jour doc associée.
- Labels: `legacy-removal`, `deprecation`, `phase2`, + domaine (ex: `connection`, `services`).
- Liens: chaque PR référence l'issue correspondante + spec calendrier.

## Validation finale (avant suppression `connection_core.py`)
1. Grep étendu `connection_core` → uniquement présent dans tracker/journal/spec.
2. Tests transport et connection passent (socketpair, fragmentation, timeout).
3. Exécution manuelle d'un flux utilisateur (commande simple via RawSocketTransport) si environnement disponible.
4. Merge PR suppression + entrée CHANGELOG « Retrait effectif ».

## Mesures post-retrait
- Nettoyage warnings (retirer tests de dépréciation spécifiques).
- Mise à jour `docs/architecture.md` pour enlever sections sur shim disparu.
- Ajout section « Breaking Changes » dans release notes.

## Tableau synthèse (mise à jour au fil des PR)
| Shim | Issue | Branche | PR | Statut |
|------|-------|---------|----|--------|
| simple_dispatcher.py / command_dispatcher.py | #30 | feature/retire-dispatcher-shims | #TBD | branche créée |
| services racine polyhaven/sketchfab/hyper3d | #31 | feature/retire-root-services | #TBD | branche créée |
| materials.py | #32 | feature/retire-materials-facade | #TBD | branche créée |
| blender_codegen.py | #33 | feature/retire-blender-codegen-facade | #TBD | branche créée |
| server shim racine | #34 | feature/retire-root-server-shim | #TBD | branche créée |
| connection_core.py | #35 | feature/retire-connection-core | #TBD | branche créée |

Mettre à jour ce tableau quand les issues/PR sont créées.
