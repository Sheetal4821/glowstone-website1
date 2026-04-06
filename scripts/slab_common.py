"""Shared slab image pipeline: trim, resize, JPEG export, HTML slab block builders."""

from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

# Large supplier photos may exceed PIL’s default decompression limit
Image.MAX_IMAGE_PIXELS = 280_000_000

ROOT = Path(__file__).resolve().parents[1]
JPEG_QUALITY = 86
MAX_LONG_EDGE = 2000
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}

SLAB_BLOCK_PATTERN = re.compile(
    r'(                    <div class="product-slab-image">\n)(.*?)(\n                    </div>\n                    <div class="product-content">)',
    re.DOTALL,
)


def normalize_folder_key(name: str) -> str:
    return name.strip().lower().replace("  ", " ")


def label_from_slug(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.split("-"))


def carousel_id_suffix_from_slug(slug: str) -> str:
    return "".join(w.capitalize() for w in slug.split("-"))


def is_closeup(name: str) -> bool:
    n = name.lower().replace("_", " ")
    return "close up" in n or "closeup" in n.replace(" ", "")


def is_backlit(name: str) -> bool:
    """True when filename suggests a backlit shot (not used if already classified as close-up)."""
    n = name.lower().replace("_", " ")
    compact = n.replace(" ", "")
    return (
        "backlit" in compact
        or "backlit" in n
        or "back lit" in n
        or "backlight" in compact
        or "back light" in n
    )


def slab_sort_key(fn: str) -> tuple[int, int, str]:
    """
    Order: full slab → close-ups (plain before backlit+close-up) → backlit-only.
    """
    if is_closeup(fn):
        # Close-ups that are also backlit sort after plain close-ups
        sub = 1 if is_backlit(fn) else 0
        return (1, sub, fn.lower())
    if is_backlit(fn):
        return (2, 0, fn.lower())
    return (0, 0, fn.lower())


def sort_slab_files(files: list[str]) -> list[str]:
    return sorted(files, key=slab_sort_key)


def sort_output_paths(paths: list[Path]) -> list[Path]:
    def key(p: Path) -> tuple[int, int, str]:
        stem = p.stem
        if stem == "slab":
            return (0, 0, stem)
        if stem.startswith("slab-"):
            try:
                return (0, int(stem.split("-", 1)[1]), stem)
            except ValueError:
                pass
        return (1, 0, stem)

    return sorted(paths, key=key)


def trim_content_bounds(im: Image.Image, tol: float = 28.0, margin: int = 8) -> Image.Image:
    im = ImageOps.exif_transpose(im)
    rgb = im.convert("RGB")
    w, h = rgb.size
    if h < 4 or w < 4:
        return rgb

    max_analyze = 1400
    scale = min(1.0, max_analyze / max(w, h))
    sw, sh = int(w * scale), int(h * scale)
    small = rgb.resize((sw, sh), Image.Resampling.LANCZOS)
    a = np.asarray(small, dtype=np.float32)

    edge = np.concatenate(
        [
            a[0, :, :].reshape(-1, 3),
            a[-1, :, :].reshape(-1, 3),
            a[:, 0, :].reshape(-1, 3),
            a[:, -1, :].reshape(-1, 3),
        ],
        axis=0,
    )
    bg = np.median(edge, axis=0)
    diff = np.abs(a - bg).sum(axis=2)
    mask = diff > tol
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any() or not cols.any():
        return rgb

    ys = np.where(rows)[0]
    xs = np.where(cols)[0]
    y0s, y1s = int(ys[0]), int(ys[-1]) + 1
    x0s, x1s = int(xs[0]), int(xs[-1]) + 1

    x0 = max(0, int(x0s / scale) - margin)
    y0 = max(0, int(y0s / scale) - margin)
    x1 = min(w, int(np.ceil(x1s / scale)) + margin)
    y1 = min(h, int(np.ceil(y1s / scale)) + margin)

    return rgb.crop((x0, y0, x1, y1))


