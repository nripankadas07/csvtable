"""Wide-character / unicode width tests."""

from __future__ import annotations

import pytest

import csvtable
from csvtable._width import char_width, pad, text_width, truncate


def test_text_width_ascii_letters() -> None:
    assert text_width("hello") == 5


def test_text_width_wide_cjk() -> None:
    # Each CJK character is 2 columns wide.
    assert text_width("中国") == 4


def test_text_width_combining_characters() -> None:
    # 'a' + combining acute (U+0301)
    assert text_width("á") == 1


def test_text_width_empty_string() -> None:
    assert text_width("") == 0


def test_char_width_control_chars() -> None:
    assert char_width("\x07") == 0
    assert char_width("\x00") == 0
    assert char_width("\x7f") == 0


def test_char_width_empty_returns_zero() -> None:
    assert char_width("") == 0


def test_pad_left_default() -> None:
    assert pad("ab", 5) == "ab   "


def test_pad_right() -> None:
    assert pad("ab", 5, "right") == "   ab"


def test_pad_center_balances_extra_on_right() -> None:
    assert pad("ab", 5, "center") == " ab  "


def test_pad_handles_wide_chars() -> None:
    # "中" is width 2; pad to width 4 leaves 2 columns.
    assert pad("中", 4) == "中  "


def test_pad_invalid_align_raises() -> None:
    with pytest.raises(ValueError):
        pad("a", 3, "diagonal")


def test_pad_overflow_raises() -> None:
    with pytest.raises(ValueError):
        pad("hello", 3)


def test_pad_invalid_fill_raises() -> None:
    with pytest.raises(ValueError):
        pad("a", 3, fill="ab")


def test_truncate_no_change_when_within_width() -> None:
    assert truncate("abc", 10) == "abc"


def test_truncate_zero_width_returns_empty() -> None:
    assert truncate("abc", 0) == ""


def test_truncate_negative_width_raises() -> None:
    with pytest.raises(ValueError):
        truncate("abc", -1)


def test_truncate_invalid_side_raises() -> None:
    with pytest.raises(ValueError):
        truncate("abcdef", 3, side="diagonal")


def test_truncate_handles_wide_chars() -> None:
    # 中国语 is width 6; truncate to width 5 with ellipsis (1 wide).
    out = truncate("中国语", 5)
    # Keep first wide char (2) + ellipsis (1) = 3 width; we still have
    # room for one more wide char (5 - 1 = 4 / 2 = 2 wide chars).
    assert text_width(out) <= 5
    assert out.endswith("…")


def test_render_with_wide_chars_widths_correct() -> None:
    out = csvtable.from_rows(
        [["中国", "x"]], headers=["国家", "v"]
    )
    # "中国" and "国家" are both width 4; column should be width 4.
    assert "| 中国 |" in out
    assert "| 国家 |" in out


def test_render_combining_marks_dont_inflate_width() -> None:
    out = csvtable.from_rows(
        [["café", "1"]], headers=["a", "b"]
    )
    # If width was wrong the headers wouldn't align under the data.
    lines = out.split("\n")
    assert len(set(len(line) for line in lines)) == 1
