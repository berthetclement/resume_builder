# resume-builder

Python lib to generate resumes (Markdown -> HTML/PDF).

## Code review

When reviewing code:
- Design: does this fit the existing architecture, not fight it.
- Functionality: does it actually do what it claims, including edge cases.
- Complexity: could this be simpler.
- Tests: real coverage, not padding — flag missing tests and weakened/removed assertions.
- Naming: clear, PEP8-compliant, no collisions with existing names.
- Consistency: matches existing patterns and conventions in the repo.
- Verify library/API behavior before trusting it — don't assume.
- Reuse existing utilities before adding new ones.
- No abstractions without a concrete, current benefit.

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

DevOps scaffolding is done (pre-commit, ruff, mypy strict, pytest, tox, CI, hatch-vcs) per the "no feature before a complete lib setup" principle. Business logic is in progress on feature branches, not yet merged to `main`:

- `src/resume_builder/models/` — `pydantic` `Resume`/`contact`/`experience` models, still being iterated on, not the final shape. **Active work in progress**: reworking the model, then `write_model_to_markdown()` (currently renders nested-model fields as flat `- **fieldname**: value` bullets — shows the field *name* as structure instead of promoting the *value*, unlike `_render_entry`'s heading-promotion for list items; being fixed for consistency). Design decision made: `Resume` stays a flat, layout-agnostic model (no `aside`/`main` grouping baked into the schema) — an aside/main visual split (contact/skills vs. name/title/experiences) will be driven separately, e.g. via a layout mapping passed to a future `write_model_to_css()`, not by restructuring the data model itself. Once this settles, next step is the CSS work (`DEFAULT_CSS`/`write_model_to_css`).
- `src/resume_builder/template/markdow_editor.py` — `write_model_to_markdown()` (generates a starter `.md` from a `Resume` instance) and `init_resume()` (writes it to a target directory, refuses to overwrite an existing file unless `force=True`). The generated `.md` also gets a commented-out `YAML_FRONT_MATTER` hint (`template/constants.py`) showing how to add a `css:` block — real, valid, inert frontmatter (all lines commented via `#`) rather than a plain-text note, so it's immediately usable by uncommenting.

Tests live in `tests/`, mirroring the `src/resume_builder/` package structure (e.g. `tests/models/` for `src/resume_builder/models/`).

Two planned ways to build a resume (see "Design inspiration" above for the pagedown reasoning):

- **Markdown-based** (current focus): `Resume` model → `write_model_to_markdown()` generates a starter `.md` → user hand-edits it directly (data, CSS/JS) → `markdown-it-py` parses that edited file *directly* into HTML via a Jinja2 template → `paged.js` pagination → Playwright → PDF. The pydantic model is only used to generate the template — rendering never parses the user's edited Markdown back into a strict model; it walks the parsed Markdown directly, same as pagedown/Pandoc.
  - `render_resume()` (`src/resume_builder/render/renderer.py`) does the actual `.md` → `.html` conversion. Done, tested (not-found, empty-file, css-frontmatter, full happy path), and working end to end (minus `paged.js`/PDF, still later steps). Validates its input first: raises `FileNotFoundError` if `md_path` doesn't exist, `ValueError` if it's empty.
  - `MarkdownIt` is configured with `.use(front_matter_plugin).use(attrs_block_plugin).use(container_plugin, "section")`. `front_matter_plugin` extracts the `css`/`js` YAML block (parsed via `pyyaml`). `attrs_block_plugin` + `container_plugin` together give each field a real `id` on a `<div>` wrapping its *entire* section (heading + content), not just the heading — needed because CSS Grid treats every direct child of the grid container as its own item, so heading and content must move together as one unit to be positioned as a section.
  - `write_model_to_markdown()` generates this as `{#field}` / `::: section` / `## field` / ...content... / `:::` — a fenced-div block, not just a two-line heading+id form. Important syntax constraint carried over from `attrs_block_plugin`: the `{#id}` block must be **on its own line, immediately before** the block it targets — trailing on the same line as the heading/div (pagedown/Pandoc's convention) does not work with this plugin.
  - The Jinja2 template itself is a real file, `src/resume_builder/render/templates/resume.html.j2`, loaded via `jinja2.PackageLoader("resume_builder.render", "templates")` — not a Python string constant. Confirmed hatchling ships non-`.py` files under `src/resume_builder/` in the wheel automatically, no extra packaging config needed.
  - `src/resume_builder/render/templates/theme.css` — a real example stylesheet using CSS Grid to lay out `name`/`title` in a left column and `contact` in a right column, `experiences` spanning full width below. Not yet wired up as an automatic default (that's the still-open `DEFAULT_CSS` fallback); currently just a hand-written example the user references via `css:` frontmatter.
- **App-based** (deferred, not started): a future app builds resume data directly (no `.md` involved) and feeds into the same render step as above.