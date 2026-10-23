# resume-builder

Python lib to generate resumes (Markdown -> HTML/PDF), modeled on R's **pagedown**.

Keep this file **normative and stable**: conventions, stack, commands. If a sentence
goes stale the moment you commit, it does not belong here — put transient status in
the branch, and reasoning in `claude_private/`.

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
- Decisions made in discussion must land in the code, its tests or this file. A choice
  that lives only in a conversation is lost.

## Conventions

The contract between the Markdown, the model and the CSS. Everything here is
deliberate — see `claude_private/pagedown-notes.md` for why. The code is not fully
aligned with it yet; the remaining gaps are tracked in
`claude_private/pipeline-schema.md`.

Its executable form is `src/resume_builder/conventions.py`, a leaf module that imports
nothing and is read by `models/`, `template/` and `render/` alike — so the writer and
the parser cannot drift apart. It may hold functions as long as they stay pure and talk
only about the format; anything needing `FieldInfo`, `BaseModel`, `Token` or a `Path`
belongs to `template/` or `render/` instead.

### Heading levels — exactly four, fixed meaning

| Level | Meaning | Where it comes from |
|---|---|---|
| `#` | document title (the person's name) | `MarkdownH1` hint on `Main.user_name` |
| `##` | section title (`Contact Information`, `Work Experience`) | `Field(title=...)` on the `Resume` field |
| `###` | entry title — **opens an `.entry` box** | `MarkdownH3` hint on the entry's first field (`Entry.title`, `TitledEntry.title`, `Main.title_position`) |
| `####` | entry subtitle — **anchors the entry's metadata lines** | `MarkdownH4` hint on `Entry.subtitle`, and nowhere else |

`main` is the only exception, and it needs no special-casing in code: it has no
`Field(title=...)` (so no `##` is emitted) and it is the only section holding the `#`.

`####` exists only inside an entry, right after its `###`. It does not open anything:
`wrap_entries()` reacts to `h3` alone. Its job is to be the fixed point the metadata
selectors count from — see "Entry field order".

### Section markup

One `::: section` per `Resume` field, `id` = the field name:

```markdown
{#experiences}

::: section

## Work Experience

### Consultant Data Scientist

#### Acme Corp

Paris, France

2021

2022

- Led the R package chain.
- Released to CRAN.

:::
```

The line order inside the entry is not free — see "Entry field order" below. Each
field is one **block**: a list field renders as `- item` lines joined by a single
newline *inside* that one block, a field carrying a heading hint renders as that
heading, every other field renders as one bare line. No
field is optional: `_write_model_to_markdown` carries no `None` branch, so an
optional field left unset would write the literal string "None" into the file.

- `{#id}` must be **on its own line, before** the block it targets.
  Pandoc/pagedown's trailing form (`## Title {#id}`) does *not* work with
  `attrs_block_plugin`. It binds to the *next* block whatever that block is —
  container, heading, paragraph or list — and blank lines in between change
  nothing (measured). A stray anchor therefore decorates whatever follows it,
  silently.
- The container wraps the *whole* section, heading included — CSS Grid treats every
  direct child of the grid container as its own item, so the heading and its content
  must move as one unit.
- **One blank line between every block, two between sections.** The first is
  load-bearing, not cosmetic: CommonMark merges adjacent lines into a single `<p>`,
  and no stylesheet can pull them apart afterwards. The second is ergonomics — this
  file exists to be hand-edited, and the wider gap shows where a section ends.
  Neither is ever written by a caller: `join_blocks()` in `conventions.py` owns the
  separator, with `PARAGRAPH_BREAK` inside a section and `SECTION_BREAK` between
  them. A value that carried its own separator would be the bug that function
  exists to prevent.

### Entry boxes

`wrap_entries()` (`render/entries.py`) inserts `<div class="entry">` at every `###`
inside a `::: section`, closing it at the next `###` or at the end of the container.

- The level is **absolute** (`h3`), never inferred from what the section happens to
  contain. Relative heuristics were tried and break on titled sections.
- A section with no `###` gets no entry (`contact`, `skills`). That is correct, not a
  gap.
- `main`'s `###` (the job headline) also produces an entry. Intentional — it mirrors
  pagedown's `--section-divs`, and `break-inside: avoid` keeping the headline with its
  paragraph is desirable.
- The box is required: `break-inside: avoid` needs an element, and the metadata
  selectors must count *within* an entry, not across the whole section.

**Nested containers were considered and rejected.** A second `entry` container gives
byte-identical HTML — checked — but moves the cost onto whoever edits the file: one
`::: entry` / `:::` pair per job, and the *outer* fence has to be the longer one
(`:::: section`), because a closing `:::` would otherwise shut the section at the end
of the first entry. The `###` is information the user types anyway; a fence is ceremony
that exists only to serve the CSS. Forget one and the job silently loses its
`break-inside: avoid` — visible only in the PDF, split across a page.

### Entry models — three shapes, each with fixed arity

One model class per shape of section content, and the class alone decides what the
writer emits:

| | `BriefEntry` | `TitledEntry` | `Entry` |
|---|---|---|---|
| sections | `contact`, `skills` | `languages` | `experiences`, `education`, `personal_projects` |
| emits a `###` | no | yes | yes |
| emits a `####` | no | no | yes |
| gets an `.entry` box | no | yes | yes |

`BriefEntry` holds free content under its `##` and nothing else. With no `###`,
`wrap_entries()` has nothing to wrap and the positional contract below does not apply
to it — the same situation as a section the user writes by hand as a plain list.

`TitledEntry` — and `main`, which has the same shape — has no `####`. Its paragraph
therefore matches none of the metadata selectors and renders as plain prose. This is
the point of the `####`: an entry without one has no metadata, and the stylesheet
knows it without being told which section it is in. Before the `####`, metadata was
counted from the start of the entry, so a `TitledEntry`'s prose sat in the subtitle
slot and was styled as one.

**Three fixed-arity classes, not one class with optional fields.** The stylesheet
addresses metadata lines by position after the `<h4>`, and a sibling chain counts what
is *present*, not what the model declares. Omitting a **trailing** field is harmless:
the unmatched rules style nothing. Omitting a **middle** one shifts everything after it
by one — an entry with dates but no location gets its start date styled as a location,
with no exception and no failing test, visible only on the rendered page. Optional
fields permit that hole; classes whose fields are all required forbid it, because every
entry in a section then has the same shape.

**An empty value is a hole too.** A field set to `""` writes an empty block; CommonMark
collapses the extra blank line and emits no `<p>`, so the next line moves into its slot
exactly as if the field were missing (measured). Required is not non-empty: a default
of `""` and an explicit `location=""` both produce it. Only the default is forbidden
today, by the all-fields-required test; an explicit empty value is not checked.

Hence the rule for any new entry class: its fields must be a **prefix** of the order in
"Entry field order" below — optional by truncation, never by holes. `description`
counts as one of the `<p>` lines when it is a plain `str`; only as a list does it
escape the count, rendering as `<ul>`. A class with metadata must start it with the
`####` subtitle: lines with no `<h4>` before them are prose, not metadata.

### Entry field order

Inside an entry, **position is meaning**. The stylesheet addresses fields by position, so
the declaration order of a model's fields is a public contract, not an implementation
detail: reordering them silently restyles the wrong thing, and neither mypy nor a
presence-based test will notice.

This is pagedown's own contract made explicit. It does the same thing — `ps[0]` place,
`ps[1]` location, `ps[2]` date — but only inside an inline script, discoverable by
reading the source. Here it is written down and pinned by a test.

`Entry` renders as:

| Order | Field | Element | Selector |
|---|---|---|---|
| 1 | `title` | `<h3>` | `.entry > h3` |
| 2 | `subtitle` | `<h4>` | `.entry > h4` |
| 3 | `location` | `<p>` | `.entry > h4 + p` |
| 4 | `start_date` | `<p>` | `.entry > h4 + p + p` |
| 5 | `end_date` | `<p>` | `.entry > h4 + p + p + p` |
| 6 | `description` | `<ul><li>` | `.entry > ul > li` |

**No selector addresses "the first `<p>` of an entry".** Metadata is counted from the
`<h4>` with adjacent-sibling combinators, never with `p:nth-of-type(n)` from the start
of the entry: that form cannot tell a metadata line from prose, which is how a
`TitledEntry`'s paragraph once came out bold. A `<p>` not preceded by an `<h4>` is
prose and gets the default paragraph style.

**Keep the child combinator on the anchor** — `.entry > h4`, not `.entry h4`. The
whole chain then lives among the entry's direct children, and nothing nested (a loose
list item renders as `<li><p>…</p></li>`) can enter it. The writer emits tight lists,
but the user hand-edits this file.

