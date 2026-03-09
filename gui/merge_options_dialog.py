"""
PDFToolKit — PDF Birleştirme Seçenekleri Diyaloğu

Birleştirme öncesinde kullanıcıya sorar:
  • Dosya sıralaması (sürükle-bırak veya yukarı/aşağı)
  • Opsiyonel sayfa numaralandırma
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QListWidget, QListWidgetItem, QCheckBox,
    QSpinBox, QAbstractItemView, QRadioButton,
)
from PyQt6.QtCore import Qt

from gui.icons import icon


class MergeOptionsDialog(QDialog):
    """
    PDF birleştirme öncesi sıralama ve numaralandırma diyaloğu.
    """

    def __init__(self, files: list[dict], parent=None):
        """
        Args:
            files: [{"path": str, "pages": str|None}, ...]
        """
        super().__init__(parent)
        self.setWindowTitle("Birleştirme Seçenekleri")
        self.setMinimumSize(550, 420)
        self.resize(600, 480)

        self._files = list(files)
        self._result_files: list[dict] | None = None
        self._add_page_numbers: bool = False
        self._start_number: int = 1
        self._numbering_mode: str = "sequential"

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Üst bilgi
        info = QLabel(
            f"{len(self._files)} PDF dosyası birleştirilecek.\n"
            "Dosyaları istediğiniz sıraya getirin, ardından birleştirin."
        )
        info.setStyleSheet("color: #cdd6f4; font-size: 14px; margin-bottom: 8px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # ── Sıralama ──
        order_group = QGroupBox("Sayfa Sıralaması")
        order_group.setStyleSheet(
            "QGroupBox { color: #89b4fa; border: 1px solid #45475a; "
            "border-radius: 6px; margin-top: 8px; padding-top: 16px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }"
        )
        order_layout = QVBoxLayout(order_group)

        order_info = QLabel(
            "Sürükleyerek veya ▲/▼ butonlarıyla sırayı değiştirin:"
        )
        order_info.setStyleSheet("color: #a6adc8; font-size: 12px;")
        order_layout.addWidget(order_info)

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

        for f in self._files:
            p = Path(f["path"])
            label = p.name
            if f.get("pages"):
                label += f"  [sayfa: {f['pages']}]"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, f)
            item.setToolTip(str(p))
            self._file_list.addItem(item)

        list_and_buttons.addWidget(self._file_list, 1)

        btn_col = QVBoxLayout()
        btn_col.addStretch()

        up_btn = QPushButton("▲")
        up_btn.setFixedSize(36, 36)
        up_btn.setToolTip("Yukarı taşı")
        up_btn.clicked.connect(self._move_up)
        btn_col.addWidget(up_btn)

        down_btn = QPushButton("▼")
        down_btn.setFixedSize(36, 36)
        down_btn.setToolTip("Aşağı taşı")
        down_btn.clicked.connect(self._move_down)
        btn_col.addWidget(down_btn)

        btn_col.addStretch()
        list_and_buttons.addLayout(btn_col)
        order_layout.addLayout(list_and_buttons)
        layout.addWidget(order_group)

        # ── Numaralandırma ──
        numbering_group = QGroupBox("Numaralandırma")
        numbering_group.setStyleSheet(
            "QGroupBox { color: #89b4fa; border: 1px solid #45475a; "
            "border-radius: 6px; margin-top: 8px; padding-top: 16px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }"
        )
        numbering_group_layout = QVBoxLayout(numbering_group)

        # Checkbox
        top_row = QHBoxLayout()
        self._numbering_check = QCheckBox("Sayfalara numara ekle")
        self._numbering_check.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        self._numbering_check.setToolTip(
            "Birleşik PDF'in her sayfasının sağ üst köşesine sayfa numarası yazılır"
        )
        top_row.addWidget(self._numbering_check)

        self._start_label = QLabel("Başlangıç:")
        self._start_label.setStyleSheet("color: #a6adc8; font-size: 12px;")
        self._start_spin = QSpinBox()
        self._start_spin.setMinimum(1)
        self._start_spin.setMaximum(9999)
        self._start_spin.setValue(1)
        self._start_spin.setFixedWidth(70)
        self._start_spin.setStyleSheet(
            "background: #313244; color: #cdd6f4; border: 1px solid #45475a; "
            "border-radius: 4px; padding: 2px;"
        )
        top_row.addWidget(self._start_label)
        top_row.addWidget(self._start_spin)
        top_row.addStretch()
        numbering_group_layout.addLayout(top_row)

        # Numbering mode radio buttons
        radio_style = "color: #cdd6f4; font-size: 12px; margin-left: 20px;"
        self._radio_sequential = QRadioButton(
            "Ardışık numaralandır (1, 2, 3, 4 …)"
        )
        self._radio_sequential.setStyleSheet(radio_style)
        self._radio_sequential.setChecked(True)

        self._radio_per_document = QRadioButton(
            "Dosya bazlı numaralandır (dosya 1 → 1, dosya 2 → 2 …)"
        )
        self._radio_per_document.setStyleSheet(radio_style)

        numbering_group_layout.addWidget(self._radio_sequential)
        numbering_group_layout.addWidget(self._radio_per_document)

        # Başlangıçta gizle
        self._start_label.setVisible(False)
        self._start_spin.setVisible(False)
        self._radio_sequential.setVisible(False)
        self._radio_per_document.setVisible(False)

        def _toggle_numbering_ui(checked):
            self._start_label.setVisible(checked)
            self._start_spin.setVisible(checked)
            self._radio_sequential.setVisible(checked)
            self._radio_per_document.setVisible(checked)

        self._numbering_check.toggled.connect(_toggle_numbering_ui)

        layout.addWidget(numbering_group)

        # ── Alt butonlar ──
        layout.addStretch()
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("İptal")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)

        ok_btn = QPushButton("Birleştir")
        ok_btn.setIcon(icon("merge"))
        ok_btn.setObjectName("primaryButton")
        ok_btn.setFixedWidth(160)
        ok_btn.clicked.connect(self._on_accept)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    # ── İşlevler ─────────────────────────────────────────────────────────

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
        self._result_files = []
        for i in range(self._file_list.count()):
            item = self._file_list.item(i)
            self._result_files.append(item.data(Qt.ItemDataRole.UserRole))

        self._add_page_numbers = self._numbering_check.isChecked()
        self._start_number = self._start_spin.value()
        self._numbering_mode = (
            "per_document" if self._radio_per_document.isChecked() else "sequential"
        )
        self.accept()

    # ── Sonuç Erişim ─────────────────────────────────────────────────────

    def get_ordered_files(self) -> list[dict] | None:
        """Kullanıcının sıraladığı dosya listesi. İptal → None."""
        return self._result_files

    def should_add_page_numbers(self) -> bool:
        return self._add_page_numbers

    def get_start_number(self) -> int:
        return self._start_number

    def get_numbering_mode(self) -> str:
        """'sequential' veya 'per_document' döner."""
        return self._numbering_mode
