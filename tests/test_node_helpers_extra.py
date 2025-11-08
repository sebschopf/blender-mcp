class MockSocket:
    def __init__(self, node_id: str, name: str):
        self.node_id = node_id
        self.name = name

    def __repr__(self):
        return f"Socket({self.node_id}.{self.name})"


class MockNode:
    def __init__(self, node_id: str, type_name: str):
        self.id = node_id
        self.type = type_name
        # common sockets
        self.outputs = {
            "Color": MockSocket(node_id, "Color"),
            "Normal": MockSocket(node_id, "Normal"),
            "R": MockSocket(node_id, "R"),
        }
        self.inputs = {
            "Color": MockSocket(node_id, "Color"),
            "Image": MockSocket(node_id, "Image"),
            "Height": MockSocket(node_id, "Height"),
            "Fac": MockSocket(node_id, "Fac"),
        }


class MockNodes:
    def __init__(self):
        self.created = []

    def new(self, type=None):
        node = MockNode(f"node_{len(self.created)}", type or "")
        self.created.append({"id": node.id, "type": node.type})
        return node


class MockLinks(list):
    def new(self, a, b):
        # a and b are socket-like objects; record a simple dict
        from_node = getattr(a, "node_id", getattr(a, "id", str(a)))
        from_sock = getattr(a, "name", None)
        to_node = getattr(b, "node_id", getattr(b, "id", str(b)))
        to_sock = getattr(b, "name", None)
        self.append({"from": from_node, "from_socket": from_sock, "to": to_node, "to_socket": to_sock})


from blender_mcp.node_helpers import (
    create_ao_mix,
    create_displacement_for,
    create_normal_map_for,
    create_separate_rgb,
)


def test_create_normal_map_for_mock():
    nodes = MockNodes()
    links = MockLinks()
    tex = MockNode("tex0", "Tex")
    principled = MockNode("principled", "Principled")

    nm = create_normal_map_for(nodes, links, tex, principled, (100, 100))
    assert isinstance(nm, (dict, MockNode))
    assert nodes.created
    assert any(n["type"].endswith("NormalMap") or n["type"] == "NormalMap" for n in nodes.created)
    assert any(isinstance(l, dict) for l in links)


def test_create_displacement_for_mock():
    nodes = MockNodes()
    links = MockLinks()
    tex = MockNode("tex1", "Tex")
    output = MockNode("output", "Output")

    d = create_displacement_for(nodes, links, tex, output, (10, -10), scale=0.2)
    assert isinstance(d, (dict, MockNode))
    dtype = d["type"] if isinstance(d, dict) else getattr(d, "type", None)
    assert dtype in ("Displacement", "ShaderNodeDisplacement")
    assert any(isinstance(l, dict) for l in links)


def test_create_separate_rgb_mock():
    nodes = MockNodes()
    links = MockLinks()
    src = MockNode("src0", "Src")

    s = create_separate_rgb(nodes, links, src, (0, 0))
    assert isinstance(s, (dict, MockNode))
    stype = s["type"] if isinstance(s, dict) else getattr(s, "type", None)
    assert stype in ("SeparateRGB", "ShaderNodeSeparateRGB")


def test_create_ao_mix_mock():
    nodes = MockNodes()
    links = MockLinks()
    base = MockNode("base", "Base")
    sep = MockNode("sep", "Sep")
    principled = MockNode("principled", "Principled")

    m = create_ao_mix(nodes, links, base, sep, principled, (1, 2), fac=0.5)
    assert isinstance(m, (dict, MockNode))
    mtype = m["type"] if isinstance(m, dict) else getattr(m, "type", None)
    assert mtype in ("MixRGB", "ShaderNodeMixRGB")
    assert any(isinstance(l, dict) for l in links)
