from resume_builder.conventions import CONTAINER_NAME

# Jinja2 template context keys (see render/templates/resume.html.j2)
CSS_KEY = "css"
JS_KEY = "js"
CONTENT_KEY = "content"

# CSS class set on the <div> wrapping each entry (see render/entries.py)
ENTRY_CLASS = "entry"

# markdown-it token types read by the entry-wrapping transform
TOKEN_CONTAINER_OPEN = f"container_{CONTAINER_NAME}_open"
TOKEN_CONTAINER_CLOSE = f"container_{CONTAINER_NAME}_close"
TOKEN_HEADING_OPEN = "heading_open"

# markdown-it token types emitted by the entry-wrapping transform
TOKEN_ENTRY_OPEN = "entry_open"
TOKEN_ENTRY_CLOSE = "entry_close"
