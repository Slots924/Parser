"""Helpers for assembling the processing pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from parser_app.config import AppConfig
from parser_app.exporters.excel_exporter import ExcelExporter
from parser_app.parsers.profile_parser import ProfileParser
from parser_app.readers.text_reader import TextReader
from parser_app.services.pipeline import ProcessingPipeline


def _normalize_remark_indices(indices: Sequence[int] | None) -> tuple[int, ...] | None:
    if indices is None:
        return None
    normalized = tuple(index for index in indices if index > 0)
    return normalized or None


def parse_remark_indices(value: str | None) -> tuple[int, ...] | None:
    """Parse a comma separated string of integers into a tuple."""

    if value is None:
        return None

    parts = [part.strip() for part in value.split(",")]
    indices: list[int] = []
    for part in parts:
        if not part:
            continue
        index = int(part)
        if index <= 0:
            raise ValueError("Remark indices must be positive integers")
        indices.append(index)
    return _normalize_remark_indices(indices)


def build_pipeline_from_text(
    text: str,
    *,
    ua_index: int | None = None,
    cookie_index: int | None = None,
    separator: str | None = None,
    remark_indices: Sequence[int] | None = None,
    output_dir: Path | str | None = None,
) -> ProcessingPipeline:
    """Create a processing pipeline instance for the provided text input."""

    config_kwargs: dict[str, object] = {}
    if ua_index is not None:
        config_kwargs["ua_index"] = ua_index
    if cookie_index is not None:
        config_kwargs["cookie_index"] = cookie_index
    if separator is not None:
        config_kwargs["separator"] = separator

    normalized_indices = _normalize_remark_indices(remark_indices)
    if normalized_indices is not None:
        config_kwargs["remark_indices"] = normalized_indices

    config = AppConfig(**config_kwargs)

    if output_dir is not None:
        config.output_dir = Path(output_dir)

    reader = TextReader(text)
    parser = ProfileParser(config)
    exporter = ExcelExporter(config)

    pipeline = ProcessingPipeline(reader=reader, parser=parser, exporter=exporter)
    return pipeline

