#!/usr/bin/env python3
"""
notion2jekyll.py
----------------
Strip the Notion HTML wrapper from an exported .html file so its content
can be embedded inside the academicpages Jekyll template.

The file is modified IN-PLACE (or renamed if --date is given). Run this once
after dropping a new Notion export.

Usage:
    # Build mode (what CI runs on every push): convert every raw export in
    # _notion/ into _posts/notion/, reading date / categories / visible from the
    # Notion property table and/or _notion/notes.yml. Hidden notes are skipped.
    python3 _scripts/notion2jekyll.py --build _notion

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
import html as html_lib
import re
import shutil
import subprocess
import sys
import urllib.parse
from datetime import datetime
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


LOCAL_LINK_RE = re.compile(r'(src|href)="(?![a-z][a-z0-9+.-]*:|#|/)([^"]+)"', flags=re.IGNORECASE)
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def publish_local_files(body: str, content_dir: Path, dest_name: str) -> tuple:
    """Copy every locally referenced file to nerd/<dest_name>/ and rewrite links.

    Works for both Notion export layouts: images next to the .html (current)
    or inside a "<Page Title>/" subfolder (older). Returns (body, cover_image).
    """
    dest_dir = BLOG_DIR / dest_name
    first_img: list = []

    def rewrite(m: re.Match) -> str:
        attr, rel_path = m.group(1), m.group(2)
        rel_decoded = urllib.parse.unquote(rel_path)
        src = content_dir / rel_decoded
        if not src.is_file():
            return m.group(0)
        dst = dest_dir / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        url = f"/nerd/{urllib.parse.quote(dest_name)}/{urllib.parse.quote(src.name)}"
        if not first_img and src.suffix.lower() in IMAGE_EXTS:
            first_img.append(url)
        return f'{attr}="{url}"'

    return LOCAL_LINK_RE.sub(rewrite, body), (first_img[0] if first_img else "")


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def clean_notion_html(src_body: str, src_path: Path, image_dir: str = "") -> tuple:
    """Strip the Notion wrapper from a raw export. Returns (content, cover_image).

    With image_dir, local files are published to nerd/<image_dir>/ (build mode);
    otherwise the legacy "<Title>/" folder rewrite is used.
    """
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
            sys.exit(f"ERROR: no <body> found in {src_path} — is this a Notion export?")
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
        if image_dir:
            body, cover_image = publish_local_files(body, src_path.parent, image_dir)
        else:
            body, cover_image = rewrite_image_paths(body, src_path)

        # ── 8. Normalize code blocks after the HTML cleanup ───────────────────
        body = normalize_notion_code_blocks(body)

        # ── 9. Wrap in scoped container ────────────────────────────────────────
        content = KATEX_CSS + '<div class="notion-content">\n' + body.strip() + "\n</div>\n"
    else:
        # Already cleaned — preserve front matter, but still normalize the HTML.
        content = normalize_notion_code_blocks(src_body)

    return content, cover_image


def process(path: str, date: str = "", categories: list = None) -> None:
    if categories is None:
        categories = []

    src_path = Path(path)
    src = src_path.read_text(encoding="utf-8")
    existing_front_matter, src_body = split_front_matter(src)

    content, cover_image = clean_notion_html(src_body, src_path)

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
# Build mode: convert every raw export in a drop folder (run by CI)
# ---------------------------------------------------------------------------

PROPERTY_ROW_RE = re.compile(
    r'<tr class="property-row[^"]*">\s*<th>(.*?)</th>\s*<td>(.*?)</td>\s*</tr>',
    flags=re.DOTALL,
)
DATE_PROPS = {"date", "日期"}
CATEGORY_PROPS = {"categories", "category", "tags", "分类"}
VISIBLE_PROPS = {"visible", "published", "可见"}


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html).strip()


def parse_date(text: str) -> str:
    """Return YYYY-MM-DD from a Notion date cell or a manifest value, or ""."""
    text = str(text)
    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if m:
        return m.group(0)
    m = re.search(r"\d{4}/\d{1,2}/\d{1,2}", text)
    if m:
        return datetime.strptime(m.group(0), "%Y/%m/%d").strftime("%Y-%m-%d")
    m = re.search(r"([A-Z][a-z]+) (\d{1,2}), (\d{4})", text)
    if m:
        for fmt in ("%B %d, %Y", "%b %d, %Y"):
            try:
                return datetime.strptime(m.group(0), fmt).strftime("%Y-%m-%d")
            except ValueError:
                pass
    return ""


def read_notion_properties(html: str) -> dict:
    """Read Date / Categories / Visible from a Notion database page's property table."""
    props = {}
    for th, td in PROPERTY_ROW_RE.findall(html):
        name = strip_tags(th).lower()
        if name in DATE_PROPS:
            date = parse_date(strip_tags(td))
            if date:
                props["date"] = date
        elif name in CATEGORY_PROPS:
            values = re.findall(r'<span class="selected-value[^"]*">(.*?)</span>', td)
            if not values:
                values = strip_tags(td).split(",")
            props["categories"] = [strip_tags(v) for v in values if strip_tags(v)]
        elif name in VISIBLE_PROPS:
            if "checkbox-on" in td:
                props["visible"] = True
            elif "checkbox-off" in td:
                props["visible"] = False
    return props


