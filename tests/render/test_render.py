from pathlib import Path

from resume_builder.render.renderer import render_resume
from resume_builder.template.markdow_editor import init_resume


def test_render_markdown_to_html_output_file(tmp_path: Path) -> None:
    # given
    md_path = init_resume(target_dir=tmp_path / "my-resume", force=True)

    # when
    render_resume(md_path, tmp_path / "my-resume/resume.html")

    # test
    assert (tmp_path / "my-resume/resume.html").exists()
