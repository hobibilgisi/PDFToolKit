"""
PDFToolKit - Uygulama Giriş Noktası

Bu dosya uygulamayı başlatır.
Kullanım: python main.py
"""

import sys
import os

# Proje kök dizinini PYTHONPATH'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QProxyStyle, QStyle
from PyQt6.QtGui import QFont
from gui.main_window import MainWindow


def main():
    """Uygulamayı başlatır."""
    app = QApplication(sys.argv)

    # Uygulama bilgileri
    app.setApplicationName("PDFToolKit")
    app.setApplicationVersion("0.2.0")

    # Varsayılan font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Tooltip anında açılsın (varsayılan ~700ms gecikmeyi kaldır)
    app.setStyleSheet("QToolTip { padding: 6px; }")
    os.environ["QT_TOOLTIP_DELAY"] = "0"

    class InstantTooltipStyle(QProxyStyle):
        def styleHint(self, hint, option=None, widget=None, returnData=None):
            if hint == QStyle.StyleHint.SH_ToolTip_WakeUpDelay:
                return 0
            if hint == QStyle.StyleHint.SH_ToolTip_FallAsleepDelay:
                return 0
            return super().styleHint(hint, option, widget, returnData)

    app.setStyle(InstantTooltipStyle())

    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
