from collections.abc import Generator
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

# Loopback only: the served folder is never reachable from the network.
_HOST = "127.0.0.1"


@contextmanager
def local_server(directory: Path) -> Generator[str, None, None]:
    """Serve `directory` over HTTP for the duration of a `with` block.

    Yields the base URL (`http://127.0.0.1:<port>`). The server is stopped when the
    block exits, even if it raises.
    """
    # Runs on entering the `with`, before anything is started.
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} does not exist or is not a directory")

    # The server builds one handler per request and passes only (request, address,
    # server), so partial pre-fills `directory`; without it the handler would serve
    # the current working directory.
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))

    # Port 0 lets the OS pick a free port. Leaving this `with` calls server_close(),
    # which releases the port.
    with ThreadingHTTPServer((_HOST, 0), handler) as server:
        port = server.server_address[1]

        # serve_forever() blocks until shutdown(): run it in a background thread so
        # the caller's `with` body can run meanwhile. daemon=True: a forgotten thread
        # never keeps Python from exiting.
        Thread(target=server.serve_forever, daemon=True).start()

        try:
            # Pause here: the caller's `with` body runs, with this URL as its value.
            yield f"http://{_HOST}:{port}"
        finally:
            # Runs when the caller's `with` body ends, normally or by an exception.
            # Stops the serve_forever() loop and waits for it to finish.
            server.shutdown()
