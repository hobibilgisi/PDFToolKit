"""
PDFToolKit - Tema & Stiller

PyQt6 için modern koyu tema CSS tanımları.
"""

DARK_THEME = """
/* ===== Ana Pencere ===== */
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

/* ===== Genel Widget ===== */
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}

/* ===== Butonlar ===== */
QPushButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: 1px solid #585b70;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 32px;
}

QPushButton:hover {
    background-color: #585b70;
    border-color: #89b4fa;
}

QPushButton:pressed {
    background-color: #313244;
}

QPushButton:disabled {
    background-color: #313244;
    color: #6c7086;
    border-color: #45475a;
}

/* ===== Birincil Buton ===== */
QPushButton#primaryButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #b4d0fb;
}

/* ===== Tehlike Butonu ===== */
QPushButton#dangerButton {
    background-color: #f38ba8;
    color: #1e1e2e;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #f5a3b8;
}

/* ===== Tablo ===== */
QTableWidget {
    background-color: #181825;
    alternate-background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    gridline-color: #313244;
    selection-background-color: #45475a;
    selection-color: #cdd6f4;
}

QTableWidget::item {
    padding: 6px 8px;
}

QHeaderView::section {
    background-color: #313244;
    color: #a6adc8;
    border: none;
    padding: 8px;
    font-weight: 600;
    border-bottom: 2px solid #89b4fa;
}

/* ===== Giriş Alanları ===== */
QLineEdit, QSpinBox, QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 6px 10px;
    min-height: 28px;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #89b4fa;
}

/* ===== Tablo İçi Özel Sayfa Girişi ===== */
QLineEdit#pageInput {
    background-color: #24273a;
    border: 1px solid #45475a;
    border-radius: 3px;
    padding: 2px 5px;
    min-height: 22px;
    font-size: 12px;
    color: #b4befe;
}

QLineEdit#pageInput:focus {
    border-color: #89b4fa;
    background-color: #313244;
}

/* ===== Tablo İçi ↑↓ Butonları ===== */
QPushButton#arrowButton {
    background-color: #313244;
    color: #89b4fa;
    border: 1px solid #45475a;
    border-radius: 3px;
    padding: 0px;
    min-height: 20px;
    min-width: 24px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#arrowButton:hover {
    background-color: #45475a;
    color: #b4befe;
    border-color: #89b4fa;
}

QPushButton#arrowButton:pressed {
    background-color: #1e1e2e;
    color: #cba6f7;
}

/* ===== ComboBox Dropdown ===== */
QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    selection-background-color: #45475a;
}

/* ===== Checkbox ===== */
QCheckBox {
    spacing: 8px;
    color: #cdd6f4;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #585b70;
    border-radius: 4px;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

/* ===== Grup Kutusu ===== */
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
    color: #a6adc8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 12px;
    color: #89b4fa;
}

/* ===== Durum Çubuğu ===== */
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
    padding: 4px;
}

/* ===== Scroll Bar ===== */
QScrollBar:vertical {
    background-color: #181825;
    width: 10px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #181825;
    height: 10px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 5px;
    min-width: 30px;
}

/* ===== Menü ===== */
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
}

QMenuBar::item:selected {
    background-color: #313244;
}

QMenu {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
}

QMenu::item:selected {
    background-color: #45475a;
}

/* ===== Label ===== */
QLabel {
    color: #cdd6f4;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: 700;
    color: #89b4fa;
}

QLabel#subtitleLabel {
    font-size: 12px;
    color: #a6adc8;
}

/* ===== Progress Bar ===== */
QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #cdd6f4;
    min-height: 20px;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 4px;
}

/* ===== Splitter ===== */
QSplitter::handle {
    background-color: #313244;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #89b4fa;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #45475a;
    color: #89b4fa;
    border-bottom: 2px solid #89b4fa;
}
"""
