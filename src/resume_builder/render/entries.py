"""Group each entry heading level (h3) and the content below it into a wrapper ``<div>``.

Mirrors what Pandoc's ``--section-divs`` gives pagedown for free: the Markdown
stays bare (a heading followed by plain lines, no containers, no classes) while
the HTML still gets one real element per entry.

That element is not cosmetic. CSS can style boxes but never create them, so
without a wrapper an experience is just a flat run of siblings: ``break-inside:
avoid`` has nothing to apply to and ``paged.js`` will split a single job across a
page break, and positional selectors count across the whole section rather than
within one entry.
"""

from markdown_it.token import Token

from resume_builder.conventions import ENTRY_HEADING_LEVEL
from resume_builder.render.constants import (
    ENTRY_CLASS,
    TOKEN_CONTAINER_CLOSE,
    TOKEN_CONTAINER_OPEN,
    TOKEN_ENTRY_CLOSE,
    TOKEN_ENTRY_OPEN,
    TOKEN_HEADING_OPEN,
)


def _heading_level(token: Token) -> int:
    """Return the numeric level of a ``heading_open`` token (``h3`` -> ``3``)."""
    return int(token.tag[1:])


def _entry_open() -> Token:
    token = Token(TOKEN_ENTRY_OPEN, "div", 1)
    token.block = True
    token.attrSet("class", ENTRY_CLASS)
    return token


def _entry_close() -> Token:
    token = Token(TOKEN_ENTRY_CLOSE, "div", -1)
    token.block = True
    return token


def _find_container_close(tokens: list[Token], start: int) -> int | None:
    """Index of the ``TOKEN_CONTAINER_CLOSE`` matching the open token at `start`.

    Counts nesting so an inner container does not close the outer one. Returns
    ``None`` when the container is left unclosed.
    """
    depth = 0
    for index in range(start, len(tokens)):
        if tokens[index].type == TOKEN_CONTAINER_OPEN:
            depth += 1
        elif tokens[index].type == TOKEN_CONTAINER_CLOSE:
            depth -= 1
            if depth == 0:
                return index
    return None


def _wrap_container_body(body: list[Token]) -> list[Token]:
    """
    The current convention is to use one entry per h3 heading found in an `div` entry tag.
    """
    entry_level = ENTRY_HEADING_LEVEL
    wrapped: list[Token] = []
    in_entry = False

    for token in body:
        if token.type == TOKEN_HEADING_OPEN and _heading_level(token) == entry_level:
            if in_entry:
                wrapped.append(_entry_close())
            wrapped.append(_entry_open())
            in_entry = True
        wrapped.append(token)

    if in_entry:
        wrapped.append(_entry_close())

    return wrapped


def wrap_entries(tokens: list[Token]) -> list[Token]:
    """Add an entry ``<div>`` around each heading-level 3 (h3) inside every section.

    Only the bodies of ``::: section`` containers are rewritten; tokens outside a
    container are passed through unchanged.

    Args:
        tokens: The token stream produced by `MarkdownIt.parse`.

    Returns:
        list[Token]: A new token stream with entry open/close tokens inserted.
    """
    output: list[Token] = []
    index = 0

    while index < len(tokens):
        token = tokens[index]

        if token.type != TOKEN_CONTAINER_OPEN:
            output.append(token)
            index += 1
            continue

        close_index = _find_container_close(tokens, index)
        if close_index is None:
            # Unclosed container — leave the remainder untouched rather than guess.
            output.extend(tokens[index:])
            break

        output.append(token)
        output.extend(_wrap_container_body(tokens[index + 1 : close_index]))
        output.append(tokens[close_index])
        index = close_index + 1

    return output
