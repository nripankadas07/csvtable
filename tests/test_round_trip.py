"""End-to-end use cases."""

from __future__ import annotations

import csvtable


def test_from_csv_to_unicode_table() -> None:
    text = "name,age,city\nAlice,30,Paris\nBob,25,Lyon\n"
    out = csvtable.from_csv(text, border="unicode")
    assert "│ name" in out or "│ name " in out
    assert "│ Alice" in out or "│ Alice " in out
    assert "│  30 │" in out or "│ 30 " in out


def test_from_rows_then_add_more_rows_renders_consistently() -> None:
    table = csvtable.Table(headers=["k", "v"])
    table.add_rows([["a", "1"], ["b", "2"]])
    out_initial = table.render()
    table.add_row(["c", "3"])
    out_extended = table.render()
    assert out_initial in out_extended.replace("| c | 3 |\n", "")
    assert "| c | 3 |" in out_extended


def test_markdown_round_trip_preserves_alignment() -> None:
    text = "name,score\nalice,90\nbob,75\n"
    out = csvtable.from_csv(text, border="markdown")
    # Score is numeric: right-aligned so dashes end with ':'.
    assert "-:" in out


def test_realistic_status_table() -> None:
    rows = [
        ["build", "passing", 12],
        ["lint", "warn", 3],
        ["tests", "passing", 156],
    ]
    out = csvtable.from_rows(rows, headers=["job", "state", "count"])
    # Numeric column (count) right-aligned; state column left-aligned
    # (since values aren't all numeric).
    assert "| build | passing |    12 |" in out
    assert "| tests | passing |   156 |" in out
