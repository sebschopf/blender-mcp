"""Re-export of `node_helpers` into services.templates for incremental migration."""

from __future__ import annotations

from ... import node_helpers as _node_helpers

# Re-export helpers
output_node = _node_helpers.output_node
principled_node = _node_helpers.principled_node
texcoord_node = _node_helpers.texcoord_node
mapping_node = _node_helpers.mapping_node
tex_image_node = _node_helpers.tex_image_node
normal_map_node = _node_helpers.normal_map_node
displacement_node = _node_helpers.displacement_node
make_link = _node_helpers.make_link
create_normal_map_for = _node_helpers.create_normal_map_for
create_displacement_for = _node_helpers.create_displacement_for
create_separate_rgb = _node_helpers.create_separate_rgb
create_ao_mix = _node_helpers.create_ao_mix

__all__ = [
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
