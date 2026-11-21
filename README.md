# Guanyu Xu's homepage

Personal academic website built with Jekyll and the Academic Pages theme.

## Content

- `_pages/about.md`: homepage introduction and selected research/course project references.
- `_research/`: research details, authors, images and resource links.
- `_portfolio/`: course project details and resources.
- `_notion/`: source exports for Nerdy notes. Keep original exports and their assets together.
- `_scripts/notion2jekyll.py`: converts Notion exports to generated `_posts/notion/` posts.
- `_pages/year-archive.html`: Nerdy index at `/nerd/`.
- `_data/news.yml`: homepage timeline; dates use `YYYY-MM` or `YYYY-MM-DD`.
- `_data/navigation.yml`: main navigation.
- `resume/main.tex` and `resume/main.pdf`: CV source and published PDF. `/cv/` redirects to the PDF.
- `files/` and `images/`: project downloads and images.

Each item is defined in exactly one place, and every list is sorted by date, newest first (file order doesn't matter):

| Item | Where | Shown / published flag |
| --- | --- | --- |
| News | an entry in `_data/news.yml` | `homepage: false` hides it (default shown) |
| Research project | a file in `_research/` | `homepage: true` puts it on the homepage; it is always on `/research/` |
| Course project | a file in `_portfolio/` | `homepage: true` puts it on the homepage; it is always on `/projects/` |
| Nerdy note | a Notion export folder in `_notion/` + optional entry in `_notion/notes.yml` | `visible: false` unpublishes it (default published) |

News `text` is Markdown (`*italic*`, `**bold**`, `[link](url)`); keep it in double quotes.

Project front matter: `title`, `date` (YYYY-MM-DD; only sorts the lists, not displayed), `homepage`, optional `short_title` (homepage card title), `excerpt`, `header.teaser` (an image, or a short `.mp4` clip that autoplays muted and loops; put a same-named `.jpg` next to it as the poster), `authors` (suffix `†` or `+` = equal contribution, `*` = corresponding author, e.g. `"Haobo Fang†"`), `venue` (shown in italics), `links` (label / icon / url; empty urls are skipped), optional `link`. `published: false` hides a project everywhere (draft).

Where a project card points is decided by `_plugins/project_pages.rb`:
- `link: "https://..."` → the card opens that site; no page is generated.
- nothing below the front matter → the card is not clickable; no page is generated.
- otherwise → the card opens the project's own page at `/research/<file name>/` or `/projects/<file name>/`; its link pills are added by the layout.

## Layout and styling

Shared Jekyll templates live in `_layouts/` and `_includes/`. Theme styles live in `_sass/`; `_custom.scss` contains shared project and Nerdy styling, and `_home.scss` contains homepage styling and accessible resource-link focus states. `assets/css/main.scss` imports them.

## Local preview

With Python, Ruby and Bundler installed:

```sh
python -m pip install pyyaml
python _scripts/notion2jekyll.py --build _notion
bundle install
bundle exec jekyll serve
```

Generated notes and `_site/` are ignored by Git. After changing `_config.yml`, restart Jekyll.

## Deployment

`.github/workflows/deploy.yml` converts Notion exports, builds Jekyll and deploys to GitHub Pages on pushes to `main`. Research, Portfolio, Nerdy and the PDF CV are maintained; unused Talks, Teaching, map generators and template example pages have been removed.

Based on [Academic Pages](https://github.com/academicpages/academicpages.github.io), under the MIT license in `LICENSE`.
