"""max_width / truncation tests."""

from __future__ import annotations

import pytest

import csvtable


def test_max_width_applies_to_all_columns() -> None:
    out = csvtable.from_rows(
        [["abcdefghij", "kl"]],
        headers=["a", "b"],
        max_width=5,
    )
    # Truncated to "abcd…" (4 chars + ellipsis).
    assert "| abcd… |" in out


def test_max_width_per_column() -> None:
    out = csvtable.from_rows(
        [["abcdefgh", "abcdefgh"]],
        headers=["a", "b"],
        max_width=[3, None],
    )
    # column 0 truncated to "ab…"; column 1 unchanged.
    assert "| ab… |" in out
    assert "abcdefgh" in out


def test_truncate_start() -> None:
    out = csvtable.from_rows(
        [["abcdefghij"]],
        headers=["x"],
        max_width=5,
        truncate="start",
    )
    assert "| …ghij |" in out


def test_truncate_middle() -> None:
    out = csvtable.from_rows(
        [["abcdefgh"]],
        headers=["x"],
        max_width=5,
        truncate="middle",
    )
    # 5 width minus 1 ellipsis = 4 kept; split 2 left + 2 right.
    assert "| ab…gh |" in out


def test_truncate_invalid_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(truncate="diagonal")


def test_max_width_int_lt_one_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(max_width=0)


def test_max_width_list_invalid_entry_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(max_width=["x"])  # type: ignore[list-item]


def test_max_width_list_non_iterable_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table(max_width=object())  # type: ignore[arg-type]


def test_short_list_extended_with_none() -> None:
    out = csvtable.from_rows(
        [["abcdefgh", "abcdefgh"]],
        headers=["a", "b"],
        max_width=[3],
    )
    assert "| ab… |" in out
    assert "abcdefgh" in out


def test_custom_ellipsis() -> None:
    out = csvtable.from_rows(
        [["abcdef"]],
        headers=["x"],
        max_width=4,
        ellipsis="..",
    )
    # 4 width - 2 ellipsis = 2 chars kept => "ab.."
    assert "| ab.. |" in out


def test_truncate_with_max_width_one_keeps_only_ellipsis() -> None:
    out = csvtable.from_rows(
        [["longstring"]],
        headers=["x"],
        max_width=1,
    )
    assert "| … |" in out


def test_newlines_in_cell_replaced_with_space() -> None:
    out = csvtable.from_rows(
        [["one\ntwo"]],
        headers=["x"],
    )
    assert "| one two |" in out


def test_carriage_return_in_cell_replaced() -> None:
    out = csvtable.from_rows(
        [["a\r\nb"]], headers=["x"]
    )
    assert "| a b |" in out
