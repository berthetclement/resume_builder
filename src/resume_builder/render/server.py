import webbrowser
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from resume_builder.conventions import ASSETS_FOLDER_NAME
from resume_builder.render.renderer import render_resume

# Loopback only: the served folder is never reachable from the network.
_HOST = "127.0.0.1"

# The running preview server, if any: entered in preview_resume(), exited in stop_preview().
_PREVIEW = ExitStack()


@contextmanager
def local_server(directory: Path) -> Generator[str, None, None]:
    """Serve local HTTP.

    Yields the base URL (`http://127.0.0.1:<port>`)
    """
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} does not exist or is not a directory")

    # The server builds one handler per request and passes only (request, address, server)
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))

    # Port 0 lets the OS pick a free port. Leaving this `with` calls server_close(),
    # which releases the port.
    with ThreadingHTTPServer((_HOST, 0), handler) as server:
        port = server.server_address[1]

        # serve_forever() blocks until shutdown(): run it in a background thread so
        # the caller's `with` body can run meanwhile. daemon=True: a forgotten thread
        # never keeps Python from exiting.
        Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

        try:
            # Pause here: the caller's `with` body runs, with this URL as its value.
            yield f"http://{_HOST}:{port}"
        finally:
            # Runs when the caller's `with` body ends, normally or by an exception.
            # Stops the serve_forever() loop and waits for it to finish.
            server.shutdown()


def preview_resume(md_path: str | Path) -> str:
    """Render a Markdown resume and preview it in the browser.

    Serves the folder on 127.0.0.1 in the background and returns at once, so the
    session stays usable: edit the `.md`, call `render_resume()`, refresh the page.
    A new call replaces the previous preview; `stop_preview()` or quitting Python
    stops it. Meant for interactive use: a script ends, and the server with it.

    Returns:
        str: the URL of the rendered page.
    """
    # html processing
    html_file = render_resume(md_path)

    # check the target is in the same folder as the source, and that the assets folder is present
    internal_assets_dir = html_file.parent / ASSETS_FOLDER_NAME
    if not internal_assets_dir.is_dir():
        raise NotADirectoryError(f"{internal_assets_dir} not found: run init_resume() first")

    _PREVIEW.close()  # stop the previous preview, if any
    url = _PREVIEW.enter_context(local_server(html_file.parent))
    page_url = f"{url}/{html_file.name}"
    print(f"Previewing {html_file.name} at {page_url}")
    webbrowser.open(page_url)
    return page_url


def stop_preview() -> None:
    """Stop the preview server started by `preview_resume()`, if any."""
    _PREVIEW.close()
