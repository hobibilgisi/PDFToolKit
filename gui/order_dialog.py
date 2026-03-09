"""
PDFToolKit - Dosya Sıralama Diyaloğu

Seçili dosyalara kullanıcının sıra numarası atamasını sağlar.
Her dosya hizasında bir metin kutusu ile numara girilir.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt


class OrderDialog(QDialog):
    """Dosya sıralama diyaloğu."""

    def __init__(self, files: list[dict], parent=None):
        """
        Args:
            files: [{"path": str, "pages": str, "order": int}, ...]
        """
        super().__init__(parent)
        self.setWindowTitle("🔢 Dosyaları Numaralandır / Sırala")
        self.setMinimumSize(550, 400)
        self.resize(600, 450)

        self._files = files
        self._order_inputs: list[QLineEdit] = []
        self._result: list[dict] | None = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Açıklama
        info = QLabel(
            "Her dosyanın yanındaki kutuya sıra numarası girin.\n"
            "Sıra numarasına göre dosyalar yeniden adlandırılacak ve\n"
            "her sayfanın sağ üst köşesine numara yazılacaktır."
        )
        info.setStyleSheet("color: #a6adc8; margin-bottom: 8px;")
        layout.addWidget(info)

        # Scroll alanı
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(6)

        # Başlık satırı
        header_layout = QHBoxLayout()
        header_sira = QLabel("Sıra")
        header_sira.setFixedWidth(60)
        header_sira.setStyleSheet("font-weight: bold; color: #89b4fa;")
        header_dosya = QLabel("Dosya Adı")
        header_dosya.setStyleSheet("font-weight: bold; color: #89b4fa;")
        header_sayfa = QLabel("Sayfa")
        header_sayfa.setFixedWidth(50)
        header_sayfa.setStyleSheet("font-weight: bold; color: #89b4fa;")
        header_layout.addWidget(header_sira)
        header_layout.addWidget(header_dosya, 1)
        header_layout.addWidget(header_sayfa)
        scroll_layout.addLayout(header_layout)

        # Dosya satırları
        for i, f in enumerate(self._files):
            row_layout = QHBoxLayout()

            order_input = QLineEdit()
            order_input.setFixedWidth(60)
            order_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            order_input.setPlaceholderText(str(i + 1))
            order_input.setStyleSheet(
                "background: #313244; color: #cdd6f4; border: 1px solid #45475a; "
                "border-radius: 4px; padding: 4px; font-size: 14px;"
            )
            self._order_inputs.append(order_input)

            src = Path(f["path"])
            name_label = QLabel(src.name)
            name_label.setToolTip(str(src))
            name_label.setStyleSheet("color: #cdd6f4;")

            # Sayfa sayısı
            page_count = "—"
            if src.suffix.lower() == ".pdf":
                try:
                    from core.pdf_metadata import get_metadata
                    metadata = get_metadata(src)
                    page_count = str(metadata["sayfa_sayisi"])
                except Exception:
                    page_count = "?"

            page_label = QLabel(page_count)
            page_label.setFixedWidth(50)
            page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page_label.setStyleSheet("color: #a6adc8;")

            row_layout.addWidget(order_input)
            row_layout.addWidget(name_label, 1)
            row_layout.addWidget(page_label)
            scroll_layout.addLayout(row_layout)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("İptal")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)

        apply_btn = QPushButton("🔢 Sırala ve Numaralandır")
        apply_btn.setObjectName("primaryButton")
        apply_btn.setFixedWidth(200)
        apply_btn.clicked.connect(self._on_apply)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

    def _on_apply(self):
        """Girilen sıra numaralarını doğrular ve sonucu hazırlar."""
        order_map: dict[int, int] = {}  # index -> sıra numarası

        for i, inp in enumerate(self._order_inputs):
            text = inp.text().strip()
            if not text:
                text = inp.placeholderText()  # Varsayılan sıra
            try:
                num = int(text)
                if num < 1:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(
                    self, "Hatalı Giriş",
                    f"'{text}' geçerli bir sıra numarası değil.\n"
                    f"Lütfen pozitif bir tam sayı girin."
                )
                inp.setFocus()
                return

            if num in order_map.values():
                # Aynı numarada başka dosya var
                QMessageBox.warning(
                    self, "Tekrarlayan Numara",
                    f"Sıra numarası {num} birden fazla dosyaya atanmış.\n"
                    f"Her dosyaya benzersiz bir numara verin."
                )
                inp.setFocus()
                return

            order_map[i] = num

        # Sonucu oluştur: sıra numarasına göre sıralı dosya listesi
        self._result = []
        for i, f in enumerate(self._files):
            self._result.append({
                "path": f["path"],
                "pages": f["pages"],
                "order_num": order_map[i]
            })

        # Sıra numarasına göre sırala
        self._result.sort(key=lambda x: x["order_num"])
        self.accept()

    def get_result(self) -> list[dict] | None:
        """Sıralama sonucunu döndürür. Diyalog iptal edildiyse None."""
        return self._result
