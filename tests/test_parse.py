"""CSV / TSV parsing tests."""

from __future__ import annotations

import pytest

import csvtable
from csvtable._parse import parse_csv, split_header


def test_from_csv_simple() -> None:
    out = csvtable.from_csv("a,b\n1,2\n3,4\n")
    assert "| a | b |" in out
    assert "| 1 | 2 |" in out
    assert "| 3 | 4 |" in out


def test_from_csv_tsv() -> None:
    out = csvtable.from_csv("a\tb\n1\t2\n", sep="\t")
    assert "| a | b |" in out
    assert "| 1 | 2 |" in out


def test_from_csv_pipe_separated() -> None:
    out = csvtable.from_csv("a|b\n1|2\n", sep="|")
    assert "| a | b |" in out
    assert "| 1 | 2 |" in out


def test_from_csv_quoted_fields_with_embedded_comma() -> None:
    out = csvtable.from_csv('a,b\n"hello, world",2\n')
    assert "hello, world" in out


def test_from_csv_no_header_treats_all_rows_as_data() -> None:
    out = csvtable.from_csv("1,2\n3,4\n", header=False)
    # No header separator since headers=None.
    assert "+---+---+" in out
    # No "a" or "b" anywhere — only numeric data.
    assert "a" not in out and "b" not in out


def test_from_csv_skip_blank_lines_default() -> None:
    out = csvtable.from_csv("a,b\n\n1,2\n\n3,4\n")
    # Two data rows.
    assert out.count("| 1 | 2 |") == 1
    assert out.count("| 3 | 4 |") == 1


def test_from_csv_keep_blank_lines() -> None:
    out = csvtable.from_csv("a,b\n,\n", skip_blank=False)
    # Blank line becomes a row of two empty cells.
    assert "|   |   |" in out


def test_parse_csv_returns_list_of_lists() -> None:
    rows = parse_csv("a,b\n1,2\n")
    assert rows == [["a", "b"], ["1", "2"]]


def test_parse_csv_rejects_non_string_input() -> None:
    with pytest.raises(csvtable.ParseError):
        parse_csv(42)  # type: ignore[arg-type]


def test_parse_csv_rejects_multi_char_separator() -> None:
    with pytest.raises(csvtable.ParseError):
        parse_csv("a,b", sep=",,")


def test_parse_csv_rejects_empty_separator() -> None:
    with pytest.raises(csvtable.ParseError):
        parse_csv("a,b", sep="")


def test_parse_csv_rejects_multi_char_quote() -> None:
    with pytest.raises(csvtable.ParseError):
        parse_csv("a,b", quote='""')


def test_split_header_empty_returns_none_and_empty() -> None:
    head, body = split_header([])
    assert head is None and body == []


def test_split_header_with_rows() -> None:
    head, body = split_header([["a", "b"], ["1", "2"]])
    assert head == ["a", "b"]
    assert body == [["1", "2"]]


def test_from_csv_alternative_quote() -> None:
    out = csvtable.from_csv("a,b\n'hello, world',2\n", quote="'")
    assert "hello, world" in out


def test_from_csv_handles_crlf_line_endings() -> None:
    out = csvtable.from_csv("a,b\r\n1,2\r\n")
    assert "| 1 | 2 |" in out
