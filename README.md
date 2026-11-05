# Resume builder

[![CI](https://github.com/berthetclement/resume_builder/actions/workflows/ci.yml/badge.svg)](https://github.com/berthetclement/resume_builder/actions/workflows/ci.yml)

This library provides you a markdown template that you can personalize and customize to have a render as your own resume.

This library was created based on the `R` library [pagedown](https://github.com/rstudio/pagedown).

You have the choice to install the library with optional dependencies:
- Display the resume with your browser and print as PDF.
- Install the pdf extra to generate the PDF directly.

## Installation

Currently, the library is only available on github.

```sh
pip install "resume-builder @ git+https://github.com/berthetclement/resume_builder"
```

To render the PDF directly, install the `pdf` extra, then `Chromium` (once per machine).

```sh
pip install "resume-builder[pdf] @ git+https://github.com/berthetclement/resume_builder"
```

The library `playwright` uses a specific version of `Chromium` (only `Chromium` is used in this lib).
Playwright can print to PDF with Chromium only.

```sh
playwright install chromium
```

Usage:
- Initialisation creating a folder and all you need
- You can edit the markdown file (the template show you an example)
- Generate the rendering as html file
- View the html file in your browser

```python
from resume_builder import init_resume, render_resume

# default: resume/resume.md
output_path = init_resume()

# generate the html output (resume/resume.html)
render_resume(output_path)
```

Most of time, you don't want only generate the html file but visualize it. You can use directly `preview_resume()` instead of `render_resume` after initialisation step.

```python
from resume_builder import preview_resume

# generate html + displaying
preview_resume("resume/resume.md")
```

At this step you can print html page to PDF with your own browser (see "NOTE" section below to have a better comprehension of rendering html page).

If you have installed optional dependencies `[pdf]`, you can directly render the markdown file into a pdf file.

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

The goal is creating your own resume from the template (the markdown file). We will see we can also customize the css. All files needed are provided inside a folder. Then you will find inside another folder for external resources (`css` and `js`).

Let's see these steps below.

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

1. Edit `resume.md` with your information.
2. Optional: to change colours and fonts, uncomment the `css` lines in the frontmatter
   of `resume.md`, then edit `resume_builder_files/theme.css`.
3. Save, then run `render_resume()` to generate html page.
4. You can display html page with `preview_resume()` or directly use `render_pdf()`.

## Note
Open the HTML through a local server, not by double-clicking it:
`paged.js` cannot paginate a page opened as `file://`.

That's why you have to use `preview_resume()` and if you are done with testing rendering, think to stop to serve with `stop_preview()`.

You can also if you want serve by yourself using:

```sh
python -m http.server --bind 127.0.0.1 --directory resume
```

Then browse to <http://127.0.0.1:8000/resume.html>, and stop the server with `Ctrl+C`.
