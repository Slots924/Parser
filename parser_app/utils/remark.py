"""Helpers for working with remark field configuration."""
from __future__ import annotations

import re


class RemarkParseError(ValueError):
    """Raised when remark indexes string contains invalid data."""


_SPLIT_PATTERN = re.compile(r"[\s,]+")


def parse_remark_indexes(value: str | None) -> tuple[int, ...]:
    """Parse a comma or whitespace separated string into remark indexes.

    Empty values return an empty tuple. The parser validates that every token
    is a positive integer (1-based) and there are no duplicates.
    """

    if value is None:
        return ()

    text = value.strip()
    if not text:
        return ()

    indexes: list[int] = []
    seen: set[int] = set()

    for token in _SPLIT_PATTERN.split(text):
        if not token:
            continue
        if not token.isdigit():
            raise RemarkParseError(
                f"Некоректне значення remark: '{token}' не є додатнім числом."
            )

        index = int(token)
        if index < 1:
            raise RemarkParseError("Індекси remark мають бути ≥ 1.")

        if index in seen:
            raise RemarkParseError(f"Значення remark містить дублікат індексу {index}.")

        seen.add(index)
        indexes.append(index)

    return tuple(indexes)
