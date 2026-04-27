"""Exception hierarchy for csvtable."""

from __future__ import annotations


class TableError(Exception):
    """Base class for all csvtable errors."""


class ConfigError(TableError):
    """Raised when an option (border, alignment, ...) is invalid."""


class RenderError(TableError):
    """Raised when a table cannot be rendered."""


class ParseError(TableError):
    """Raised when CSV input cannot be parsed."""


__all__ = ["ConfigError", "ParseError", "RenderError", "TableError"]
