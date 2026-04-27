"""Basic Table behaviour tests."""

from __future__ import annotations

import pytest

import csvtable


def test_module_exports() -> None:
    assert csvtable.__version__
    assert callable(csvtable.from_csv)
    assert callable(csvtable.from_rows)
    assert hasattr(csvtable, "Table")
    assert issubclass(csvtable.ConfigError, csvtable.TableError)
    assert issubclass(csvtable.ParseError, csvtable.TableError)
    assert issubclass(csvtable.RenderError, csvtable.TableError)


def test_render_simple_ascii_table() -> None:
    out = csvtable.from_rows([["a", "1"], ["b", "2"]], headers=["k", "v"])
    expected = (
        "+---+---+\n"
        "| k | v |\n"
        "+---+---+\n"
        "| a | 1 |\n"
        "| b | 2 |\n"
        "+---+---+"
    )
    assert out == expected


def test_render_no_headers() -> None:
    out = csvtable.from_rows([["a", "1"], ["b", "2"]])
    expected = (
        "+---+---+\n"
        "| a | 1 |\n"
        "| b | 2 |\n"
        "+---+---+"
    )
    assert out == expected


def test_render_only_headers_no_rows() -> None:
    out = csvtable.from_rows([], headers=["h1", "h2"])
    expected = (
        "+----+----+\n"
        "| h1 | h2 |\n"
        "+----+----+"
    )
    assert out == expected


def test_render_empty_returns_empty_string() -> None:
    assert csvtable.from_rows([]) == ""


def test_table_class_repr_via_str() -> None:
    table = csvtable.Table(headers=["x"], rows=[["1"]])
    assert str(table) == table.render()


def test_add_row_after_construction_extends_output() -> None:
    table = csvtable.Table(headers=["a", "b"])
    table.add_row(["x", "1"])
    table.add_row(["y", "22"])
    assert "x" in table.render()
    assert "22" in table.render()


def test_column_count_handles_ragged_rows() -> None:
    table = csvtable.Table(headers=["a"], rows=[["1", "extra"]])
    assert table.column_count() == 2


def test_ragged_rows_get_padded_with_missing() -> None:
    table = csvtable.Table(headers=["a", "b", "c"], missing="-")
    table.add_row(["1"])
    out = table.render()
    assert "| - | - |" in out


def test_none_values_get_substituted() -> None:
    out = csvtable.from_rows([[None, 1]], headers=["a", "b"], none="∅")
    assert "∅" in out


def test_extra_cells_in_row_get_truncated_to_header_width_disabled() -> None:
    # With three headers and rows of length 5 the renderer expands to
    # match the widest row.
    out = csvtable.from_rows([[1, 2, 3, 4, 5]], headers=["a", "b", "c"])
    # Five columns total, with the last two headers padded to "".
    assert out.count("|") == 6 * 2  # 6 vertical bars per row line, 2 data rows


def test_add_row_with_string_argument_raises() -> None:
    with pytest.raises(csvtable.ConfigError):
        csvtable.Table().add_row("abc")  # type: ignore[arg-type]


def test_add_row_chains() -> None:
    table = csvtable.Table(headers=["a"])
    result = table.add_row(["1"]).add_row(["2"])
    assert result is table


def test_add_rows_iterates() -> None:
    table = csvtable.Table(headers=["a"])
    table.add_rows([["1"], ["2"], ["3"]])
    assert len(table.rows) == 3
