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
    with open(tmp_path / "test_resume.md") as f:
        content = f.read()
        # main sections
        assert "# Resume" in content
        assert "## name" in content
        assert "## title" in content
        assert "## contact" in content
        assert "## experiences" in content

        # track markdown "container_plugin" ("section")
        assert "::: section" in content

        # check contact details
        assert "John Doe" in content
        assert "- **email**: john.doe@example.com" in content
        assert "- **phone**: 123-456-7890" in content

        # check experiences details
        assert "### Acme Corp" in content
        assert "- **position**: Developer" in content
        assert "- **start_date**: 2020-01-01" in content
        assert "- **end_date**: 2021-01-01" in content

        assert "### Globex Corporation" in content
        assert "Software Engineer" in content
        assert "- **start_date**: 2021-02-01" in content
        assert "- **end_date**: 2022-01-01" in content

        assert "### Initech" in content
        assert "Project Manager" in content
        assert "- **start_date**: 2022-02-01" in content
        assert "- **end_date**: 2023-01-01" in content


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
