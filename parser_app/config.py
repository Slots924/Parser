"""Application configuration models and helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(slots=True)
class AppConfig:
    """Holds runtime configuration for the parsing pipeline."""

    ua_index: int = 3
    cookie_index: int = 5
    separator: str = " :: "
    tab_value: str = "https://www.facebook.com/"
    proxy_type: str = "noproxy"
    output_dir: Path = Path("results")
    remark_indices: tuple[int, ...] | None = None
    workbook_title: str = "Parsed Data"
    headers: Sequence[str] = field(
        default_factory=lambda: (
            "name",
            "remark",
            "tab",
            "platform",
            "username",
            "password",
            "fakey",
            "cookie",
            "proxytype",
            "ipchecker",
            "proxy",
            "proxyurl",
            "proxyid",
            "ip",
            "countrycode",
            "regioncode",
            "citycode",
            "ua",
            "resolution",
        )
    )

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
