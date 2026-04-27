"""Alignment tests."""

from __future__ import annotations

import pytest

import csvtable


def test_default_auto_align_numeric_column_right() -> None:
    out = csvtable.from_rows(
        [["alice", "10"], ["bob", "200"]],
        headers=["name", "n"],
    )
    # alice column is left, n column is right (numeric).
    assert "| alice |  10 |" in out
    assert "| bob   | 200 |" in out


def test_default_auto_align_text_column_left() -> None:
    out = csvtable.from_rows(
        [["alice"], ["bobby"]],
        headers=["name"],
    )
    assert "| alice |" in out
    assert "| bobby |" in out


def test_explicit_align_string_applies_to_all_columns() -> None:
    out = csvtable.from_rows(
        [["a", "b"], ["c", "d"]], headers=["x", "y"], align="right"
    )
    assert "| x | y |" in out
    assert "| a | b |" in out


def test_align_per_column() -> None:
    out = csvtable.from_rows(
        [["foo", "1"], ["x", "2222"]],
        headers=["L", "R"],
        align=["left", "right"],
    )
    assert "| foo |    1 |" in out
    assert "| x   | 2222 |" in out


def test_align_center() -> None:
    out = csvtable.from_rows(
        [["x"]], headers=["abc"], align=["center"]
    )
    # 3-wide header padded to 3 with center align (no padding diff).
    # Row "x" gets centered as " x ".
    assert "| abc |" in out
    assert "|  x  |" in out


def test_align_short_list_extended_with_auto() -> None:
    out = csvtable.from_rows(
        [["a", "b"]], headers=["x", "y"], align=["right"]
    )
    # Both header and data are width 1; right-align is invisible here
    # but the call must not error.
    assert out.count("|") == 6


def test_invalid_align_value_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.from_rows([["a"]], align="diagonal")


def test_invalid_align_in_list_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.from_rows([["a", "b"]], align=["left", "weird"])


def test_align_must_be_string_or_sequence() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(align=42)  # type: ignore[arg-type]


def test_numeric_with_thousands_separator_still_right_aligns() -> None:
    out = csvtable.from_rows(
        [["a", "1,000"], ["b", "2"]], headers=["k", "n"]
    )
    # right-aligned column => narrow values padded on the left.
    assert "| a | 1,000 |" in out
    assert "| b |     2 |" in out


def test_mixed_numeric_and_text_column_left_aligns() -> None:
    out = csvtable.from_rows(
        [["a", "1"], ["b", "two"]], headers=["k", "v"]
    )
    # column has both numeric and text → left align
    assert "| a | 1   |" in out
    assert "| b | two |" in out


def test_align_with_empty_data_rows_still_renders_headers() -> None:
    out = csvtable.from_rows([], headers=["a", "b"], align="right")
    assert "| a | b |" in out
