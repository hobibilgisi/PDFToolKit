"""
PDFToolKit - Güncelleme Denetleyici

GitHub Releases API üzerinden yeni sürüm kontrolü yapar.
İndirme ve self-replace mantığını içerir.

Kullanım (QThread içinden çağrılır, UI'ya sinyal gönderir):
    from utils.updater import UpdateChecker
    checker = UpdateChecker(current_version="0.2.0", owner="KULLANICI", repo="PDFToolKit")
    checker.update_available.connect(self._on_update_available)
    checker.start()
"""

import sys
import shutil
import tempfile
import zipfile
import urllib.request
import urllib.error
import json
from collections.abc import Callable
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from utils.logger import get_logger

logger = get_logger(__name__)

# ─── GitHub Repo Bilgileri ──────────────────────────────────────────────────
GITHUB_OWNER = "hobibilgisi"
GITHUB_REPO  = "PDFToolKit"
# ────────────────────────────────────────────────────────────────────────────


def _version_tuple(v: str) -> tuple[int, ...]:
    """'1.2.3' → (1, 2, 3) — sürüm karşılaştırması için."""
    try:
        return tuple(int(x) for x in v.strip().lstrip("v").split("."))
    except ValueError:
        return (0,)


def check_for_update(current_version: str) -> tuple[str | None, str | None]:
    """
    GitHub Releases'daki son sürümü kontrol eder.

    Returns:
        (latest_version, zip_download_url) — yeni sürüm varsa
        (None, None)                        — güncel veya hata varsa
    """
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"PDFToolKit/{current_version}"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        latest_tag = data.get("tag_name", "").lstrip("v")
        if not latest_tag:
            return None, None

        if _version_tuple(latest_tag) > _version_tuple(current_version):
            # ZIP asset'ini bul
            assets = data.get("assets", [])
            zip_url = None
            for asset in assets:
                name: str = asset.get("name", "")
                if name.endswith(".zip") and "PDFToolKit" in name:
                    zip_url = asset.get("browser_download_url")
                    break
            # Asset yoksa release sayfasının kendisini döndür
            if not zip_url:
                zip_url = data.get("html_url", "")
            return latest_tag, zip_url

    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as e:
        logger.debug(f"Güncelleme kontrolü başarısız (internet?: {e})")

    return None, None


