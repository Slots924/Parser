import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from parser_app.services.pipeline_builder import build_pipeline_from_text, parse_remark_indices


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

    def center_on_screen(self):
        """Центрує вікно по екрану."""
        rect = self.frameGeometry()
        center = QApplication.primaryScreen().availableGeometry().center()
        rect.moveCenter(center)
        self.move(rect.topLeft())

    def on_start_clicked(self):
        """При натисканні Start — зчитуємо налаштування користувача."""
        ua_index = int(self.combo_useragent.currentText())
        cookie_index = int(self.combo_cookies.currentText())
        remark_raw = self.remark_edit.toPlainText().strip()

        remark_indices = None
        if remark_raw:
            try:
                remark_indices = parse_remark_indices(remark_raw)
            except ValueError as exc:
                self.log_text.append(f"[ERROR] Некоректні remark-індекси: {exc}")
                return

        text = self.main_text.toPlainText()
        if not text.strip():
            self.log_text.append("[WARN] Введіть текст для парсингу перед стартом.")
            return

        try:
            pipeline = build_pipeline_from_text(
                text,
                ua_index=ua_index,
                cookie_index=cookie_index,
                remark_indices=remark_indices,
            )
            output_path = pipeline.run()
        except Exception as exc:  # pragma: no cover - GUI runtime error path
            self.log_text.append(f"[ERROR] Не вдалося виконати парсинг: {exc}")
            return

        self.UserSettings = {
            "user_agent": ua_index,
            "cookies": cookie_index,
            "remark": remark_raw,
        }
        self.log_text.append(f"[INFO] Збережено UserSettings: {self.UserSettings}")
        self.log_text.append(f"[INFO] Файл створено: {output_path}")

    def on_test_clicked(self):
        """
        Тимчасова заглушка:
        При натисканні 'Test' має розпарситись перший рядок масиву даних.
        Наразі просто показує приклад форматування у правому вікні.
        """
        parsed_example = "[1] Jon\n[2] email\n[3] Cookie"
        self.info_text.setPlainText(parsed_example)
        self.log_text.append("[DEBUG] Виконано тестове парсення (приклад).")


# ---------- Точка входу ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 12))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())