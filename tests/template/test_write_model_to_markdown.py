from itertools import pairwise

from resume_builder.models.resume_model import Resume
from resume_builder.template.constants import CONTACT_SECTION_TITLE, WORK_EXPERIENCE_TITLE_NAME

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
def _find_next_section(lines: list[str], start: int) -> int:
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("{#"):
            return i

    return len(lines)


def _section_lines(content: str, section_name: str) -> list[str]:
    """Lines from section {#section_name}, until the next."""
    lines = content.splitlines()
    start = lines.index(f"{{#{section_name}}}")
    end = _find_next_section(lines, start)
    return lines[start:end]


# ----helper track plain text content
def _is_plain_text(line: str) -> bool:
    """A line that would merge into the previous paragraph — not a heading, bullet or fence."""
    return bool(line) and not line.startswith(("#", "- ", ":::", "{#"))


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


# test title field parameter construction by Pydantic
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


# test blank lines necessary for Markdown plugin to not disturbing CommonMark rules
def test_fields_are_separated_by_blank_lines(default_markdown_resume_content: str) -> None:
    # then — only two consecutive plain-text lines merge into a single <p>, and no
    # stylesheet can split them again. Headings and bullets interrupt paragraphs.
    for field_name in Resume.model_fields:
        body = _section_lines(default_markdown_resume_content, field_name)

        for previous, current in pairwise(body):
            assert not (_is_plain_text(previous) and _is_plain_text(current)), (
                f"{field_name}: {previous!r} then {current!r} would merge into one paragraph"
            )


def test_generated_markdown_is_evenly_spaced(default_markdown_resume_content: str) -> None:
    """Ergonomics: the generated file is meant to be opened and hand-edited.

    Every content line gets its own blank line, uniformly — including after headings,
    where CommonMark would not require it. If this fails, the output just got denser;
    update the expectation if the spacing changed on purpose.
    """
    for field_name in Resume.model_fields:
        body = _section_lines(default_markdown_resume_content, field_name)[2:]

        for previous, current in pairwise(body):
            if previous and current:
                assert previous.startswith("- ") and current.startswith("- ")


# "Experience" is only section who need a strict positioning to be used then by CSS
def test_experience_fields_appear_in_the_imposed_order(
    default_resume: Resume, default_markdown_resume_content: str
) -> None:
    """The order is the contract — CSS addresses these lines by position."""
    # given
    entry = default_resume.experiences[0]
    section = _section_lines(default_markdown_resume_content, "experiences")

    # then
    expected = [
        f"### {entry.position}",
        entry.company,
        entry.location,
        entry.start_date,
        entry.end_date,
    ]
    positions = [section.index(line) for line in expected]

    assert positions == sorted(positions)

    # field "description" is at the end
    assert section.index(f"- {entry.description[0]}") > positions[-1]


def test_every_model_value_reaches_the_file(default_resume: Resume, default_markdown_resume_content: str) -> None:
    """Presence, not format: every value the model holds must land in its own section.

    Derived from the model on purpose — it survives every formatting change, but still
    fails if a section renders empty or a value lands in the wrong one.
    """
    for field_name in Resume.model_fields:
        body = "\n".join(_section_lines(default_markdown_resume_content, field_name))

        section_value = getattr(default_resume, field_name)
        items = section_value if isinstance(section_value, list) else [section_value]

        for item in items:
            for value in item.model_dump().values():
                for leaf in value if isinstance(value, list) else [value]:
                    assert str(leaf) in body, f"{field_name}: {leaf!r} is missing"