`description` is `str | list[str]`: as a list it becomes a `<ul>` and the positions
above hold; as a plain string it becomes a fourth `<p>` after the `<h4>`
(`.entry > h4 + p + p + p + p`).

The test that guards this order is the one place that must **not** derive from the
model. Presence tests should iterate `model_fields` so they survive format changes;
an order test that does the same follows any reordering and asserts nothing. Write the
expected sequence out explicitly.

### Where the heading hints live

Two different things, two different homes — do not mix them:

- **Data** written as a heading → `Annotated` + `Field(json_schema_extra=...)`, via the
  `MarkdownH1`/`MarkdownH3`/`MarkdownH4` aliases in `models/resume_model.py`. Use
  `json_schema_extra`, never bare `Field(..., markdown=...)` — deprecated in pydantic v2,
  removed in v3. The stored value is the heading **level** as an `int`, never the markup:
  pydantic types that metadata as arbitrary JSON, so `heading_marker()` is the single
  place that turns it back into `#`/`##`/`###`/`####` and rejects anything else. There is
  no `MarkdownH2`: see below.
- **Labels** (section titles) → native `Field(title=...)`, read back via
  `model_fields[name].title`. The `##` never comes from an `Annotated` hint.

The rule that decides: `Field(title=...)` is fixed at class-definition time and shared
by every instance, so it can only ever hold a label. Anything that varies per resume is
data and belongs in a field.

