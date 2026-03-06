#!/usr/bin/env python3
"""
notion2jekyll.py
----------------
Strip the Notion HTML wrapper from an exported .html file so its content
can be embedded inside the academicpages Jekyll template via include_relative.

The file is modified IN-PLACE. Run this once after dropping a new Notion export.

Usage:
    python3 _scripts/notion2jekyll.py _posts/my-post.html

What it removes:
  - The entire <html>/<head>/<body> scaffold
  - Notion's large <style> block (CSS reset, fonts, layout rules)
  - The Notion page header (<h1 class="page-title">) — shown by the Jekyll layout
  - 75+ inline <style>@import url(katex)…</style> tags (one per equation)
    → replaced by a single <link> to the KaTeX CDN stylesheet

What it keeps:
  - All article content (<div class="page-body"> and everything inside)
  - KaTeX-rendered math HTML (just needs the CSS loaded once)
  - Toggles, images, equations, code blocks, etc.

The output is wrapped in <div class="notion-content"> so the SCSS in
_sass/_notion.scss can style Notion-specific elements without leaking.
"""

import re
import sys
from pathlib import Path

KATEX_CSS = (
    '<link rel="stylesheet"'
    ' href="https://cdn.jsdelivr.net/npm/katex@0.16.25/dist/katex.min.css"'
    ' crossorigin="anonymous">\n'
)


def process(path: str) -> None:
    src = Path(path).read_text(encoding="utf-8")

    # Already processed — nothing to do.
    if "<html" not in src and "<body" not in src:
        print(f"  (already processed, skipping): {path}")
        return

    # ── 1. Remove the main Notion <style>…</style> block ──────────────────
    # It's the first (and largest) <style> tag; everything else is @import katex.
    src = re.sub(r"<style>(?!@import).*?</style>", "", src, count=1, flags=re.DOTALL)

    # ── 2. Extract <body> content ──────────────────────────────────────────
    m = re.search(r"<body>(.*)</body>", src, re.DOTALL)
    if not m:
        sys.exit(f"ERROR: no <body> found in {path} — is this a Notion export?")
    body = m.group(1).strip()

    # ── 3. Remove Notion page header (<header>…</header>) ─────────────────
    # Contains <h1 class="page-title"> which duplicates the Jekyll page title.
    body = re.sub(r"<header>.*?</header>", "", body, count=1, flags=re.DOTALL)

    # ── 4. Remove all remaining inline <style> tags (KaTeX @imports) ──────
    body = re.sub(r"<style[^>]*>.*?</style>", "", body, flags=re.DOTALL)

    # ── 5. Unwrap the outer <article …> tag (keep inner content) ──────────
    body = re.sub(r"^<article[^>]*>", "", body.strip())
    body = re.sub(r"</article>\s*(<span[^>]*>\s*</span>)?\s*$", "", body.strip())

    # ── 6. Remove contenteditable / user-select artifacts ─────────────────
    body = re.sub(r'\s*contenteditable="false"', "", body)
    body = re.sub(
        r'\s*style="user-select:all;-webkit-user-select:all;-moz-user-select:all"',
        "",
        body,
    )

    # ── 7. Wrap in scoped container ────────────────────────────────────────
    output = KATEX_CSS + '<div class="notion-content">\n' + body.strip() + "\n</div>\n"

    Path(path).write_text(output, encoding="utf-8")
    print(f"  Cleaned: {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <path/to/notion-export.html> ...")
        sys.exit(1)
    for arg in sys.argv[1:]:
        process(arg)
