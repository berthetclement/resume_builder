import re
import sys
from pathlib import Path

import pytest

from resume_builder.conventions import ASSETS_FOLDER_NAME
from resume_builder.render import renderer_pdf
from resume_builder.render.renderer import render_resume
from resume_builder.render.renderer_pdf import _html_to_pdf, render_pdf
from resume_builder.template.markdown_writer import init_resume


# test html to pdf processing
@pytest.mark.pdf
def test_html_pdf_without_js(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # given
    monkeypatch.setattr(renderer_pdf, "_PAGED_TIMEOUT_MS", 500)

    # 'throw' raise an error for javascript with type 'Error'
    html_content_test = "<script>throw new Error('test')</script>"
    html_path = tmp_path / "error.html"

    html_path.write_text(html_content_test, encoding="utf-8")

    # then
    with pytest.raises(RuntimeError, match=re.escape("Java Script report 'pageerror': test")):
        _html_to_pdf(html_path)


@pytest.mark.pdf
def test_html_pdf_works(tmp_path: Path) -> None:
    # given
    test_path = tmp_path / "test_pdf"
    md_path = init_resume(path=test_path)
    output_path = render_resume(md_path)

    # then
    output_pdf_path = _html_to_pdf(output_path)
    assert output_pdf_path == output_path.with_suffix(".pdf")
    assert output_pdf_path.read_bytes().startswith(b"%PDF")


# rendering final pdf file
def test_render_pdf_raise_md_not_found(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "nothing.md"

    # then
    with pytest.raises(FileNotFoundError, match=re.escape(f"{md_path} does not exist or is not a file")):
        render_pdf(md_path)


def test_render_pdf_import_lib_not_found(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # given
    monkeypatch.setitem(sys.modules, "playwright", None)

    # then
    with pytest.raises(
        ImportError, match=re.escape("render_pdf needs the [pdf] extra: pip install resume-builder[pdf]")
    ):
        render_pdf(tmp_path / "nothing.md")


def test_render_pdf_with_no_asset_folder(tmp_path: Path) -> None:
    # given
    md_file = tmp_path / "empty.md"
    md_file.write_text("empty")

    # then
    with pytest.raises(
        NotADirectoryError,
        match=re.escape(f"{md_file.parent / ASSETS_FOLDER_NAME} not found: run init_resume() first"),
    ):
        render_pdf(md_file)


@pytest.mark.pdf
def test_render_pdf_works(tmp_path: Path) -> None:
    # given
    test_path = tmp_path / "test_render_pdf"
    md_path = init_resume(path=test_path)

    # then
    output_pdf_path = render_pdf(md_path)
    assert output_pdf_path == md_path.with_suffix(".pdf")
    assert output_pdf_path.read_bytes().startswith(b"%PDF")