def download_update(zip_url: str, progress_callback: Callable[[int, int], None] | None = None) -> Path | None:
    """
    Güncelleme ZIP'ini geçici dizine indirir.

    Args:
        zip_url: GitHub asset indirme bağlantısı.
        progress_callback: (bytes_downloaded, total_bytes) → None

    Returns:
        İndirilen ZIP dosyasının yolu veya None (hata durumunda).
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="pdftoolkit_update_"))
    zip_path = tmp_dir / "update.zip"

    try:
        req = urllib.request.Request(
            zip_url,
            headers={"User-Agent": "PDFToolKit-Updater"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 65536  # 64 KB

            with open(zip_path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total)

        logger.info(f"Güncelleme indirildi: {zip_path} ({downloaded} bayt)")
        return zip_path

    except Exception as e:
        logger.error(f"İndirme hatası: {e}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return None


def apply_update(zip_path: Path) -> bool:
    """
    İndirilen ZIP'ten TÜM uygulama dosyalarını günceller.
    Nuitka standalone çıktısı yüzlerce DLL/.pyd içerdiğinden
    sadece EXE değiştirmek yetmez.

    Strateji:
        1. ZIP'i geçici klasöre çıkart
        2. ZIP içindeki kök klasörü bul (PDFToolKit/)
        3. Mevcut EXE'yi .old olarak yedekle
        4. tesseract/ ve .pdf_data/ HARİÇ tüm dosyaları kopyala
        (Kullanıcı verileri korunur, sadece program dosyaları güncellenir.)

    Returns:
        True — başarılı, kullanıcıdan yeniden başlatma istenmeli.
        False — hata oluştu.
    """
    if not getattr(sys, 'frozen', False):
        logger.warning("apply_update yalnızca EXE modunda çalışır.")
        return False

    current_exe = Path(sys.executable).resolve()
    current_dir = current_exe.parent
    backup_exe  = current_dir / "PDFToolKit.exe.old"
    extract_dir = zip_path.parent / "extracted"

    # Güncelleme sırasında dokunulmayacak klasörler
    SKIP_DIRS = {"tesseract", ".pdf_data"}

    try:
        # Önceki .old varsa temizle
        if backup_exe.exists():
            backup_exe.unlink(missing_ok=True)

        # ZIP'i çıkart
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        # ZIP içindeki PDFToolKit/ kök klasörünü bul
        new_root = None
        for candidate in extract_dir.iterdir():
            if candidate.is_dir() and "PDFToolKit" in candidate.name:
                new_root = candidate
                break
        if not new_root:
            new_root = extract_dir

        # Yeni EXE var mı kontrol et
        new_exe = new_root / "PDFToolKit.exe"
        if not new_exe.exists():
            logger.error("ZIP içinde PDFToolKit.exe bulunamadı.")
            return False

        # Mevcut EXE'yi yedekle
        if current_exe.exists():
            current_exe.rename(backup_exe)

        # tesseract/ ve .pdf_data/ HARİÇ tüm dosyaları kopyala
        for item in new_root.rglob("*"):
            rel = item.relative_to(new_root)
            # Atlanan klasörlerdeki dosyaları geç
            if rel.parts and rel.parts[0] in SKIP_DIRS:
                continue
            dst = current_dir / rel
            if item.is_dir():
                dst.mkdir(parents=True, exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dst)

        logger.info("Güncelleme tamamlandı, yeniden başlatma gerekli.")
        return True

    except Exception as e:
        logger.error(f"Güncelleme uygulama hatası: {e}")
        # Yedekten geri yükle
        if backup_exe.exists() and not current_exe.exists():
            backup_exe.rename(current_exe)
        return False

    finally:
        # Geçici dosyaları temizle
        shutil.rmtree(extract_dir, ignore_errors=True)
        try:
            zip_path.unlink(missing_ok=True)
        except Exception:
            pass


def cleanup_old_exe():
    """
    Uygulama başlangıcında çağrılır.
    Önceki güncellemeden kalan .exe.old dosyasını sessizce siler.
    """
    if not getattr(sys, 'frozen', False):
        return
    old_backup = Path(sys.executable).with_suffix(".exe.old")
    if old_backup.exists():
        try:
            old_backup.unlink()
            logger.info("Eski EXE yedeği temizlendi.")
        except Exception:
            pass


# ─── QThread Tabanlı Güncelleme Kontrolcüsü ────────────────────────────────

class UpdateChecker(QThread):
    """
    Arka planda güncelleme kontrolü yapar, UI'yı sinyal ile bilgilendirir.

    Sinyaller:
        update_available(str, str): (yeni_sürüm, indirme_url)
        check_done():               Kontrol bitti (güncelleme yok veya hata)
    """

    update_available = pyqtSignal(str, str)
    check_done       = pyqtSignal()

    def __init__(self, current_version: str, skipped_version: str = "", parent: object | None = None):
        super().__init__(parent)  # type: ignore[arg-type]
        self._current  = current_version
        self._skipped  = skipped_version

    def run(self):
        latest, url = check_for_update(self._current)
        if latest and url:
            # Kullanıcı bu sürümü daha önce "atla" demediyse bildir
            if latest != self._skipped:
                self.update_available.emit(latest, url)
                return
        self.check_done.emit()


class UpdateDownloader(QThread):
    """
    Arka planda güncelleme ZIP'ini indirir.

    Sinyaller:
        progress(int, int): (indirilen_bayt, toplam_bayt)
        finished(bool):     True=başarılı, False=hata
    """

    progress = pyqtSignal(int, int)
    finished = pyqtSignal(bool)

    def __init__(self, zip_url: str, parent: object | None = None):
        super().__init__(parent)  # type: ignore[arg-type]
        self._url = zip_url
        self._zip_path: Path | None = None

    @property
    def zip_path(self) -> Path | None:
        return self._zip_path

    def run(self):
        self._zip_path = download_update(
            self._url,
            progress_callback=lambda d, t: self.progress.emit(d, t)
        )
        success = self._zip_path is not None
        self.finished.emit(success)
