"""
PDFToolKit - Konfigürasyon Yönetimi

.env dosyasından ortam değişkenlerini okur ve uygulama genelinde
tek bir Settings nesnesi üzerinden erişim sağlar (Singleton pattern).
"""

import os
import sys
import ctypes
from pathlib import Path
from dotenv import load_dotenv


def _get_base_dir() -> Path:
    """Uygulama kök dizinini döndürür. EXE ise EXE'nin klasörü, değilse proje kökü."""
    if getattr(sys, 'frozen', False):
        # Nuitka veya PyInstaller ile paketlenmiş EXE
        return Path(sys.executable).resolve().parent
    else:
        # Geliştirme ortamı
        return Path(__file__).resolve().parent.parent


def _hide_folder_windows(folder_path: Path):
    """Windows'ta klasörü gizli yapar."""
    try:
        if sys.platform == "win32":
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(str(folder_path), FILE_ATTRIBUTE_HIDDEN)
    except Exception:
        pass


class Settings:
    """Uygulama konfigürasyonu. Singleton pattern ile tek bir örnek oluşturulur."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Proje kök dizini
        self.base_dir = _get_base_dir()

        # .env dosyasını yükle
        env_path = self.base_dir / ".env"
        load_dotenv(dotenv_path=env_path)

        # Gizli veri klasörü (.pdf_data)
        data_dir = self.base_dir / ".pdf_data"
        data_dir.mkdir(parents=True, exist_ok=True)
        _hide_folder_windows(data_dir)

        # Giriş/Çıkış Dizinleri
        self.input_dir = data_dir / os.getenv("PDF_INPUT_DIR", "input")
        self.output_dir = data_dir / os.getenv("PDF_OUTPUT_DIR", "output")

        # Loglama
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        # Harici araç yolları — önce .env, sonra gömülü Tesseract
        self.tesseract_path = os.getenv("TESSERACT_PATH", "")
        self._detect_bundled_tesseract()

        # Güncelleme kontrol ayarları
        self.skipped_update_version = os.getenv("SKIPPED_UPDATE_VERSION", "")

        # Dizinlerin var olduğundan emin ol
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _detect_bundled_tesseract(self):
        """
        EXE modunda: yanındaki tesseract/ klasörünü otomatik algılar.
        .env'de TESSERACT_PATH zaten tanımlıysa ona dokunmaz.
        """
        if self.tesseract_path:
            # .env ile açıkça belirtilmiş, üzerine yazma
            return

        if getattr(sys, 'frozen', False):
            # EXE modunda: EXE'nin yanındaki tesseract/ klasörü
            bundled_exe = self.base_dir / "tesseract" / "tesseract.exe"
            if bundled_exe.exists():
                self.tesseract_path = str(bundled_exe)
                os.environ["TESSDATA_PREFIX"] = str(
                    self.base_dir / "tesseract" / "tessdata"
                )
        else:
            # Geliştirme ortamında: proje kökündeki tesseract/ klasörünü dene
            dev_bundled = self.base_dir / "tesseract" / "tesseract.exe"
            if dev_bundled.exists():
                self.tesseract_path = str(dev_bundled)
                os.environ["TESSDATA_PREFIX"] = str(
                    self.base_dir / "tesseract" / "tessdata"
                )

    def set_skipped_version(self, version: str):
        """Belirtilen sürümü 'atla' listesine ekler (.env dosyasına yazar)."""
        self.skipped_update_version = version
        env_path = self.base_dir / ".env"
        try:
            # Mevcut .env içeriğini oku, SKIPPED_UPDATE_VERSION satırını güncelle
            lines = []
            found = False
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("SKIPPED_UPDATE_VERSION="):
                            lines.append(f"SKIPPED_UPDATE_VERSION={version}\n")
                            found = True
                        else:
                            lines.append(line)
            if not found:
                lines.append(f"SKIPPED_UPDATE_VERSION={version}\n")
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception:
            pass  # Yazma hatası sessizce geçilir

    def __repr__(self):
        return (
            f"Settings(\n"
            f"  base_dir={self.base_dir},\n"
            f"  input_dir={self.input_dir},\n"
            f"  output_dir={self.output_dir},\n"
            f"  log_level={self.log_level},\n"
            f"  tesseract_path={self.tesseract_path!r}\n"
            f")"
        )


# Modül seviyesinde kolay erişim
settings = Settings()