def process_to_jpeg(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        out = trim_content_bounds(im)
        w, h = out.size
        if max(w, h) > MAX_LONG_EDGE:
            if w >= h:
                nw, nh = MAX_LONG_EDGE, int(h * MAX_LONG_EDGE / w)
            else:
                nh, nw = MAX_LONG_EDGE, int(w * MAX_LONG_EDGE / h)
            out = out.resize((nw, nh), Image.Resampling.LANCZOS)
        out.save(
            dest,
            "JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True,
        )


def clear_old_slabs(out_dir: Path) -> None:
    if not out_dir.is_dir():
        return
    for p in list(out_dir.glob("slab*.png")) + list(out_dir.glob("slab*.jpg")):
        try:
            p.unlink()
        except OSError:
            pass


def dest_stem_for_index(i: int) -> str:
    return "slab" if i == 0 else f"slab-{i + 1}"


def build_slab_inner_html(label: str, carousel_id: str, rel_paths: list[str]) -> str:
    if len(rel_paths) == 1:
        return (
            f'                        <img src="{rel_paths[0]}" alt="{label} slab" '
            f'width="800" height="600" loading="lazy" fetchpriority="high">'
        )

    item_lines = []
    for i, rp in enumerate(rel_paths):
        item_active = " active" if i == 0 else ""
        alt = f"{label} slab" if i == 0 else f"{label} slab view {i + 1}"
        fp = ' fetchpriority="high"' if i == 0 else ' loading="lazy"'
        item_lines.append(
            f'                                <div class="carousel-item{item_active}">\n'
            f'                                    <img src="{rp}" class="d-block w-100" alt="{alt}" '
            f'width="800" height="600"{fp}>\n'
            f"                                </div>"
        )

    fixed_inds = []
    for i in range(len(rel_paths)):
        if i == 0:
            fixed_inds.append(
                f'                                <button type="button" data-bs-target="#{carousel_id}" '
                f'data-bs-slide-to="0" class="active" aria-current="true" aria-label="Full slab"></button>'
            )
        else:
            fixed_inds.append(
                f'                                <button type="button" data-bs-target="#{carousel_id}" '
                f'data-bs-slide-to="{i}" aria-label="Slab view {i + 1}"></button>'
            )

    inner = [
        f'                        <div id="{carousel_id}" class="carousel slide carousel-fade" '
        f'data-bs-ride="carousel" data-bs-interval="6000" aria-label="{label} slab views">',
        '                            <div class="carousel-indicators">',
        *fixed_inds,
        "                            </div>",
        '                            <div class="carousel-inner">',
        *item_lines,
        "                            </div>",
        f'                            <button class="carousel-control-prev" type="button" data-bs-target="#{carousel_id}" data-bs-slide="prev">',
        '                                <span class="carousel-control-prev-icon" aria-hidden="true"></span>',
        '                                <span class="visually-hidden">Previous slab image</span>',
        "                            </button>",
        f'                            <button class="carousel-control-next" type="button" data-bs-target="#{carousel_id}" data-bs-slide="next">',
        '                                <span class="carousel-control-next-icon" aria-hidden="true"></span>',
        '                                <span class="visually-hidden">Next slab image</span>',
        "                            </button>",
        "                        </div>",
    ]
    return "\n".join(inner)


def collect_manifest_for_out_root(out_root: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    if not out_root.is_dir():
        return out
    for d in sorted(out_root.iterdir()):
        if not d.is_dir():
            continue
        jpgs = sort_output_paths(list(d.glob("slab*.jpg")))
        if jpgs:
            out[d.name] = [str(p.relative_to(ROOT)).replace("\\", "/") for p in jpgs]
            continue
        pngs = sort_output_paths(list(d.glob("slab*.png")))
        if pngs:
            out[d.name] = [str(p.relative_to(ROOT)).replace("\\", "/") for p in pngs]
    return out


def sync_html_pages(
    manifest: dict[str, list[str]],
    html_for_slug: dict[str, str],
) -> None:
    """manifest: slug -> rel paths. html_for_slug: slug -> filename in ROOT."""
    for slug, rel_paths in manifest.items():
        html_name = html_for_slug.get(slug)
        if not html_name:
            continue
        html_path = ROOT / html_name
        if not html_path.is_file():
            print("Skip HTML (missing file):", html_name)
            continue

        label = label_from_slug(slug)
        cid = "carouselSlab" + carousel_id_suffix_from_slug(slug)
        new_inner = build_slab_inner_html(label, cid, rel_paths)
        raw = html_path.read_text(encoding="utf-8")
        m = SLAB_BLOCK_PATTERN.search(raw)
        if not m:
            print("Skip HTML (no slab block):", html_name)
            continue
        updated = raw[: m.start()] + m.group(1) + new_inner + m.group(3) + raw[m.end() :]
        html_path.write_text(updated, encoding="utf-8")
        print("Updated", html_name, f"({len(rel_paths)} slab image(s))")


def process_source_tree(
    src_parent: Path,
    out_root: Path,
    folder_to_slug: dict[str, str],
) -> None:
    if not src_parent.is_dir():
        print("Missing source:", src_parent)
        return

    for entry in sorted(src_parent.iterdir()):
        if not entry.is_dir():
            continue
        key = normalize_folder_key(entry.name)
        slug = folder_to_slug.get(key)
        if not slug:
            print("Skip unmapped folder:", repr(entry.name), "in", src_parent.name)
            continue

        files = [f for f in os.listdir(entry) if Path(f).suffix.lower() in IMG_EXT]
        if not files:
            print("No images in", repr(entry.name), "— leaving", slug)
            continue

        ordered = sort_slab_files(files)
        out_dir = out_root / slug
        clear_old_slabs(out_dir)

        for i, fn in enumerate(ordered):
            stem = dest_stem_for_index(i)
            dest = out_dir / f"{stem}.jpg"
            process_to_jpeg(entry / fn, dest)
            print("Wrote", dest.relative_to(ROOT), "<-", entry.name, "/", fn)
