# resume-builder

Python lib to generate resumes (Markdown -> HTML/PDF).

## Design inspiration

Modeled on R's **pagedown** package: write a resume in Markdown, render it to a paginated HTML page, export that to PDF. Pandoc (which pagedown uses) bundles Markdown parsing, YAML frontmatter parsing, and templating into one tool; this project deliberately composes separate, pure-Python libraries instead, to stay a plain `pip install` with no external binary dependency:

| Job | pagedown/Pandoc | resume-builder |
|---|---|---|
| Parse Markdown | Pandoc's own reader | `markdown-it-py` |
| Parse YAML frontmatter | Pandoc's reader (built in) | `pyyaml` |
| Stitch content + metadata into HTML | Pandoc's own template engine | `Jinja2` |
| Pagination | `paged.js` | `paged.js` (same tool) |
| HTML → PDF | headless Chrome print | Playwright (headless Chromium) |

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
uv run pytest --cov=resume_builder --cov-report=term-missing tests/ # coverage
uv run tox -p                              # run the full matrix (py311/py312/py313/lint/type) in parallel, local dev only (CI runs it sequentially, see below)
```

## Current state

DevOps scaffolding is done (pre-commit, ruff, mypy strict, pytest, tox, CI, hatch-vcs) per the "no feature before a complete lib setup" principle. Business logic is in progress on branch `poc/markdown-render` (not yet merged):

- `src/resume_builder/models/` — `pydantic` `Resume`/`contact`/`experience` models, still being iterated on, not the final shape.
- `src/resume_builder/template/markdow_editor.py` — `write_model_to_markdown()` (generates a starter `.md` from a `Resume` instance) and `init_resume()` (writes it to a target directory, refuses to overwrite an existing file unless `force=True`). The generated `.md` also gets a commented-out `YAML_FRONT_MATTER` hint (`template/constants.py`) showing how to add a `css:` block — real, valid, inert frontmatter (all lines commented via `#`) rather than a plain-text note, so it's immediately usable by uncommenting.

Tests live in `tests/`, mirroring the `src/resume_builder/` package structure (e.g. `tests/models/` for `src/resume_builder/models/`).

Two planned ways to build a resume (see "Design inspiration" above for the pagedown reasoning):

- **Markdown-based** (current focus): `Resume` model → `write_model_to_markdown()` generates a starter `.md` → user hand-edits it directly (data, CSS/JS) → `markdown-it-py` parses that edited file *directly* into HTML via a Jinja2 template → `paged.js` pagination → Playwright → PDF. The pydantic model is only used to generate the template — rendering never parses the user's edited Markdown back into a strict model; it walks the parsed Markdown directly, same as pagedown/Pandoc.
  - `render_resume()` (`src/resume_builder/render/renderer.py`) does the actual `.md` → `.html` conversion. Done, tested (not-found, empty-file, css-frontmatter, full happy path), and working end to end (minus `paged.js`/PDF, still later steps). Validates its input first: raises `FileNotFoundError` if `md_path` doesn't exist, `ValueError` if it's empty.
  - `MarkdownIt` is configured with `.use(front_matter_plugin).use(attrs_block_plugin)`. `front_matter_plugin` extracts the `css`/`js` YAML block (parsed via `pyyaml`). `attrs_block_plugin` gives each `## field` section a real `id` matching the field name (e.g. `id="contact"`) — needed so a future default/user CSS can target specific sections.
  - Important syntax constraint: `attrs_block_plugin` only recognizes a `{#id}` block when it's **on its own line, immediately before** the block it targets (`{#contact}` then `## contact` on the next line) — trailing on the same line as the heading (pagedown/Pandoc's convention) does not work with this plugin. `write_model_to_markdown()` generates this two-line form.
  - The Jinja2 template itself is a real file, `src/resume_builder/render/templates/resume.html.j2`, loaded via `jinja2.PackageLoader("resume_builder.render", "templates")` — not a Python string constant. Confirmed hatchling ships non-`.py` files under `src/resume_builder/` in the wheel automatically, no extra packaging config needed.
- **App-based** (deferred, not started): a future app builds resume data directly (no `.md` involved) and feeds into the same render step as above.