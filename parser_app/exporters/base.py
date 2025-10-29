"""Exporter abstractions."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from parser_app.models import ProfileRecord


class BaseExporter(ABC):
    """Export a collection of profile records."""

    @abstractmethod
    def export(self, records: Iterable[ProfileRecord]) -> Path:
        """Persist records and return the path to the generated artifact."""
