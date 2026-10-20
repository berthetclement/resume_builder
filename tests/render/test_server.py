import re
from pathlib import Path

import pytest

from resume_builder.render.server import local_server


def test_server_raise_directory_not_found(tmp_path: Path) -> None:
    # given
    directory = tmp_path / "nothing"

    # then
    with (
        pytest.raises(NotADirectoryError, match=re.escape(f"{directory} does not exist or is not a directory")),
        local_server(directory),
    ):
        pass


def test_server_starts_and_stops(tmp_path: Path) -> None:
    # given
    directory = tmp_path / "my_directory"
    directory.mkdir()

    # when
    with local_server(directory) as url:
        # then
        assert re.match(r"^http://127\.0\.0\.1:\d+$", url)
