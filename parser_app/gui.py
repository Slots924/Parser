"""Graphical interface for the parser application."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
from typing import Sequence

from parser_app.config import AppConfig
from parser_app.exporters.excel_exporter import ExcelExporter
from parser_app.parsers.profile_parser import ProfileParser
from parser_app.readers.text_reader import TextReader
from parser_app.services.pipeline import ProcessingPipeline
from parser_app.services.preview import preview_first_row
from parser_app.gui_state import (
    default_profile_name,
    load_gui_state,
    read_int,
    read_int_list,
    read_str,
    save_gui_state,
)


class ParserGUI:
    """Tkinter based GUI shell around the parsing pipeline."""

    REMARK_FIELD_COUNT = 6
    MULTI_FIELD_COUNT = 3

    def __init__(self, root: tk.Tk | None = None, config: AppConfig | None = None) -> None:
        self.root = root or tk.Tk()
        self.config = config or AppConfig()
        self._persisted_state = load_gui_state()

        self._init_variables()
        self._setup_styles()
        self._configure_root()
        self._build_layout()

    def _init_variables(self) -> None:
        """Initialize Tk variables bound to the settings form."""

        state = self._persisted_state

        self.ua_index_var = tk.IntVar(value=read_int(state.get("ua_index"), default=self.config.ua_index))
        self.cookie_index_var = tk.IntVar(
            value=read_int(state.get("cookie_index"), default=self.config.cookie_index)
        )

        persisted_name = read_str(state.get("name"), default=self.config.profile_name).strip()
        name_default = persisted_name or default_profile_name()
        self.name_var = tk.StringVar(value=name_default)

        self.platform_var = tk.StringVar(
            value=read_str(state.get("platform"), default=self.config.platform_value)
        )
        self.additional_breakdown_var = tk.IntVar(
            value=read_int(state.get("additional_breakdown"), default=self.config.additional_breakdown_index)
        )
        self.additional_separator_var = tk.StringVar(
            value=read_str(state.get("additional_separator"), default=self.config.additional_separator)
        )

        remark_defaults = read_int_list(state.get("remark_indices"), self.REMARK_FIELD_COUNT)
        if not any(remark_defaults):
            remark_defaults = self._normalize_indices(self.config.remark_indices, size=self.REMARK_FIELD_COUNT)
        self.remark_index_vars: list[tk.IntVar] = [tk.IntVar(value=value) for value in remark_defaults]

        username_defaults = read_int_list(state.get("username_indices"), self.MULTI_FIELD_COUNT)
        if not any(username_defaults):
            username_defaults = self._normalize_indices(self.config.username_indices)

        password_defaults = read_int_list(state.get("password_indices"), self.MULTI_FIELD_COUNT)
        if not any(password_defaults):
            password_defaults = self._normalize_indices(self.config.password_indices)

        fakey_defaults = read_int_list(state.get("fakey_indices"), self.MULTI_FIELD_COUNT)
        if not any(fakey_defaults):
            fakey_defaults = self._normalize_indices(self.config.fakey_indices)

        self.username_index_vars = [tk.IntVar(value=value) for value in username_defaults]
        self.password_index_vars = [tk.IntVar(value=value) for value in password_defaults]
        self.fakey_index_vars = [tk.IntVar(value=value) for value in fakey_defaults]

        separator_options = list(dict.fromkeys(self.config.separator_options))
        if not separator_options:
            separator_options = [self.config.separator]
        if self.config.separator not in separator_options:
            separator_options.insert(0, self.config.separator)

        persisted_separator = read_str(state.get("separator"), default=self.config.separator)
        if persisted_separator and persisted_separator not in separator_options:
            separator_options.insert(0, persisted_separator)

        self.separator_options = separator_options
        self.separator_var = tk.StringVar(value=persisted_separator or self.config.separator)

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
        style.configure("Test.TButton", font=("Segoe UI", 10), padding=(4, 2))

    def _configure_root(self) -> None:
        self.root.title("Parser App")
        default_width, default_height = 960, 640
        self.root.geometry(self._center_geometry(default_width, default_height))
        self.root.minsize(820, 520)

        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

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

        self.test_button = ttk.Button(
            self.settings_container,
            text="Тест",
            style="Test.TButton",
            command=self._on_test,
        )
        self.test_button.grid(row=3, column=0, sticky="swe", pady=(8, 0))

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
        persisted_text = read_str(self._persisted_state.get("raw_text"), default="")
        if persisted_text:
            self.text_widget.insert("1.0", persisted_text)

    def _build_settings_form(self) -> None:
        form = ttk.Frame(self.settings_container, style="Settings.TFrame")
        form.grid(row=1, column=0, sticky="new", pady=(12, 0))
        form.columnconfigure(0, weight=0)
        form.columnconfigure(1, weight=1)

        row = 0
        self._add_labeled_entry(form, row, "NAME", self.name_var)
        row += 1
        self._add_labeled_spinbox(form, row, "UA_INDEX", self.ua_index_var)
        row += 1
        self._add_labeled_spinbox(form, row, "COOKIE_INDEX", self.cookie_index_var)
        row += 1
        self._add_remark_row(form, row)
        row += 1
        self._add_labeled_entry(form, row, "PLATFORM", self.platform_var)
        row += 1
        self._add_multi_spinbox_row(form, row, "USERNAME", self.username_index_vars)
        row += 1
        self._add_multi_spinbox_row(form, row, "PASSWORD", self.password_index_vars)
        row += 1
        self._add_multi_spinbox_row(form, row, "FAKEY", self.fakey_index_vars)
        row += 1
        self._add_separator_row(form, row)
        row += 1
        self._add_labeled_spinbox(form, row, "ADDITIONAL_BREAKDOWN", self.additional_breakdown_var)
        row += 1
        self._add_labeled_entry(form, row, "ADDITIONAL_SEPARATOR", self.additional_separator_var)

    def _add_labeled_spinbox(self, parent: ttk.Frame, row: int, label_text: str, variable: tk.IntVar) -> None:
        label = ttk.Label(parent, text=label_text, anchor="w")
        label.grid(row=row, column=0, sticky="w", pady=(0, 8))
        spinbox = self._create_spinbox(parent, variable)
        spinbox.grid(row=row, column=1, sticky="w", pady=(0, 8))

    def _add_labeled_entry(
        self,
        parent: ttk.Frame,
        row: int,
        label_text: str,
        variable: tk.StringVar,
    ) -> None:
        label = ttk.Label(parent, text=label_text, anchor="w")
        label.grid(row=row, column=0, sticky="w", pady=(0, 8))
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, sticky="we", pady=(0, 8))

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

    def _add_multi_spinbox_row(
        self,
        parent: ttk.Frame,
        row: int,
        label_text: str,
        variables: list[tk.IntVar],
    ) -> None:
        label = ttk.Label(parent, text=label_text, anchor="w")
        label.grid(row=row, column=0, sticky="w", pady=(0, 8))

        values_frame = ttk.Frame(parent, style="Settings.TFrame")
        values_frame.grid(row=row, column=1, sticky="w", pady=(0, 8))
        for idx, variable in enumerate(variables):
            spinbox = self._create_spinbox(values_frame, variable)
            padx = (0, 8) if idx < len(variables) - 1 else 0
            spinbox.grid(row=0, column=idx, sticky="w", padx=padx)

    def _create_spinbox(self, parent: ttk.Widget, variable: tk.IntVar) -> ttk.Spinbox:
        spinbox = ttk.Spinbox(
            parent,
            from_=0,
            to=9999,
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
        self._reveal_output_path(Path(output_path))

    def _sync_config_from_form(self) -> None:
        self.config.ua_index = self._clamp_spinbox_value(self.ua_index_var)
        self.config.cookie_index = self._clamp_spinbox_value(self.cookie_index_var)
        self.config.profile_name = self.name_var.get().strip()
        self.config.remark_indices = tuple(
            self._clamp_spinbox_value(variable) for variable in self.remark_index_vars
        )
        self.config.platform_value = self.platform_var.get().strip()
        self.config.username_indices = tuple(
            self._clamp_spinbox_value(variable) for variable in self.username_index_vars
        )
        self.config.password_indices = tuple(
            self._clamp_spinbox_value(variable) for variable in self.password_index_vars
        )
        self.config.fakey_indices = tuple(
            self._clamp_spinbox_value(variable) for variable in self.fakey_index_vars
        )
        self.config.separator = self.separator_var.get()
        self.config.additional_breakdown_index = self._clamp_spinbox_value(self.additional_breakdown_var)
        self.config.additional_separator = self.additional_separator_var.get()
        self._persist_form_state()

    def _clamp_spinbox_value(self, variable: tk.IntVar) -> int:
        try:
            value = int(variable.get())
        except (tk.TclError, ValueError):
            return 0
        return max(0, min(9999, value))

    def _normalize_indices(self, indices: Sequence[int], size: int | None = None) -> list[int]:
        expected_size = size or self.MULTI_FIELD_COUNT
        values = [read_int(value) for value in indices]
        if len(values) < expected_size:
            values.extend([0] * (expected_size - len(values)))
        else:
            values = values[:expected_size]
        return values

    def _collect_form_state(self) -> dict[str, object]:
        """Collect current form values for safe persistence."""

        return {
            "ua_index": self._clamp_spinbox_value(self.ua_index_var),
            "cookie_index": self._clamp_spinbox_value(self.cookie_index_var),
            "name": self.name_var.get(),
            "platform": self.platform_var.get(),
            "remark_indices": [self._clamp_spinbox_value(variable) for variable in self.remark_index_vars],
            "username_indices": [self._clamp_spinbox_value(variable) for variable in self.username_index_vars],
            "password_indices": [self._clamp_spinbox_value(variable) for variable in self.password_index_vars],
            "fakey_indices": [self._clamp_spinbox_value(variable) for variable in self.fakey_index_vars],
            "separator": self.separator_var.get(),
            "additional_breakdown": self._clamp_spinbox_value(self.additional_breakdown_var),
            "additional_separator": self.additional_separator_var.get(),
            "raw_text": self.text_widget.get("1.0", "end-1c"),
        }

    def _persist_form_state(self) -> None:
        """Persist form values without interrupting UI flow."""

        save_gui_state(self._collect_form_state())

    def _on_close(self) -> None:
        """Persist values before window closes."""

        self._persist_form_state()
        self.root.destroy()

    def _on_test(self) -> None:
        """Parse only the first row and show the result in a separate window."""

        self._sync_config_from_form()
        raw_text = self.text_widget.get("1.0", "end-1c")
        if not raw_text.strip():
            messagebox.showinfo("Немає даних", "Введіть або вставте дані для тесту.")
            return

        lines = [line for line in raw_text.splitlines() if line.strip()]
        if not lines:
            messagebox.showinfo("Немає даних", "Введіть або вставте дані для тесту.")
            return

        separator = self.separator_var.get() or self.config.separator
        parsed_values = preview_first_row(
            lines,
            separator=separator,
            additional_breakdown_index=self.config.additional_breakdown_index,
            additional_separator=self.config.additional_separator,
        )
        self._show_test_result(parsed_values)

    def _show_test_result(self, values: list[tuple[int, str]]) -> None:
        """Display parsed values of the first line in a scrollable window."""

        result_window = tk.Toplevel(self.root)
        result_window.title("Результат тесту")
        result_window.minsize(360, 240)

        frame = ttk.Frame(result_window, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        result_window.columnconfigure(0, weight=1)
        result_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        text_widget = tk.Text(frame, wrap="none", font=("Consolas", 11), state="normal")
        text_widget.grid(row=0, column=0, sticky="nsew")

        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")

        h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=text_widget.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")

        text_widget.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        formatted_lines = [f"[{idx}] - {value.strip()}" for idx, value in values]
        if not formatted_lines:
            formatted_lines = ["Дані для відображення відсутні."]

        text_widget.insert("1.0", "\n".join(formatted_lines))
        text_widget.configure(state="disabled")

    def _reveal_output_path(self, output_path: Path) -> None:
        try:
            if sys.platform.startswith("win"):
                subprocess.run(["explorer", "/select,", str(output_path)], check=False)
                return
            if sys.platform == "darwin":
                subprocess.run(["open", "-R", str(output_path)], check=False)
                return
            if shutil.which("nautilus"):
                subprocess.run(["nautilus", "--select", str(output_path)], check=False)
                return
            subprocess.run(["xdg-open", str(output_path.parent)], check=False)
        except Exception:
            # Ignore errors silently; parsing result is already created.
            pass


def run() -> None:
    """Entry point to run the GUI application."""
    gui = ParserGUI()
    gui.root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    run()
