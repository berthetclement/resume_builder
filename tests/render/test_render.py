import re
from pathlib import Path

import pytest

from resume_builder.render.renderer import render_resume
from resume_builder.template.markdown_writer import init_resume


def test_render_raises_file_not_found(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "non_existent_resume.md"

    # when/then
    with pytest.raises(FileNotFoundError, match=re.escape(f"{md_path} does not exist or is not a file")):
        render_resume(md_path)


def test_render_with_empty_content(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "empty_resume.md"
    md_path.write_text("", encoding="utf-8")

    # when/then
    with pytest.raises(ValueError, match=re.escape(f"{md_path} is empty")):
        render_resume(md_path)


def test_render_rejects_non_mapping_frontmatter(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "resume.md"
    md_path.write_text("---\n[css: my-theme.css]\n---\n\n# Resume\n", encoding="utf-8")

    # then
    with pytest.raises(ValueError, match="frontmatter must be a mapping, got list"):
        render_resume(md_path)


def test_render_rejects_a_nested_asset_value(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "resume.md"
    md_path.write_text("---\ncss:\n  theme: my-theme.css\n---\n\n# Resume\n", encoding="utf-8")

    # then
    with pytest.raises(ValueError, match="frontmatter 'css' must be a string or a list, got dict"):
        render_resume(md_path)


def test_render_writes_html_next_to_md_with_same_name(tmp_path: Path) -> None:
    # given — not named "resume", so a hardcoded "resume.html" cannot pass
    md_path = tmp_path / "cv.md"
    md_path.write_text("# Resume\n", encoding="utf-8")

    # when
    output_path = render_resume(md_path)

    # then
    assert output_path.exists()
    assert output_path == tmp_path / "cv.html"


def test_render_without_frontmatter_links_internal_assets(tmp_path: Path) -> None:
    # given — the common case: the user adds none at all
    md_path = tmp_path / "resume.md"
    md_path.write_text("# Resume\n", encoding="utf-8")

    # when
    output_path = render_resume(md_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert html.count("<link") == 1
    assert html.count("<script") == 1
    assert '<link rel="stylesheet" href="resume_builder_files/resume.css">' in html
    assert '<script src="resume_builder_files/paged.polyfill.min.js"></script>' in html


def test_render_ignores_unknown_frontmatter_keys(tmp_path: Path) -> None:
    # given — frontmatter stays open for metadata; only css is consumed, js included
    md_path = tmp_path / "resume.md"
    md_path.write_text("---\ntheme: my-theme.css\njs: my-script.js\n---\n\n# Resume\n", encoding="utf-8")

    # when
    output_path = render_resume(md_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert "my-theme.css" not in html
    assert "my-script.js" not in html


def test_render_with_frontmatter_links_custom_assets_ordered(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "resume.md"
    md_path.write_text("---\ncss:\n  - my-theme.css\n---\n\n# Resume\n", encoding="utf-8")

    # when
    output_path = render_resume(md_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert html.count("<link") == 2
    list_links = re.findall(r'<link rel="stylesheet" href="([^"]+)">', html)
    assert list_links[0] == "resume_builder_files/resume.css"
    assert list_links[1] == "my-theme.css"


def test_render_includes_yaml_with_str_values(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "resume.md"
    md_path.write_text("---\ncss: my-theme.css\n---\n\n# Resume\n", encoding="utf-8")

    # when
    output_path = render_resume(md_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert '<link rel="stylesheet" href="my-theme.css">' in html


def test_render_includes_yaml_list_of_css(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "resume.md"
    md_path.write_text("---\ncss:\n  - my-theme.css\n  - my-theme2.css\n---\n\n# Resume\n", encoding="utf-8")

    # when
    output_path = render_resume(md_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert '<link rel="stylesheet" href="my-theme.css">' in html
    assert '<link rel="stylesheet" href="my-theme2.css">' in html


def test_render_puts_the_markdown_body_in_the_page(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "resume.md"
    md_path.write_text("# Resume\n\nSome text.\n", encoding="utf-8")

    # when
    output_path = render_resume(md_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert "<h1>Resume</h1>" in html
    assert "<p>Some text.</p>" in html


def test_init_then_render_produces_a_complete_page(tmp_path: Path) -> None:
    # given
    md_path = init_resume(target_dir=tmp_path / "my-resume", force=True)

    # when
    output_path = render_resume(md_path)

    # then
    html = output_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html
    assert '<div id="main" class="section">' in html
    assert '<div id="contact" class="section">' in html
    assert '<div id="experiences" class="section">' in html
    assert '<div class="entry">' in html

    for ref in re.findall(r'(?:href|src)="([^"]+)"', html):
        assert (output_path.parent / ref).is_file(), ref
