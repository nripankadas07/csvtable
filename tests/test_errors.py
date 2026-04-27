"""Configuration / error condition tests."""

from __future__ import annotations

import pytest

import csvtable


def test_negative_padding_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(padding=-1)


def test_non_int_padding_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(padding="2")  # type: ignore[arg-type]


def test_invalid_truncate_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(truncate="elsewhere")


def test_invalid_align_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(align="diagonal")


def test_invalid_max_width_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(max_width=-3)


def test_invalid_max_width_list_entry_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(max_width=[-1])


def test_invalid_border_string_raises() -> None:
    with pytest.raises(ValueError):
        csvtable.from_rows([["1"]], border="exotic")


def test_table_error_is_base_for_all() -> None:
    assert issubclass(csvtable.ConfigError, csvtable.TableError)
    assert issubclass(csvtable.ParseError, csvtable.TableError)
    assert issubclass(csvtable.RenderError, csvtable.TableError)


def test_padding_zero_renders_without_inner_padding() -> None:
    out = csvtable.from_rows(
        [["a", "b"]], headers=["x", "y"], padding=0
    )
    # "+-+-+" border (one dash per column).
    assert "+-+-+" in out
    assert "|x|y|" in out


def test_explicit_padding_renders_correctly() -> None:
    out = csvtable.from_rows(
        [["a"]], headers=["h"], padding=2
    )
    assert "|  a  |" in out
    assert "|  h  |" in out


def test_header_separator_can_be_disabled() -> None:
    out = csvtable.from_rows(
        [["1"]], headers=["a"], header_separator=False
    )
    # No header divider line.
    lines = out.split("\n")
    # 4 lines total without header separator: top, header, data, bottom.
    assert len(lines) == 4
