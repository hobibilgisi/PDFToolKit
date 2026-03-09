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


def check_for_update(current_version: str) -> tuple[str | None, str | None, str | None]:
    """
    GitHub Releases'daki son sürümü kontrol eder.

    Returns:
        (latest_version, zip_download_url, release_name) — yeni sürüm varsa
        (None, None, None)                                — güncel veya hata varsa
    """
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"PDFToolKit/{current_version}"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # Draft veya prerelease ise güncelleme bildirme
        if data.get("draft", False) or data.get("prerelease", False):
            return None, None

        latest_tag = data.get("tag_name", "").lstrip("v")
        if not latest_tag:
            return None, None

        if _version_tuple(latest_tag) > _version_tuple(current_version):
            release_name = data.get("name", "").strip()
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
            return latest_tag, zip_url, release_name

    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as e:
        logger.debug(f"Güncelleme kontrolü başarısız (internet?: {e})")

    return None, None, None


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

    Strateji (batch script yaklaşımı):
        1. ZIP'i geçici klasöre çıkart
        2. ZIP içindeki kök klasörü bul (PDFToolKit/)
        3. Bir .cmd batch dosyası oluştur:
           - Uygulamanın kapanmasını bekle
           - tesseract/ ve .pdf_data/ HARİÇ tüm dosyaları kopyala
           - Uygulamayı yeniden başlat
           - Kendi kendini sil
        4. Batch dosyasını başlat ve uygulamayı kapat

    Returns:
        True — batch hazır, uygulama kapanmalı.
        False — hata oluştu.
    """
    if not getattr(sys, 'frozen', False):
        logger.warning("apply_update yalnızca EXE modunda çalışır.")
        return False

    current_exe = Path(sys.executable).resolve()
    current_dir = current_exe.parent
    extract_dir = zip_path.parent / "extracted"

    try:
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

        # Batch script oluştur
        batch_path = zip_path.parent / "_pdftoolkit_update.cmd"
        _write_update_batch(batch_path, new_root, current_dir, current_exe)

        # Batch'i başlat (bağımsız süreç)
        import subprocess
        subprocess.Popen(
            ["cmd.exe", "/c", str(batch_path)],
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            close_fds=True,
        )

        logger.info("Güncelleme batch başlatıldı, uygulama kapanıyor.")
        return True

    except Exception as e:
        logger.error(f"Güncelleme uygulama hatası: {e}")
        shutil.rmtree(extract_dir, ignore_errors=True)
        return False


def _write_update_batch(batch_path: Path, src_dir: Path, dst_dir: Path, exe_path: Path):
    """
    Güncelleme batch script dosyasını yazar.

    Batch akışı:
        1. PDFToolKit.exe kapanana kadar bekle (max 30s)
        2. Dosyaları kopyala (tesseract/ ve .pdf_data/ hariç)
        3. Uygulamayı yeniden başlat
        4. Geçici dosyaları temizle
    """
    # Kaynak ve hedef yol — batch'te tırnak içi
    src = str(src_dir)
    dst = str(dst_dir)
    exe = str(exe_path)
    temp_root = str(batch_path.parent)  # extracted + zip dosyasının bulunduğu klasör

    script = f'''@echo off
chcp 65001 >nul
title PDFToolKit Güncelleme

:: Uygulamanın kapanmasını bekle (max 30 saniye)
set /a count=0
:WAIT_LOOP
tasklist /FI "IMAGENAME eq PDFToolKit.exe" 2>nul | find /I "PDFToolKit.exe" >nul
if errorlevel 1 goto COPY_FILES
timeout /t 1 /nobreak >nul
set /a count+=1
if %count% GEQ 30 (
    echo Uygulama 30 saniye icinde kapanamadi, guncelleme iptal.
    goto CLEANUP
)
goto WAIT_LOOP

:COPY_FILES
:: 2 saniye ek bekleme (dosya kilitleri tam kalksin)
timeout /t 2 /nobreak >nul

:: Dosyalari kopyala (tesseract ve .pdf_data haric)
xcopy "{src}\\*" "{dst}\\" /E /Y /I /EXCLUDE:{batch_path.parent / "_exclude.txt"}

:: Uygulamayi yeniden baslat
start "" "{exe}"

:CLEANUP
:: Gecici dosyalari temizle
timeout /t 3 /nobreak >nul
rd /S /Q "{temp_root}" 2>nul
del "%~f0" 2>nul
'''

    # xcopy exclude listesi
    exclude_path = batch_path.parent / "_exclude.txt"
    exclude_path.write_text("\\tesseract\\\n\\.pdf_data\\\n", encoding="utf-8")

    batch_path.write_text(script, encoding="utf-8")


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

    update_available = pyqtSignal(str, str, str)  # version, url, release_name
    check_done       = pyqtSignal()

    def __init__(self, current_version: str, skipped_version: str = "", parent: object | None = None):
        super().__init__(parent)  # type: ignore[arg-type]
        self._current  = current_version
        self._skipped  = skipped_version

    def run(self):
        latest, url, release_name = check_for_update(self._current)
        if latest and url:
            # Kullanıcı bu sürümü daha önce "atla" demediyse bildir
            if latest != self._skipped:
                self.update_available.emit(latest, url, release_name or "")
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
