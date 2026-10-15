import pytest

from resume_builder.conventions import SECTION_BREAK, anchor, heading_marker, join_blocks


# join_blocks owns the separator: one blank line inside a section, two between sections.
# Expected strings are written out on purpose: the separator is the contract under test.
def test_join_blocks_separates_with_one_blank_line_by_default() -> None:
    assert join_blocks(["Paris, France", "2021"]) == "Paris, France\n\n2021"


def test_join_blocks_separates_sections_with_two_blank_lines() -> None:
    assert join_blocks(["{#contact}", "{#skills}"], SECTION_BREAK) == "{#contact}\n\n\n{#skills}"


def test_join_blocks_adds_no_separator_around_a_single_block() -> None:
    assert join_blocks(["2021"]) == "2021"


def test_join_blocks_keeps_a_list_block_tight() -> None:
    # a list field is ONE block: its `- item` lines are joined by a single newline
    # before reaching join_blocks, and must stay that way (a tight list)
    bullets = "- Led the R package chain.\n- Released to CRAN."
    assert join_blocks(["2022", bullets]) == "2022\n\n- Led the R package chain.\n- Released to CRAN."


# heading_marker: the four levels of CLAUDE.md, nothing else
@pytest.mark.parametrize(
    ("level", "expected"),
    [(1, "#"), (2, "##"), (3, "###"), (4, "####")],
)
def test_heading_marker_returns_the_markup_of_each_level(level: int, expected: str) -> None:
    assert heading_marker(level) == expected


@pytest.mark.parametrize(
    "level",
    [
        None,  # field without a heading hint
        0,
        5,  # outside the four levels
        "3",  # a string, not an int
        True,  # a bool is an int in Python, and True == 1
    ],
)
def test_heading_marker_rejects_anything_else(level: object) -> None:
    assert heading_marker(level) is None


def test_anchor_is_the_attrs_block_syntax() -> None:
    assert anchor("experiences") == "{#experiences}"
