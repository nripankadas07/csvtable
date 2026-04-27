"""Visible-width helpers.

Cell strings can contain wide characters (CJK, fullwidth Latin) that
take two terminal columns. ``unicodedata.east_asian_width`` gives us
the categories we need to handle the common cases without pulling in a
third-party width library.
"""

from __future__ import annotations

import unicodedata


_WIDE_CATEGORIES = frozenset({"W", "F"})


def char_width(char: str) -> int:
    """Return the number of terminal columns occupied by *char*.

    Returns 0 for combining marks and zero-width control characters,
    1 for narrow characters, 2 for wide / fullwidth characters.
    """

    if not char:
        return 0
    code = ord(char)
    if code == 0:
        return 0
    if code < 32 or code == 0x7F:
        return 0
    if unicodedata.combining(char):
        return 0
    if unicodedata.east_asian_width(char) in _WIDE_CATEGORIES:
        return 2
    return 1


def text_width(text: str) -> int:
    """Return the visible width of *text* in terminal columns."""

    return sum(char_width(c) for c in text)


def truncate(text: str, max_width: int, ellipsis: str = "…", side: str = "end") -> str:
    """Truncate *text* so its visible width is at most *max_width*.

    *side* may be ``"end"`` (default), ``"start"`` or ``"middle"``.
    The *ellipsis* marker is inserted at the truncation point so the
    return value still fits within ``max_width``.
    """

    if max_width < 0:
        raise ValueError("max_width must be non-negative")
    if max_width == 0:
        return ""
    if text_width(text) <= max_width:
        return text
    ellipsis_width = text_width(ellipsis)
    if max_width <= ellipsis_width:
        return ellipsis[:max_width]
    keep = max_width - ellipsis_width
    if side == "end":
        return _take_prefix(text, keep) + ellipsis
    if side == "start":
        return ellipsis + _take_suffix(text, keep)
    if side == "middle":
        left = keep // 2
        right = keep - left
        return _take_prefix(text, left) + ellipsis + _take_suffix(text, right)
    raise ValueError(f"unknown truncate side: {side!r}")


def _take_prefix(text: str, width: int) -> str:
    out: list[str] = []
    used = 0
    for ch in text:
        w = char_width(ch)
        if used + w > width:
            break
        out.append(ch)
        used += w
    return "".join(out)


def _take_suffix(text: str, width: int) -> str:
    # Take from the right.
    out: list[str] = []
    used = 0
    for ch in reversed(text):
        w = char_width(ch)
        if used + w > width:
            break
        out.append(ch)
        used += w
    out.reverse()
    return "".join(out)


def pad(text: str, width: int, align: str = "left", fill: str = " ") -> str:
    """Pad *text* with *fill* so its visible width equals *width*.

    Wide characters are accounted for so that the resulting string
    occupies exactly ``width`` terminal columns. Raises ``ValueError``
    if *fill* is not exactly one column wide or if the input already
    overflows the requested width.
    """

    if not isinstance(fill, str) or len(fill) != 1 or char_width(fill) != 1:
        raise ValueError("fill must be a single narrow character")
    current = text_width(text)
    if current > width:
        raise ValueError("text is wider than target width")
    deficit = width - current
    if deficit == 0:
        return text
    if align == "left":
        return text + fill * deficit
    if align == "right":
        return fill * deficit + text
    if align == "center":
        left = deficit // 2
        right = deficit - left
        return fill * left + text + fill * right
    raise ValueError(f"unknown align: {align!r}")


__all__ = ["char_width", "pad", "text_width", "truncate"]
