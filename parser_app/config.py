"""Application configuration models and helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

from settings import (
    COOKIE_INDEX,
    HEADERS,
    OUTPUT_DIR,
    PROXY_TYPE,
    REMARK_DELIMITER,
    REMARK_INDICES,
    SEPARATOR,
    TAB_VALUE,
    UA_INDEX,
    WORKBOOK_TITLE,
)


@dataclass(slots=True)
class AppConfig:
    """Holds runtime configuration for the parsing pipeline."""

    ua_index: int = UA_INDEX
    cookie_index: int = COOKIE_INDEX
    remark_indices: Sequence[int] = field(default_factory=lambda: REMARK_INDICES)
    remark_delimiter: str = REMARK_DELIMITER
    separator: str = SEPARATOR
    tab_value: str = TAB_VALUE
    proxy_type: str = PROXY_TYPE
    output_dir: Path = field(default_factory=lambda: Path(OUTPUT_DIR))
    workbook_title: str = WORKBOOK_TITLE
    headers: Sequence[str] = field(default_factory=lambda: HEADERS)

    def ensure_output_dir(self) -> Path:
        """Ensure the configured output directory exists and return it."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir

    def build_output_path(self, prefix: str = "parsed_data") -> Path:
        """Construct a timestamped output path inside the output directory."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{prefix}_{timestamp}.xlsx"
        return self.ensure_output_dir() / filename

    def header_iter(self) -> Iterable[str]:
        """Return an iterator over headers preserving configured order."""
        return iter(self.headers)
