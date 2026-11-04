import re
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest

from resume_builder.render.server import local_server, preview_resume


def test_server_raise_directory_not_found(tmp_path: Path) -> None:
    # given
    directory = tmp_path / "nothing"

    # then
    with (
        pytest.raises(NotADirectoryError, match=re.escape(f"{directory} does not exist or is not a directory")),
        local_server(directory),
    ):
        pass


def test_server_starts(tmp_path: Path) -> None:
    # given
    directory = tmp_path / "my_directory"
    directory.mkdir()

    # when
    with local_server(directory) as url:
        # then
        assert re.match(r"^http://127\.0\.0\.1:\d+$", url)


def test_server_serves_files(tmp_path: Path) -> None:
    # given
    directory = tmp_path / "my_directory"
    directory.mkdir()
    file_path = directory / "test.txt"
    file_path.write_text("Hello, world!", encoding="utf-8")

    # when
    with local_server(directory) as url:
        # then
        response = urlopen(f"{url}/test.txt").read()
        assert response.decode("utf-8") == "Hello, world!"


def test_server_stops_after_context(tmp_path: Path) -> None:
    # given
    directory = tmp_path / "my_directory"
    directory.mkdir()

    # when
    with local_server(directory) as url:
        pass

    # then
    with pytest.raises(URLError):
        urlopen(url)


def test_server_stops_even_on_exception(tmp_path: Path) -> None:
    # given
    directory = tmp_path / "my_directory"
    directory.mkdir()

    # when
    with pytest.raises(RuntimeError, match="Simulated error"), local_server(directory) as url:
        raise RuntimeError("Simulated error")

    # then
    with pytest.raises(URLError):
        urlopen(url)


def test_preview_opens_browser(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # given
    directory = tmp_path / "dir_preview"
    directory.mkdir()
    md_file = directory / "resume.md"
    md_file.write_text("# Resume", encoding="utf-8")
    asset_dir = directory / "resume_builder_files"
    asset_dir.mkdir()

    opened: list[str] = []

    def fake_open(url: str) -> None:
        opened.append(url)

    def fake_input(prompt: str) -> str:
        assert re.match(r"http://127\.0\.0\.1:\d+/resume.html", opened[0])
        return ""

    monkeypatch.setattr(webbrowser, "open", fake_open)
    monkeypatch.setattr("builtins.input", fake_input)

    # when
    preview_resume(md_file)
