"""
PDFToolKit - Durum Çubuğu Bileşeni

İşlem durumunu ve mesajları gösterir.
"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar
from PyQt6.QtCore import QTimer


class StatusBar(QStatusBar):
    """Özel durum çubuğu: mesaj gösterimi ve ilerleme çubuğu."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Kalıcı mesaj etiketi
        self.status_label = QLabel("Hazır")
        self.addWidget(self.status_label, 1)

        # İlerleme çubuğu (varsayılan gizli)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setVisible(False)
        self.addPermanentWidget(self.progress_bar)

        # Dosya sayacı
        self.file_count_label = QLabel("")
        self.addPermanentWidget(self.file_count_label)

    def show_message(self, message: str, timeout_ms: int = 5000):
        """Geçici bir mesaj gösterir."""
        self.status_label.setText(message)
        if timeout_ms > 0:
            QTimer.singleShot(timeout_ms, self._reset_status)

    def show_error(self, message: str):
        """Hata mesajı gösterir (kırmızı)."""
        self.status_label.setStyleSheet("color: #f38ba8;")
        self.status_label.setText(f"❌ {message}")
        self.hide_progress()
        QTimer.singleShot(8000, self._reset_status)

    def show_success(self, message: str):
        """Başarı mesajı gösterir (yeşil)."""
        self.status_label.setStyleSheet("color: #a6e3a1;")
        self.status_label.setText(f"✅ {message}")
        QTimer.singleShot(5000, self._reset_status)

    def _reset_status(self):
        """Durum çubuğunu varsayılan haline sıfırlar."""
        self.status_label.setStyleSheet("")
        self.status_label.setText("Hazır")

    def show_progress(self, value: int, maximum: int = 100):
        """İlerleme çubuğunu gösterir ve günceller."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def hide_progress(self):
        """İlerleme çubuğunu gizler."""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def update_file_count(self, count: int):
        """Dosya sayacını günceller."""
        self.file_count_label.setText(f"📄 {count} dosya")
