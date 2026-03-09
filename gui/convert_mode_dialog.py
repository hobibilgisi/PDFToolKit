"""
PDFToolKit — Dönüştürme Modu Diyaloğu

Çoklu dosya dönüştürme işlemlerinde kullanıcıya sorar:
  • Ayrı ayrı dönüştür (her dosya → ayrı PDF)
  • Tek PDF olarak birleştir (sıralama + opsiyonel numaralandırma)
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QGroupBox, QScrollArea,
    QWidget, QCheckBox, QSpinBox, QListWidget, QListWidgetItem,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt

from gui.icons import icon


class ConvertModeDialog(QDialog):
    """
    Çoklu dosya dönüştürme modu seçim diyaloğu.

    Kullanıcıya iki seçenek sunar:
      1) Ayrı ayrı dönüştür
      2) Tek PDF olarak birleştir  →  sıralama + sayfa numaralandırma seçenekleri
    """

    MODE_SEPARATE = "separate"
    MODE_MERGE = "merge"

    def __init__(self, file_paths: list[str], file_type_label: str = "dosya", parent=None):
        """
        Args:
            file_paths: Dönüştürülecek dosya yolları listesi.
            file_type_label: Dosya türü etiketi (ör: "görsel", "Word", "Excel").
        """
        super().__init__(parent)
        self.setWindowTitle("Dönüştürme Modu")
        self.setMinimumSize(550, 420)
        self.resize(600, 500)

        self._file_paths = list(file_paths)
        self._file_type_label = file_type_label
        self._mode: str | None = None
        self._ordered_paths: list[str] | None = None
        self._add_page_numbers: bool = False

        self._setup_ui()

    # ── UI ────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Üst bilgi
        count = len(self._file_paths)
        info = QLabel(
            f"{count} adet {self._file_type_label} seçtiniz.\n"
            f"Bu dosyaları nasıl dönüştürmek istiyorsunuz?"
        )
        info.setStyleSheet("color: #cdd6f4; font-size: 14px; margin-bottom: 8px;")
        layout.addWidget(info)

        # ── Mod seçimi ──
        self._mode_group = QButtonGroup(self)

        self._radio_separate = QRadioButton(
            f"Her {self._file_type_label} dosyasını ayrı PDF olarak dönüştür"
        )
        self._radio_separate.setChecked(True)
        self._radio_separate.setStyleSheet("color: #cdd6f4; font-size: 13px;")

        self._radio_merge = QRadioButton(
            "Hepsini tek PDF olarak birleştir"
        )
        self._radio_merge.setStyleSheet("color: #cdd6f4; font-size: 13px;")

        self._mode_group.addButton(self._radio_separate, 0)
        self._mode_group.addButton(self._radio_merge, 1)

        layout.addWidget(self._radio_separate)
        layout.addWidget(self._radio_merge)

        # ── Birleştirme seçenekleri (başlangıçta gizli) ──
        self._merge_options = QGroupBox("Birleştirme Seçenekleri")
        self._merge_options.setStyleSheet(
            "QGroupBox { color: #89b4fa; border: 1px solid #45475a; "
            "border-radius: 6px; margin-top: 8px; padding-top: 16px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }"
        )
        merge_layout = QVBoxLayout(self._merge_options)

        # Sıralama açıklaması
        order_info = QLabel(
            "Dosyaları sürükleyerek veya yukarı/aşağı butonlarıyla "
            "istediğiniz sıraya getirin:"
        )
        order_info.setStyleSheet("color: #a6adc8; font-size: 12px;")
        order_info.setWordWrap(True)
        merge_layout.addWidget(order_info)

        # Dosya listesi (sürükle-bırak sıralama)
        list_and_buttons = QHBoxLayout()

        self._file_list = QListWidget()
        self._file_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._file_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._file_list.setStyleSheet(
            "QListWidget { background: #1e1e2e; color: #cdd6f4; "
            "border: 1px solid #45475a; border-radius: 4px; }"
            "QListWidget::item { padding: 4px 8px; }"
            "QListWidget::item:selected { background: #45475a; }"
        )
        for p in self._file_paths:
            item = QListWidgetItem(Path(p).name)
            item.setData(Qt.ItemDataRole.UserRole, p)
            item.setToolTip(p)
            self._file_list.addItem(item)

        list_and_buttons.addWidget(self._file_list, 1)

        # Yukarı/aşağı butonları
        btn_col = QVBoxLayout()
        btn_col.addStretch()

        self._up_btn = QPushButton("▲")
        self._up_btn.setFixedSize(36, 36)
        self._up_btn.setToolTip("Seçili dosyayı yukarı taşı")
        self._up_btn.clicked.connect(self._move_up)
        btn_col.addWidget(self._up_btn)

        self._down_btn = QPushButton("▼")
        self._down_btn.setFixedSize(36, 36)
        self._down_btn.setToolTip("Seçili dosyayı aşağı taşı")
        self._down_btn.clicked.connect(self._move_down)
        btn_col.addWidget(self._down_btn)

        btn_col.addStretch()
        list_and_buttons.addLayout(btn_col)

        merge_layout.addLayout(list_and_buttons)

        # Numaralandırma seçeneği
        numbering_layout = QHBoxLayout()
        self._numbering_check = QCheckBox("Sayfalara numara ekle")
        self._numbering_check.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        self._numbering_check.setToolTip(
            "Her sayfanın sağ üst köşesine sayfa numarası yazılır"
        )
        numbering_layout.addWidget(self._numbering_check)

        self._start_num_label = QLabel("Başlangıç:")
        self._start_num_label.setStyleSheet("color: #a6adc8; font-size: 12px;")
        self._start_num_spin = QSpinBox()
        self._start_num_spin.setMinimum(1)
        self._start_num_spin.setMaximum(9999)
        self._start_num_spin.setValue(1)
        self._start_num_spin.setFixedWidth(70)
        self._start_num_spin.setStyleSheet(
            "background: #313244; color: #cdd6f4; border: 1px solid #45475a; "
            "border-radius: 4px; padding: 2px;"
        )
        numbering_layout.addWidget(self._start_num_label)
        numbering_layout.addWidget(self._start_num_spin)
        numbering_layout.addStretch()

        merge_layout.addLayout(numbering_layout)

        # Başlangıçta numaralandırma kontrollerini gizle
        self._start_num_label.setVisible(False)
        self._start_num_spin.setVisible(False)
        self._numbering_check.toggled.connect(self._on_numbering_toggled)

        layout.addWidget(self._merge_options)
        self._merge_options.setVisible(False)

        # Radio değiştiğinde birleştirme panelini göster/gizle
        self._radio_merge.toggled.connect(self._on_mode_changed)

        # ── Alt butonlar ──
        layout.addStretch()
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("İptal")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)

        self._ok_btn = QPushButton("Dönüştür")
        self._ok_btn.setIcon(icon("jpg_to_pdf"))
        self._ok_btn.setObjectName("primaryButton")
        self._ok_btn.setFixedWidth(160)
        self._ok_btn.clicked.connect(self._on_accept)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self._ok_btn)
        layout.addLayout(btn_layout)

    # ── Sinyal Bağlantıları ──────────────────────────────────────────────

    def _on_mode_changed(self, merge_checked: bool):
        self._merge_options.setVisible(merge_checked)
        # Dialog boyutunu güncelle
        self.adjustSize()

    def _on_numbering_toggled(self, checked: bool):
        self._start_num_label.setVisible(checked)
        self._start_num_spin.setVisible(checked)

    def _move_up(self):
        row = self._file_list.currentRow()
        if row <= 0:
            return
        item = self._file_list.takeItem(row)
        self._file_list.insertItem(row - 1, item)
        self._file_list.setCurrentRow(row - 1)

    def _move_down(self):
        row = self._file_list.currentRow()
        if row < 0 or row >= self._file_list.count() - 1:
            return
        item = self._file_list.takeItem(row)
        self._file_list.insertItem(row + 1, item)
        self._file_list.setCurrentRow(row + 1)

    def _on_accept(self):
        if self._radio_merge.isChecked():
            self._mode = self.MODE_MERGE
            # Listedeki sıraya göre yolları al
            self._ordered_paths = []
            for i in range(self._file_list.count()):
                item = self._file_list.item(i)
                self._ordered_paths.append(item.data(Qt.ItemDataRole.UserRole))
            self._add_page_numbers = self._numbering_check.isChecked()
        else:
            self._mode = self.MODE_SEPARATE
            self._ordered_paths = list(self._file_paths)
            self._add_page_numbers = False

        self.accept()

    # ── Sonuç Erişim ─────────────────────────────────────────────────────

    def get_mode(self) -> str | None:
        """Seçilen mod: MODE_SEPARATE veya MODE_MERGE. İptal → None."""
        return self._mode

    def get_ordered_paths(self) -> list[str]:
        """Kullanıcının belirlediği sıraya göre dosya yolları."""
        return self._ordered_paths or list(self._file_paths)

    def should_add_page_numbers(self) -> bool:
        """Sayfa numaralandırma istenip istenmediği."""
        return self._add_page_numbers

    def get_start_number(self) -> int:
        """Numaralandırma başlangıç değeri."""
        return self._start_num_spin.value()
