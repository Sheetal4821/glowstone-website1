#!/usr/bin/env python3
"""
Process slab source images for Domestic Calacatta, Carrara, Onyx, Pastel, Plain.

Source roots (see typos/spaces in paths):
  files/ serises/calacatta series/slab images
  files/ serises/carrara series /slab images
  files/ serises/onyx series/slab images
  files/ serises/pastel series /slab images
  files/ serises/plain series/slab images
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

FILES_SERISES = ROOT / "files" / " serises"

SERIES: list[tuple[str, Path, Path, dict[str, str]]] = [
    (
        "calacatta",
        FILES_SERISES / "calacatta series" / "slab images",
        ROOT / "images" / "collections" / "calacatta-series",
        {
            "alabadma": "alabama",
            "aspen gold": "aspen-gold",
            "aurika": "aurika",
            "avalanche": "avalanche",
            "everest grey": "everest-grey",
            "harmony gold": "harmony-gold",
            "maarquina noir": "marquina-noir",
            "narina gold": "narina-gold",
            "narina grey": "narina-grey",
            "nova": "nova",
            "panda white": "panda-white",
            "pearl venata": "perla-venata",
            "sahara noir": "sahara-noir",
            "vienna": "vienna",
        },
    ),
    (
        "carrara",
        FILES_SERISES / "carrara series " / "slab images",
        ROOT / "images" / "collections" / "carrara-series",
        {
            "aurum": "aurum",
            "bellagio": "bellagio",
            "bianco nova": "bianco-nova",
            "blaze": "blaze",
            "fosil": "fossil",
            "gold mine": "gold-mine",
            "orion white": "orion-white",
            "rayon": "rayon",
        },
    ),
    (
        "onyx",
        FILES_SERISES / "onyx series" / "slab images",
        ROOT / "images" / "collections" / "onyx-series",
        {
            "crystal ash": "crystal-ash",
            "luminous gold": "luminous-gold",
            "marigold": "marigold",
            "nectar": "nectar",
            "trinity": "trinity",
        },
    ),
    (
        "pastel",
        FILES_SERISES / "pastel series " / "slab images",
        ROOT / "images" / "collections" / "pastel-series",
        {
            "mauve": "mauve",
            "peony": "peony",
            "sage": "sage",
            "seaform": "seafoam",
        },
    ),
    (
        "plain",
        FILES_SERISES / "plain series" / "slab images",
        ROOT / "images" / "collections" / "plain-series",
        {
            "frost white": "frost-white",
            "glacier white": "glacier-white",
            "meraki": "meraki",
        },
    ),
]


def main() -> None:
    full_manifest: dict[str, dict[str, list[str]]] = {}

    for series_key, src, out_root, folder_map in SERIES:
        print("\n===", series_key.upper(), "===")
        process_source_tree(src, out_root, folder_map)
        man = collect_manifest_for_out_root(out_root)
        full_manifest[series_key] = man

        html_for_slug = {slug: f"collection-domestic-{series_key}-{slug}.html" for slug in man}
        sync_html_pages(man, html_for_slug)

    manifest_path = ROOT / "scripts" / "domestic_series_slab_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(full_manifest, f, indent=2)
    print("\nWrote", manifest_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
