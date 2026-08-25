import re

from markdown_it import MarkdownIt
from mdit_py_plugins.attrs import attrs_block_plugin
from mdit_py_plugins.container import container_plugin

from resume_builder.render.entries import wrap_entries


def _render(markdown: str) -> str:
    md = MarkdownIt("commonmark", {"html": True}).use(attrs_block_plugin).use(container_plugin, "section")
    env: dict[str, object] = {}
    tokens = md.parse(markdown, env)
    html: str = md.renderer.render(wrap_entries(tokens), md.options, env)
    return html


TWO_EXPERIENCES = """{#experiences}
::: section
# Acme Corp

## Developer

2020

2021

# Globex

## Engineer

2021

2022

:::"""


def test_each_heading_led_block_becomes_an_entry() -> None:
    # when
    html = _render(TWO_EXPERIENCES)

    # then
    assert html.count('<div class="entry">') == 2


def test_entry_keeps_heading_and_content_together() -> None:
    # when
    html = _render(TWO_EXPERIENCES)

    # then — the first entry holds its own heading, subheading and both dates
    first_entry = re.findall(r'<div class="entry">(.*?)</div>', html, re.S)[0]
    assert "<h1>Acme Corp</h1>" in first_entry
    assert "<h2>Developer</h2>" in first_entry
    assert "<p>2020</p>" in first_entry
    assert "<p>2021</p>" in first_entry
    # ...and none of the next one
    assert "Globex" not in first_entry


def test_entry_breaks_on_the_shallowest_heading_level_only() -> None:
    # when
    html = _render(TWO_EXPERIENCES)

    # then — the h2 must not start an entry of its own
    assert '<div class="entry">\n<h2>' not in html


def test_single_entry_is_wrapped_like_any_other() -> None:
    # given — structure must not depend on how many experiences exist
    single = "{#experiences}\n::: section\n# Acme Corp\n\n2020\n\n:::"

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
    html = _render(TWO_EXPERIENCES)

    # then
    assert '<div id="experiences" class="section">' in html


def test_entry_divs_are_balanced() -> None:
    # when
    html = _render(TWO_EXPERIENCES)

    # then — every div opened is closed
    assert html.count("<div") == html.count("</div>")
