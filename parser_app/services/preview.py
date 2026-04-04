"""Utilities for previewing parsed data."""
from __future__ import annotations

from typing import Iterable, List, Tuple

from parser_app.models import RawRecord


PreviewRow = Tuple[int, str]


def preview_first_row(
    lines: Iterable[str],
    separator: str = " :: ",
    additional_breakdown_index: int = 0,
    additional_separator: str = "",
) -> List[PreviewRow]:
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
        preview_rows: List[PreviewRow] = [(index, part) for index, part in enumerate(parts, start=1)]
        if additional_breakdown_index <= 0 or not additional_separator:
            return preview_rows

        source_pos = additional_breakdown_index - 1
        if source_pos < 0 or source_pos >= len(parts):
            return preview_rows
        source_value = parts[source_pos].strip()
        if not source_value:
            return preview_rows

        extra_parts = [item.strip() for item in source_value.split(additional_separator) if item.strip()]
        extra_prefix = additional_breakdown_index * 100
        preview_rows.extend((extra_prefix + order, value) for order, value in enumerate(extra_parts, start=1))
        return preview_rows
    return []
