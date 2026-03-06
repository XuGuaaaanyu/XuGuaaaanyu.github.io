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

Image handling:
  - Relative src="..." paths are rewritten to absolute /blog/... paths
  - Image directories sibling to the content file are copied to blog/
"""

import re
import shutil
import sys
import urllib.parse
from pathlib import Path

KATEX_CSS = (
    '<link rel="stylesheet"'
    ' href="https://cdn.jsdelivr.net/npm/katex@0.16.25/dist/katex.min.css"'
    ' crossorigin="anonymous">\n'
)

BLOG_DIR = Path("blog")


def rewrite_image_paths(body: str, content_file: Path) -> str:
    """Rewrite relative src="..." to absolute /blog/... and copy image dirs."""
    src_pattern = re.compile(r'src="(?!https?://)([^"]+)"')
    content_dir = content_file.parent
    copied: set[str] = set()

    def rewrite(m: re.Match) -> str:
        rel_path = m.group(1)
        # URL-decode to get the real filesystem path
        rel_decoded = urllib.parse.unquote(rel_path)
        top_dir = rel_decoded.split("/")[0]

        if top_dir and top_dir not in copied:
            src = content_dir / top_dir
            dst = BLOG_DIR / top_dir
            if src.is_dir() and not dst.exists():
                shutil.copytree(src, dst)
                print(f"  Copied images: {src} → {dst}")
            elif src.is_dir() and dst.exists():
                # Copy any missing files (idempotent)
                for item in src.iterdir():
                    if item.is_file() and not (dst / item.name).exists():
                        shutil.copy2(item, dst / item.name)
            copied.add(top_dir)

        return f'src="/blog/{rel_path}"'

    return src_pattern.sub(rewrite, body)


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

    # ── 7. Rewrite relative image paths to /blog/... absolute paths ────────
    body = rewrite_image_paths(body, Path(path))

    # ── 8. Wrap in scoped container ────────────────────────────────────────
    output = KATEX_CSS + '<div class="notion-content">\n' + body.strip() + "\n</div>\n"

    Path(path).write_text(output, encoding="utf-8")
    print(f"  Cleaned: {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <path/to/notion-export.html> ...")
        sys.exit(1)
    for arg in sys.argv[1:]:
        process(arg)
