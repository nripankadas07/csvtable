"""csvtable — pretty-print CSV / TSV / tabular data.

Public API:

- :class:`Table` — incrementally configurable table renderer.
- :func:`from_csv` — render a CSV / TSV string.
- :func:`from_rows` — render an iterable of row sequences.

Errors:

- :class:`TableError` (base), :class:`ConfigError`, :class:`ParseError`,
  :class:`RenderError`.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

from ._borders import BorderStyle
from ._errors import ConfigError, ParseError, RenderError, TableError
from ._parse import parse_csv, split_header
from ._table import Table


def from_rows(
    rows: Iterable[Sequence[Any]],
    *,
    headers: Sequence[Any] | None = None,
    align: str | Sequence[str] | None = None,
    max_width: int | Sequence[int | None] | None = None,
    truncate: str = "end",
    ellipsis: str = "…",
    border: str | BorderStyle = "ascii",
    padding: int = 1,
    header_separator: bool = True,
    row_separator: bool = False,
    missing: str = "",
    none: str = "",
) -> str:
    """Render an iterable of row sequences as a string.

    See :class:`Table` for a description of every keyword option.
    """

    table = Table(
        headers=headers,
        rows=rows,
        align=align,
        max_width=max_width,
        truncate=truncate,
        ellipsis=ellipsis,
        border=border,
        padding=padding,
        header_separator=header_separator,
        row_separator=row_separator,
        missing=missing,
        none=none,
    )
    return table.render()


def from_csv(
    text: str,
    *,
    sep: str = ",",
    quote: str = '"',
    header: bool = True,
    skip_blank: bool = True,
    align: str | Sequence[str] | None = None,
    max_width: int | Sequence[int | None] | None = None,
    truncate: str = "end",
    ellipsis: str = "…",
    border: str | BorderStyle = "ascii",
    padding: int = 1,
    header_separator: bool = True,
    row_separator: bool = False,
    missing: str = "",
    none: str = "",
) -> str:
    """Parse *text* as CSV and return a formatted table string.

    Set *header* to False to treat every parsed row as a data row.
    The remaining keyword arguments are forwarded to :class:`Table`.
    """

    rows = parse_csv(text, sep=sep, quote=quote, skip_blank=skip_blank)
    headers: list[str] | None
    if header:
        headers, body = split_header(rows)
    else:
        headers, body = None, rows
    return from_rows(
        body,
        headers=headers,
        align=align,
        max_width=max_width,
        truncate=truncate,
        ellipsis=ellipsis,
        border=border,
        padding=padding,
        header_separator=header_separator,
        row_separator=row_separator,
        missing=missing,
        none=none,
    )


__version__ = "0.1.0"

__all__ = [
    "BorderStyle",
    "ConfigError",
    "ParseError",
    "RenderError",
    "Table",
    "TableError",
    "from_csv",
    "from_rows",
    "__version__",
]
