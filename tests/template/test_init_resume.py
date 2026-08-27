import re
from pathlib import Path

import pytest

from resume_builder.template.markdown_editor import init_resume


def test_init_resume_default(tmp_path: Path) -> None:
    # when
    init_resume(target_dir=tmp_path)

    # then
    test_resume_path = tmp_path / "resume.md"
    assert test_resume_path.exists()


def test_init_resume_raise_overwrite(tmp_path: Path) -> None:
    # when
    test_resume_path = tmp_path / "resume.md"
    init_resume(target_dir=tmp_path)

    # then
    with pytest.raises(
        FileExistsError, match=re.escape(f"{test_resume_path} already exists — pass force=True to overwrite")
    ):
        init_resume(target_dir=tmp_path)


def test_init_resume_accept_overwrite(tmp_path: Path) -> None:
    # given
    init_resume(target_dir=tmp_path)

    # when
    init_resume(target_dir=tmp_path, force=True)

    # then
    test_resume_path = tmp_path / "resume.md"
    assert test_resume_path.exists()


def test_init_resume_with_directory(tmp_path: Path) -> None:
    # given
    target_dir = tmp_path / "subdir"

    # when
    init_resume(target_dir=target_dir)

    # then
    test_resume_path = target_dir / "resume.md"
    assert test_resume_path.exists()


def test_init_resume_with_name(tmp_path: Path) -> None:
    # given
    name_file = "my_resume.md"

    # when
    init_resume(target_dir=tmp_path, filename=name_file)

    # then
    test_resume_path = tmp_path / name_file
    assert test_resume_path.exists()
