"""Helpers to load and configure images for texture maps.

These helpers are intentionally small and accept a `loader` callable so
they can be unit-tested without importing `bpy`.
"""
from __future__ import annotations

from typing import Any, Callable, Optional


def configure_image(image: Any, map_type: str, pack_if_missing: bool = True) -> Any:
    """Configure an existing image object for a specific map type.

    - Sets a sensible color space: sRGB for color maps, Non-Color otherwise.
    - Packs the image if requested and not already packed.

    The `image` object is expected to expose at least:
      - image.colorspace_settings.name (assignable)
      - image.packed_file (truthy when packed)
      - image.pack() (callable)

    Returns the image for convenience.
    """
    try:
        if map_type.lower() in ("color", "diffuse", "albedo"):
            try:
                image.colorspace_settings.name = "sRGB"
            except Exception:
                # some Blender versions may not allow assignment; ignore
                pass
        else:
            try:
                image.colorspace_settings.name = "Non-Color"
            except Exception:
                pass
    except Exception:
        # If the image is missing a colorspace_settings attribute, ignore
        pass

    if pack_if_missing:
        try:
            if not getattr(image, "packed_file", None):
                try:
                    image.pack()
                except Exception:
                    # pack may not be supported in the fake object; ignore
                    pass
        except Exception:
            pass

    return image


def load_and_configure_image(
    path: str,
    map_type: str,
    name: Optional[str] = None,
    loader: Optional[Callable[[str], Any]] = None,
    pack_if_missing: bool = True,
) -> Any:
    """Load an image from `path` using `loader` and configure it for `map_type`.

    The `loader` callable must accept a single path argument and return an
    image-like object. The function will set the image.name if `name` is
    provided, configure colorspace and pack the image if requested.
    """
    if loader is None:
        raise RuntimeError("A loader callable must be provided in this environment")

    image = loader(path)
    if name:
        try:
            image.name = name
        except Exception:
            pass

    configure_image(image, map_type, pack_if_missing=pack_if_missing)
    return image
