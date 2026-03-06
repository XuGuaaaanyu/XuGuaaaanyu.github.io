#!/usr/bin/env python3
"""
notion2jekyll.py
----------------
Strip the Notion HTML wrapper from an exported .html file so its content
can be embedded inside the academicpages Jekyll template.

The file is modified IN-PLACE (or renamed if --date is given). Run this once
after dropping a new Notion export.

Usage:
    # Clean only (original behaviour):
    python3 _scripts/notion2jekyll.py _posts/my-post.html

    # Clean + add Jekyll front matter + rename to dated slug:
    python3 _scripts/notion2jekyll.py --date 2023-10-23 --categories Mathematics "_posts/My Post Title.html"
    python3 _scripts/notion2jekyll.py -d 2023-10-23 -c Mathematics -c Physics "_posts/My Post Title.html"

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

Front matter (when --date is given):
  - layout, author_profile are always set
  - title, permalink, image_dir are inferred from the filename
  - date and categories come from CLI arguments
  - The output file is renamed to YYYY-MM-DD-slug.html
"""

import argparse
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_title(stem: str) -> str:
    """Derive a human-readable title from a Notion export filename stem.

    Notion appends a 32-char hex UUID to export filenames, e.g.:
        "Solving First and Second Order ODEs 1a2b3c4d..."
    This function strips that hash if present.  If the stem looks like a
    slug (no spaces, contains hyphens/underscores) it converts it to title
    case; otherwise it uses the stem as-is.
    """
    # Strip trailing Notion UUID hash (32 lowercase hex chars)
    cleaned = re.sub(r"\s+[0-9a-f]{32}$", "", stem).strip()

    if not cleaned:
        cleaned = stem

    # If it looks like a slug (no spaces), convert to title case
    if " " not in cleaned and ("-" in cleaned or "_" in cleaned):
        cleaned = cleaned.replace("-", " ").replace("_", " ").title()

    return cleaned


def slugify(title: str) -> str:
    """Convert a title to a URL-safe slug."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)   # remove non-word chars except dash
    slug = re.sub(r"[\s]+", "-", slug)     # spaces → dash
    slug = re.sub(r"-+", "-", slug)        # collapse multiple dashes
    return slug.strip("-")


def build_front_matter(
    title: str,
    date: str,
    categories: list,
    permalink: str,
    image_dir: str,
) -> str:
    cats = ", ".join(categories) if categories else ""
    return (
        "---\n"
        "layout: blog-post\n"
        "author_profile: true\n"
        f'title: "{title}"\n'
        f"date: {date}\n"
        f"permalink: {permalink}\n"
        f"categories: [{cats}]\n"
        f'image_dir: "{image_dir}"\n'
        "---\n"
    )


# ---------------------------------------------------------------------------
# Image path rewriting
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def process(path: str, date: str = "", categories: list = None) -> None:
    if categories is None:
        categories = []

    src = Path(path).read_text(encoding="utf-8")

    # Already processed — nothing to do if no front matter is requested.
    if "<html" not in src and "<body" not in src:
        if not date:
            print(f"  (already processed, skipping): {path}")
            return
        # If front matter was requested but file is already processed,
        # we still need to (re)add front matter and rename.

    if "<html" in src or "<body" in src:
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
        content = KATEX_CSS + '<div class="notion-content">\n' + body.strip() + "\n</div>\n"
    else:
        # Already cleaned — use as-is (strip any existing front matter for re-wrapping)
        content = re.sub(r"^---\n.*?\n---\n", "", src, count=1, flags=re.DOTALL)

    # ── 9. Optionally prepend Jekyll front matter and rename ───────────────────
    if date:
        stem = Path(path).stem
        title = extract_title(stem)
        slug = slugify(title)
        permalink = f"/blog/{slug}.html"
        image_dir = title  # matches the Notion image folder name (without UUID)

        front_matter = build_front_matter(title, date, categories, permalink, image_dir)
        output = front_matter + content

        out_path = Path(path).parent / f"{date}-{slug}.html"
        out_path.write_text(output, encoding="utf-8")
        print(f"  Written:  {out_path}")
        print(f"  Title:    {title}")
        print(f"  Slug:     {slug}")
        if categories:
            print(f"  Categories: {', '.join(categories)}")

        # Remove original if it was renamed
        if out_path.resolve() != Path(path).resolve():
            Path(path).unlink()
            print(f"  Removed original: {path}")
    else:
        Path(path).write_text(content, encoding="utf-8")
        print(f"  Cleaned: {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean a Notion HTML export for use with Jekyll."
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Path(s) to Notion-exported .html file(s) in _posts/",
    )
    parser.add_argument(
        "-d", "--date",
        default="",
        metavar="YYYY-MM-DD",
        help="Post date. When set, Jekyll front matter is added and the file is "
             "renamed to YYYY-MM-DD-slug.html.",
    )
    parser.add_argument(
        "-c", "--categories",
        action="append",
        default=[],
        metavar="CATEGORY",
        help="Post category (repeatable, e.g. -c Mathematics -c Physics).",
    )

    args = parser.parse_args()

    for f in args.files:
        process(f, date=args.date, categories=args.categories)
