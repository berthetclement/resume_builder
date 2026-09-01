import re

from resume_builder.render.entries import wrap_entries
from resume_builder.render.renderer import build_parser


def _render(markdown: str) -> str:
    md = build_parser()
    env: dict[str, object] = {}
    tokens = md.parse(markdown, env)
    html: str = md.renderer.render(wrap_entries(tokens), md.options, env)
    return html


EXPERIENCES = """{#experiences}
::: section
## WORK EXPERIENCE

### Developer

Acme Corp

Boston, MA

2020

2021

### Engineer

Globex

New York, NY

2021

2022

:::"""


def test_each_heading_led_block_becomes_an_entry() -> None:
    # when
    html = _render(EXPERIENCES)

    # then
    assert html.count('<div class="entry">') == 2


def test_entry_keeps_heading_and_content_together() -> None:
    # when
    html = _render(EXPERIENCES)

    # then — the first entry holds its own heading, subheading and both dates
    first_entry = re.findall(r'<div class="entry">(.*?)</div>', html, re.S)[0]
    assert "<h3>Developer</h3>" in first_entry
    assert "<p>Acme Corp</p>" in first_entry
    assert "<p>Boston, MA</p>" in first_entry
    assert "<p>2020</p>" in first_entry
    assert "<p>2021</p>" in first_entry

    second_entry = re.findall(r'<div class="entry">(.*?)</div>', html, re.S)[1]
    assert "<h3>Engineer</h3>" in second_entry
    assert "<p>Globex</p>" in second_entry
    assert "<p>New York, NY</p>" in second_entry
    assert "<p>2021</p>" in second_entry
    assert "<p>2022</p>" in second_entry


def test_section_title_stays_outside_any_entry() -> None:
    # when
    html = _render(EXPERIENCES)

    # then — the ## belongs to the section, not to the first job
    first_entry = re.findall(r'<div class="entry">(.*?)</div>', html, re.S)[0]
    assert "WORK EXPERIENCE" not in first_entry
    assert "<h2>WORK EXPERIENCE</h2>" in html


def test_single_entry_is_wrapped_like_any_other() -> None:
    # given — structure must not depend on how many experiences exist
    single = "{#experiences}\n::: section\n### Acme Corp\n\n2020\n\n:::"

    # when
    html = _render(single)

    # then
    assert html.count('<div class="entry">') == 1


def test_section_without_heading_is_left_untouched() -> None:
    # given
    contact = "{#contact}\n::: section\njohn.doe@example.com\n\n123-456-7890\n\n:::"

    # when
    html = _render(contact)

    # then
    assert "entry" not in html
    assert "<p>john.doe@example.com</p>" in html


def test_content_outside_a_section_is_left_untouched() -> None:
    # when
    html = _render("# Loose heading\n\nSome text\n")

    # then
    assert "entry" not in html
    assert "<h1>Loose heading</h1>" in html


def test_section_id_and_class_survive_the_transform() -> None:
    # when
    html = _render(EXPERIENCES)

    # then
    assert '<div id="experiences" class="section">' in html


def test_heading_deeper_than_an_entry_stays_inside_it() -> None:
    # given — a user subdividing one job, as pagedown resumes commonly do
    markdown = (
        "{#experiences}\n::: section\n## WORK EXPERIENCE\n\n"
        "### Developer\n\nAcme Corp\n\n#### Achievements\n\nShipped things.\n\n:::"
    )

    # when
    html = _render(markdown)

    # then — the h4 belongs to the job, it does not open a new box
    assert html.count('<div class="entry">') == 1
    entry = re.findall(r'<div class="entry">(.*?)</div>', html, re.S)[0]
    assert "<h4>Achievements</h4>" in entry


def test_entry_divs_are_balanced() -> None:
    # when
    html = _render(EXPERIENCES)

    # then — every div opened is closed
    assert html.count("<div") == html.count("</div>")
