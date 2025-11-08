"""Unit tests for node_helpers using minimal fake node/links objects.

These tests avoid importing `bpy` by providing small fakes that implement
the minimal surface used by the helpers: nodes.new(...), links.new(src, dst),
and sockets with `.links` lists. The goal is to validate wiring logic.
"""
from __future__ import annotations

from typing import List

from blender_mcp import node_helpers


class FakeSocket:
    def __init__(self, name: str, node: "FakeNode") -> None:
        self.name = name
        self.node = node
        self.links: List[FakeLink] = []


class FakeLink:
    def __init__(self, from_socket: FakeSocket, to_socket: FakeSocket) -> None:
        self.from_socket = from_socket
        self.to_socket = to_socket


class FakeNode:
    def __init__(self, node_type: str) -> None:
        self.type = node_type
        self.location = (0, 0)
        # simple mapping of sockets by common names used in helpers
        # Configure inputs/outputs depending on node type to mimic Blender
        if node_type == "ShaderNodeNormalMap":
            self.inputs = {"Color": FakeSocket("Color", self)}
            self.outputs = {"Normal": FakeSocket("Normal", self)}
        elif node_type == "ShaderNodeDisplacement":
            self.inputs = {"Height": FakeSocket("Height", self), "Scale": FakeSocket("Scale", self)}
            self.outputs = {"Displacement": FakeSocket("Displacement", self)}
        elif node_type == "ShaderNodeSeparateRGB":
            self.inputs = {"Image": FakeSocket("Image", self)}
            self.outputs = {
                "R": FakeSocket("R", self),
                "G": FakeSocket("G", self),
                "B": FakeSocket("B", self),
            }
        elif node_type == "ShaderNodeMixRGB":
            # Mix node supports string key 'Fac' and numeric indices for inputs 1/2
            self.inputs = {"Fac": FakeSocket("Fac", self), 1: FakeSocket("1", self), 2: FakeSocket("2", self)}
            self.outputs = {"Color": FakeSocket("Color", self)}
        else:
            # Default for image/texture nodes and others
            self.outputs = {"Color": FakeSocket("Color", self)}
            self.inputs = {"Color": FakeSocket("Color", self), "Height": FakeSocket("Height", self)}


class FakeNodes:
    def __init__(self) -> None:
        self._nodes: List[FakeNode] = []

    def new(self, type: str) -> FakeNode:
        n = FakeNode(type)
        self._nodes.append(n)
        return n


class FakeLinks:
    def __init__(self) -> None:
        self.created: List[FakeLink] = []

    def new(self, from_socket: FakeSocket, to_socket: FakeSocket) -> FakeLink:
        link = FakeLink(from_socket, to_socket)
        from_socket.links.append(link)
        to_socket.links.append(link)
        self.created.append(link)
        return link

    def remove(self, link: FakeLink) -> None:
        with suppress_value_errors():
            link.from_socket.links.remove(link)
        with suppress_value_errors():
            link.to_socket.links.remove(link)
        with suppress_value_errors():
            self.created.remove(link)


def suppress_value_errors():
    """Context manager that ignores ValueError during removals."""
    class CM:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return exc_type is ValueError

    return CM()


def make_principled(nodes: FakeNodes) -> FakeNode:
    p = FakeNode("BSDF_PRINCIPLED")
    # add typical inputs the helpers target
    p.inputs = {
        "Base Color": FakeSocket("Base Color", p),
        "Roughness": FakeSocket("Roughness", p),
        "Metallic": FakeSocket("Metallic", p),
        "Normal": FakeSocket("Normal", p),
    }
    nodes._nodes.append(p)
    return p


def make_output(nodes: FakeNodes) -> FakeNode:
    o = FakeNode("OUTPUT_MATERIAL")
    o.inputs = {"Displacement": FakeSocket("Displacement", o)}
    nodes._nodes.append(o)
    return o


def test_create_normal_map_for_wires_normal_and_principled():
    nodes = FakeNodes()
    links = FakeLinks()
    tex = nodes.new(type="TEX_IMAGE")
    principled = make_principled(nodes)

    normal = node_helpers.create_normal_map_for(nodes, links, tex, principled, (10, 20))

    # normal node should be created
    assert normal.type == "ShaderNodeNormalMap" or normal.type == "ShaderNodeNormalMap"
    # There should be exactly one link from tex.outputs['Color']
    assert len(tex.outputs["Color"].links) == 1
    link = tex.outputs["Color"].links[0]
    assert link.to_socket in normal.inputs.values() or link.to_socket == normal.inputs.get("Color")
    # Principled should have one incoming normal link
    assert any(l.to_socket in principled.inputs.values() for l in links.created)


def test_create_displacement_for_wires_to_output():
    nodes = FakeNodes()
    links = FakeLinks()
    tex = nodes.new(type="TEX_IMAGE")
    output = make_output(nodes)

    disp = node_helpers.create_displacement_for(nodes, links, tex, output, (1, 2), 0.2)

    # displacement node created
    assert disp.type == "ShaderNodeDisplacement"
    # tex should have a link to displacement height
    assert len(tex.outputs["Color"].links) == 1
    # output should have a link from displacement
    assert len(output.inputs["Displacement"].links) == 1


def test_create_separate_rgb_and_ao_mix():
    nodes = FakeNodes()
    links = FakeLinks()
    tex = nodes.new(type="TEX_IMAGE")
    principled = make_principled(nodes)
    base = nodes.new(type="TEX_IMAGE")

    sep = node_helpers.create_separate_rgb(nodes, links, tex, (-5, -5))
    assert sep.type == "ShaderNodeSeparateRGB"
    # ensure link created between tex and separate rgb
    assert len(tex.outputs["Color"].links) == 1

    # create a fake existing link from base -> principled Base Color
    links.new(base.outputs["Color"], principled.inputs["Base Color"])
    assert len(base.outputs["Color"].links) == 1

    mix = node_helpers.create_ao_mix(nodes, links, base, sep, principled, (0, 0), 0.5)
    assert mix.type == "ShaderNodeMixRGB"
    # base should no longer have a direct link to principled base color
    assert all(l.to_socket != principled.inputs["Base Color"] for l in base.outputs["Color"].links)
    # mix node should be linked to principled
    assert any(l.to_socket == principled.inputs["Base Color"] for l in links.created)
