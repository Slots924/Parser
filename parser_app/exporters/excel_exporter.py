"""Excel exporter implementation."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

try:  # pragma: no cover - handled in runtime branch
    from openpyxl import Workbook
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
    Workbook = None  # type: ignore[assignment]
    _OPENPYXL_IMPORT_ERROR: Optional[Exception] = exc
else:  # pragma: no cover - exercised when dependency exists
    _OPENPYXL_IMPORT_ERROR = None

from parser_app.config import AppConfig
from parser_app.exporters.base import BaseExporter
from parser_app.models import ProfileRecord


class ExcelExporter(BaseExporter):
    """Export records to an Excel file using :mod:`openpyxl`."""

    def __init__(self, config: AppConfig) -> None:
        if Workbook is None:  # pragma: no cover - requires missing dependency
            raise ImportError(
                "openpyxl is required for Excel export. Install it with 'pip install openpyxl'."
            ) from _OPENPYXL_IMPORT_ERROR
        self.config = config

    def export(self, records: Iterable[ProfileRecord]) -> Path:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = self.config.workbook_title

        headers = list(self.config.header_iter())
        worksheet.append(headers)

        for record in records:
            worksheet.append(record.to_row(headers))

        output_path = self.config.build_output_path()
        workbook.save(output_path)
        return output_path
