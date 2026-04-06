#!/usr/bin/env python3
"""Add missing canonical, robots, theme-color, Open Graph, and Twitter meta to HTML heads."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.glowstone.co.in"
DEFAULT_OG_IMAGE = f"{BASE}/images/hero-2.jpg"


def esc_attr(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;")


def collection_image_url(html: str) -> str:
    _head, sep, body = html.partition("</head>")
    if not sep:
        body = html
    m = re.search(r'fetchpriority="high"[^>]+src="([^"]+)"', body, re.I)
    if not m:
        m = re.search(r'src="(images/collections/[^"]+)"', body)
    if not m:
        return DEFAULT_OG_IMAGE
    path = m.group(1).strip()
    if path.startswith("http"):
        return path
    path = path.lstrip("/")
    return f"{BASE}/{path}"


def build_canonical_block(html: str, filename: str) -> str:
    url = f"{BASE}/{filename}"
    lines: list[str] = []
    if 'name="theme-color"' not in html[:4000]:
        lines.append('    <meta name="theme-color" content="#0f0f0f">')
    if not re.search(r'<meta\s+name="robots"\s', html[:4000]):
        lines.append('    <meta name="robots" content="index, follow">')
    if 'rel="canonical"' not in html:
        lines.append(f'    <link rel="canonical" href="{url}">')
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def inject_canonical_block(html: str, block: str) -> str:
    if not block:
        return html
    if re.search(r'<meta\s+name="keywords"\s', html[:3000]):
        return re.sub(
            r'(<meta\s+name="keywords"\s+content="[^"]*">\s*\n)',
            r"\1" + block,
            html,
            count=1,
        )
    return re.sub(
        r'(<meta\s+name="description"\s+content="[^"]*">\s*\n)',
        r"\1" + block,
        html,
        count=1,
    )


def normalize_canonical_to_file(html: str, filename: str) -> str:
    """If canonical path last segment equals the file stem and has no .html, append .html."""
    if not filename.endswith(".html"):
        return html
    stem = filename.removesuffix(".html")
    m = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html)
    if not m:
        return html
    url = m.group(1).strip()
    path = urlparse(url).path.strip("/")
    last = path.split("/")[-1] if path else ""
    if last != stem or url.endswith(".html"):
        return html
    new_url = url + ".html"
    html = html.replace(m.group(0), f'<link rel="canonical" href="{new_url}"', 1)
    html = html.replace(
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:url" content="{new_url}">',
    )
    return html


def inject_og_block(html: str, filename: str, page_url: str) -> str:
    if 'property="og:title"' in html:
        return html
    tm = re.search(r"<title>([^<]+)</title>", html)
    dm = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    og_title = esc_attr(tm.group(1).strip() if tm else "Glowstone")
    og_desc = esc_attr(dm.group(1).strip() if dm else "")
    og_image = collection_image_url(html)
    block = f"""    <meta property="og:title" content="{og_title}">
    <meta property="og:description" content="{og_desc}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{page_url}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:locale" content="en_IN">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{og_title}">
    <meta name="twitter:description" content="{og_desc}">
"""
    return re.sub(
        r"(</title>\s*\n)",
        r"\1" + block,
        html,
        count=1,
    )


def main() -> None:
    changed = 0
    for path in sorted(ROOT.glob("*.html")):
        raw = path.read_text(encoding="utf-8")
        html = raw
        fname = path.name
        block = build_canonical_block(html, fname)
        html = inject_canonical_block(html, block)
        html = normalize_canonical_to_file(html, fname)
        cm = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html)
        page_url = cm.group(1) if cm else f"{BASE}/{fname}"
        html = inject_og_block(html, fname, page_url)
        if html != raw:
            path.write_text(html, encoding="utf-8")
            changed += 1
            print(fname)
    print(f"Updated {changed} files.", file=sys.stderr)


if __name__ == "__main__":
    main()
