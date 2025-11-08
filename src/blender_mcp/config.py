from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BridgeConfig:
    verbose: bool = False
    save_blend: bool = False
    photoreal: bool = False
    engraving_default: Optional[str] = "geometry"
    mcp_base: str = "http://127.0.0.1:8000"
    gemini_model: str = "gemini-2.5-flash"

    @classmethod
    def from_env(cls) -> "BridgeConfig":
        import os

        return cls(
            verbose=False,
            save_blend=False,
            photoreal=False,
            engraving_default=os.environ.get("GEMINI_BRIDGE_ENGRAVING", "geometry"),
            mcp_base=os.environ.get("MCP_BASE", "http://127.0.0.1:8000"),
            gemini_model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        )
