"""Core ``Table`` class: stores rows + config and renders them."""

from __future__ import annotations

import re
from typing import Any, Iterable, Sequence

from ._borders import BorderStyle, get_style
from ._errors import ConfigError, RenderError
from ._width import pad, text_width, truncate as _truncate


_VALID_ALIGN = frozenset({"left", "right", "center", "auto"})
_VALID_TRUNCATE = frozenset({"end", "start", "middle"})

# Loose check for "this column is numeric so right-align it by default."
_NUMERIC_RE = re.compile(r"^[+-]?(?:\d{1,3}(?:[,_]\d{3})*|\d+)(?:\.\d+)?%?$")


class Table:
    """A renderable table.

    All values are coerced to ``str`` via the standard ``str()`` builtin
    at render time. Pass the headers either via the constructor or by
    setting :pyattr:`headers` later. Add rows incrementally with
    :meth:`add_row` or all at once via the constructor.
    """

    def __init__(
        self,
        headers: Sequence[Any] | None = None,
        rows: Iterable[Sequence[Any]] | None = None,
        *,
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
    ) -> None:
        if not isinstance(padding, int) or isinstance(padding, bool) or padding < 0:
            raise ConfigError("padding must be a non-negative int")
        if truncate not in _VALID_TRUNCATE:
            raise ConfigError(
                f"truncate must be one of {sorted(_VALID_TRUNCATE)}"
            )
        if not isinstance(ellipsis, str):
            raise ConfigError("ellipsis must be a string")
        _validate_align_arg(align)
        _validate_max_width_arg(max_width)
        self._align_arg = align
        self._max_width_arg = max_width
        self.truncate_side = truncate
        self.ellipsis = ellipsis
        self.padding = padding
        self.header_separator = bool(header_separator)
        self.row_separator = bool(row_separator)
        self.missing = str(missing)
        self.none = str(none)
        self.border_style = (
            border if isinstance(border, BorderStyle) else get_style(border)
        )
        self.headers: list[str] | None = (
            [self._cell(h) for h in headers] if headers is not None else None
        )
        self.rows: list[list[str]] = []
        if rows is not None:
            for row in rows:
                self.add_row(row)

    # -- mutation ----------------------------------------------------------

    def add_row(self, row: Sequence[Any]) -> "Table":
        if isinstance(row, (str, bytes)):
            raise ConfigError("row must be a sequence of cells, not a string")
        try:
            cells = [self._cell(value) for value in row]
        except TypeError as exc:
            raise ConfigError("row must be iterable") from exc
        self.rows.append(cells)
        return self

    def add_rows(self, rows: Iterable[Sequence[Any]]) -> "Table":
        for row in rows:
            self.add_row(row)
        return self

    def _cell(self, value: Any) -> str:
        if value is None:
            text = self.none
        else:
            text = str(value)
        # Collapse line breaks so each row stays on one terminal line.
        return text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")

    # -- introspection -----------------------------------------------------

    def column_count(self) -> int:
        widths = [len(self.headers) if self.headers else 0]
        widths.extend(len(row) for row in self.rows)
        return max(widths) if widths else 0

    # -- public render -----------------------------------------------------

    def render(self) -> str:
        cols = self.column_count()
        if cols == 0:
            return ""
        normalised = self._normalised_rows(cols)
        widths = self._compute_widths(normalised, cols)
        aligns = self._resolve_aligns(cols, normalised)
        cells = self._format_cells(normalised, widths, aligns)
        return self._draw(cells, widths, aligns)

    def __str__(self) -> str:  # pragma: no cover - thin wrapper
        return self.render()

    # -- helpers -----------------------------------------------------------

    def _normalised_rows(self, cols: int) -> list[list[str]]:
        result: list[list[str]] = []
        if self.headers is not None:
            result.append(self._extend(self.headers, cols))
        for row in self.rows:
            result.append(self._extend(row, cols))
        return result

    def _extend(self, row: Sequence[str], cols: int) -> list[str]:
        out = list(row[:cols])
        if len(out) < cols:
            out.extend([self.missing] * (cols - len(out)))
        return out

    def _compute_widths(
        self, rows: list[list[str]], cols: int
    ) -> list[int]:
        max_widths = self._resolve_max_widths(cols)
        widths = [0] * cols
        for row in rows:
            for i, cell in enumerate(row):
                w = text_width(cell)
                cap = max_widths[i]
                if cap is not None and w > cap:
                    w = cap
                if w > widths[i]:
                    widths[i] = w
        # If a column is completely empty, give it width 0; the padding
        # frame will still be drawn.
        return widths

    def _resolve_max_widths(self, cols: int) -> list[int | None]:
        spec = self._max_width_arg
        if spec is None:
            return [None] * cols
        if isinstance(spec, int):
            if spec < 1:
                raise ConfigError("max_width int must be >= 1")
            return [spec] * cols
        try:
            entries = list(spec)
        except TypeError as exc:
            raise ConfigError("max_width must be int or sequence") from exc
        if any(e is not None and (not isinstance(e, int) or e < 1) for e in entries):
            raise ConfigError("max_width entries must be None or int >= 1")
        if len(entries) < cols:
            entries.extend([None] * (cols - len(entries)))
        return entries[:cols]

    def _resolve_aligns(
        self, cols: int, rows: list[list[str]]
    ) -> list[str]:
        spec = self._align_arg
        if spec is None:
            entries: list[str] = ["auto"] * cols
        elif isinstance(spec, str):
            self._check_align(spec)
            entries = [spec] * cols
        else:
            try:
                user_entries = [str(a) for a in spec]
            except TypeError as exc:
                raise ConfigError("align must be str or sequence") from exc
            for a in user_entries:
                self._check_align(a)
            if len(user_entries) < cols:
                user_entries.extend(["auto"] * (cols - len(user_entries)))
            entries = user_entries[:cols]
        # Resolve "auto": numeric columns right-align, else left.
        data_rows = rows[1:] if self.headers is not None else rows
        for i, align in enumerate(entries):
            if align == "auto":
                entries[i] = "right" if self._column_is_numeric(data_rows, i) else "left"
        return entries

    def _check_align(self, value: str) -> None:
        if value not in _VALID_ALIGN:
            raise ConfigError(
                f"align must be one of {sorted(_VALID_ALIGN)}; got {value!r}"
            )

    def _column_is_numeric(
        self, data_rows: list[list[str]], col: int
    ) -> bool:
        seen_value = False
        for row in data_rows:
            cell = row[col].strip() if col < len(row) else ""
            if cell == "":
                continue
            seen_value = True
            if not _NUMERIC_RE.match(cell):
                return False
        return seen_value

    def _format_cells(
        self,
        rows: list[list[str]],
        widths: list[int],
        aligns: list[str],
    ) -> list[list[str]]:
        result: list[list[str]] = []
        for row in rows:
            formatted: list[str] = []
            for i, cell in enumerate(row):
                w = widths[i]
                if text_width(cell) > w:
                    cell = _truncate(cell, w, self.ellipsis, self.truncate_side)
                try:
                    formatted.append(pad(cell, w, aligns[i]))
                except ValueError as exc:  # pragma: no cover - defensive
                    raise RenderError(str(exc)) from exc
            result.append(formatted)
        return result

    def _draw(
        self,
        cells: list[list[str]],
        widths: list[int],
        aligns: list[str],
    ) -> str:
        style = self.border_style
        pad_str = " " * self.padding
        lines: list[str] = []
        if style.draw_outer:
            lines.append(self._draw_horizontal(widths, "top"))
        header_idx = 0 if self.headers is not None else None
        for i, row in enumerate(cells):
            lines.append(self._draw_row(row, pad_str, style))
            is_last = i == len(cells) - 1
            if (
                header_idx is not None
                and i == header_idx
                and self.header_separator
                and style.draw_header_separator
                and not is_last
            ):
                lines.append(self._draw_horizontal(widths, "header", aligns))
            elif not is_last and self.row_separator and style.draw_inner_horizontal:
                lines.append(self._draw_horizontal(widths, "middle"))
        if style.draw_outer:
            lines.append(self._draw_horizontal(widths, "bottom"))
        return "\n".join(lines)

    def _draw_row(
        self, row: list[str], pad_str: str, style: BorderStyle
    ) -> str:
        sep = style.vertical if style.draw_inner_vertical else ""
        edge = style.vertical if style.draw_outer else ""
        # Markdown style uses inner vertical bars on the edges too.
        if not style.draw_outer and style.draw_inner_vertical and style is not None:
            # markdown: use inner vertical glyph for the edges as well.
            edge = style.vertical
        body = (sep.join(f"{pad_str}{cell}{pad_str}" for cell in row))
        return f"{edge}{body}{edge}"

    def _draw_horizontal(
        self,
        widths: list[int],
        position: str,
        aligns: list[str] | None = None,
    ) -> str:
        style = self.border_style
        h = style.horizontal
        pad_w = self.padding * 2
        if position == "top":
            left, junction, right = (
                style.top_left,
                style.top_junction,
                style.top_right,
            )
        elif position == "bottom":
            left, junction, right = (
                style.bottom_left,
                style.bottom_junction,
                style.bottom_right,
            )
        else:
            left, junction, right = (
                style.middle_left,
                style.middle_junction,
                style.middle_right,
            )
        # Markdown header separator uses ':' to denote alignment when
        # applicable. We honour that for the "header" position only.
        segments: list[str] = []
        for i, w in enumerate(widths):
            seg_width = w + pad_w
            if (
                position == "header"
                and aligns is not None
                and style is get_style("markdown")
            ):
                segments.append(_markdown_header_segment(aligns[i], seg_width))
            else:
                segments.append(h * seg_width)
        return left + junction.join(segments) + right


