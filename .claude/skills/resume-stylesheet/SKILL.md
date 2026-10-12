---
name: resume-stylesheet
description: Rules and verification loop for the paginated CV stylesheet. Use when editing src/resume_builder/assets/resume.css or theme.css, when the rendered HTML or PDF looks wrong (shifted columns, missing band, overlapping dates, a blank PDF), or when writing a test that asserts something about a rendered resume.
---

# Working on the resume stylesheet

The CV is paginated by **pagedjs 0.4.3**, vendored at
`src/resume_builder/assets/paged.polyfill.min.js`. Paged.js rewrites the document
while it paginates, so several ordinary CSS assumptions do not hold. Each rule below
cost a debugging session; the symptom is given first, because that is how you will
meet it.

## Hard constraints

**`var()` is silently ignored inside `@page`.**
*Symptom:* the printed band and the content disagree by exactly 25.4 mm (paged.js
fell back to its 1 in default).
Paged.js parses `@page` with its own parser and drops what it cannot read, including
custom properties — `size` and `margin` alike. Page geometry is written **literally**
in `resume.css`, and `theme.css` says so. Keep the literal `@page` values in sync by
hand with the `--margin-*` variables.

**Ids lose their priority during pagination.**
*Symptom:* a rule applies *in part* — the sidebar keeps its `float` but takes the main
column's width.
Paged.js rewrites `#contact` into `[data-id="contact"]`, dropping specificity from
(1,0,0) to (0,1,0) — a tie with any class rule, broken by source order. So: **defaults
on `.section`, exceptions after them.** Never rely on an id outranking a class.
Measured again on 0.4.3: still 8 rewritten elements.

**`@media screen` is deleted unless it also names `pagedjs-ignore`.**
*Symptom:* pagination runs (`.pagedjs_page` count is right, the PDF is fine) but on
screen the pages sit edge to edge on white — no grey desk, no shadow, one long strip.
Paged.js 0.4.3 unwraps `@media print` and removes every other @media block whose
query names neither `all` nor `pagedjs-ignore`. 0.1.43 let it through, which is why
the version A/B missed it: it compared PDFs only, and print never sees screen rules.
Write `@media screen, pagedjs-ignore { … }` — the browser treats the extra name as an
unknown media type, so the block stays screen-only. Verified: screen preview restored,
PDF page hashes unchanged. Any check of the screen preview must look at the screen,
not the PDF.

**Metadata is counted from the `<h4>`, never from the start of the entry.**
*Symptom:* a `TitledEntry`'s prose (or `main`'s intro paragraph) comes out bold, or
right-aligned and grey — styled as a subtitle or a location it is not.
`.entry > p:nth-of-type(n)` counts every `<p>` in the entry, so it cannot tell a
metadata line from prose. The subtitle is an `<h4>` (`####`) and the lines after it
are addressed with adjacent siblings: `.entry > h4 + p` (location), `+ p + p`
(start date), and so on — the table in CLAUDE.md "Entry field order" is the mapping.
An entry with no `<h4>` has no metadata, so its `<p>` match nothing and stay prose.
Keep `>` on the anchor (`.entry > h4`): the chain then stays among the entry's direct
children, and a `<p>` inside a loose list item (`<li><p>…</p></li>`) cannot enter it.

**Entry content is a grid, decoration is absolute.**
*Symptom:* dates overlap or blur in the paginated output.
Absolutely positioned content reserves no space, so paged.js lays it out on top of
itself. Content goes in the per-entry grid; only `::before` / `::after` (the rule and
the dot) are absolute, because a pseudo-element never has to reserve space.

**Backgrounds need `print_background=True`.**
The band is painted on `.pagedjs_page`. Playwright drops element backgrounds from the
PDF unless that argument is passed.

## Which file to edit

| file | belongs to | edit it? |
|---|---|---|
| `src/resume_builder/assets/resume.css` | the library | yes — this is the layout |
| `src/resume_builder/assets/theme.css` | the user, after init | only its comments and its *taste* values |
| `resume_builder_files/*` in a user's folder | copies | no — regenerated |

`theme.css` is loaded **after** `resume.css`, so anything there wins. Only put values
in it that are a matter of taste (colours, fonts, base size): an active declaration
freezes that value in every project ever created, and blocks a later improvement.
Spacing and geometry stay commented.

## Verification loop

Looking at the HTML in a browser is not enough — paged.js only runs its full layout
when it paginates, and the PDF is the artifact that matters.

1. Render the Markdown to HTML.
2. Serve the folder on `127.0.0.1` (an ephemeral port, loopback only).
3. Open it with Playwright's bundled Chromium, and **wait for pagination to finish**:
   inject `window.PagedConfig = { after: () => { window.__pagedDone = true } }`
   with `add_init_script`, then `wait_for_function("window.__pagedDone === true")`.
   Waiting on a `.pagedjs_page` selector races — the first page appears while later
   ones are still being laid out.
4. `page.pdf(print_background=True, prefer_css_page_size=True)`.
5. Rasterise with `pypdfium2` and look at it.

**Never serve over `file://`.** Paged.js re-fetches every stylesheet over XHR; under
`file://` the origin is `null` and CORS blocks it, so pagination never starts — and
`page.pdf()` still succeeds, writing a plausible-looking **blank PDF with no error**.

## Asserting things about a rendered resume

Anything that checks a CV must first assert that pagination actually ran, for the
reason above:

```python
assert page.eval_on_selector_all(".pagedjs_page", "e => e.length") > 0
```

Three useful levels, cheapest first:

- **Structure** — query the paginated DOM: page count, which elements carry
  `[data-id]`, how many `<p>` an entry has.
- **Geometry** — read boxes in millimetres rather than eyeballing them. Measure
  px-per-mm from a probe element instead of assuming 96 dpi:
  `el.getBoundingClientRect().width / 96 * 25.4` is a starting point, not a truth.
  This is how the sidebar's 65 mm and the 25.4 mm `@page` drift were both caught.
- **Pixels** — render each PDF page with `pypdfium2` and compare sha256 against a
  known-good run. Use it to prove a change is inert (a dependency bump, a refactor),
  not to pin a design: any deliberate visual change invalidates every hash.

A test that only asserts "the PDF exists" or "it has 2 pages" will pass on a blank
document. Assert something a blank page cannot satisfy.

## Known open points

- Page margins and the sidebar band are wider than they should be.
- `--text-family` names a font nothing loads, so everything renders in the fallback.
  Naming a font is not shipping it; the rendering machine must already have it.
- Until the `####` subtitle lands in the model and `resume.css` (decided 2026-10-12,
  tracked in `claude_private/pipeline-schema.md`), the stylesheet still uses
  `p:nth-of-type(n)`, so prose in a `TitledEntry` and in `main` still comes out bold.
