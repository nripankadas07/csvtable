# csvtable

Pretty-print CSV / TSV (or any tabular data) as aligned ASCII,
Unicode, Markdown or plain-text tables — with column-width inference,
per-column alignment, configurable truncation and proper handling of
wide (CJK) characters. Zero dependencies, pure Python.

```python
import csvtable

print(csvtable.from_csv("""
job,state,count
build,passing,12
lint,warn,3
tests,passing,156
""".strip()))
```

```
+-------+---------+-------+
| job   | state   | count |
+-------+---------+-------+
| build | passing |    12 |
| lint  | warn    |     3 |
| tests | passing |   156 |
+-------+---------+-------+
```

## Install

```bash
pip install csvtable
```

Requires Python 3.10+. No third-party runtime dependencies.

## Quick examples

### From in-memory rows

```python
import csvtable

rows = [
    ["alice", 30, "Paris"],
    ["bob",   25, "Lyon"],
]
print(csvtable.from_rows(rows, headers=["name", "age", "city"]))
```

### Markdown output

```python
print(csvtable.from_csv(
    "name,score\nalice,90\nbob,75\n",
    border="markdown",
))
```

```
| name  | score |
| :---- | ----: |
| alice |    90 |
| bob   |    75 |
```

### Unicode borders

```python
print(csvtable.from_rows(
    [["中国", 14], ["日本", 125]],
    headers=["国家", "millions"],
    border="unicode",
))
```

```
┌──────┬──────────┐
│ 国家 │ millions │
├──────┼──────────┤
│ 中国 │       14 │
│ 日本 │      125 │
└──────┴──────────┘
```

### Per-column alignment and truncation

```python
print(csvtable.from_rows(
    [["nginx-very-long-name", "running", 4096]],
    headers=["service", "state", "memory"],
    align=["left", "center", "right"],
    max_width=[12, None, None],
    truncate="middle",
))
```

```
+--------------+---------+--------+
| service      |  state  | memory |
+--------------+---------+--------+
| nginx…-name  | running |   4096 |
+--------------+---------+--------+
```

## Public API

### Functions

`csvtable.from_csv(text, **options) -> str`

Parse CSV text and render it. Useful options: `sep` (delimiter,
default `","`), `quote` (default `'"'`), `header` (treat the first
row as headers, default `True`), `skip_blank` (default `True`).

`csvtable.from_rows(rows, *, headers=None, **options) -> str`

Render an iterable of row sequences. Pass `headers` separately or
omit them to render a body-only table.

### `Table` class

```python
table = csvtable.Table(
    headers=["a", "b"],
    align=["left", "right"],
    max_width=[20, 10],
    border="unicode",
)
table.add_row(["alpha", 1])
table.add_row(["beta",  2])
print(table.render())
```

Constructor options (also accepted by `from_rows` and `from_csv`):

| Option | Default | Description |
| --- | --- | --- |
| `align` | `None` | `"left"`, `"right"`, `"center"`, `"auto"`, or a per-column list. `"auto"` right-aligns columns whose values all parse as numbers. |
| `max_width` | `None` | Single int (applies to every column) or per-column list of `int | None`. |
| `truncate` | `"end"` | Where to elide overflowing cells: `"end"`, `"start"` or `"middle"`. |
| `ellipsis` | `"…"` | Marker inserted at truncation point. |
| `border` | `"ascii"` | `"ascii"`, `"unicode"`, `"markdown"`, `"plain"` / `"none"`, or a custom `BorderStyle`. |
| `padding` | `1` | Inner cell padding (each side). |
| `header_separator` | `True` | Draw the row of dashes under the header. |
| `row_separator` | `False` | Draw a divider between every data row (only honoured by styles that enable inner horizontals). |
| `missing` | `""` | Placeholder for short rows that don't fill every column. |
| `none` | `""` | Placeholder for `None` cells. |

`Table.add_row(row)` and `Table.add_rows(iterable)` append data
incrementally and return `self` so calls can be chained.

`Table.render()` returns the formatted string. `str(table)` is a
shortcut for `Table.render()`.

### Errors

All exceptions inherit from `csvtable.TableError`:

- `csvtable.ConfigError` — invalid option (bad `align`, `truncate`, …).
- `csvtable.ParseError` — `from_csv` could not parse the input.
- `csvtable.RenderError` — internal render failure (rare).

### Border styles

Built-in styles: `ascii`, `unicode`, `markdown`, `plain` (alias
`none`). Build your own with `csvtable.BorderStyle(...)` and pass it
to `border=`.

## Wide-character support

Column widths are computed with `unicodedata.east_asian_width` so CJK
text and fullwidth Latin glyphs occupy two terminal columns; combining
marks (e.g. `é`) take zero. This makes the table align correctly in
mixed-script content rather than exploding when a CJK character lands
in a header.

## Running tests

```bash
git clone https://github.com/nripankadas07/csvtable.git
cd csvtable
pip install -e .[dev]
pytest -q
```

The suite ships **103 tests** covering rendering, alignment,
truncation, every border style, CSV / TSV / pipe-separated parsing,
wide-character widths, and exhaustive option-validation error paths.
Coverage stays ≥95% across the package.

## License

MIT — see [LICENSE](LICENSE).
