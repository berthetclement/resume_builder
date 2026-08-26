import re
from pathlib import Path

import pytest

from resume_builder.models.resume_model import Resume
from resume_builder.template.markdow_editor import init_resume, write_model_to_markdown


def test_write_model_to_markdown(tmp_path: Path, default_resume: Resume) -> None:
    # when
    write_model_to_markdown(default_resume, tmp_path / "test_resume.md")

    # then
    assert (tmp_path / "test_resume.md").exists()

    # check markdown content is in line with the model data
    content = (tmp_path / "test_resume.md").read_text(encoding="utf-8")

    # main sections
    assert "{#main}" in content
    assert "{#contact}" in content
    assert "{#experiences}" in content

    # track markdown "container_plugin" ("section")
    assert "::: section" in content

    # check contact details
    assert "John Doe" in content
    assert "john.doe@example.com" in content
    assert "123-456-7890" in content

    # every experience value reaches the file — derived from the model, so this
    # survives formatting changes but still fails if an entry renders empty
    for entry in default_resume.experiences:
        for value in entry.model_dump().values():
            if isinstance(value, list):
                for item in value:
                    assert str(item) in content
            else:
                assert str(value) in content


def test_init_default_resume(tmp_path: Path) -> None:
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
