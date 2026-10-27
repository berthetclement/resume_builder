from pathlib import Path

import pytest

from resume_builder.conventions import (
    ASSET_CSS_BUILTIN_FILE_NAME,
    ASSET_CSS_USER_FILE_NAME,
    ASSET_JS_BUILTIN_FILE_NAME,
    ASSETS_FOLDER_NAME,
    INIT_RESUME_FILE_NAME,
)
from resume_builder.template.markdown_writer import init_resume


def test_init_resume_raise_wrong_extension() -> None:
    # then
    with pytest.raises(ValueError, match="Only '.md' extension is accepted"):
        init_resume(path="wrong_file.txt")


@pytest.mark.parametrize(
    "given",
    [
        "resume",
        "tests/resume",
    ],
)
def test_init_resume_raise_for_existing_dir(given: str, tmp_path: Path) -> None:
    # given
    init_path = tmp_path / given
    md_path = init_resume(path=init_path)

    # update an asset to test a file inside is preserved
    css_path = md_path.parent / ASSETS_FOLDER_NAME / ASSET_CSS_USER_FILE_NAME
    with css_path.open("a") as myfile:
        myfile.write("\nappended text")
    before = css_path.read_text()

    # then
    with pytest.raises(FileExistsError):
        init_resume(path=init_path)
    assert before == css_path.read_text()


def test_init_resume_raise_for_empty_existing_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # given
    monkeypatch.chdir(tmp_path)

    path = tmp_path / "empty"
    path.mkdir()

    # then
    with pytest.raises(FileExistsError):
        init_resume(path="empty")


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("resume", "resume/resume.md"),
        ("tests/resume", "tests/resume/resume.md"),
        ("resume.md", "resume/resume.md"),
        ("tests/resume.md", "tests/resume/resume.md"),
    ],
)
def test_init_resume_md_path(given: str, expected: str, tmp_path: Path) -> None:
    # given
    init_path = tmp_path / given

    # when
    output_path_file = init_resume(path=init_path)

    # then
    assert output_path_file == tmp_path / expected


def test_init_resume_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Check if all files are created in the target directory.
    - .md file
    - folder for assets
    - asset files
    """
    # given
    monkeypatch.chdir(tmp_path)

    # when
    output_path_file = init_resume()

    # then
    root = Path("resume")
    assert output_path_file == root / INIT_RESUME_FILE_NAME
    assert output_path_file.is_file()

    assets_name_file = [ASSET_CSS_BUILTIN_FILE_NAME, ASSET_CSS_USER_FILE_NAME, ASSET_JS_BUILTIN_FILE_NAME]
    for asset in assets_name_file:
        path = output_path_file.parent / ASSETS_FOLDER_NAME / asset
        assert path.is_file()
