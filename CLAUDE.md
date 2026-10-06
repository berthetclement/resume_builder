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

### Heading levels — exactly three, fixed meaning

| Level | Meaning | Where it comes from |
|---|---|---|
| `#` | document title (the person's name) | `MarkdownH1` hint on `Main.user_name` |
| `##` | section title (`Contact Information`, `Work Experience`) | `Field(title=...)` on the `Resume` field |
| `###` | entry title — **opens an `.entry` box** | `MarkdownH3` hint on the entry's first field (`Entry.title`, `TitledEntry.title`, `Main.title_position`) |

`main` is the only exception, and it needs no special-casing in code: it has no
`Field(title=...)` (so no `##` is emitted) and it is the only section holding the `#`.

### Section markup

One `::: section` per `Resume` field, `id` = the field name:

```markdown
{#experiences}
::: section
## WORK EXPERIENCE

### Consultant Data Scientist

Acme Corp

Paris, France

2021

2022

- Led the R package chain.
- Released to CRAN.

:::
```

The line order inside the entry is not free — see "Entry field order" below. A list
field renders as `- item` lines; every other field renders as one bare line. No
field is optional: `_write_model_to_markdown` carries no `None` branch, so an
optional field left unset would write the literal string "None" into the file.

- `{#id}` must be **on its own line, immediately before** the block it targets.
  Pandoc/pagedown's trailing form (`## Title {#id}`) does *not* work with
  `attrs_block_plugin`.
- The container wraps the *whole* section, heading included — CSS Grid treats every
  direct child of the grid container as its own item, so the heading and its content
  must move as one unit.
- **One blank line between every field.** This is load-bearing, not cosmetic:
  CommonMark merges adjacent lines into a single `<p>`, and no stylesheet can pull
  them apart afterwards.

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
- The box is required: `break-inside: avoid` needs an element, and positional
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
| gets an `.entry` box | no | yes | yes |

`BriefEntry` holds free content under its `##` and nothing else. With no `###`,
`wrap_entries()` has nothing to wrap and the positional contract below does not apply
to it — the same situation as a section the user writes by hand as a plain list.

**Three fixed-arity classes, not one class with optional fields.** The stylesheet
addresses lines by index, and `nth-of-type` counts what is *present*, not what the
model declares. Omitting a **trailing** field is harmless: the unmatched rules style
nothing. Omitting a **middle** one shifts everything after it by one — an entry with
dates but no location gets its start date styled as a location, with no exception and
no failing test, visible only on the rendered page. Optional fields permit that hole;
classes whose fields are all required forbid it, because every entry in a section then
has the same shape.

Hence the rule for any new entry class: its `<p>`-producing fields must be a **prefix**
of the order in "Entry field order" below — optional by truncation, never by holes.
`description` counts as one of those `<p>` fields when it is a plain `str`; only as a
list does it escape the count, rendering as `<ul>`.

### Entry field order

Inside an entry, **position is meaning**. The stylesheet addresses fields by index, so
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
| 2 | `subtitle` | `<p>` | `.entry > p:nth-of-type(1)` |
| 3 | `location` | `<p>` | `.entry > p:nth-of-type(2)` |
| 4 | `start_date` | `<p>` | `.entry > p:nth-of-type(3)` |
| 5 | `end_date` | `<p>` | `.entry > p:nth-of-type(4)` |
| 6 | `description` | `<ul><li>` | `.entry > ul > li` |

**The child combinator is load-bearing.** Written `.entry p:nth-of-type(1)`, the
selector also matches the `<p>` inside a loose list item — bullets separated by a
blank line render as `<li><p>…</p></li>`, and that `<p>` is the first of its kind
among its siblings, so it would pick up the styling meant for `subtitle`. The
writer emits tight lists, but the user hand-edits this file.

`description` is `str | list[str]`: as a list it becomes a `<ul>` and the indices above
hold; as a plain string it becomes a fifth `<p>` instead.

The test that guards this order is the one place that must **not** derive from the
model. Presence tests should iterate `model_fields` so they survive format changes;
an order test that does the same follows any reordering and asserts nothing. Write the
expected sequence out explicitly.

### Where the heading hints live

Two different things, two different homes — do not mix them:

- **Data** written as a heading → `Annotated` + `Field(json_schema_extra=...)`, via the
  `MarkdownH1`/`MarkdownH3` aliases in `models/resume_model.py`. Use `json_schema_extra`,
  never bare `Field(..., markdown=...)` — deprecated in pydantic v2, removed in v3.
  The stored value is the heading **level** as an `int`, never the markup: pydantic types
  that metadata as arbitrary JSON, so `heading_marker()` is the single place that turns it
  back into `#`/`##`/`###` and rejects anything else. There is no `MarkdownH2`: see below.
- **Labels** (section titles) → native `Field(title=...)`, read back via
  `model_fields[name].title`. The `##` never comes from an `Annotated` hint.

The rule that decides: `Field(title=...)` is fixed at class-definition time and shared
by every instance, so it can only ever hold a label. Anything that varies per resume is
data and belongs in a field.

### Frontmatter

An optional YAML block at the top of the file. Only `css` and `js` are read; each takes
one path or a list of paths. Every other key is ignored — the block stays open for the
user's own metadata, and closing it would turn every future key into a breaking change.

Two things are checked and raise: the block must be a mapping, and `css`/`js` must hold
a string or a list. Nothing else is validated. We constrain the shape of what we read,
not the presence of what we do not.

### CSS

Every section div carries both its `id` and `class="section"`, so levels never collide
across sections — `#contact h2` and `#experiences h2` are styled independently, and
`#experiences .entry > p:nth-of-type(1)` addresses one job's first line.

## Architecture

`Resume` (pydantic) → `_write_model_to_markdown()` generates a starter `.md` → the user
hand-edits it → `render_resume()` parses that file directly into HTML via Jinja2 →
`paged.js` → Playwright → PDF.

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
