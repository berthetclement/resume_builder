from pathlib import Path

import yaml
from jinja2 import Template
from markdown_it import MarkdownIt
from mdit_py_plugins.attrs import attrs_block_plugin
from mdit_py_plugins.front_matter import front_matter_plugin

from resume_builder.render.html_template import RESUME_TEMPLATE


def render_resume(md_path: Path, output_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")

    md = MarkdownIt("commonmark", {"html": True}).use(front_matter_plugin).use(attrs_block_plugin)
    tokens = md.parse(text)

    frontmatter: dict[str, object] = {}
    if tokens and tokens[0].type == "front_matter":
        frontmatter = yaml.safe_load(tokens[0].content) or {}

    body_html = md.render(text)

    template = Template(RESUME_TEMPLATE)
    final_html = template.render(
        css=frontmatter.get("css", []),
        js=frontmatter.get("js", []),
        content=body_html,
    )

    output_path.write_text(final_html, encoding="utf-8")
