<!-- Endpoint PR template — use for changes that add or modify an API endpoint -->
# Titre succinct de la PR

Résumé court (1-2 lignes) décrivant la fonctionnalité / correction d'endpoint.

## Checklist d'acceptation
- [ ] J'ai ajouté/mis à jour des tests couvrant le comportement attendu (unit + integration si applicable)
- [ ] Les tests locaux passent : ruff, mypy, pytest
- [ ] La documentation/endpoints mapping a été mise à jour (`docs/endpoint_mapping.md` / `docs/endpoint_mapping_detailed.md`)
- [ ] Si changement de comportement ou breaking change : une proposition OpenSpec est ajoutée sous `openspec/changes/<id>/`
- [ ] Les changements sont import-safe (compatible avec l'import dans `addon.py` si applicable)

## Détails techniques
- Module(s) modifié(s) : `src/...`
- Points d'entrée (HTTP/ASGI) : `/v1/....` (méthode)
- Contrat d'entrée/sortie (exemples JSON)

## Scénarios de test (Acceptance)
- Scenario: comportement attendu X
  - Given ...
  - When ...
  - Then ...

## Notes pour le reviewer
- Points d'attention, décisions de conception, alternatives rejetées
- Si tu veux exécuter localement : `PYTHONPATH='src;.' ruff check ... && mypy ... && pytest tests/test_...` (Windows: séparateur `;`)

----
Merci de garder la PR ciblée (petits commits, messages clairs). Si la PR change l'API publique, ajoute une proposition OpenSpec et attache les scénarios d'acceptation ci-dessus.
