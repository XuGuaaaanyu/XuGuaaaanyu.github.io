Place your Overleaf source at `resume/Resume.tex`.

How it works:
- On every push that changes files in `resume/`, GitHub Actions compiles `resume/Resume.tex`.
- The workflow writes the compiled PDF to `files/Resume.pdf`.
- If `files/Resume.pdf` changed, the workflow commits it automatically.

Notes:
- Keep any required assets (for example `.sty`, `.bib`, images) inside `resume/`.
- Your site navigation already points to `/files/Resume.pdf`, so no website link changes are needed.
