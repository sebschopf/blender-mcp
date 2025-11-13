# OpenSpec Change: Phase 2 Endpoint Porting

Change ID: phase-2-endpoint-porting
Status: draft
Author: AI Assistant Session (2025-11-13)

## 1. Contexte
Les endpoints `@tool` et `@prompt` présents dans `docs/endpoint_mapping_detailed.md` sont issus du fichier legacy `copy_server.py`. Ils doivent être portés vers des services testables et enregistrés dans un registre central (`services/registry.py`) afin de réduire duplication, clarifier l’architecture et permettre une évolution conforme SOLID.

## 2. Objectifs
- Éliminer l’accès direct à `copy_server.py` dans le code runtime.
- Normaliser les services: exceptions internes uniquement, pas de dict d’erreur.
- Fournir tests unitaires pour chaque service (cas nominal + erreurs).
- Mettre à jour la documentation (`PROJECT_JOURNAL.md`, statut de mapping `endpoint_mapping_detailed.md`).
- Préparer base pour extension (registre dynamique, injection de stratégies plus tard).

## 3. Portée
Inclus:
- Création du fichier `services/registry.py` et API minimale.
- Portage des services: scène, objets, screenshot, execute code, polyhaven, sketchfab, hyper3d, prompt strategy.
- Ajout tests unitaires ciblés (un fichier de test par domaine si pertinent).

Exclus (reportés Phase 4+):
- Sandbox avancée pour `execute_blender_code`.
- Stratégies d’injection parser/framing/policy.
- Optimisations performance réseau.

## 4. Table Endpoints (Initial)
| Endpoint | Fichier cible service | Registre key | Phase ordre | Sécurité spéciale | Notes |
|----------|-----------------------|--------------|-------------|-------------------|-------|
| get_scene_info | services/scene.py | get_scene_info | 1 | Non | Simple accès bpy |
| get_object_info | services/object.py | get_object_info | 1 | Non | Vérifier existence objet |
| get_viewport_screenshot | services/scene.py | get_viewport_screenshot | 2 | Éviter very large size | Mock rendu |
| execute_blender_code | services/exec.py | execute_blender_code | 3 | Oui (sandbox) | Limiter builtins |
| get_polyhaven_categories | services/polyhaven.py | polyhaven.get_categories | 4 | Réseau | Catégories cache optionnel |
| search_polyhaven_assets | services/polyhaven.py | polyhaven.search_assets | 4 | Réseau | Filtrage params |
| download_polyhaven_asset | services/polyhaven.py | polyhaven.download_asset | 4 | Réseau/Fichier | Chemins sûrs |
| set_texture | services/polyhaven.py | polyhaven.set_texture | 4 | Accès bpy | Valider material |
| get_polyhaven_status | services/polyhaven.py | polyhaven.status | 4 | Non | Simple flag |
| get_hyper3d_status | services/hyper3d.py | hyper3d.status | 5 | Non | Simple flag |
| get_sketchfab_status | services/sketchfab.py | sketchfab.status | 5 | Non | Simple flag |
| search_sketchfab_models | services/sketchfab.py | sketchfab.search_models | 5 | Réseau | Pagination |
| download_sketchfab_model | services/sketchfab.py | sketchfab.download_model | 5 | Réseau/Fichier | UID validation |
| generate_hyper3d_model_via_text | services/hyper3d.py | hyper3d.generate_text | 6 | Réseau/Async | Bbox validation |
| generate_hyper3d_model_via_images | services/hyper3d.py | hyper3d.generate_images | 6 | Réseau/Async | Type listes |
| poll_rodin_job_status | services/hyper3d.py | hyper3d.poll_job_status | 6 | Réseau | Timeout tests |
| import_generated_asset | services/hyper3d.py | hyper3d.import_generated | 6 | Fichier | Existence asset |
| asset_creation_strategy (prompt) | services/strategy.py | strategy.asset_creation_strategy | 7 | Non | Peut devenir config |

## 5. Format Service (Exemple `get_scene_info`)
```python
def get_scene_info(ctx) -> dict:
    if not hasattr(ctx, 'scene'):
        raise BlenderNotAvailableError("No scene context")
    # construire et retourner dict (objets, frames, etc.)
```

## 6. Tests (Exemples)
Nom fichier: `tests/test_scene_service.py`
Cas:
- `test_get_scene_info_success`
- `test_get_scene_info_no_bpy` (mock suppression de module `bpy` ou attribut ctx)
- `test_get_object_info_not_found`

## 7. Registre
```python
# services/registry.py
_SERVICES: dict[str, callable] = {}
def register_service(name: str, fn: callable) -> None: _SERVICES[name] = fn
def get_service(name: str): return _SERVICES[name]
def list_services() -> list[str]: return sorted(_SERVICES)
```
Le dispatcher s’adaptera: résolution via `get_service(name)`.

## 8. Migration Workflow (PR par domaine)
1. Créer service + tests.
2. Ajouter au registre.
3. Mettre à jour `endpoint_mapping_detailed.md` (pending → ported).
4. Journal + changelog interne.
5. Linter + type checks.
6. Merge une fois vert.

## 9. Risques & Mitigation
| Risque | Impact | Mitigation |
|--------|--------|-----------|
| Sandbox insuffisante execute code | Exposition API interne | Spec séparée + validation pré-exec |
| Tests réseau lents | Lenteur CI | Mock httpx + fixtures |
| Divergence signatures | Incohérence clients | Documenter dans spec + alias éventuels |
| Erreurs mapping absentes | Réponses non standard | Ajouter tests mapping exceptions |

## 10. Rollback
Maintenir temporairement exports legacy (shims) avec warnings. Rollback = réactiver anciens imports sans supprimer nouveaux services.

## 11. Validation Acceptation
- Tous endpoints Phase 1–3 marqués `ported`.
- Tests unitaires ajoutés et verts.
- Registre expose toutes les clés listées.
- Pas d’import runtime de `copy_server.py`.

## 12. Suivi
Ajouter entrée dans `PROJECT_JOURNAL.md` à chaque endpoint porté.

## 13. Prochaines Extensions (Hors Portée Immédiate)
- Caching PolyHaven catégories.
- Async job polling généralisé (Hyper3D).
- Stratégies d’autorisation pour execute code.

## 14. Décision Ouverte
- Granularité des clés registre (noms plats vs namespaces). À décider après portage scène/objets.

## 15. Checklist PR Type (Endpoint)
1. Fichier service créé.
2. Tests ajoutés (>=2 cas).
3. Registre mis à jour.
4. Mapping modifié (statut).
5. Journal / spec mis à jour.
6. Lint + mypy OK.
7. Aucun dict d’erreur (exceptions seulement).
