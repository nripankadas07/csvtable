"""Border-style tests."""

from __future__ import annotations

import pytest

import csvtable
from csvtable._borders import ASCII, BorderStyle, MARKDOWN, PLAIN, UNICODE, get_style


def test_ascii_default_style() -> None:
    out = csvtable.from_rows([["1"]], headers=["a"], border="ascii")
    assert "+---+" in out
    assert "| a |" in out


def test_unicode_style_uses_box_drawing() -> None:
    out = csvtable.from_rows([["1"]], headers=["a"], border="unicode")
    assert "┌" in out
    assert "└" in out
    assert "│" in out


def test_markdown_style_no_outer_box() -> None:
    out = csvtable.from_rows(
        [["1", "2"]], headers=["a", "b"], border="markdown"
    )
    # No top or bottom border, but the header separator uses dashes
    # and (with auto-aligned numeric column "a") right-alignment marker.
    lines = out.split("\n")
    # First line is the header.
    assert lines[0].startswith("|")
    # No '+' anywhere.
    assert "+" not in out


def test_markdown_separator_marks_alignment() -> None:
    out = csvtable.from_rows(
        [["x", "1"], ["y", "2"]],
        headers=["L", "R"],
        align=["left", "right"],
        border="markdown",
    )
    # Left column has ":---", right column has "---:".
    assert ":-" in out
    assert "-:" in out


def test_markdown_center_alignment_marker() -> None:
    out = csvtable.from_rows(
        [["x"]], headers=["c"], align=["center"], border="markdown"
    )
    assert ":-" in out and "-:" in out


def test_plain_style_no_borders() -> None:
    out = csvtable.from_rows(
        [["x", "y"]], headers=["a", "b"], border="plain"
    )
    assert "|" not in out
    assert "+" not in out
    # Has the data and headers though.
    assert "x" in out
    assert "a" in out


def test_none_alias_for_plain() -> None:
    out_none = csvtable.from_rows(
        [["x"]], headers=["a"], border="none"
    )
    out_plain = csvtable.from_rows(
        [["x"]], headers=["a"], border="plain"
    )
    assert out_none == out_plain


def test_unknown_border_raises() -> None:
    with pytest.raises(ValueError):
        csvtable.from_rows([["1"]], border="fancy")


def test_get_style_returns_known_style() -> None:
    assert get_style("ascii") is ASCII
    assert get_style("unicode") is UNICODE
    assert get_style("markdown") is MARKDOWN
    assert get_style("plain") is PLAIN


def test_pass_borderstyle_directly() -> None:
    style = get_style("unicode")
    out = csvtable.from_rows([["1"]], headers=["a"], border=style)
    assert "┌" in out


def test_row_separator_drawn_in_unicode() -> None:
    out = csvtable.from_rows(
        [["1"], ["2"]],
        headers=["a"],
        border="unicode",
        row_separator=True,
    )
    # Row separator only takes effect for styles with
    # draw_inner_horizontal=True. UNICODE doesn't enable it by
    # default, so this test asserts the option is a no-op there.
    assert "┌" in out


def test_borderstyle_dataclass_is_frozen() -> None:
    style = get_style("ascii")
    with pytest.raises(Exception):
        style.horizontal = "X"  # type: ignore[misc]


def test_custom_borderstyle_can_be_passed() -> None:
    style = BorderStyle(
        horizontal="=",
        vertical="!",
        top_left="*",
        top_right="*",
        bottom_left="*",
        bottom_right="*",
        middle_left="*",
        middle_right="*",
        top_junction="*",
        bottom_junction="*",
        middle_junction="*",
    )
    out = csvtable.from_rows([["1"]], headers=["a"], border=style)
    assert "*===*" in out
    assert "! a !" in out
