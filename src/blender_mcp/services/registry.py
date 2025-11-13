"""Service & Handler Registry (hybrid legacy + nouvelle API).

Historique:
Ce module enregistrait seulement des handlers réseau (PolyHaven, Sketchfab)
directement dans un `CommandDispatcher`, en retournant des dicts contenant
éventuellement une clé `error`. Le modèle cible supprime ce pattern au
profit d'un registre générique de services qui lèvent des exceptions
standardisées, laissant l'adapter formater la réponse.

Transition:
Nous conservons les fonctions d'enregistrement legacy (`register_default_handlers`)
pour compatibilité, tout en ajoutant un registre générique `_SERVICES` avec
`register_service`, `get_service`, `list_services`, `has_service`.

Nouveau contrat service:
- Les services enregistrés via `register_service` ne doivent pas retourner
    de dict contenant une clé `error` pour conditions normales : ils lèvent
    des exceptions (Mapper par l'adapter plus haut niveau).
"""

import os
from typing import Any, Dict

from ..command_dispatcher import CommandDispatcher
from . import (
    object as object_service,
    polyhaven,
    scene,
    screenshot as screenshot_service,
    sketchfab,
)

# --- Nouveau registre générique de services ---
_SERVICES: dict[str, Any] = {}

def register_service(name: str, fn: Any) -> None:
    """Enregistrer une fonction de service générique.

    Overwrite implicite (nous privilégions idempotence pour phase migration).
    """
    _SERVICES[name] = fn

def get_service(name: str) -> Any:
    return _SERVICES.get(name)

def list_services() -> list[str]:
    return sorted(_SERVICES.keys())

def has_service(name: str) -> bool:
    return name in _SERVICES

# Pré-enregistrer le service existant de scène (portage validé)
register_service("get_scene_info", scene.get_scene_info)
# Portage validé: service objet
register_service("get_object_info", object_service.get_object_info)
# Portage validé: service capture viewport
register_service("get_viewport_screenshot", screenshot_service.get_viewport_screenshot)


def _get_polyhaven_categories(asset_type: str = "hdris") -> Dict[str, Any]:
    try:
        return polyhaven.fetch_categories(asset_type=asset_type)
    except Exception as e:
        return {"error": str(e)}


def _search_polyhaven_assets(
    asset_type: str = "all",
    categories: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    try:
        return polyhaven.search_assets_network(
            asset_type=asset_type, categories=categories, page=page, per_page=per_page
        )
    except Exception as e:
        return {"error": str(e)}


def _download_polyhaven_asset(
    asset_id: str | None = None,
    download_url: str | None = None,
    asset_type: str = "models",
    resolution: str = "1k",
    file_format: str | None = None,
) -> Dict[str, Any]:
    try:
        return polyhaven.download_asset(
            download_url=download_url,
            asset_id=asset_id,
            asset_type=asset_type,
            resolution=resolution,
            file_format=file_format,
        )
    except Exception as e:
        return {"error": str(e)}


def _get_sketchfab_status(api_key: str | None = None) -> Dict[str, Any]:
    try:
        # Prefer explicit api_key param, fall back to env
        key = api_key or os.environ.get("SKETCHFAB_API_KEY")
        return sketchfab.get_sketchfab_status(key)
    except Exception as e:
        return {"error": str(e)}


def _search_sketchfab_models(
    api_key: str | None = None,
    query: str = "",
    categories: str | None = None,
    count: int = 20,
    downloadable: bool = True,
) -> Dict[str, Any]:
    try:
        key = api_key or os.environ.get("SKETCHFAB_API_KEY")
        if not key:
            return {"error": "No Sketchfab API key configured"}
        return sketchfab.search_models(key, query, categories=categories, count=count, downloadable=downloadable)
    except Exception as e:
        return {"error": str(e)}


def _download_sketchfab_model(api_key: str | None = None, uid: str | None = None) -> Dict[str, Any]:
    try:
        key = api_key or os.environ.get("SKETCHFAB_API_KEY")
        if not key:
            return {"error": "No Sketchfab API key configured"}
        if not uid:
            return {"error": "No UID provided"}
        return sketchfab.download_model(key, uid)
    except Exception as e:
        return {"error": str(e)}


def register_default_handlers(dispatcher: CommandDispatcher) -> None:
    """Register a small set of default handlers.

    Handlers accept keyword arguments matching the command `params` and return
    serializable dicts. They should not raise for normal error conditions;
    instead they return dicts containing `error` keys where appropriate.
    """

    dispatcher.register("get_polyhaven_categories", _get_polyhaven_categories)
    dispatcher.register("search_polyhaven_assets", _search_polyhaven_assets)
    dispatcher.register("download_polyhaven_asset", _download_polyhaven_asset)

    dispatcher.register("get_sketchfab_status", _get_sketchfab_status)
    dispatcher.register("search_sketchfab_models", _search_sketchfab_models)
    dispatcher.register("download_sketchfab_model", _download_sketchfab_model)

__all__ = [
    "register_default_handlers",
    # nouveau registre
    "register_service",
    "get_service",
    "list_services",
    "has_service",
]
