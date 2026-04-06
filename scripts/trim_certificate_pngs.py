#!/usr/bin/env python3
"""
Trim certificate PNGs: remove large transparent margins (exports are often ~9989² canvases).
Safe for white-on-transparent marks — only fully transparent rows/cols are shaved.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

CERT_DIR = Path(__file__).resolve().parent.parent / "images" / "certificates"
FILES = ("ce-logo.png", "iso-logo.png", "greenguard-logo.png", "nsf-logo.png")

# Pixels with alpha below this are treated as empty for edge shaving.
ALPHA_EMPTY = 22

# Longest edge after trim (enough for ~120px CSS × DPR)
MAX_SIDE = 900


def transparent_crop_box(alpha: np.ndarray) -> tuple[int, int, int, int]:
    """Inclusive-exclusive crop from edges while rows/cols are entirely 'empty'."""
    h, w = alpha.shape
    empty = alpha < ALPHA_EMPTY

    top = 0
    while top < h and empty[top].all():
        top += 1
    bottom = h - 1
    while bottom > top and empty[bottom].all():
        bottom -= 1
    left = 0
    while left < w and empty[:, left].all():
        left += 1
    right = w - 1
    while right > left and empty[:, right].all():
        right -= 1

    if top > bottom or left > right:
        return 0, 0, w, h
    return left, top, right + 1, bottom + 1


def downscale_max_side(im: Image.Image, max_side: int) -> Image.Image:
    w, h = im.size
    m = max(w, h)
    if m <= max_side:
        return im
    if w >= h:
        nw = max_side
        nh = max(1, int(round(h * max_side / w)))
    else:
        nh = max_side
        nw = max(1, int(round(w * max_side / h)))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def main() -> None:
    for name in FILES:
        path = CERT_DIR / name
        if not path.exists():
            print(f"skip (missing): {path}")
            continue

        im = Image.open(path)
        im.load()
        w0, h0 = im.size
        arr = np.asarray(im.convert("RGBA"))
        l, t, r, b = transparent_crop_box(arr[:, :, 3])
        cropped = Image.fromarray(arr[t:b, l:r])
        w1, h1 = cropped.size
        out = downscale_max_side(cropped, MAX_SIDE)
        w2, h2 = out.size
        out.save(path, optimize=True, compress_level=9)
        print(f"{name}: {w0}x{h0} -> trim {w1}x{h1} -> save {w2}x{h2}")


if __name__ == "__main__":
    main()
