"""Utilities for previewing parsed data."""
from __future__ import annotations

from typing import Iterable, List, Tuple

from parser_app.models import RawRecord


PreviewRow = Tuple[int, str]


def preview_first_row(lines: Iterable[str], separator: str = " :: ") -> List[PreviewRow]:
    """Return the indexed parts of the first non-empty row.

    Parameters
    ----------
    lines:
        An iterable of raw text rows supplied by the user.
    separator:
        The delimiter used to split a row into distinct fields. By default it
        matches the application's global separator (``" :: "``).

    Returns
    -------
    list[tuple[int, str]]
        A list of ``(index, value)`` tuples representing the extracted fields
        where the index is 1-based. Empty input yields an empty list.
    """

    for line_no, line in enumerate(lines, start=1):
        cleaned = line.strip()
        if not cleaned:
            continue
        raw = RawRecord(line_no=line_no, content=cleaned)
        parts = raw.parts(separator)
        return [(index, part) for index, part in enumerate(parts, start=1)]
    return []
