"""
PDFToolKit - Arka Plan İşlem Worker'ı

PDF işlemlerini ana UI thread'inden ayırarak GUI donmasını önler.
QThread tabanlı çalışır, progress ve sonuç sinyalleri yayar.

Not: Word/Excel→PDF dönüşümlerinde COM (pywin32) kullanılır.
Windows COM, her thread'de ayrıca başlatılmalıdır; her iki worker
da CoInitialize/CoUninitialize çağrılarıyla bunu sağlar.
"""

import sys
from typing import Any, Callable
from PyQt6.QtCore import QThread, pyqtSignal
from utils.logger import get_logger

logger = get_logger(__name__)


def _com_init():
    """COM'u mevcut thread için başlatır (sadece Windows'ta)."""
    if sys.platform == "win32":
        try:
            import pythoncom
            pythoncom.CoInitialize()
            return True
        except ImportError:
            pass
    return False


def _com_uninit():
    """COM'u mevcut thread için sonlandırır (sadece Windows'ta)."""
    if sys.platform == "win32":
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except ImportError:
            pass


class PdfWorker(QThread):
    """
    PDF işlemlerini arka planda çalıştıran thread.

    Sinyaller:
        progress(int, str): İlerleme yüzdesi (0-100) ve durum mesajı.
        finished(object): İşlem sonucu (Path veya list[Path]).
        error(str): Hata mesajı.
    """

    progress = pyqtSignal(int, str)       # (yüzde, mesaj)
    finished = pyqtSignal(object)          # sonuç
    error = pyqtSignal(str)               # hata mesajı

    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any):
        """
        Args:
            func: Çalıştırılacak fonksiyon (core/converters modülünden).
            *args: Fonksiyona iletilecek konumsal argümanlar.
            **kwargs: Fonksiyona iletilecek anahtar argümanlar.
        """
        super().__init__()
        self._func = func
        self._args: tuple[Any, ...] = args
        self._kwargs: dict[str, Any] = kwargs

    def run(self) -> None:
        """Fonksiyonu arka planda çalıştırır."""
        _com_init()
        try:
            self.progress.emit(0, "İşlem başlatılıyor...")
            result = self._func(*self._args, **self._kwargs)
            self.progress.emit(100, "Tamamlandı")
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Worker hatası: {e}")
            self.error.emit(str(e))
        finally:
            _com_uninit()


class BatchWorker(QThread):
    """
    Birden fazla dosya üzerinde aynı işlemi sırayla çalıştıran thread.

    Sinyaller:
        progress(int, str): İlerleme yüzdesi ve durum mesajı.
        finished(list): Başarılı sonuçların listesi.
        error(str): Hata mesajı (bireysel dosya hataları toplanır).
    """

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, func: Callable[..., Any], file_args_list: list[dict[str, Any]]):
        """
        Args:
            func: Her dosya için çalıştırılacak fonksiyon.
            file_args_list: Her dosya için argüman dict listesi.
                [{"args": (arg1,), "kwargs": {...}}, ...]
        """
        super().__init__()
        self._func = func
        self._file_args_list = file_args_list

    def run(self) -> None:
        """Tüm dosyalar üzerinde sırayla işlem yapar."""
        _com_init()
        results: list[Any] = []
        errors: list[str] = []
        total = len(self._file_args_list)

        for i, item in enumerate(self._file_args_list):
            args: tuple[Any, ...] = item.get("args", ())
            kwargs: dict[str, Any] = item.get("kwargs", {})
            label: str = item.get("label", f"Dosya {i + 1}")

            percent = int((i / total) * 100)
            self.progress.emit(percent, f"{label} işleniyor... ({i + 1}/{total})")

            try:
                result = self._func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                errors.append(f"{label}: {e}")
                logger.error(f"Batch hatası — {label}: {e}")

        if errors:
            self.error.emit(
                f"{len(errors)} dosyada hata:\n" + "\n".join(errors)
            )
        else:
            self.progress.emit(100, f"{len(results)}/{total} dosya işlendi")
            self.finished.emit(results)
        _com_uninit()
