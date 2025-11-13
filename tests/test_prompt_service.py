from __future__ import annotations

from blender_mcp.dispatchers.dispatcher import Dispatcher
from blender_mcp.services import registry


def test_prompt_service_registered_and_callable() -> None:
    # Le service doit être enregistré dans le registre
    assert "asset_creation_strategy" in registry.list_services()
    assert callable(registry.get_service("asset_creation_strategy"))

    # Le dispatcher doit résoudre le fallback service et renvoyer une chaîne non vide
    d = Dispatcher()
    res = d.dispatch("asset_creation_strategy")
    assert isinstance(res, str)
    assert len(res.strip()) > 0
