# Resume builder

[![CI](https://github.com/berthetclement/resume_builder/actions/workflows/ci.yml/badge.svg)](https://github.com/berthetclement/resume_builder/actions/workflows/ci.yml)

This library provides you a markdown template that you can personalize and customize to have a render as your own resume.

This library was created based on the `R` library [pagedown](https://github.com/rstudio/pagedown).

You have the choice to install the library with optional dependencies:
- Display the resume with your browser and print as PDF.
- Install the pdf extra to generate the PDF directly.

## Installation

Currently, the library is still only in development mode.

```sh
# Last development version from github
pip install "resume-builder @ git+https://github.com/berthetclement/resume_builder"

# with uv
uv pip install "resume-builder @ git+https://github.com/berthetclement/resume_builder"
```

Usage:

```python
from resume_builder import init_resume, render_resume

# init the folder and generate the template as a markdown file
output_path = init_resume()  # resume/resume.md

# generate the html output (near markdown file)
render_resume(output_path)
```

Install the optional dependencies to generate pdf file.
Then install `Chromium`, once per machine: it is the browser that prints the PDF.

```sh
pip install "resume-builder[pdf] @ git+https://github.com/berthetclement/resume_builder"

# with uv
uv pip install "resume-builder[pdf] @ git+https://github.com/berthetclement/resume_builder"

# install Chromium
playwright install chromium

# with uv
uv run playwright install chromium
```

Now you can directly render the markdown file into a pdf file.

```python
from resume_builder import render_pdf

# generate the pdf output (near markdown file)
render_pdf("resume/resume.md")
```

See the documentation of `init_resume()` to initiate with your own name and own tree directory.

```python
help(init_resume)
```

## Customize your resume

`init_resume()` creates this folder:

```
resume/
├── resume.md                  # your resume: edit this file
└── resume_builder_files/
    ├── resume.css             # layout
    ├── theme.css              # colours and fonts, yours to edit
    └── paged.polyfill.min.js  # pagination
```

Follow these steps to customize it to your needs:

1. Edit `resume.md` with your content.
2. Optional: to change colours and fonts, uncomment the `css` lines in the frontmatter
   of `resume.md`, then edit `resume_builder_files/theme.css`.
3. Save, then run `render_resume()` (or `render_pdf()`) again.

> **Note:** open the HTML through a local server, not by double-clicking it:
> paged.js cannot paginate a page opened as `file://`.
>
> ```sh
> python -m http.server --bind 127.0.0.1 --directory resume
>
> # with uv
> uv run python -m http.server --bind 127.0.0.1 --directory resume
> ```
>
> Then browse to <http://127.0.0.1:8000/resume.html>, and stop the server with `Ctrl+C`.
