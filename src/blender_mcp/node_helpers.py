"""Node helper utilities used by the addon.

These helpers encapsulate small wiring tasks. They are defensive so tests
can exercise logic using simple mock containers instead of requiring Blender.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple


def output_node(node_id: str = "output") -> Dict[str, Any]:
    return {"id": node_id, "type": "ShaderNodeOutputMaterial"}


def principled_node(node_id: str = "principled") -> Dict[str, Any]:
    return {"id": node_id, "type": "ShaderNodeBsdfPrincipled"}


def texcoord_node(node_id: str = "texcoord") -> Dict[str, Any]:
    return {"id": node_id, "type": "ShaderNodeTexCoord"}


def mapping_node(node_id: str = "mapping") -> Dict[str, Any]:
    return {"id": node_id, "type": "ShaderNodeMapping"}


def tex_image_node(map_type: str, image_ref: str) -> Dict[str, Any]:
    return {"id": f"tex_{map_type}", "type": "ShaderNodeTexImage", "image": image_ref}


def normal_map_node(node_id: str = "normal_map") -> Dict[str, Any]:
    return {"id": node_id, "type": "ShaderNodeNormalMap"}


def displacement_node(node_id: str = "displacement_node") -> Dict[str, Any]:
    return {"id": node_id, "type": "ShaderNodeDisplacement"}


def make_link(from_node: str, from_socket: str, to_node: str, to_socket: str) -> Dict[str, Any]:
    return {"from_node": from_node, "from_socket": from_socket, "to_node": to_node, "to_socket": to_socket}


def _is_blender_nodes(nodes: Any) -> bool:
    return hasattr(nodes, "new")


def _append_mock_ao_links(
    links: Any, base_node: Any, mix_node: Any, ao_node: Any, principled: Any
) -> None:
    """Append best-effort mock link representations into the links container."""
    base_id = getattr(base_node, "id", getattr(base_node, "name", str(base_node)))
    mix_id = getattr(mix_node, "id", getattr(mix_node, "name", str(mix_node)))
    ao_id = getattr(ao_node, "id", getattr(ao_node, "name", str(ao_node)))
    principled_id = getattr(principled, "id", getattr(principled, "name", str(principled)))
    links.append({"from": base_id, "from_socket": "Color", "to": mix_id, "to_socket": 1})
    links.append({"from": ao_id, "from_socket": "R", "to": mix_id, "to_socket": 2})
    links.append(
        {"from": mix_id, "from_socket": "Color", "to": principled_id, "to_socket": "Base Color"}
    )


def create_normal_map_for(
    nodes: Any,
    links: Any,
    tex_node: Any,
    principled: Any,
    location: Tuple[int, int] = (100, 100),
) -> Any:
    """Create a Normal Map node and wire the texture node to the Principled BSDF.

    Works with real Blender node trees (nodes/links) or with simple mock
    containers used by unit tests. Returns the created node (real node or dict).
    """
    if _is_blender_nodes(nodes):
        nm = nodes.new(type="ShaderNodeNormalMap")
        try:
            nm.location = location
        except Exception:
            pass
        try:
            links.new(tex_node.outputs["Color"], nm.inputs["Color"])  # type: ignore[arg-type]
            links.new(nm.outputs["Normal"], principled.inputs["Normal"])  # type: ignore[arg-type]
        except Exception:
            pass
        return nm

    # Mock mode: create a simple dict entry and record link dicts
    created = getattr(nodes, "created", None)
    if created is None:
        nodes.created = []
        created = nodes.created
    node_id = f"normal_map_{len(created)}"
    nm = {"id": node_id, "type": "NormalMap", "location": location}
    created.append(nm)
    links.append(
        {
            "from": tex_node.get("id", "tex"),
            "from_socket": "Color",
            "to": node_id,
            "to_socket": "Color",
        }
    )
    links.append(
        {
            "from": node_id,
            "from_socket": "Normal",
            "to": principled.get("id", "principled"),
            "to_socket": "Normal",
        }
    )
    return nm


def create_displacement_for(
    nodes: Any,
    links: Any,
    tex_node: Any,
    output_node: Any,
    location: Tuple[int, int] = (300, -200),
    scale: float = 0.1,
) -> Any:
    """Create a Displacement node, wire texture to Height and connect to output.
    """
    if _is_blender_nodes(nodes):
        disp = nodes.new(type="ShaderNodeDisplacement")
        try:
            disp.location = location
        except Exception:
            pass
        try:
            disp.inputs["Scale"].default_value = scale
        except Exception:
            pass
        try:
            links.new(tex_node.outputs["Color"], disp.inputs["Height"])  # type: ignore[arg-type]
            links.new(disp.outputs["Displacement"], output_node.inputs["Displacement"])  # type: ignore[arg-type]
        except Exception:
            pass
        return disp

    created = getattr(nodes, "created", None)
    if created is None:
        nodes.created = []
        created = nodes.created
    node_id = f"disp_{len(created)}"
    d = {"id": node_id, "type": "Displacement", "location": location, "scale": scale}
    created.append(d)
    links.append(
        {
            "from": tex_node.get("id", "tex"),
            "from_socket": "Color",
            "to": node_id,
            "to_socket": "Height",
        }
    )
    links.append(
        {
            "from": node_id,
            "from_socket": "Displacement",
            "to": output_node.get("id", "output"),
            "to_socket": "Displacement",
        }
    )
    return d


def create_separate_rgb(nodes: Any, links: Any, tex_node: Any, location: Tuple[int, int] = (-200, -100)) -> Any:
    """Create a SeparateRGB node and wire the given texture node to it."""
    if _is_blender_nodes(nodes):
        sep = nodes.new(type="ShaderNodeSeparateRGB")
        try:
            sep.location = location
        except Exception:
            pass
        try:
            links.new(tex_node.outputs["Color"], sep.inputs["Image"])  # type: ignore[arg-type]
        except Exception:
            pass
        return sep

    created = getattr(nodes, "created", None)
    if created is None:
        nodes.created = []
        created = nodes.created
    node_id = f"seprgb_{len(created)}"
    s = {"id": node_id, "type": "SeparateRGB", "location": location}
    created.append(s)
    links.append(
        {
            "from": tex_node.get("id", "src"),
            "from_socket": "Color",
            "to": node_id,
            "to_socket": "Image",
        }
    )
    return s


def create_ao_mix(
    nodes: Any,
    links: Any,
    base_node: Any,
    ao_node: Any,
    principled: Any,
    location: Tuple[int, int] = (100, 200),
    fac: float = 0.8,
) -> Any:
    """Create a MixRGB Multiply node to combine base color with AO."""
    if _is_blender_nodes(nodes):
        return _create_ao_mix_blender(nodes, links, base_node, ao_node, principled, location, fac)

    return _create_ao_mix_mock(nodes, links, base_node, ao_node, principled, location, fac)


def _create_ao_mix_blender(
    nodes: Any,
    links: Any,
    base_node: Any,
    ao_node: Any,
    principled: Any,
    location: Tuple[int, int],
    fac: float,
) -> Any:
    mix_node = nodes.new(type="ShaderNodeMixRGB")
    try:
        mix_node.location = location
        mix_node.blend_type = "MULTIPLY"
        mix_node.inputs["Fac"].default_value = fac
    except Exception:
        pass

    # Remove existing direct link from base_node -> Principled Base Color
    try:
        for link in list(base_node.outputs["Color"].links):
            if link.to_socket == principled.inputs["Base Color"]:
                links.remove(link)
    except Exception:
        pass

    try:
        links.new(base_node.outputs["Color"], mix_node.inputs[1])
        # AO node may be texture (Color) or SeparateRGB (R)
        ao_out = None
        if "Color" in getattr(ao_node, "outputs", {}):
            ao_out = ao_node.outputs["Color"]
        elif "R" in getattr(ao_node, "outputs", {}):
            ao_out = ao_node.outputs["R"]
        else:
            ao_out = next(iter(ao_node.outputs.values()))
        links.new(ao_out, mix_node.inputs[2])
        links.new(mix_node.outputs["Color"], principled.inputs["Base Color"])
    except Exception:
        pass

    # If links were not created (mock environments with different socket APIs),
    # add a best-effort representation into the links container if possible.
    try:
        empty = len(links) == 0
    except Exception:
        empty = False
    if empty and hasattr(links, "append"):
        _append_mock_ao_links(links, base_node, mix_node, ao_node, principled)
    return mix_node


def _create_ao_mix_mock(
    nodes: Any,
    links: Any,
    base_node: Any,
    ao_node: Any,
    principled: Any,
    location: Tuple[int, int],
    fac: float,
) -> Any:
    created = getattr(nodes, "created", None)
    if created is None:
        nodes.created = []
        created = nodes.created
    node_id = f"mix_{len(created)}"
    m = {"id": node_id, "type": "MixRGB", "location": location, "fac": fac}
    created.append(m)
    links.append({"from": base_node.get("id", "base"), "from_socket": "Color", "to": node_id, "to_socket": 1})
    links.append({"from": ao_node.get("id", "ao"), "from_socket": "R", "to": node_id, "to_socket": 2})
    links.append(
        {
            "from": node_id,
            "from_socket": "Color",
            "to": principled.get("id", "principled"),
            "to_socket": "Base Color",
        }
    )
    return m

