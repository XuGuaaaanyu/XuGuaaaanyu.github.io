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
  - Relative src="..." paths are rewritten to absolute /nerd/... paths
  - Image directories sibling to the content file are copied to blog/

Front matter (when --date is given):
  - layout, author_profile are always set
  - title, permalink, image_dir are inferred from the filename
  - date and categories come from CLI arguments
  - cover_image is set to the first embedded figure found in the post (if any)
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

BLOG_DIR = Path("nerd")
PRISM_ASSET_RE = re.compile(
    r'\s*(?:<script[^>]*src="https://cdnjs\.cloudflare\.com/ajax/libs/prism/[^"]+"[^>]*>\s*</script>'
    r'|<link[^>]*href="https://cdnjs\.cloudflare\.com/ajax/libs/prism/[^"]+"[^>]*/?>)\s*',
    flags=re.IGNORECASE,
)
FRONT_MATTER_RE = re.compile(r"^(---\n.*?\n---\n)", flags=re.DOTALL)


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
    cover_image: str = "",
) -> str:
    cats = ", ".join(categories) if categories else ""
    lines = [
        "---",
        "layout: blog-post",
        "author_profile: true",
        f'title: "{title}"',
        f"date: {date}",
        f"permalink: {permalink}",
        f"categories: [{cats}]",
        f'image_dir: "{image_dir}"',
    ]
    if cover_image:
        lines.append(f'cover_image: "{cover_image}"')
    lines.append("---")
    return "\n".join(lines) + "\n"


def split_front_matter(text: str) -> tuple[str, str]:
    """Return (front_matter, remainder) if a Jekyll front matter block exists."""
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return "", text
    return match.group(1), text[match.end():]


def normalize_notion_code_blocks(fragment: str) -> str:
    """Normalize Notion-exported code blocks for the site CSS/JS pipeline."""
    fragment = PRISM_ASSET_RE.sub("", fragment)

    # Prism language classes are conventionally lowercase.
    fragment = re.sub(
        r"language-([A-Za-z0-9_+-]+)",
        lambda m: f"language-{m.group(1).lower()}",
        fragment,
    )

    # Remove Notion's wrapping styles so code can scroll horizontally again.
    def strip_code_style(match: re.Match) -> str:
        prefix = match.group(1)
        style = match.group(2)
        declarations = []
        for declaration in style.split(";"):
            declaration = declaration.strip()
            if not declaration:
                continue
            prop = declaration.split(":", 1)[0].strip().lower()
            if prop in {"white-space", "word-break", "overflow-wrap"}:
                continue
            declarations.append(declaration)
        if declarations:
            return f'{prefix} style="{";".join(declarations)}"'
        return prefix

    fragment = re.sub(
        r'(<code\b[^>]*?)\sstyle="([^"]*)"',
        strip_code_style,
        fragment,
        flags=re.IGNORECASE,
    )

    # Surface the language on the <pre> so CSS can render a small IDE-style label.
    def add_language_attr(match: re.Match) -> str:
        pre_open = match.group(1)
        if "data-language=" in pre_open:
            return match.group(0)
        return f'{pre_open} data-language="{match.group(4).lower()}"{match.group(2)}{match.group(3)}'

    fragment = re.sub(
        r'(<pre\b[^>]*\bclass="[^"]*\bcode\b[^"]*"[^>]*)(>)(\s*<code\b[^>]*\bclass="[^"]*language-([a-z0-9_+-]+)[^"]*"[^>]*>)',
        add_language_attr,
        fragment,
        flags=re.IGNORECASE,
    )

    return fragment


# ---------------------------------------------------------------------------
# Image path rewriting
# ---------------------------------------------------------------------------

def rewrite_image_paths(body: str, content_file: Path) -> tuple:
    """Rewrite relative src="..." to absolute /nerd/... and copy image dirs.

    Returns (rewritten_body, first_local_image_url).
    first_local_image_url is the /nerd/... URL of the first embedded image,
    or "" if the post contains no local images.
    """
    src_pattern = re.compile(r'src="(?!https?://)([^"]+)"')
    content_dir = content_file.parent
    copied: set = set()
    first_img: list = []  # populated on first match

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

        abs_url = f"/nerd/{rel_path}"
        if not first_img:
            first_img.append(abs_url)
        return f'src="{abs_url}"'

    new_body = src_pattern.sub(rewrite, body)
    return new_body, (first_img[0] if first_img else "")


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def process(path: str, date: str = "", categories: list = None) -> None:
    if categories is None:
        categories = []

    src_path = Path(path)
    src = src_path.read_text(encoding="utf-8")
    existing_front_matter, src_body = split_front_matter(src)

    cover_image = ""

    if "<html" in src_body or "<body" in src_body:
        # ── 1. Remove the main Notion <style>…</style> block ──────────────────
        # It's the first (and largest) <style> tag; everything else is @import katex.
        src_body = re.sub(
            r"<style>(?!@import).*?</style>",
            "",
            src_body,
            count=1,
            flags=re.DOTALL,
        )

        # ── 2. Extract <body> content ──────────────────────────────────────────
        m = re.search(r"<body>(.*)</body>", src_body, re.DOTALL)
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

        # ── 7. Rewrite relative image paths to /nerd/... absolute paths ────────
        body, cover_image = rewrite_image_paths(body, src_path)

        # ── 8. Normalize code blocks after the HTML cleanup ───────────────────
        body = normalize_notion_code_blocks(body)

        # ── 9. Wrap in scoped container ────────────────────────────────────────
        content = KATEX_CSS + '<div class="notion-content">\n' + body.strip() + "\n</div>\n"
    else:
        # Already cleaned — preserve front matter, but still normalize the HTML.
        content = normalize_notion_code_blocks(src_body)

    # ── 10. Optionally prepend Jekyll front matter and rename ──────────────────
    if date:
        stem = Path(path).stem
        title = extract_title(stem)
        slug = slugify(title)
        permalink = f"/nerd/{slug}.html"
        image_dir = title  # matches the Notion image folder name (without UUID)

        front_matter = build_front_matter(
            title, date, categories, permalink, image_dir, cover_image
        )
        output = front_matter + content

        out_path = src_path.parent / f"{date}-{slug}.html"
        out_path.write_text(output, encoding="utf-8")
        print(f"  Written:  {out_path}")
        print(f"  Title:    {title}")
        print(f"  Slug:     {slug}")
        if categories:
            print(f"  Categories: {', '.join(categories)}")
        if cover_image:
            print(f"  Cover:    {cover_image}")
        else:
            print(f"  Cover:    (none — no embedded figures found)")

        # Remove original if it was renamed
        if out_path.resolve() != src_path.resolve():
            src_path.unlink()
            print(f"  Removed original: {path}")
    else:
        output = existing_front_matter + content
        if output == src:
            print(f"  (already processed, skipping): {path}")
            return
        src_path.write_text(output, encoding="utf-8")
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
