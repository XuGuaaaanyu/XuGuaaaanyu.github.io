Place your Overleaf source at `resume/main.tex`.

How it works:
- On every push that changes files in `resume/`, GitHub Actions compiles `resume/main.tex`.
- The workflow publishes the compiled PDF to the `resume-pdf` branch as `Resume.pdf`.
- `master` is not modified by the workflow, so your local branch does not diverge from bot commits.

Notes:
- Keep any required assets (for example `.sty`, `.bib`, images) inside `resume/`.
- Your site navigation should link to the branch-hosted PDF URL.
