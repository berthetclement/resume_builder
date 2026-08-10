# resume-builder

Python lib to generate resumes (Markdown -> HTML/PDF).

## Stack

- Project and dependency management: **uv** (no manual pip/venv — use `uv add`, `uv sync`, `uv run`).
- Build backend: **hatchling**.
- Python version: floor `>=3.11` (`requires-python`), dev on **3.13**.
- Runtime dependencies: **markdown-it-py[plugins]** (Markdown parsing, incl. `mdit-py-plugins` for Pandoc-style attributes/fenced-divs/frontmatter), **pydantic** (structured resume data model).
- Dev tooling: **ruff** (lint + format), **mypy** (strict), **pytest**, **pre-commit**, **tox** (+ `tox-uv`).
- Dev dependencies are split into PEP 735 groups in `pyproject.toml`: `lint`, `type`, `test`, and `dev` (which includes all three plus `pre-commit`/`tox`/`tox-uv`). Plain `uv sync` installs everything via the `dev` group.
- CI: GitHub Actions (`.github/workflows/ci.yml`), matrix over Windows/Linux/macOS, on every push to any branch. Ubuntu runs the full tox matrix (`py311`/`py312`/`py313`/`lint`/`type`); Windows/macOS only run the `py311`/`py312`/`py313` test envs (lint/type are OS-independent, no need to repeat them, and macOS Actions minutes are the most constrained).
- Versioning: **hatch-vcs** derives the package version from git (tags/commit distance), not a hand-edited `version` field. `src/resume_builder/_version.py` is generated automatically on every `uv sync`/build — it's gitignored, never edited by hand, and exposed as `resume_builder.__version__`. Requires an actual git clone (with history) to resolve correctly; a ZIP download or shallow clone won't compute the version properly.

## Available commands

```bash
uv sync                                    # installs deps (project + dev group) and creates/syncs the .venv
uv build                                   # generates wheel + sdist in dist/
uv run python -c "import resume_builder"   # sanity-checks that the package imports

uv run pre-commit install                  # one-time per clone: wires up the git commit hook
uv run pre-commit run --all-files          # run ruff check/format + mypy against the whole repo

uv run ruff check .                        # lint
uv run mypy src tests                      # type-check (strict) — src and tests both, kept in sync with pre-commit/tox
uv run pytest                              # run tests
uv run tox -p                              # run the full matrix (py311/py312/py313/lint/type) in parallel, local dev only (CI runs it sequentially, see below)
```

## Current state

DevOps scaffolding is done (pre-commit, ruff, mypy strict, pytest, tox, CI, hatch-vcs) per the "no feature before a complete lib setup" principle. Business logic is in progress on branch `poc/markdown-render` (not yet merged):

- `src/resume_builder/models/` — `pydantic` `Resume`/`contact`/`experience` models, still being iterated on, not the final shape.
- `src/resume_builder/template/markdow_editor.py` — `write_model_to_markdown()`, generates a starter `.md` template from a `Resume` instance. Done.

Tests live in `tests/`, mirroring the `src/resume_builder/` package structure (e.g. `tests/models/` for `src/resume_builder/models/`).

Two planned ways to build a resume (see project's own private planning notes for the full pagedown-inspired reasoning):

- **Markdown-based** (current focus): `Resume` model → `write_model_to_markdown()` generates a starter `.md` → user hand-edits it directly (data, CSS/JS) → `markdown-it-py` parses that edited file *directly* into HTML via a Jinja2 template → `paged.js` pagination → Playwright → PDF. The pydantic model is only used to generate the template — rendering never parses the user's edited Markdown back into a strict model; it walks the parsed Markdown directly, same as pagedown/Pandoc. Not built past template generation yet.
- **App-based** (deferred, not started): a future app builds resume data directly (no `.md` involved) and feeds into the same render step as above.