"""Text-based reader implementations."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from parser_app.models import RawRecord
from parser_app.readers.base import BaseReader


class TextReader(BaseReader):
    """Reads records from text sources."""

    def __init__(self, text: str) -> None:
        self._text = text

    def read(self) -> Iterable[RawRecord]:
        for line_no, line in enumerate(self._text.splitlines(), start=1):
            cleaned = line.strip()
            if not cleaned:
                continue
            yield RawRecord(line_no=line_no, content=cleaned)


class FileReader(TextReader):
    """Reads records from a file on disk."""

    def __init__(self, path: Path, encoding: str = "utf-8") -> None:
        self.path = path
        self.encoding = encoding
        text = path.read_text(encoding=encoding)
        super().__init__(text=text)

    @classmethod
    def from_optional_path(cls, path: Optional[Path], fallback_text: str) -> "TextReader":
        if path is None:
            return TextReader(fallback_text)
        return cls(path)
