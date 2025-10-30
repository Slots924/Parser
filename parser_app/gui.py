"""Graphical interface for the parser application."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from parser_app.config import AppConfig
from parser_app.exporters.excel_exporter import ExcelExporter
from parser_app.parsers.profile_parser import ProfileParser
from parser_app.readers.text_reader import TextReader
from parser_app.services.pipeline import ProcessingPipeline


class ParserGUI:
    """Tkinter based GUI shell around the parsing pipeline."""

    def __init__(self, root: tk.Tk | None = None, config: AppConfig | None = None) -> None:
        self.root = root or tk.Tk()
        self.config = config or AppConfig()

        self._setup_styles()
        self._configure_root()
        self._build_layout()

    def _setup_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            # Fall back silently if the theme is not available on the platform.
            pass

        style.configure("TFrame", background="#f7f7f9")
        style.configure(
            "Settings.TFrame",
            background="#ffffff",
            relief="flat",
            borderwidth=0,
        )
        style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"), foreground="#2f2f33")
        style.configure("Hint.TLabel", font=("Segoe UI", 10), foreground="#6b6b76")
        style.configure("Start.TButton", font=("Segoe UI", 11, "bold"))

    def _configure_root(self) -> None:
        self.root.title("Parser App")
        default_width, default_height = 960, 640
        self.root.geometry(self._center_geometry(default_width, default_height))
        self.root.minsize(820, 520)

        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

    def _center_geometry(self, width: int, height: int) -> str:
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        return f"{width}x{height}+{x}+{y}"

    def _build_layout(self) -> None:
        self.settings_container = ttk.Frame(self.root, style="Settings.TFrame", padding=(16, 20, 16, 16))
        self.settings_container.grid(row=0, column=0, sticky="nswe")
        self.settings_container.columnconfigure(0, weight=1)
        self.settings_container.rowconfigure(1, weight=1)

        heading = ttk.Label(self.settings_container, text="Налаштування", style="Heading.TLabel")
        heading.grid(row=0, column=0, sticky="nw")

        placeholder = ttk.Label(
            self.settings_container,
            text="Місце для додаткових опцій",
            style="Hint.TLabel",
            anchor="n",
            justify="center",
        )
        placeholder.grid(row=1, column=0, sticky="nwe", pady=(12, 0))

        self.start_button = ttk.Button(
            self.settings_container,
            text="Старт",
            style="Start.TButton",
            command=self._on_start,
        )
        self.start_button.grid(row=2, column=0, sticky="swe", pady=(24, 0))

        main_area = ttk.Frame(self.root, padding=(16, 16, 16, 16))
        main_area.grid(row=0, column=1, sticky="nsew")
        main_area.columnconfigure(0, weight=1)
        main_area.rowconfigure(0, weight=1)

        self.text_widget = tk.Text(main_area, wrap="none", font=("Consolas", 11), undo=True)
        self.text_widget.grid(row=0, column=0, sticky="nsew")

        v_scroll = ttk.Scrollbar(main_area, orient="vertical", command=self.text_widget.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")

        h_scroll = ttk.Scrollbar(main_area, orient="horizontal", command=self.text_widget.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")

        self.text_widget.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    def _on_start(self) -> None:
        raw_text = self.text_widget.get("1.0", "end-1c")
        if not raw_text.strip():
            messagebox.showinfo("Немає даних", "Введіть або вставте дані для парсингу.")
            return

        reader = TextReader(raw_text)
        parser = ProfileParser(self.config)
        exporter = ExcelExporter(self.config)
        pipeline = ProcessingPipeline(reader=reader, parser=parser, exporter=exporter)

        try:
            output_path = pipeline.run()
        except Exception as exc:  # pragma: no cover - GUI notification path
            messagebox.showerror("Помилка", f"Не вдалося виконати парсинг.\n\n{exc}")
            return

        messagebox.showinfo("Успіх", f"Файл успішно створено:\n{output_path}")


def run() -> None:
    """Entry point to run the GUI application."""
    gui = ParserGUI()
    gui.root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    run()
