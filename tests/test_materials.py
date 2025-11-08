from blender_mcp.materials import _build_spec_from_keys, build_material_spec


def test_build_spec_from_keys_basic():
    keys = ["color", "roughness", "metallic", "normal", "displacement"]
    spec = _build_spec_from_keys(keys)
    assert spec["base_color"] == "color"
    assert spec["roughness"] in ("roughness", "rough", "arm.g")
    assert spec["metallic"] in ("metallic", "metal", "arm.b")
    assert spec["normal"] in ("normal", "nor")
    assert spec["displacement"] in ("displacement", "disp", "height")


def test_build_material_spec_mapping():
    images_map = {
        "color": "col.png",
        "roughness": "r.png",
        "normal": "n.png",
    }
    spec = build_material_spec(images_map, material_name="mat1")
    assert spec["name"] == "mat1"
    # Check nodes include principled and output
    types = {n["type"] for n in spec["nodes"]}
    assert "ShaderNodeBsdfPrincipled" in types
    assert "ShaderNodeOutputMaterial" in types
    # Ensure links include Base Color and Roughness destinations
    dests = {(l["to_node"], l["to_socket"]) for l in spec["links"]}
    assert ("principled", "Base Color") in dests
    assert ("principled", "Roughness") in dests
