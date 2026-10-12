import re
from pathlib import Path

import pytest

from resume_builder.conventions import (
    ASSET_CSS_BUILTIN_FILE_NAME,
    ASSET_CSS_USER_FILE_NAME,
    ASSET_JS_BUILTIN_FILE_NAME,
    ASSETS_FOLDER_NAME,
    INIT_FOLDER_NAME,
    INIT_RESUME_FILE_NAME,
)
from resume_builder.template.markdown_writer import init_resume


def test_init_resume_default(tmp_path: Path) -> None:
    """Check if all files are created in the target directory."""
    # when
    init_resume(target_dir=tmp_path)

    # then
    init_resume_path = tmp_path / INIT_FOLDER_NAME
    init_resume_assets_path = init_resume_path / ASSETS_FOLDER_NAME
    test_resume_path = init_resume_path / INIT_RESUME_FILE_NAME
    assert test_resume_path.exists()
    test_css_path = init_resume_assets_path / ASSET_CSS_BUILTIN_FILE_NAME
    assert test_css_path.exists()
    test_js_path = init_resume_assets_path / ASSET_JS_BUILTIN_FILE_NAME
    assert test_js_path.exists()
    test_user_css_path = init_resume_assets_path / ASSET_CSS_USER_FILE_NAME
    assert test_user_css_path.exists()


def test_init_resume_raise_overwrite(tmp_path: Path) -> None:
    # when
    test_resume_path = tmp_path / INIT_FOLDER_NAME / INIT_RESUME_FILE_NAME
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
    test_resume_path = tmp_path / INIT_FOLDER_NAME / INIT_RESUME_FILE_NAME
    assert test_resume_path.exists()


def test_init_resume_with_directory(tmp_path: Path) -> None:
    # given
    target_dir = tmp_path / "subdir"

    # when
    init_resume(target_dir=target_dir)

    # then
    init_resume_path = target_dir / INIT_FOLDER_NAME
    test_resume_path = init_resume_path / INIT_RESUME_FILE_NAME

    assert test_resume_path.exists()


def test_init_resume_with_name(tmp_path: Path) -> None:
    # given
    name_file = "my_resume.md"

    # when
    init_resume(target_dir=tmp_path, filename=name_file)

    # then
    test_resume_path = tmp_path / INIT_FOLDER_NAME / name_file
    assert test_resume_path.exists()
