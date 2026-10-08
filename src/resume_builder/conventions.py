"""
The contract between the Markdown, the model and the CSS
"""

# Pydantic model field metadata keys
CUSTOM_FIELD = "markdown"


# Conventions for Markdown headers
HEADING_MARKERS = {1: "#", 2: "##", 3: "###"}


# Heading levels for Markdown sections and entries
def heading_marker(level: object) -> str | None:
    """Markdown markup for a heading level read from `json_schema_extra`.

    pydantic types that metadata as arbitrary JSON, so the value arrives
    untyped; anything outside `HEADING_MARKERS` means "not a heading".
    """
    if isinstance(level, bool) or not isinstance(level, int):
        return None
    return HEADING_MARKERS.get(level)


SECTION_TITLE_LEVEL = 2  # `##` — see the heading table in CLAUDE.md
ENTRY_HEADING_LEVEL = 3  # `###` — opens an .entry box

# CSS class set on the <div> wrapping each entry (see render/entries.py)
ENTRY_CLASS = "entry"

# Conventions for Markdown blocks
PARAGRAPH_BREAK = "\n\n"  # between blocks inside a section
SECTION_BREAK = "\n\n\n"  # between sections — two blank lines


def join_blocks(blocks: list[str], separator: str = PARAGRAPH_BREAK) -> str:
    """Join Markdown blocks, separated by one blank line unless told otherwise."""
    return separator.join(blocks)


# MarkdownIt plugins values

# container_plugin
CONTAINER_NAME = "section"
FENCE_MARKER = ":::"
FENCE_OPEN = f"{FENCE_MARKER} {CONTAINER_NAME}"
FENCE_CLOSE = FENCE_MARKER


# attrs_block_plugin
def anchor(section_id: str) -> str:
    return f"{{#{section_id}}}"


# FOLDER NAMES FOR ASSETS
ASSETS_FOLDER_NAME = "resume_builder_files"
ASSET_CSS_USER_FILE_NAME = "theme.css"
ASSET_CSS_BUILTIN_FILE_NAME = "resume.css"
ASSET_JS_BUILTIN_FILE_NAME = "paged.polyfill.min.js"
INIT_FOLDER_NAME = "resume_builder_template"

# not Path objects so they do not depend on the OS path separator
PATH_FILE_YAML_CSS = ASSETS_FOLDER_NAME + "/" + ASSET_CSS_USER_FILE_NAME


# Default name of the Markdown file init_resume() creates
INIT_RESUME_FILE_NAME = "resume.md"
