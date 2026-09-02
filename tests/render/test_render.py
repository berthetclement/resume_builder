import re
from pathlib import Path

import pytest

from resume_builder.render.renderer import render_resume
from resume_builder.template.markdown_editor import init_resume


def test_render_resume_raises_file_not_found(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "non_existent_resume.md"
    output_path = tmp_path / "output_resume.html"

    # when/then
    with pytest.raises(FileNotFoundError, match=re.escape(f"{md_path} does not exist or is not a file")):
        render_resume(md_path, output_path)


def test_render_resume_with_empty_content(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "empty_resume.md"
    md_path.write_text("", encoding="utf-8")
    output_path = tmp_path / "output_resume.html"

    # when/then
    with pytest.raises(ValueError, match=re.escape(f"{md_path} is empty")):
        render_resume(md_path, output_path)


def test_render_resume_includes_yaml_css_from_frontmatter(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "resume.md"
    md_path.write_text("---\ncss:\n  - my-theme.css\n  - my-theme2.css\n---\n\n# Resume\n", encoding="utf-8")
    output_path = tmp_path / "resume.html"

    # when
    render_resume(md_path, output_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert '<link rel="stylesheet" href="my-theme.css">' in html
    assert '<link rel="stylesheet" href="my-theme2.css">' in html


def test_render_resume_puts_the_markdown_body_in_the_page(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "resume.md"
    md_path.write_text("# Resume\n\nSome text.\n", encoding="utf-8")
    output_path = tmp_path / "resume.html"

    # when
    render_resume(md_path, output_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert "<h1>Resume</h1>" in html
    assert "<p>Some text.</p>" in html


def test_render_resume_without_frontmatter_links_no_assets(tmp_path: Path) -> None:
    # given — the common case: the user adds none at all
    md_path = tmp_path / "resume.md"
    md_path.write_text("# Resume\n", encoding="utf-8")
    output_path = tmp_path / "resume.html"

    # when
    render_resume(md_path, output_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert "<link" not in html
    assert "<script" not in html


def test_render_resume_includes_every_js_from_frontmatter(tmp_path: Path) -> None:
    # given — two entries, so the template loop is actually exercised
    md_path = tmp_path / "resume.md"
    md_path.write_text("---\njs:\n  - a.js\n  - b.js\n---\n\n# Resume\n", encoding="utf-8")
    output_path = tmp_path / "resume.html"

    # when
    render_resume(md_path, output_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert '<script src="a.js"></script>' in html
    assert '<script src="b.js"></script>' in html


def test_init_then_render_produces_a_complete_page(tmp_path: Path) -> None:
    # given
    md_path = init_resume(target_dir=tmp_path / "my-resume", force=True)

    # when
    output_path = tmp_path / "my-resume/resume.html"
    render_resume(md_path, output_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html
    assert '<div id="main" class="section">' in html
    assert '<div id="contact" class="section">' in html
    assert '<div id="experiences" class="section">' in html
    assert '<div class="entry">' in html