### Frontmatter

An optional YAML block at the top of the file. Only `css` is read; it takes one path or
a list of paths, relative to the `.md`. Every other key is ignored — the block stays
open for the user's own metadata, and closing it would turn every future key into a
breaking change.

Two things are checked and raise: the block must be a mapping, and `css` must hold a
string or a list. Nothing else is validated. We constrain the shape of what we read,
not the presence of what we do not.

**`js` is not read, deliberately.** It used to be; it was dropped because no current
need justifies it, and because a user script is not just a path to append: one that
configures paged.js (`window.PagedConfig`, handlers) must load *before* the polyfill,
anything else after it. That ordering deserves its own design the day a real need
shows up. A `js:` key is now ordinary ignored metadata. For instrumenting a render
(measuring boxes, waiting for pagination), inject the script from Playwright with
`add_init_script` instead.

### Assets and the rendered page

`render_resume(md_path)` writes the HTML **next to the `.md`**, as
`md_path.with_suffix(".html")`, and returns that path. There is no output-path
argument, and that is load-bearing: every `href`/`src` in the page is relative, and
the browser resolves it against the HTML file, not against the working directory.
Writing the HTML anywhere else would break every link, silently. `render_pdf(md_path)`
follows the same rule: the PDF lands next to the `.md` too.

`init_resume()` copies the bundled assets into `resume_builder_files/` beside the `.md`
(`force=True` overwrites every file of the same name, `theme.css` included). The page
never points into the installed package: it depends only on what sits next to it.

Load order in the page, fixed by the renderer:

1. `resume_builder_files/resume.css` — always, first. The layout.
2. the frontmatter `css` entries, in the order given — so a user stylesheet (typically
   the copied `theme.css`, uncommented in the frontmatter) overrides the layout.
3. `resume_builder_files/paged.polyfill.min.js` — always, the only script, last in
   `<body>`, after the content it paginates.

### CSS

Every section div carries both its `id` and `class="section"`, so levels never collide
across sections — `#contact h2` and `#experiences h2` are styled independently, and
`#experiences .entry > h4` addresses one job's subtitle.

## Architecture

`Resume` (pydantic) → `_write_model_to_markdown()` generates a starter `.md` → the user
hand-edits it → `render_resume()` parses that file directly into HTML via Jinja2,
written next to it → `paged.js` → Playwright → PDF.

`render_pdf(md_path)` (`render/renderer_pdf.py`) is the whole chain in one call, and
writes the PDF next to the `.md` as `md_path.with_suffix(".pdf")`. Its contract is **a
paginated PDF or an exception, never a blank PDF**: `page.pdf()` happily prints a page
paged.js never touched, with no error. In order:

1. `importlib.util.find_spec("playwright")`, before anything else: without the `[pdf]`
   extra, an `ImportError` naming `resume-builder[pdf]`. Playwright itself is imported
   only inside the function, so `import resume_builder` works on the base install.
2. `render_resume(md_path)`, always: it checks the `.md`, and a PDF built from an HTML
   left over from an earlier render could silently lag behind the edited file.
3. `resume_builder_files/` must sit next to the `.md` (`NotADirectoryError`), checked
   here rather than discovered as a timeout.
4. `_html_to_pdf()`, private, trusts its caller and does not re-check the HTML. It
   serves the folder with `local_server()` (`render/server.py`: `127.0.0.1`, port 0,
   stopped on exit even on error), never `file://`: paged.js re-fetches stylesheets over
   XHR, which Chromium blocks there, and pagination never runs. It drives Playwright's
   bundled Chromium (no `channel=`: a bare Ubuntu has no Chrome) and waits for paged.js
   itself: an init script sets `window.PagedConfig.after`, registered **before**
   `goto()` because the polyfill reads its config once, on load. No fixed sleep, no
   `networkidle`. A timeout (`_PAGED_TIMEOUT_MS`) becomes a `RuntimeError` carrying the
   page's JavaScript errors. `print_background=True` (the sidebar band is a CSS
   background) and `prefer_css_page_size=True` (`@page` decides the format) are both
   load-bearing.

pydantic appears only on the way *out*. Rendering never parses the user's edited
Markdown back into a strict model — it walks the token stream directly, same as
pagedown/Pandoc.

