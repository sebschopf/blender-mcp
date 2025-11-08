from blender_mcp.services.polyhaven import (
    download_asset_message,
    format_categories_output,
    format_search_assets,
)


def test_format_categories_output():
    cats = {"a": 10, "b": 5}
    out = format_categories_output(cats, "textures")
    assert "Categories for textures" in out
    assert "- a: 10 assets" in out


def test_format_search_assets():
    result = {
        "assets": {
            "id1": {"name": "Tex1", "type": 1, "categories": ["c1"], "download_count": 3}
        },
        "total_count": 1,
        "returned_count": 1,
    }
    out = format_search_assets(result, "c1")
    assert "Found 1 assets" in out
    assert "Tex1" in out


def test_download_asset_message_textures():
    res = {"success": True, "message": "ok", "material": "mat1", "maps": ["diff"]}
    out = download_asset_message(res, "textures")
    assert "Created material 'mat1'" in out
