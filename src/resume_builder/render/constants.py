# MarkdownIt config
CONTAINER_NAME_SECTION = "section"

# uses in html template string and rendering call
CSS_KEY = "css"
JS_KEY = "js"
CONTENT_KEY = "content"

# CSS class set on the <div> wrapping each entry (see render/entries.py)
ENTRY_CLASS = "entry"
ENTRY_HEADING_LEVEL = 3

# markdown-it token types read by the entry-wrapping transform
CONTAINER_OPEN = f"container_{CONTAINER_NAME_SECTION}_open"
CONTAINER_CLOSE = f"container_{CONTAINER_NAME_SECTION}_close"
HEADING_OPEN = "heading_open"

# markdown-it token types emitted by the entry-wrapping transform
ENTRY_OPEN = "entry_open"
ENTRY_CLOSE = "entry_close"
