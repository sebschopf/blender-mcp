from blender_mcp.services.hyper3d import prepare_rodin_payload


def test_prepare_rodin_payload_text():
    payload = prepare_rodin_payload("a prompt", None, [1, 1])
    assert payload["text_prompt"] == "a prompt"
    assert payload["images"] is None
    assert isinstance(payload["bbox_condition"], list)


def test_prepare_rodin_payload_images():
    payload = prepare_rodin_payload(None, ["http://x"], None)
    assert payload["text_prompt"] is None
    assert payload["images"] == ["http://x"]
