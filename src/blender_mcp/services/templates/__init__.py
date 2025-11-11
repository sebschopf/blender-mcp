"""Package for template/asset specification helpers (materials, node specs).

Move pure logic for generating material specs and node templates here so it can
be tested without Blender.
"""

from .materials import build_material_spec, create_material_in_blender
from .node_helpers import (
    create_ao_mix,
    create_displacement_for,
    create_normal_map_for,
    create_separate_rgb,
    displacement_node,
    make_link,
    mapping_node,
    normal_map_node,
    output_node,
    principled_node,
    tex_image_node,
    texcoord_node,
)

__all__ = [
    "build_material_spec",
    "create_material_in_blender",
    "output_node",
    "principled_node",
    "texcoord_node",
    "mapping_node",
    "tex_image_node",
    "normal_map_node",
    "displacement_node",
    "make_link",
    "create_normal_map_for",
    "create_displacement_for",
    "create_separate_rgb",
    "create_ao_mix",
]
