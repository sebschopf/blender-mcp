# Brouillons d'issues de retrait legacy

Ce fichier regroupe les corps d'issues à créer sur GitHub pour orchestrer le retrait progressif des shims legacy conformément à la spec:
`openspec/changes/2025-11-14-legacy-retirement-schedule/spec.md`.

Labels à appliquer: `phase2`, `legacy-removal`, `deprecation`, (ajouter selon besoin: `connection`, `services`, `docs`).

## 1. Retrait `connection_core.py`
Titre: Retrait progressif `connection_core.py` (migration vers couche services.connection)

Corps:
```
Objectif: Supprimer le module legacy `connection_core.py` après migration complète vers `services.connection` (NetworkCore + transports).

Contexte:
- DeprecationWarning déjà émis à l'import.
- Transport Phase A implémenté (RawSocketTransport/CoreTransport/ResponseReceiver).
- Spec calendrier: retrait en cycle N+2 après audit (voir spec 2025-11-14 legacy retirement).

Checklist:
- [ ] Recenser tous les imports internes (grep connection_core) et remplacer par façade moderne ou couche transport.
- [ ] Mettre à jour tests utilisant directement `connection_core` pour cibler `services.connection` ou API publique stable.
- [ ] Ajouter entrée CHANGELOG annonçant retrait planifié.
- [ ] Vérifier absence d'import dans `scripts/` et `addon.py`.
- [ ] Supprimer le fichier et adapter exports `__init__.py`.
- [ ] Lancer script parité CI (`scripts/verify_local_ci.ps1`) → vert.
- [ ] Mettre à jour `docs/LEGACY_TRACKER.md` & `PROJECT_JOURNAL.md`.
Critères d'acceptation:
- Aucune référence restante dans repo (hors journal / tracker / CHANGELOG historique).
- Suite de tests et lint/type OK.
```

## 2. Retrait shims dispatchers (`simple_dispatcher.py`, `command_dispatcher.py`)
Titre: Retrait façades legacy dispatcher (`simple_dispatcher.py`, `command_dispatcher.py`)

Corps:
```
Objectif: Enlever les ré-exportations legacy du dispatcher pour centraliser sur `dispatchers/`.

Contexte:
- Les deux fichiers ne contiennent que des ré-exports + DeprecationWarning.
- Tests utilisent encore les chemins legacy pour valider warnings.

Checklist:
- [ ] Confirmer que les projets externes disposent d'une fenêtre de migration (annoncer dans CHANGELOG).
- [ ] Ajouter note de migration dans README (section Legacy si absent).
- [ ] Mettre à jour tests pour pointer vers nouveaux imports ou supprimer tests warnings.
- [ ] Supprimer fichiers + nettoyer imports dans `services/registry.py`.
- [ ] Script parité CI vert.
- [ ] Journal + tracker mis à jour.
Critères d'acceptation:
- Plus aucun import des shims dans code actif.
```

## 3. Retrait double shim serveur (`blender_mcp/server.py` racine + `src/blender_mcp/server.py`)
Titre: Consolidation serveur et retrait double shim serveur

Corps:
```
Objectif: Supprimer le shim racine (et idéalement le shim src si redondant) pour ne garder qu'une implémentation claire (services + façade moderne).

Checklist:
- [ ] Identifier usages tests/externes du chemin racine (`blender_mcp.server`).
- [ ] Ajouter avertissement dans CHANGELOG (préavis N+1).
- [ ] Mettre à jour docs architecture (section serveur) pour pointer vers emplacement final.
- [ ] Supprimer shim racine puis valider CI.
- [ ] Décider si shim src reste (si encore nécessaire pour compat) sinon répéter cycle.
Critères d'acceptation:
- Un seul point d'entrée serveur référencé dans README + architecture.
```

## 4. Retrait façades `materials.py` et `blender_codegen.py`
Titre: Retrait façades `materials.py` / `blender_codegen.py` (migration définitive vers packages)

Corps:
```
Objectif: Supprimer les fichiers de compat hérités au profit des packages `materials` et `codegen`.

Checklist:
- [ ] Grep usages directs dans tests / scripts.
- [ ] Ajouter note CHANGELOG de retrait planifié.
- [ ] Mettre à jour README (si mention directe des anciens chemins).
- [ ] Supprimer façades + ajuster imports restants (ex: `primitive.py`).
- [ ] CI parité verte.
Critères d'acceptation:
- Imports modernes uniquement (`from blender_mcp.materials import ...`, `from blender_mcp.codegen.blender_codegen import ...`).
```

## 5. Retrait services racine (`polyhaven.py`, `sketchfab.py`, `hyper3d.py`, etc.)
Titre: Retrait services racine (PolyHaven/Sketchfab/Hyper3D) au profit des services canoniques

Corps:
```
Objectif: Enlever les modules racine qui émettent des DeprecationWarning au profit des implémentations exceptions-first dans `services/`.

Checklist:
- [ ] Vérifier que tous les endpoints sont portés (voir `docs/endpoint_mapping_detailed.md`).
- [ ] Supprimer tests spécifiques aux warnings (adapter vers tests services existants).
- [ ] CHANGELOG + README notent migration.
- [ ] CI verte après suppression.
Critères d'acceptation:
- Plus aucune importation `blender_mcp.polyhaven` / `blender_mcp.sketchfab` / `blender_mcp.hyper3d` hors archive.
```

## 6. Audit final & suppression `connection_core` (issue de validation finale)
Titre: Audit final usages avant suppression physique `connection_core`

Corps:
```
Objectif: Vérifier qu'aucune régression n'est introduite avant merge de suppression de `connection_core.py`.

Checklist:
- [ ] Exécuter script parité CI.
- [ ] Lancer un grep étendu (inclure docs, tests, scripts) pour « connection_core ».
- [ ] Confirmer que le transport Raw/Core couvre toutes les routes de tests.
- [ ] Supprimer fichier dans branche feature dédiée.
- [ ] Merge après review + entrée CHANGELOG.
Critères d'acceptation:
- Commit suppression isolé <= 3 fichiers modifiés (respect conventions repo).
```

## Notes générales pour création GitHub
Pour chaque issue:
1. Créer issue avec le corps correspondant.
2. Appliquer labels recommandés.
3. Lier la spec calendrier dans description.
4. Ajouter un lien vers PR quand créé.

## Prochaine étape
Créer les issues, puis ouvrir PRs petites (≤3 fichiers code hors docs/tests) pour chaque retrait.