def _validate_align_arg(spec: Any) -> None:
    if spec is None:
        return
    if isinstance(spec, str):
        if spec not in _VALID_ALIGN:
            raise ConfigError(
                f"align must be one of {sorted(_VALID_ALIGN)}; got {spec!r}"
            )
        return
    try:
        entries = list(spec)
    except TypeError as exc:
        raise ConfigError("align must be str or sequence of str") from exc
    for entry in entries:
        if not isinstance(entry, str) or entry not in _VALID_ALIGN:
            raise ConfigError(
                f"align entry must be one of {sorted(_VALID_ALIGN)}; got {entry!r}"
            )


def _validate_max_width_arg(spec: Any) -> None:
    if spec is None:
        return
    if isinstance(spec, bool):
        raise ConfigError("max_width must be int or sequence")
    if isinstance(spec, int):
        if spec < 1:
            raise ConfigError("max_width int must be >= 1")
        return
    try:
        entries = list(spec)
    except TypeError as exc:
        raise ConfigError("max_width must be int or sequence") from exc
    for entry in entries:
        if entry is None:
            continue
        if isinstance(entry, bool) or not isinstance(entry, int) or entry < 1:
            raise ConfigError("max_width entries must be None or int >= 1")


def _markdown_header_segment(align: str, width: int) -> str:
    """Build a markdown header separator segment with alignment marks."""

    if width < 3:
        return "-" * max(width, 1)
    body = "-" * width
    chars = list(body)
    if align == "left":
        chars[0] = ":"
    elif align == "right":
        chars[-1] = ":"
    elif align == "center":
        chars[0] = ":"
        chars[-1] = ":"
    return "".join(chars)


__all__ = ["Table"]
