"""Parser abstractions."""
from __future__ import annotations

from abc import ABC, abstractmethod

from parser_app.models import ProfileRecord, RawRecord


class BaseParser(ABC):
    """Abstract parser that turns raw records into structured ones."""

    @abstractmethod
    def parse(self, raw: RawRecord) -> ProfileRecord:
        """Parse a raw record into a :class:`ProfileRecord`."""
