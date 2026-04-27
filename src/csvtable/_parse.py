"""CSV / TSV / DSV parsing wrappers.

Wraps the standard library's :mod:`csv` module so callers don't have
to deal with file-like objects when they have a string in hand.
"""

from __future__ import annotations

import csv
import io
from typing import Iterable

from ._errors import ParseError


def parse_csv(
    text: str,
    *,
    sep: str = ",",
    quote: str = '"',
    skip_blank: bool = True,
) -> list[list[str]]:
    """Parse a CSV / TSV string into a list of rows.

    *sep* is the field delimiter (default comma; pass ``"\\t"`` for
    TSV). *quote* is the quoting character. Blank lines are skipped
    when *skip_blank* is True.
    """

    if not isinstance(text, str):
        raise ParseError("text must be a str")
    if not isinstance(sep, str) or len(sep) != 1:
        raise ParseError("sep must be a single character")
    if not isinstance(quote, str) or len(quote) != 1:
        raise ParseError("quote must be a single character")
    try:
        reader = csv.reader(
            io.StringIO(text), delimiter=sep, quotechar=quote
        )
        rows = [list(row) for row in reader]
    except csv.Error as exc:
        raise ParseError(f"invalid CSV: {exc}") from exc
    if skip_blank:
        rows = [r for r in rows if any(cell != "" for cell in r) or len(r) > 1]
    return rows


def split_header(
    rows: Iterable[list[str]],
) -> tuple[list[str] | None, list[list[str]]]:
    """Split parsed rows into ``(header, body)``.

    Returns ``(None, [])`` when the input is empty.
    """

    rows = list(rows)
    if not rows:
        return None, []
    header = rows[0]
    body = rows[1:]
    return header, body


__all__ = ["parse_csv", "split_header"]
