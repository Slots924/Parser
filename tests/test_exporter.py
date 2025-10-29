from pathlib import Path

import pytest

openpyxl = pytest.importorskip("openpyxl")
load_workbook = openpyxl.load_workbook

from parser_app.config import AppConfig
from parser_app.exporters.excel_exporter import ExcelExporter
from parser_app.models import ProfileRecord


def test_excel_exporter_creates_file(tmp_path):
    config = AppConfig(output_dir=tmp_path)
    exporter = ExcelExporter(config)

    records = [
        ProfileRecord(remark="remark", tab="tab", cookie="cookie", ua="ua", proxytype="proxy"),
    ]

    output_path = exporter.export(records)

    assert Path(output_path).exists()

    workbook = load_workbook(output_path)
    sheet = workbook.active

    assert sheet.title == config.workbook_title
    assert sheet.max_row == 2
    assert sheet.max_column == len(tuple(config.header_iter()))

    first_row = next(sheet.iter_rows(min_row=2, max_row=2, values_only=True))
    assert first_row[1] == "remark"
    assert first_row[2] == "tab"
