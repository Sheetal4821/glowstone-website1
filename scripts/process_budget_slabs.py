#!/usr/bin/env python3
"""
Process Budget Series slab images from:
  files/ serises/budget series/slab images /
"""

from __future__ import annotations

import json
from pathlib import Path

from slab_common import (
    ROOT,
    collect_manifest_for_out_root,
    process_source_tree,
    sync_html_pages,
)

SRC_PARENT = ROOT / "files" / " serises" / "budget series" / "slab images "
OUT_PARENT = ROOT / "images" / "collections" / "budget-series"
MANIFEST_JSON = ROOT / "scripts" / "budget_slab_manifest.json"

FOLDER_TO_SLUG = {
    "black starlight": "black-starlight",
    "brown starlight": "brown-starlight",
    "cream mirrior": "cream-mirror",
    "cream mirror": "cream-mirror",
    "crema": "crema",
    "gracio": "gracio",
    "gret starlight": "grey-starlight",
    "grey starlight": "grey-starlight",
    "grey terrazo": "grey-terrazo",
    "halo": "halo",
    "snow flake": "snowflake",
    "walnut": "walnut",
    "white starlight": "white-starlight",
    "white terrazo": "white-terrazo",
}

HTML_FOR_SLUG = {
    slug: f"collection-domestic-budget-{slug}.html"
    for slug in [
        "black-starlight",
        "brown-starlight",
        "cream-mirror",
        "crema",
        "gracio",
        "grey-starlight",
        "grey-terrazo",
        "halo",
        "snowflake",
        "walnut",
        "white-starlight",
        "white-terrazo",
    ]
}


def main() -> None:
    if SRC_PARENT.is_dir():
        process_source_tree(SRC_PARENT, OUT_PARENT, FOLDER_TO_SLUG)
    else:
        print("Missing source:", SRC_PARENT)

    manifest = collect_manifest_for_out_root(OUT_PARENT)
    with open(MANIFEST_JSON, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("Wrote", MANIFEST_JSON.relative_to(ROOT))

    txt_path = ROOT / "scripts" / "budget_slab_manifest.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        for slug in sorted(manifest):
            f.write(f"{slug}: {','.join(manifest[slug])}\n")

    sync_html_pages(manifest, HTML_FOR_SLUG)


if __name__ == "__main__":
    main()
