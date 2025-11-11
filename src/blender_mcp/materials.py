"""Material helpers: build a testable material specification and an optional
Blender-backed creator.

The pure function `build_material_spec` returns a JSON-serializable dict that
describes nodes and links needed to build a Principled BSDF material from a
set of texture maps (color, roughness, metallic, normal, displacement...).

`create_material_in_blender` is a convenience wrapper that will attempt to
create the material using `bpy` when available; it's not covered by unit
tests here to avoid needing Blender in CI.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

from .node_helpers import (
    displacement_node,
    make_link,
    mapping_node,
    normal_map_node,
    output_node,
    principled_node,
    tex_image_node,
    texcoord_node,
)


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
    # If caller passed a mapping dict, build full spec; otherwise treat as sequence of keys
    if isinstance(images_map, dict):
        mapping: Dict[str, str] = images_map  # narrow type for the type-checker
    else:
        return _build_spec_from_keys(list(images_map))

    # At this point, assume a mapping dict was provided. Build full spec.
    # Basic nodes
    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []

    # Output node
    nodes.append(output_node("output"))

    # Principled BSDF
    nodes.append(principled_node("principled"))
    links.append(make_link("principled", "BSDF", "output", "Surface"))

    # Optional nodes based on available maps
    # Add mapping and texcoord as common inputs
    nodes.append(texcoord_node("texcoord"))
    nodes.append(mapping_node("mapping"))
    links.append(make_link("texcoord", "Generated", "mapping", "Vector"))

    # x was previously used for layout offsets; not required in spec

    # Helper to add an image texture node and link it to mapping
    def add_tex_node(map_type: str, img_ref: str):
        node = tex_image_node(map_type, img_ref)
        nodes.append(node)
        links.append(make_link("mapping", "Vector", node["id"], "Vector"))
        return node["id"]

    # Base color
    if any(k in mapping for k in ("color", "diffuse", "albedo")):
        key = next(k for k in ("color", "diffuse", "albedo") if k in mapping)
        nid = add_tex_node("base_color", mapping[key])
        links.append(make_link(nid, "Color", "principled", "Base Color"))

    # Roughness
    if "roughness" in mapping or "rough" in mapping:
        key = "roughness" if "roughness" in mapping else "rough"
        nid = add_tex_node("roughness", mapping[key])
        links.append(make_link(nid, "Color", "principled", "Roughness"))

    # Metallic
    if "metallic" in mapping or "metal" in mapping:
        key = "metallic" if "metallic" in mapping else "metal"
        nid = add_tex_node("metallic", mapping[key])
        links.append(make_link(nid, "Color", "principled", "Metallic"))

    # Normal map (adds a normal map node)
    if "normal" in mapping or "nor" in mapping:
        key = "normal" if "normal" in mapping else "nor"
        tex_id = add_tex_node("normal", mapping[key])
        nodes.append(normal_map_node("normal_map"))
        links.append(make_link(tex_id, "Color", "normal_map", "Color"))
        links.append(make_link("normal_map", "Normal", "principled", "Normal"))

    # Displacement
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


def _build_spec_from_keys(keys: Sequence[str]) -> Dict[str, Any]:
    """Build a small mapping of semantic slots to map keys from a sequence.

    This mirrors the older compatibility behaviour but is factored out for
    testability and clarity.
    """
    kset = set(keys)
    spec: Dict[str, Any] = {}

    # Base color
    for k in ("color", "diffuse", "albedo"):
        if k in kset:
            spec["base_color"] = k
            break

    # Consolidate mapping rules to reduce branching/complexity
    rules = [
        ("base_color", ("color", "diffuse", "albedo"), lambda k: k),
        (
            "roughness",
            ("roughness", "rough", "arm"),
            lambda k: "arm.g" if k == "arm" else k,
        ),
        (
            "metallic",
            ("metallic", "metal", "arm"),
            lambda k: "arm.b" if k == "arm" else k,
        ),
        ("normal", ("normal", "nor"), lambda k: k),
        ("displacement", ("displacement", "disp", "height"), lambda k: k),
    ]

    for name, candidates, transform in rules:
        for cand in candidates:
            if cand in kset:
                spec[name] = transform(cand)
                break

    return spec


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

    # Clear default nodes
    for n in list(nodes):
        nodes.remove(n)

    # Create nodes according to the spec
    spec = build_material_spec(images_map, material_name)
    node_objs = {}
    for n in spec["nodes"]:
        node = nodes.new(type=n["type"]) if hasattr(nodes, "new") else nodes.new(n["type"])
        # Some node types don't expose an 'image' attribute; set name and optionally image
        try:
            node.name = n["id"]
        except Exception:
            pass
        if "image" in n and hasattr(node, "image"):
            try:
                node.image = bpy.data.images.get(n["image"]) or bpy.data.images.load(n["image"])
            except Exception:
                # Image loading may fail in tests or if path invalid; ignore
                pass
        node_objs[n["id"]] = node

    # Create links
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
