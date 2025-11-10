from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class GenericResponse(TypedDict, total=False):
    status: str
    message: str
    result: Any


class SceneObject(TypedDict, total=False):
    name: Optional[str]
    type: Optional[str]


class SceneResponse(TypedDict):
    status: str
    scene_name: Optional[str]
    objects: List[SceneObject]
    active_camera: Optional[str]


class ObjectResponse(TypedDict, total=False):
    status: str
    object: Dict[str, Any]


class MaterialSpec(TypedDict, total=False):
    name: Optional[str]
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]
