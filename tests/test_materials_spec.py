import os
import sys

# Ensure local src is importable
TEST_ROOT = os.path.dirname(__file__)
SRC_PATH = os.path.abspath(os.path.join(TEST_ROOT, "..", "src"))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from blender_mcp.materials import build_material_spec


def test_build_material_spec_basic():
    keys = ["color", "roughness", "normal"]
    spec = build_material_spec(keys)
    assert spec["base_color"] == "color"
    assert spec["roughness"] == "roughness"
    assert spec["normal"] == "normal"


def test_build_material_spec_arm_fallback():
    keys = ["color", "arm"]
    spec = build_material_spec(keys)
    assert spec["base_color"] == "color"
    # arm provides roughness (G) and metallic (B) when separate maps absent
    assert spec["roughness"] == "arm.g"
    assert spec["metallic"] == "arm.b"
