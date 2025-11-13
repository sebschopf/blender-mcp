"""Pure helpers to build a JSON-serializable material specification.

This module contains pure functions that do not depend on Blender's bpy.
They produce a nodes/links graph used to build a Principled BSDF material
from provided texture maps.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union, Callable, Tuple

from ..node_helpers import (
    displacement_node,
    make_link,
    mapping_node,
    normal_map_node,
    output_node,
    principled_node,
    tex_image_node,
    texcoord_node,
)

def _build_spec_from_keys(keys: Sequence[str]) -> Dict[str, Any]:
    """Build a small mapping of semantic slots to map keys from a sequence.

    Mirrors the previous compatibility behaviour for tests.
    """
    kset = set(keys)
    spec: Dict[str, Any] = {}

    for k in ("color", "diffuse", "albedo"):
        if k in kset:
            spec["base_color"] = k
            break

    rules: List[Tuple[str, Tuple[str, ...], Callable[[str], str]]] = [
        ("base_color", ("color", "diffuse", "albedo"), lambda k: k),
        ("roughness", ("roughness", "rough", "arm"), lambda k: "arm.g" if k == "arm" else k),
        ("metallic", ("metallic", "metal", "arm"), lambda k: "arm.b" if k == "arm" else k),
        ("normal", ("normal", "nor"), lambda k: k),
        ("displacement", ("displacement", "disp", "height"), lambda k: k),
    ]

    for name, candidates, transform in rules:
        for cand in candidates:
            if cand in kset:
                spec[name] = transform(cand)
                break

    return spec


def build_material_spec(
    images_map: Union[Dict[str, str], Sequence[str]],
    material_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a material specification for given image maps.

    Two accepted call styles are supported for backwards compatibility:
    - build_material_spec(dict_of_maptype_to_image, material_name=None)
      returns a full nodes/links spec (used by the Blender creator).
    - build_material_spec(list_of_map_keys)
      returns a small mapping of semantic slots to map keys (used by tests).
    """
    if isinstance(images_map, dict):
        mapping: Dict[str, str] = images_map
    else:
        return _build_spec_from_keys(list(images_map))

    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []

    nodes.append(output_node("output"))

    nodes.append(principled_node("principled"))
    links.append(make_link("principled", "BSDF", "output", "Surface"))

    nodes.append(texcoord_node("texcoord"))
    nodes.append(mapping_node("mapping"))
    links.append(make_link("texcoord", "Generated", "mapping", "Vector"))

    def add_tex_node(map_type: str, img_ref: str):
        node = tex_image_node(map_type, img_ref)
        nodes.append(node)
        links.append(make_link("mapping", "Vector", node["id"], "Vector"))
        return node["id"]

    if any(k in mapping for k in ("color", "diffuse", "albedo")):
        key = next(k for k in ("color", "diffuse", "albedo") if k in mapping)
        nid = add_tex_node("base_color", mapping[key])
        links.append(make_link(nid, "Color", "principled", "Base Color"))

    if "roughness" in mapping or "rough" in mapping:
        key = "roughness" if "roughness" in mapping else "rough"
        nid = add_tex_node("roughness", mapping[key])
        links.append(make_link(nid, "Color", "principled", "Roughness"))

    if "metallic" in mapping or "metal" in mapping:
        key = "metallic" if "metallic" in mapping else "metal"
        nid = add_tex_node("metallic", mapping[key])
        links.append(make_link(nid, "Color", "principled", "Metallic"))

    if "normal" in mapping or "nor" in mapping:
        key = "normal" if "normal" in mapping else "nor"
        tex_id = add_tex_node("normal", mapping[key])
        nodes.append(normal_map_node("normal_map"))
        links.append(make_link(tex_id, "Color", "normal_map", "Color"))
        links.append(make_link("normal_map", "Normal", "principled", "Normal"))

    if any(k in mapping for k in ("displacement", "disp", "height")):
        key = next(k for k in ("displacement", "disp", "height") if k in mapping)
        nid = add_tex_node("displacement", mapping[key])
        nodes.append(displacement_node("displacement_node"))
        links.append(make_link(nid, "Color", "displacement_node", "Height"))
        links.append(make_link("displacement_node", "Displacement", "output", "Displacement"))

    spec: Dict[str, Any] = {
        "name": material_name,
        "nodes": nodes,
        "links": links,
    }
    return spec
