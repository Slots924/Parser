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

        self._init_variables()
        self._setup_styles()
        self._configure_root()
        self._build_layout()

    def _init_variables(self) -> None:
        """Initialize Tk variables bound to the settings form."""

        self.ua_index_var = tk.IntVar(value=self.config.ua_index)
        self.cookie_index_var = tk.IntVar(value=self.config.cookie_index)

        remark_defaults = list(self.config.remark_indices)
        if len(remark_defaults) < 3:
            remark_defaults.extend([0] * (3 - len(remark_defaults)))
        else:
            remark_defaults = remark_defaults[:3]
        self.remark_index_vars: list[tk.IntVar] = [tk.IntVar(value=value) for value in remark_defaults]

        separator_options = list(dict.fromkeys(self.config.separator_options))
        if not separator_options:
            separator_options = [self.config.separator]
        if self.config.separator not in separator_options:
            separator_options.insert(0, self.config.separator)
        self.separator_options = separator_options
        self.separator_var = tk.StringVar(value=self.config.separator)

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

        self._build_settings_form()

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

    def _build_settings_form(self) -> None:
        form = ttk.Frame(self.settings_container, style="Settings.TFrame")
        form.grid(row=1, column=0, sticky="new", pady=(12, 0))
        form.columnconfigure(0, weight=0)
        form.columnconfigure(1, weight=1)

        row = 0
        self._add_labeled_spinbox(form, row, "UA_INDEX", self.ua_index_var)
        row += 1
        self._add_labeled_spinbox(form, row, "COOKIE_INDEX", self.cookie_index_var)
        row += 1
        self._add_remark_row(form, row)
        row += 1
        self._add_separator_row(form, row)

    def _add_labeled_spinbox(self, parent: ttk.Frame, row: int, label_text: str, variable: tk.IntVar) -> None:
        label = ttk.Label(parent, text=label_text, anchor="w")
        label.grid(row=row, column=0, sticky="w", pady=(0, 8))
        spinbox = self._create_spinbox(parent, variable)
        spinbox.grid(row=row, column=1, sticky="w", pady=(0, 8))

    def _add_remark_row(self, parent: ttk.Frame, row: int) -> None:
        label = ttk.Label(parent, text="REMARK_INDEX", anchor="w")
        label.grid(row=row, column=0, sticky="w", pady=(0, 8))

        remark_frame = ttk.Frame(parent, style="Settings.TFrame")
        remark_frame.grid(row=row, column=1, sticky="w", pady=(0, 8))
        for idx, variable in enumerate(self.remark_index_vars):
            spinbox = self._create_spinbox(remark_frame, variable)
            padx = (0, 8) if idx < len(self.remark_index_vars) - 1 else 0
            spinbox.grid(row=0, column=idx, sticky="w", padx=padx)

    def _add_separator_row(self, parent: ttk.Frame, row: int) -> None:
        label = ttk.Label(parent, text="SEPARATOR", anchor="w")
        label.grid(row=row, column=0, sticky="w", pady=(0, 8))

        separator_box = ttk.Combobox(
            parent,
            textvariable=self.separator_var,
            values=self.separator_options,
            state="readonly",
        )
        separator_box.grid(row=row, column=1, sticky="we", pady=(0, 8))
        self.separator_combobox = separator_box

    def _create_spinbox(self, parent: ttk.Widget, variable: tk.IntVar) -> ttk.Spinbox:
        spinbox = ttk.Spinbox(
            parent,
            from_=0,
            to=99,
            textvariable=variable,
            width=4,
            justify="center",
            wrap=False,
        )
        return spinbox

    def _on_start(self) -> None:
        self._sync_config_from_form()
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

    def _sync_config_from_form(self) -> None:
        self.config.ua_index = self._clamp_spinbox_value(self.ua_index_var)
        self.config.cookie_index = self._clamp_spinbox_value(self.cookie_index_var)
        self.config.remark_indices = tuple(
            self._clamp_spinbox_value(variable) for variable in self.remark_index_vars
        )
        self.config.separator = self.separator_var.get()

    def _clamp_spinbox_value(self, variable: tk.IntVar) -> int:
        try:
            value = int(variable.get())
        except (tk.TclError, ValueError):
            return 0
        return max(0, min(99, value))


def run() -> None:
    """Entry point to run the GUI application."""
    gui = ParserGUI()
    gui.root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    run()