def load_manifest(src_dir: Path) -> dict:
    manifest = src_dir / "notes.yml"
    if not manifest.exists():
        return {}
    try:
        import yaml
    except ImportError:
        sys.exit("ERROR: PyYAML is required to read notes.yml (pip install pyyaml)")
    return yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}


def git_added_date(path: Path) -> str:
    """Date the file was first committed, so undated notes keep a stable date."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%as", "--", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout.split()
        return out[-1] if out else ""
    except (OSError, subprocess.CalledProcessError):
        return ""


def build(src_dir: str, out_dir: str) -> None:
    src_root = Path(src_dir)
    out_root = Path(out_dir)
    manifest = load_manifest(src_root)

    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True)

    for src_path in sorted(src_root.rglob("*.html")):
        raw = src_path.read_text(encoding="utf-8")
        file_title = extract_title(src_path.stem)
        m = re.search(r'<h1 class="page-title"[^>]*>(.*?)</h1>', raw, flags=re.DOTALL)
        title = html_lib.unescape(strip_tags(m.group(1))) if m else file_title

        keys = [title, file_title]
        if src_path.parent != src_root:
            keys.insert(0, src_path.parent.name)
        entry = next((manifest[k] for k in keys if k in manifest), None)
        if entry is None:
            print(f"  WARNING:  no notes.yml entry for {keys[0]!r} — using defaults")

        meta = {"visible": True, "categories": []}
        meta.update(read_notion_properties(raw))
        meta.update(entry or {})

        if not meta["visible"]:
            print(f"  Hidden:   {title}")
            continue

        date = (
            parse_date(meta.get("date", ""))
            or git_added_date(src_path)
            or datetime.now().strftime("%Y-%m-%d")
        )
        categories = meta["categories"]
        if isinstance(categories, str):
            categories = [categories]

        slug = slugify(title)
        content, cover_image = clean_notion_html(raw, src_path, image_dir=slug)
        front_matter = build_front_matter(
            title.replace('"', '\\"'), date, categories, f"/nerd/{slug}.html", slug, cover_image
        )
        out_path = out_root / f"{date}-{slug}.html"
        out_path.write_text(front_matter + content, encoding="utf-8")
        print(f"  Built:    {out_path}  [{', '.join(categories)}]")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean a Notion HTML export for use with Jekyll."
    )
    parser.add_argument(
        "files",
        nargs="*",
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

    parser.add_argument(
        "--build",
        metavar="SRC_DIR",
        help="Convert every raw Notion export in SRC_DIR (plus notes.yml) into "
             "posts under --out. Used by the GitHub Actions deploy workflow.",
    )
    parser.add_argument(
        "--out",
        default="_posts/notion",
        metavar="OUT_DIR",
        help="Output folder for --build (default: _posts/notion, git-ignored).",
    )

    args = parser.parse_args()

    if args.build:
        build(args.build, args.out)
    elif not args.files:
        parser.error("give FILE(s) to convert, or --build SRC_DIR")

    for f in args.files:
        process(f, date=args.date, categories=args.categories)
