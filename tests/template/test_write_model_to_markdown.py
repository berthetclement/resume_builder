from pathlib import Path

from resume_builder.models.resume_model import Resume
from resume_builder.template.constants import CONTACT_SECTION_TITLE, WORK_EXPERIENCE_TITLE_NAME
from resume_builder.template.markdown_editor import write_model_to_markdown

"""Pin the Markdown contract that `write_model_to_markdown` produces.

These tests check *structure*, not prose: which heading level a field becomes, what
wraps a section, in which order an entry's lines appear. The contract is the one in
CLAUDE.md "Conventions" — the stylesheet addresses these elements by level and by
position, so a silent change here breaks the CSS with nothing else failing.

The library ships a single resume shape (`DEFAULT_RESUME`), so these tests describe
that shape.

Presence assertions derive from the model, so they survive formatting changes.
Structure assertions are written out literally — derived ones would follow the code
and assert nothing.
"""


# ----helper track Pydantic "section" tag with ("{#id}")
def _section_lines(content: str, section_name: str) -> list[str]:
    """Lines from section {#section_name}, until the next."""
    lines = content.splitlines()
    start = lines.index(f"{{#{section_name}}}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("{#")), len(lines))
    return lines[start:end]


# test building section according to Pydantic fields
def test_each_field_gets_its_own_section(default_markdown_resume_content: str) -> None:
    # then
    lines = default_markdown_resume_content.splitlines()

    for field_name in Resume.model_fields:
        section = _section_lines(default_markdown_resume_content, field_name)

        assert section[0] == f"{{#{field_name}}}"
        assert section[1] == "::: section"
        assert section.count(":::") == 1

    assert lines.count("::: section") == len(Resume.model_fields)


# test title field construction by Pydantic
def test_section_title_comes_from_field_title(default_markdown_resume_content: str) -> None:
    # then
    lines = default_markdown_resume_content.splitlines()

    assert f"## {CONTACT_SECTION_TITLE}" in lines
    assert f"## {WORK_EXPERIENCE_TITLE_NAME}" in lines


def test_main_has_no_section_title(default_markdown_resume_content: str) -> None:
    # then — main's heading is the h1 name, by design
    assert not [line for line in _section_lines(default_markdown_resume_content, "main") if line.startswith("## ")]


# test json_extra_field drive well levels contructions by Pydantic
def test_heading_hint_drives_the_level(default_resume: Resume, default_markdown_resume_content: str) -> None:
    # then
    lines = default_markdown_resume_content.splitlines()

    assert f"# {default_resume.main.user_name}" in lines  # MarkdownH1
    assert f"### {default_resume.main.title_position}" in lines  # MarkdownH3
    assert f"### {default_resume.experiences[0].position}" in lines  # MarkdownH3


# TODO old test
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
