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
from PyQt6.QtGui import QFont, QIcon
from gui.main_window import MainWindow
from gui.splash_screen import SplashScreen
from config import __version__


def main():
    """Uygulamayı başlatır."""
    app = QApplication(sys.argv)

    # Uygulama bilgileri
    app.setApplicationName("PDFToolKit")
    app.setApplicationVersion(__version__)

    # Uygulama ikonu
    from pathlib import Path
    icon_path = Path(__file__).parent / "assets" / "icon.ico"
    if not icon_path.exists():
        icon_path = Path(sys.executable).parent / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

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

    # Splash screen göster → bitince ana pencereyi aç
    splash = SplashScreen()

    def show_main_window():
        window = MainWindow()
        window.show()
        # splash kapandıktan sonra window GC'ye gitmesin
        app._main_window = window

    splash.start(on_finished=show_main_window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
