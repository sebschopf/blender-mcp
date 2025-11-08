from blender_mcp.materials import build_material_spec


def test_build_material_spec_basic():
    images = {
        "color": "albedo.png",
        "roughness": "rough.png",
        "normal": "normal.png",
    }
    spec = build_material_spec(images, "TestMaterial")

    assert spec["name"] == "TestMaterial"

    # Must contain principled and output nodes
    node_types = {n["type"]: n for n in spec["nodes"]}
    assert "ShaderNodeBsdfPrincipled" in node_types
    assert "ShaderNodeOutputMaterial" in node_types

    # Ensure base color tex image node present and linked to principled base color
    tex_nodes = [n for n in spec["nodes"] if n["type"] == "ShaderNodeTexImage"]
    imgs = {n.get("image") for n in tex_nodes}
    assert "albedo.png" in imgs
    assert "rough.png" in imgs
    assert "normal.png" in imgs

    # Check essential links exist: principled->output, tex(base_color)->principled Base Color
    link_pairs = {(l["from_node"], l["to_node"], l["to_socket"]) for l in spec["links"]}
    assert ("principled", "output", "Surface") in link_pairs
    # there should be at least one link to principled Base Color
    assert any(l["to_node"] == "principled" and l["to_socket"] == "Base Color" for l in spec["links"])
