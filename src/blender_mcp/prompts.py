import logging
from pathlib import Path

from .tools import mcp


@mcp.prompt()
def asset_creation_strategy() -> str:
    """Load a long human-facing prompt from a template kept out of the source to satisfy linters."""
    try:
        tpl_path = (
            Path(__file__).resolve().parent
            / "templates"
            / "asset_creation_strategy.txt"
        )
        if tpl_path.exists():
            return tpl_path.read_text(encoding="utf-8")
    except Exception:
        logger = logging.getLogger("blender_mcp.prompts")
        logger.debug(
            "Could not load asset_creation_strategy template, using fallback",
            exc_info=True,
        )

    # Fallback short message for cases where the template is not available
    return (
        "Check integrations (PolyHaven, Sketchfab, Hyper3D) with get_*_status() and prefer "
        "available libraries before scripting or generation. Use generate_*/poll/import workflow."
    )
