"""Orchestration layer for the parsing workflow."""
from __future__ import annotations

from typing import Iterable, List

from parser_app.exporters.base import BaseExporter
from parser_app.models import ProfileRecord
from parser_app.parsers.base import BaseParser
from parser_app.readers.base import BaseReader


class ProcessingPipeline:
    """Coordinates reader, parser and exporter to process the data."""

    def __init__(self, reader: BaseReader, parser: BaseParser, exporter: BaseExporter) -> None:
        self.reader = reader
        self.parser = parser
        self.exporter = exporter

    def run(self) -> str:
        records: List[ProfileRecord] = []
        for raw in self.reader.read():
            parsed = self.parser.parse(raw)
            records.append(parsed)
        output_path = self.exporter.export(records)
        return str(output_path)

    def run_and_iter(self) -> Iterable[ProfileRecord]:
        for raw in self.reader.read():
            yield self.parser.parse(raw)
