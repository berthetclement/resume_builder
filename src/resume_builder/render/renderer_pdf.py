import importlib.util
from pathlib import Path

from resume_builder.conventions import ASSETS_FOLDER_NAME
from resume_builder.render.renderer import render_resume
from resume_builder.render.server import local_server

_PAGED_FLAG = "__pagedDone"
_PAGED_HOOK = f"window.PagedConfig = {{ after: () => {{ window.{_PAGED_FLAG} = true; }} }};"
_PAGED_FINISHED = f"() => window.{_PAGED_FLAG} !== undefined"
_PAGED_TIMEOUT_MS = 30_000


def _html_to_pdf(html_path: Path) -> Path:
    """Print an HTML resume to a PDF next to it, once paged.js has paginated it.

    Private: `render_pdf()` is the only caller and guarantees that `html_path`
    exists with `resume_builder_files/` next to it, so nothing is re-checked here.
    The folder is served over HTTP (`local_server`), never `file://`, and the
    PDF is printed only after paged.js's `after` hook has fired.

    Raises:
        RuntimeError: paged.js did not finish within `_PAGED_TIMEOUT_MS`;
            the page's JavaScript errors, if any, are in the message.
    """
    directory = html_path.parent
    with local_server(directory) as url:
        # because 'playwright' is [project.optional-dependencies]
        from playwright.sync_api import Error, TimeoutError, sync_playwright

        output = html_path.with_suffix(".pdf")
        errors: list[Error] = []
        with sync_playwright() as p:
            # init process
            browser = p.chromium.launch()  # page.pdf() is Chromium-only; no channel=: Playwright's bundled build
            page = browser.new_page()

            # catch "event" from paged.js
            page.on("pageerror", lambda error: errors.append(error))

            # goto() returns on page load, but paged.js paginates afterwards:
            # its `after` hook sets a flag, and we wait for that flag.
            page.add_init_script(_PAGED_HOOK)
            page.goto(f"{url}/{html_path.name}")
            try:
                page.wait_for_function(_PAGED_FINISHED, timeout=_PAGED_TIMEOUT_MS)
            except TimeoutError as err:
                context_err = f"paged.js did not finish paginating {html_path.name} within {_PAGED_TIMEOUT_MS} ms."
                message = f"Java Script report 'pageerror': {'; '.join(str(e) for e in errors)}"
                raise RuntimeError(f"{context_err}\n{message}") from err

            # write the final pdf file
            page.pdf(path=output, print_background=True, prefer_css_page_size=True)
            browser.close()

    return output


def render_pdf(md_path: Path) -> Path:
    """Render a Markdown resume file into a paginated PDF.

    Renders the HTML with `render_resume()`, then prints it with Chromium once
    paged.js has paginated it. The PDF is written next to the `.md`.

    Args:
        md_path: Path to the source `.md` file, with `resume_builder_files/`
            next to it (as set up by `init_resume()`).

    Returns:
        Path: The path to the generated PDF file.

    Raises:
        ImportError: The `[pdf]` extra (Playwright) is not installed.
        FileNotFoundError: `md_path` does not exist.
        NotADirectoryError: `resume_builder_files/` is missing next to `md_path`.
        RuntimeError: paged.js did not finish paginating within the timeout.
    """
    # raise error if optional dep are not installed
    if importlib.util.find_spec("playwright") is None:
        raise ImportError("render_pdf needs the [pdf] extra: pip install resume-builder[pdf]")

    # html processing
    html_file = render_resume(md_path)

    # pdf processing (using internal ressources)
    internal_assets_dir = md_path.parent / ASSETS_FOLDER_NAME
    if not internal_assets_dir.is_dir():
        raise NotADirectoryError(f"{internal_assets_dir} not found: run init_resume() first")

    pdf_file = _html_to_pdf(html_file)

    return pdf_file
