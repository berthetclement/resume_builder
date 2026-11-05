import re
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest

from resume_builder.render.server import local_server, preview_resume, stop_preview


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


## Test preview_resume() function
def test_preview_raise_without_assets_folder(tmp_path: Path) -> None:
    # given
    md_file = tmp_path / "resume.md"
    md_file.write_text("# Resume", encoding="utf-8")

    # then
    with pytest.raises(NotADirectoryError, match="run init_resume\\(\\) first"):
        preview_resume(md_file)


def test_preview_serves_page_until_stopped(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # given
    directory = tmp_path / "dir_preview"
    directory.mkdir()
    md_file = directory / "resume.md"
    md_file.write_text("# Resume", encoding="utf-8")
    asset_dir = directory / "resume_builder_files"
    asset_dir.mkdir()

    def fake_open(url: str) -> None:
        opened.append(url)

    opened: list[str] = []
    monkeypatch.setattr(webbrowser, "open", fake_open)

    # when
    url = preview_resume(md_file)

    # then
    try:
        assert re.match(r"http://127\.0\.0\.1:\d+/resume\.html", url)
        assert b"Resume" in urlopen(url).read()
        assert opened == [url]
    finally:
        stop_preview()

    with pytest.raises(URLError):
        urlopen(url)


def test_preview_second_call_replaces_the_first(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # given
    md_file = tmp_path / "resume.md"
    md_file.write_text("# Resume", encoding="utf-8")
    (tmp_path / "resume_builder_files").mkdir()
    monkeypatch.setattr(webbrowser, "open", lambda url: None)

    # when
    first = preview_resume(md_file)
    second = preview_resume(md_file)

    # then
    try:
        with pytest.raises(URLError):
            urlopen(first)
        assert b"Resume" in urlopen(second).read()
    finally:
        stop_preview()
