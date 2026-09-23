"""
The contract between the Markdown, the model and the CSS
"""

# Pydantic model field metadata keys
CUSTOM_FIELD = "markdown"


# Conventions for Markdown headers
HEADING_MARKERS = {1: "#", 2: "##", 3: "###"}


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


# MarkdownIt plugins values

# container_plugin
CONTAINER_NAME = "section"
FENCE_MARKER = ":::"
FENCE_OPEN = f"{FENCE_MARKER} {CONTAINER_NAME}"
FENCE_CLOSE = FENCE_MARKER


# attrs_block_plugin
def anchor(section_id: str) -> str:
    return f"{{#{section_id}}}"
