import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QComboBox,
    QFrame,
)
from PyQt6.QtGui import QFont

from parser_app.services.pipeline_builder import build_pipeline_from_text, parse_remark_indices
from parser_app.services.preview import preview_first_row


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # ---------- Налаштування вікна ----------
        self.setWindowTitle("Parser App (PyQt6)")
        self.resize(1200, 720)
        self.setMinimumSize(960, 600)

        # ---------- Стилі (темна тема у стилі PyCharm) ----------
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                color: #E6E6E6;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 13px;
            }
            QFrame#Panel {
                background-color: #313335;
                border: 1px solid #444;
                border-radius: 8px;
            }
            QComboBox, QTextEdit {
                background-color: #3C3F41;
                border: 1px solid #5A5A5A;
                border-radius: 6px;
                padding: 6px;
            }
            QComboBox:focus, QTextEdit:focus {
                border: 1px solid #6A9FB5;
            }
            QPushButton {
                background: #3C3F41;
                border: 1px solid #5F5F5F;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background: #4C5052;
            }
            QPushButton:pressed {
                background: #2E3133;
            }
            QLabel[role="title"] {
                font-size: 14px;
                font-weight: 700;
                color: #F0F0F0;
            }
        """)

        # ---------- Основний горизонтальний макет ----------
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ========== ЛІВА ПАНЕЛЬ (Налаштування) ==========
        self.settings_panel = QFrame()
        self.settings_panel.setObjectName("Panel")
        self.settings_panel.setFixedWidth(300)
        settings_layout = QVBoxLayout(self.settings_panel)
        settings_layout.setContentsMargins(12, 12, 12, 12)
        settings_layout.setSpacing(10)

        # Заголовок
        title_settings = QLabel("Налаштування")
        title_settings.setProperty("role", "title")
        settings_layout.addWidget(title_settings)

        # --- Поле: User Agent ---
        label_ua = QLabel("User Agent")
        settings_layout.addWidget(label_ua)

        self.combo_useragent = QComboBox()
        # Створюємо список чисел 1-12
        self.combo_useragent.addItems([str(i) for i in range(1, 13)])
        # За замовчуванням — 3
        self.combo_useragent.setCurrentIndex(2)
        settings_layout.addWidget(self.combo_useragent)

        # --- Поле: Cookies ---
        label_cookie = QLabel("Cookies")
        settings_layout.addWidget(label_cookie)

        self.combo_cookies = QComboBox()
        self.combo_cookies.addItems([str(i) for i in range(1, 13)])
        # За замовчуванням — 5
        self.combo_cookies.setCurrentIndex(4)
        settings_layout.addWidget(self.combo_cookies)

        # --- Поле: Remark ---
        label_remark = QLabel("Remark")
        settings_layout.addWidget(label_remark)

        self.remark_edit = QTextEdit()
        self.remark_edit.setPlaceholderText("Наприклад: 7,8...")
        self.remark_edit.setFixedHeight(60)
        settings_layout.addWidget(self.remark_edit)

        # --- Кнопка Start ---
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.on_start_clicked)
        settings_layout.addWidget(self.start_button)

        # --- Кнопка Test ---
        self.test_button = QPushButton("Test")
        self.test_button.setFixedWidth(80)
        settings_layout.addWidget(self.test_button)
        # TODO: при натисканні цієї кнопки має розпарситись перший рядок масиву даних
        # (для прикладу — лише демонстрація)
        self.test_button.clicked.connect(self.on_test_clicked)

        settings_layout.addStretch()

        # ========== ЦЕНТРАЛЬНА ПАНЕЛЬ ==========
        self.center_panel = QFrame()
        self.center_panel.setObjectName("Panel")
        center_layout = QVBoxLayout(self.center_panel)
        center_layout.setContentsMargins(12, 12, 12, 12)
        center_layout.setSpacing(10)

        self.main_text = QTextEdit()
        self.main_text.setPlaceholderText("Тут основна робоча область...")
        center_layout.addWidget(self.main_text, stretch=1)

        self.log_text = QTextEdit()
        self.log_text.setPlaceholderText("Лог виводу...")
        self.log_text.setFixedHeight(120)
        center_layout.addWidget(self.log_text)

        # ========== ПРАВА ПАНЕЛЬ (Розпарсена інформація) ==========
        self.right_panel = QFrame()
        self.right_panel.setObjectName("Panel")
        self.right_panel.setMinimumWidth(260)

        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(10)

        label_info = QLabel("Розпарсена інформація")
        label_info.setProperty("role", "title")
        right_layout.addWidget(label_info)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setPlaceholderText(
            "Тут відображатиметься ваша інформація в готовому вигляді"
        )
        right_layout.addWidget(self.info_text, stretch=1)

        # TODO: тут має відображатись перший розпарсений рядок у вигляді:
        # [1] Jon
        # [2] email
        # [3] Cookie

        # ---------- Додаємо все до головного макету ----------
        main_layout.addWidget(self.settings_panel)
        main_layout.addWidget(self.center_panel, stretch=1)
        main_layout.addWidget(self.right_panel)

        # ---------- Центруємо вікно ----------
        self.center_on_screen()

        # Змінна для збереження налаштувань користувача
        self.UserSettings = {}

        # Підвантажуємо перші рядки з файлу, якщо він доступний
        self._load_initial_text()

    def center_on_screen(self):
        """Центрує вікно по екрану."""
        rect = self.frameGeometry()
        center = QApplication.primaryScreen().availableGeometry().center()
        rect.moveCenter(center)
        self.move(rect.topLeft())

    def log_info(self, message: str) -> None:
        self.log_text.append(f"[INFO] {message}")

    def log_error(self, message: str) -> None:
        self.log_text.append(f"[ERROR] {message}")

    def _load_initial_text(self) -> None:
        """Load the first three lines from my_input.txt into the editor."""
        input_path = Path(__file__).resolve().parent.parent / "my_input.txt"
        if not input_path.exists():
            self.log_error("Файл my_input.txt не знайдено для початкового завантаження.")
            return

        try:
            lines: list[str] = []
            with input_path.open(encoding="utf-8") as fh:
                for _ in range(3):
                    line = fh.readline()
                    if not line:
                        break
                    lines.append(line.rstrip("\n"))
        except OSError as exc:  # pragma: no cover - залежить від файлової системи
            self.log_error(f"Не вдалося прочитати my_input.txt: {exc}")
            return

        if lines:
            self.main_text.setPlainText("\n".join(lines))
            self.log_info("Завантажено перші три рядки з my_input.txt.")

    def _collect_inputs(self) -> dict[str, object]:
        """Validate user inputs and prepare pipeline arguments."""
        try:
            ua_index = int(self.combo_useragent.currentText())
            cookie_index = int(self.combo_cookies.currentText())
        except ValueError:
            raise ValueError("Некоректні числові значення індексів User Agent або Cookies.")

        text = self.main_text.toPlainText()
        if not text.strip():
            raise ValueError("Вхідний текст порожній. Додайте дані для парсингу.")

        remark_raw = self.remark_edit.toPlainText().strip()
        remark_indices = None
        if remark_raw:
            try:
                remark_indices = parse_remark_indices(remark_raw)
            except ValueError as exc:
                raise ValueError(f"Некоректні remark-індекси: {exc}") from exc

        return {
            "text": text,
            "ua_index": ua_index,
            "cookie_index": cookie_index,
            "remark_raw": remark_raw,
            "remark_indices": remark_indices,
        }

    def _build_pipeline(self, params: dict[str, object]):
        return build_pipeline_from_text(
            params["text"],
            ua_index=params["ua_index"],
            cookie_index=params["cookie_index"],
            remark_indices=params["remark_indices"],
        )

    def _display_first_record(self, pipeline) -> bool:
        try:
            raw_iter = pipeline.reader.read()
            first_raw = next(raw_iter)
        except StopIteration:
            self.info_text.clear()
            self.log_error("Не знайдено жодного рядка для парсингу.")
            return False
        except Exception as exc:  # pragma: no cover - GUI runtime error path
            self.info_text.clear()
            self.log_error(f"Помилка при читанні даних: {exc}")
            return False

        try:
            record = pipeline.parser.parse(first_raw)
        except Exception as exc:  # pragma: no cover - GUI runtime error path
            self.info_text.clear()
            self.log_error(f"Не вдалося розпарсити перший рядок: {exc}")
            return False

        separator = pipeline.parser.config.separator
        preview_rows = preview_first_row([first_raw.content], separator=separator)
        if not preview_rows:
            self.info_text.clear()
            self.log_error("Перший рядок порожній після обробки.")
            return False

        formatted_parts = "\n".join(f"[{index}] {value}" for index, value in preview_rows)
        details = [
            formatted_parts,
            "",
            f"UA: {record.ua or '(порожньо)'}",
            f"Cookie: {record.cookie or '(порожньо)'}",
            f"Remark: {record.remark or '(порожньо)'}",
        ]
        self.info_text.setPlainText("\n".join(details))
        return True

    def on_start_clicked(self):
        """Handle Start button: run pipeline and export data."""
        try:
            params = self._collect_inputs()
        except ValueError as exc:
            self.info_text.clear()
            self.log_error(str(exc))
            return

        pipeline = self._build_pipeline(params)

        self.UserSettings = {
            "user_agent": params["ua_index"],
            "cookies": params["cookie_index"],
            "remark": params["remark_raw"],
        }

        try:
            output_path = pipeline.run()
        except Exception as exc:  # pragma: no cover - GUI runtime error path
            self.info_text.clear()
            self.log_error(f"Не вдалося виконати парсинг: {exc}")
            return

        if self._display_first_record(pipeline):
            self.log_info("Відображено перший розпарсений рядок.")

        self.log_info(f"Збережено UserSettings: {self.UserSettings}")
        self.log_info(f"Файл створено: {output_path}")

    def on_test_clicked(self):
        """Handle Test button: preview the first parsed row without exporting."""
        try:
            params = self._collect_inputs()
        except ValueError as exc:
            self.info_text.clear()
            self.log_error(str(exc))
            return

        pipeline = self._build_pipeline(params)

        if self._display_first_record(pipeline):
            self.log_info("Успішно розпарсено перший рядок (без експорту).")


# ---------- Точка входу ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 12))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