`MarkdownIt` is configured with `.use(front_matter_plugin).use(attrs_block_plugin)
.use(container_plugin, CONTAINER_NAME)`. That one constant drives the keyword on the
opening fence (`::: section`), the token types (`container_section_open`/`_close`) and
the CSS class on the rendered `<div>` — hence shared, never retyped. The closing fence
carries markers only: the name is forbidden there, so the open and close constants are
deliberately asymmetric.

The Jinja2 template is a real file
(`render/templates/resume.html.j2`, loaded via `PackageLoader`) — hatchling ships
non-`.py` files under `src/resume_builder/` in the wheel automatically.

Tests live in `tests/`, mirroring the `src/resume_builder/` package structure.

Deeper notes live in `claude_private/`, which is gitignored — a fresh clone will not
have it, and everything normative is in this file instead. Locally: `pipeline-schema.md` (the two axes, Markdown-based
and the deferred app-based one), `pagedown-notes.md` (why the conventions are what they
are), `css-layout-notes.md`, `devops-setup.md`, `project-goals.md`.

## Stack

- Project and dependency management: **uv** (no manual pip/venv — use `uv add`, `uv sync`, `uv run`).
- Build backend: **hatchling**.
- Python version: floor `>=3.11` (`requires-python`), dev on **3.13**.
- Runtime dependencies: **markdown-it-py[plugins]** (Markdown parsing, incl. `mdit-py-plugins` for Pandoc-style attributes/fenced-divs/frontmatter), **pydantic** (structured resume data model).
- Optional extra `[pdf]`: **playwright**, for `render_pdf()`. The base install renders HTML only (the user can print it from a browser); `pip install resume-builder[pdf]` adds the PDF step. Chromium is a browser binary, not a Python package: it is installed apart, once per machine, with `uv run playwright install chromium`.
- Dev tooling: **ruff** (lint + format), **mypy** (strict), **pytest**, **pre-commit**, **tox** (+ `tox-uv`).
- Dev dependencies are split into PEP 735 groups in `pyproject.toml`: `lint`, `type`, `test`, and `dev` (which includes all three plus `pre-commit`/`tox`/`tox-uv`). Plain `uv sync` installs everything via the `dev` group. A developer gets everything: `test` lists `resume-builder[pdf]` (the project itself with its extra), so Playwright comes with it; `include-group` cannot reference an extra.
- tox runs on tox-uv's `uv-venv-lock-runner` with `package = "wheel"` (`[tool.tox.env_run_base]`). Every env is built by `uv sync --locked` from `uv.lock`, same as `.venv`, so tox and `.venv` never disagree on a version — and Playwright always matches the Chromium revision installed from the lock (each Playwright release expects its own). The lock moves only when you move it (`uv add`, `uv lock --upgrade`), never as a side effect of tox recreating an env. `package = "wheel"` overrides the runner's `editable` default: tests run against the built wheel, not `src/`, so a non-`.py` file missing from the wheel (template, CSS, polyfill) fails the suite instead of passing silently. Trade-off accepted: CI no longer sees new dependency releases on its own; that signal is meant to come from lock upgrades in their own PR, never mixed into a feature.
- CI: GitHub Actions (`.github/workflows/ci.yml`), matrix over Windows/Linux/macOS, on every push to any branch. Ubuntu runs the full tox matrix (`py311`/`py312`/`py313`/`lint`/`type`); Windows/macOS only run the `py311`/`py312`/`py313` test envs (lint/type are OS-independent, no need to repeat them, and macOS Actions minutes are the most constrained).
- PDF tests in CI: **Ubuntu and Windows, not macOS.** Many users are on Windows, so it cannot be skipped; macOS is the slowest and most limited runner. PDF tests carry the pytest marker `pdf`; macOS runs `-m "not pdf"`. The exclusion is explicit, never "skip when Chromium is missing": a broken install would then turn every PDF test into a silent skip on a green CI. Chromium is installed by one step **per OS**: Ubuntu with `--with-deps` (system libraries), Windows without it, because on Windows Server `--with-deps` installs the Server-Media-Foundation feature (read in Playwright 1.64's `install_media_pack.ps1`), useless for a PDF.
- Versioning: **hatch-vcs** derives the package version from git (tags/commit distance), not a hand-edited `version` field. `src/resume_builder/_version.py` is generated automatically on every `uv sync`/build — it's gitignored, never edited by hand, and exposed as `resume_builder.__version__`. Requires an actual git clone (with history) to resolve correctly; a ZIP download or shallow clone won't compute the version properly.

## Available commands

```bash
uv sync                                    # installs deps (project + dev group) and creates/syncs the .venv
uv run playwright install chromium         # one-time per machine: the browser render_pdf() drives
uv run playwright install --list           # where Chromium is installed, and for which Playwright version
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
