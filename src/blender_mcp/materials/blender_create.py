"""Blender-backed material creation helper (optional bpy dependency).

This module wraps the pure spec builder and tries to instantiate the nodes
inside Blender if bpy is available at runtime.
"""
from __future__ import annotations

from typing import Dict, Optional

from .spec import build_material_spec


def create_material_in_blender(images_map: Dict[str, str], material_name: str) -> Optional[str]:
    """Create the material in Blender if `bpy` is importable.

    Returns the created material name or None if bpy is not available.
    """
    try:
        import bpy  # type: ignore
    except Exception:
        return None

    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for n in list(nodes):
        nodes.remove(n)

    spec = build_material_spec(images_map, material_name)
    node_objs = {}
    for n in spec["nodes"]:
        node = nodes.new(type=n["type"]) if hasattr(nodes, "new") else nodes.new(n["type"])
        try:
            node.name = n["id"]
        except Exception:
            pass
        if "image" in n and hasattr(node, "image"):
            try:
                node.image = bpy.data.images.get(n["image"]) or bpy.data.images.load(n["image"])
            except Exception:
                pass
        node_objs[n["id"]] = node

    for link in spec["links"]:
        try:
            from_node = node_objs[link["from_node"]]
            to_node = node_objs[link["to_node"]]
            links.new(
                from_node.outputs[link["from_socket"]],
                to_node.inputs[link["to_socket"]],
            )
        except Exception:
            pass

    return mat.name
