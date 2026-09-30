from pathlib import Path

import yaml
from jinja2 import Environment, PackageLoader
from markdown_it import MarkdownIt
from mdit_py_plugins.attrs import attrs_block_plugin
from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.front_matter import front_matter_plugin

from resume_builder.conventions import CONTAINER_NAME
from resume_builder.render.constants import CONTENT_KEY, CSS_KEY, JS_KEY, TOKEN_FRONT_MATTER
from resume_builder.render.entries import wrap_entries

# autoescape stays off: `content` is already-rendered HTML and must not be escaped
_env = Environment(loader=PackageLoader("resume_builder.render", "templates"))


def _asset_list(key: str, value: object) -> list[str]:
    """Frontmatter asset entries as a list of paths — `css: a.css` and `css: [a.css]` both work."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    raise ValueError(f"frontmatter '{key}' must be a string or a list, got {type(value).__name__}")


def build_parser() -> MarkdownIt:
    """Build the MarkdownIt parser plugin configuration.

    Base: `commonmark` with `html=True` so raw HTML in the source is passed through.

    Plugins:
    - `front_matter_plugin` - reads the YAML block at the top of
      the file.
    - `attrs_block_plugin` - reads `{#id}` on its own line and sets that attribute on
      the block below it.
    - `container_plugin` - reads `::: section` down to the closing `:::`.

    Returns:
        MarkdownIt: the configured parser.
    """
    return (
        MarkdownIt("commonmark", {"html": True})
        .use(front_matter_plugin)
        .use(attrs_block_plugin)
        .use(container_plugin, CONTAINER_NAME)
    )


def render_resume(md_path: Path, output_path: Path) -> None:
    """Render a Markdown resume file into a standalone HTML file.

    Reads an optional YAML frontmatter block from `md_path` for
    rendering options (`css`, `js` - one path or a list of paths), and
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

    md = build_parser()
    env: dict[str, object] = {}
    tokens = md.parse(text, env)

    frontmatter: dict[str, object] = {}
    if tokens and tokens[0].type == TOKEN_FRONT_MATTER:
        loaded = yaml.safe_load(tokens[0].content)
        if loaded is not None and not isinstance(loaded, dict):
            raise ValueError(f"{md_path}: frontmatter must be a mapping, got {type(loaded).__name__}")
        frontmatter = loaded or {}

    # Give each entry a real element for CSS/paged.js to work with.
    body_html = md.renderer.render(wrap_entries(tokens), md.options, env)

    template = _env.get_template("resume.html.j2")
    final_html = template.render(
        **{
            CSS_KEY: _asset_list(CSS_KEY, frontmatter.get(CSS_KEY)),
            JS_KEY: _asset_list(JS_KEY, frontmatter.get(JS_KEY)),
            CONTENT_KEY: body_html,
        }
    )

    output_path.write_text(final_html, encoding="utf-8")
