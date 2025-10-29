"""Reader abstractions for acquiring raw data."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from parser_app.models import RawRecord


class BaseReader(ABC):
    """Abstract reader that produces :class:`RawRecord` instances."""

    @abstractmethod
    def read(self) -> Iterable[RawRecord]:
        """Yield raw records from the underlying data source."""


class InMemoryReader(BaseReader):
    """A simple reader useful in tests."""

    def __init__(self, lines: Iterable[str]) -> None:
        self._lines = list(lines)

    def read(self) -> Iterable[RawRecord]:
        for line_no, line in enumerate(self._lines, start=1):
            cleaned = line.strip()
            if not cleaned:
                continue
            yield RawRecord(line_no=line_no, content=cleaned)
