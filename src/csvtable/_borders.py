"""Border style definitions.

A border style defines the characters used for the table outline,
column separators and row separators. The renderer never assumes a
particular charset: every glyph (corner, junction, vertical, horizontal)
is supplied by the style.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BorderStyle:
    """Glyphs for one border style.

    A style may set ``draw_outer`` to False to suppress the outer box
    while still rendering inner separators (used by the ``markdown``
    style). When ``draw_inner_horizontal`` is False, no separator row
    is drawn between data rows; the header separator is still drawn
    when ``draw_header_separator`` is True.
    """

    horizontal: str
    vertical: str
    top_left: str
    top_right: str
    bottom_left: str
    bottom_right: str
    middle_left: str
    middle_right: str
    top_junction: str
    bottom_junction: str
    middle_junction: str
    draw_outer: bool = True
    draw_inner_vertical: bool = True
    draw_inner_horizontal: bool = False
    draw_header_separator: bool = True


ASCII = BorderStyle(
    horizontal="-",
    vertical="|",
    top_left="+",
    top_right="+",
    bottom_left="+",
    bottom_right="+",
    middle_left="+",
    middle_right="+",
    top_junction="+",
    bottom_junction="+",
    middle_junction="+",
)


UNICODE = BorderStyle(
    horizontal="─",
    vertical="│",
    top_left="┌",
    top_right="┐",
    bottom_left="└",
    bottom_right="┘",
    middle_left="├",
    middle_right="┤",
    top_junction="┬",
    bottom_junction="┴",
    middle_junction="┼",
)


MARKDOWN = BorderStyle(
    horizontal="-",
    vertical="|",
    top_left="",
    top_right="",
    bottom_left="",
    bottom_right="",
    middle_left="|",
    middle_right="|",
    top_junction="",
    bottom_junction="",
    middle_junction="|",
    draw_outer=False,
    draw_header_separator=True,
)


PLAIN = BorderStyle(
    horizontal=" ",
    vertical=" ",
    top_left="",
    top_right="",
    bottom_left="",
    bottom_right="",
    middle_left="",
    middle_right="",
    top_junction="",
    bottom_junction="",
    middle_junction="",
    draw_outer=False,
    draw_inner_vertical=False,
    draw_header_separator=False,
)


_STYLES: dict[str, BorderStyle] = {
    "ascii": ASCII,
    "unicode": UNICODE,
    "markdown": MARKDOWN,
    "plain": PLAIN,
    "none": PLAIN,
}


def get_style(name: str) -> BorderStyle:
    """Look up a built-in border style by name."""

    try:
        return _STYLES[name]
    except KeyError as exc:
        raise ValueError(
            f"unknown border style: {name!r} (available: {sorted(_STYLES)})"
        ) from exc


__all__ = ["ASCII", "UNICODE", "MARKDOWN", "PLAIN", "BorderStyle", "get_style"]
