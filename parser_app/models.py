"""Domain models used throughout the parsing pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(slots=True)
class RawRecord:
    """Represents a single raw line before parsing."""

    line_no: int
    content: str

    def parts(self, separator: str) -> list[str]:
        """Split the content into parts using the given separator."""
        return [part.strip() for part in self.content.split(separator)]


@dataclass(slots=True)
class ProfileRecord:
    """Structured representation of a parsed profile."""

    name: str = ""
    remark: str = ""
    tab: str = ""
    platform: str = ""
    username: str = ""
    password: str = ""
    fakey: str = ""
    cookie: str = ""
    proxytype: str = ""
    ipchecker: str = ""
    proxy: str = ""
    proxyurl: str = ""
    proxyid: str = ""
    ip: str = ""
    countrycode: str = ""
    regioncode: str = ""
    citycode: str = ""
    ua: str = ""
    resolution: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    def to_row(self, headers: Sequence[str]) -> list[str]:
        """Return the record in the order defined by ``headers``."""
        values: list[str] = []
        for header in headers:
            if hasattr(self, header):
                values.append(getattr(self, header))
            else:
                values.append(self.metadata.get(header, ""))
        return values

    @classmethod
    def from_mapping(cls, mapping: dict[str, str]) -> "ProfileRecord":
        """Create a record from a mapping of column names to values."""
        known_fields = {field.name for field in cls.__dataclass_fields__.values() if field.name != "metadata"}
        init_kwargs = {k: v for k, v in mapping.items() if k in known_fields}
        metadata = {k: v for k, v in mapping.items() if k not in known_fields}
        return cls(**init_kwargs, metadata=metadata)

    def merge(self, **fields: str) -> None:
        """Update the record in-place with new field values."""
        for key, value in fields.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.metadata[key] = value


def safe_get(parts: Sequence[str], index_1based: int) -> str:
    """Return a part by index (1-based) or an empty string if it is missing."""
    index = index_1based - 1
    if 0 <= index < len(parts):
        return parts[index]
    return ""
