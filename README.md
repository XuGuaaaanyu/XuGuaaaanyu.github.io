# Guanyu Xu's homepage

Personal academic website built with Jekyll and the Academic Pages theme.

## Content

- `_pages/about.md`: homepage introduction and selected research/course project references.
- `_research/`: research details, authors, images and resource links.
- `_portfolio/`: course project details and resources.
- `_notion/`: source exports for Nerdy notes. Keep original exports and their assets together.
- `_scripts/notion2jekyll.py`: converts Notion exports to generated `_posts/notion/` posts.
- `_pages/year-archive.html`: Nerdy index at `/nerd/`.
- `_data/news.yml`: homepage timeline, newest first; dates use `YYYY-MM`.
- `_data/navigation.yml`: main navigation.
- `resume/main.tex` and `resume/main.pdf`: CV source and published PDF. `/cv/` redirects to the PDF.
- `files/` and `images/`: project downloads and images.

Homepage project cards read metadata from the referenced research/portfolio document. Add references under `projects.research` or `projects.course` in `_pages/about.md`; avoid duplicating project metadata.

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
