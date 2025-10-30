"""Command line interface for the parser application."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from parser_app.config import AppConfig
from parser_app.exporters.excel_exporter import ExcelExporter
from parser_app.parsers.profile_parser import ProfileParser
from parser_app.readers.text_reader import FileReader, TextReader
from parser_app.services.pipeline import ProcessingPipeline


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse profile data and export to Excel.")
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        help="Path to the input text file. If omitted stdin will be used or fallback sample data",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Directory where the generated Excel file will be stored.",
    )
    parser.add_argument(
        "--separator",
        default=" :: ",
        help="Field separator used in the input data (default: ' :: ').",
    )
    parser.add_argument(
        "--ua-index",
        type=int,
        default=3,
        help="1-based index of the field containing the user agent.",
    )
    parser.add_argument(
        "--cookie-index",
        type=int,
        default=5,
        help="1-based index of the field containing cookies.",
    )
    return parser


def load_text(input_path: Optional[Path] = None) -> str:
    if input_path:
        return input_path.read_text(encoding="utf-8")

    if not sys.stdin.isatty():
        return sys.stdin.read()

    sample_path = Path(__file__).resolve().parent.parent / "data" / "samples.txt"
    if sample_path.exists():
        print(f"ℹ️  Використовую приклад з {sample_path}")
        return sample_path.read_text(encoding="utf-8")

    raise FileNotFoundError("Не вдалося знайти джерело даних. Вкажіть --input або передайте дані через stdin.")


def main(argv: Optional[list[str]] = None) -> int:
    args = build_argument_parser().parse_args(argv)

    config = AppConfig(
        ua_index=args.ua_index,
        cookie_index=args.cookie_index,
        separator=args.separator,
    )
    if args.output_dir:
        config.output_dir = args.output_dir

    if args.input:
        reader: TextReader = FileReader(args.input)
    else:
        text = load_text()
        reader = TextReader(text)

    parser = ProfileParser(config)
    exporter = ExcelExporter(config)
    pipeline = ProcessingPipeline(reader=reader, parser=parser, exporter=exporter)

    output_path = pipeline.run()
    print(f"✅ Файл створено: {output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
