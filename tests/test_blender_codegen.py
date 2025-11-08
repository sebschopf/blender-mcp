from blender_mcp.blender_codegen import append_save_blend, generate_primitive_code


def test_generate_cube():
    code = generate_primitive_code({"type": "cube", "size": 2})
    assert "primitive_cube_add" in code
    assert "size=2" in code


def test_append_save_blend(tmp_path):
    base = generate_primitive_code({"type": "cube"})
    out_dir = tmp_path / "out"
    new_code = append_save_blend(base, str(out_dir))
    assert "bpy.ops.wm.save_mainfile" in new_code
    # ensure the path is present (escaped)
    assert "designed_scene_" in new_code
