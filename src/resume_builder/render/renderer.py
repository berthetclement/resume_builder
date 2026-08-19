from pathlib import Path

import yaml
from jinja2 import Environment, PackageLoader
from markdown_it import MarkdownIt
from mdit_py_plugins.attrs import attrs_block_plugin
from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.front_matter import front_matter_plugin

from resume_builder.render.constants import CONTENT_KEY, CSS_KEY, JS_KEY

_env = Environment(loader=PackageLoader("resume_builder.render", "templates"))


def render_resume(md_path: Path, output_path: Path) -> None:
    """Render a Markdown resume file into a standalone HTML file.

    Reads an optional YAML frontmatter block from `md_path` for
    rendering options (`css`, `js` — lists of asset paths), and
    converts the rest of the file's Markdown content into HTML via
    a Jinja2 template.

    Args:
        md_path: Path to the source `.md` file (as produced by
            `write_model_to_markdown`, then optionally hand-edited).
        output_path: Path the final `.html` file is written to.
    """
    if not md_path.is_file():
        raise FileNotFoundError(f"{md_path} does not exist or is not a file")

    text = md_path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"{md_path} is empty")

    md = (
        MarkdownIt("commonmark", {"html": True})
        .use(front_matter_plugin)
        .use(attrs_block_plugin)
        .use(container_plugin, "section")
    )
    tokens = md.parse(text)

    frontmatter: dict[str, object] = {}
    if tokens and tokens[0].type == "front_matter":
        frontmatter = yaml.safe_load(tokens[0].content) or {}

    body_html = md.render(text)

    template = _env.get_template("resume.html.j2")
    final_html = template.render(
        **{
            CSS_KEY: frontmatter.get(CSS_KEY, []),
            JS_KEY: frontmatter.get(JS_KEY, []),
            CONTENT_KEY: body_html,
        }
    )

    output_path.write_text(final_html, encoding="utf-8")
