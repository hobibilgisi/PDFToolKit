"""
PDFToolKit — Nuitka Derleme Scripti
====================================

Tek komutla EXE üretir:
    python build.py

Çıktı: C:\\Build\\PDFToolKit\\PDFToolKit.exe  (OneDrive dışında)

İlk çalıştırmada Nuitka, MinGW64 (GCC) indirmek isteyecek (~60 MB).
"yes" diyerek izin verin — tek seferlik, sonra cache'den kullanır.

Gereksinimler:
    pip install nuitka ordered-set zstandard
"""

import subprocess
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# ─── AYARLAR ────────────────────────────────────────────────────────────────
APP_NAME    = "PDFToolKit"
MAIN_SCRIPT = "main.py"

# Sürüm numarasını config/__init__.py'den oku (tek kaynak)
def _read_version() -> str:
    ver_file = Path(__file__).parent.resolve() / "config" / "__init__.py"
    with open(ver_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return "0.0.0"

APP_VERSION = _read_version()

# Çıktı OneDrive dışında olmalı! (senkronizasyon çakışmasını önler)
OUTPUT_DIR  = Path("C:/Build/PDFToolKit")
DIST_DIR    = OUTPUT_DIR / "dist" / APP_NAME
BUILD_DIR   = OUTPUT_DIR / "build"

PROJECT_DIR = Path(__file__).parent.resolve()
PYTHON      = sys.executable
# ────────────────────────────────────────────────────────────────────────────


def run_nuitka():
    """Nuitka ile standalone EXE derler."""

    # Derleme argümanları
    args = [
        PYTHON, "-m", "nuitka",

        # Standalone: Python kurulumu gerektirmeyen, kendi başına çalışan klasör
        "--standalone",

        # MinGW64 indirme sorusuna otomatik "evet" de
        "--assume-yes-for-downloads",

        # PyQt6 plugin'i — Qt bileşenlerini dahil etmek için zorunlu
        "--enable-plugin=pyqt6",

        # Konsol penceresi çıkmasın (GUI uygulaması)
        "--windows-console-mode=disable",

        # Uygulama ikonu
        f"--windows-icon-from-ico={PROJECT_DIR / 'assets' / 'icon.ico'}",

        # Şirket adı, versiyon bilgileri (EXE özelliklerinde görünür)
        f"--windows-product-name={APP_NAME}",
        f"--windows-file-version={APP_VERSION}.0",
        f"--windows-product-version={APP_VERSION}.0",
        "--windows-company-name=PDFToolKit",

        # Gizli import'lar — dinamik import kullanan paketler için
        "--include-package=fitz",           # PyMuPDF
        "--include-package=pytesseract",
        "--include-package=docx",           # python-docx
        "--include-package=pdf2docx",
        "--include-package=openpyxl",
        "--include-package=fpdf",            # fpdf2 (PyPI ad: fpdf2, modül ad: fpdf)
        "--include-package=send2trash",
        "--include-package=dotenv",         # python-dotenv
        "--include-package=PIL",            # Pillow
        "--include-package=win32com",       # pywin32
        "--include-package=pythoncom",
        "--include-package=win32timezone",
        "--include-package=pywintypes",

        # PyMuPDF'nin dahili veri dosyalarını dahil et
        "--include-package-data=fitz",

        # Çıktı dizini (OneDrive dışında)
        f"--output-dir={OUTPUT_DIR}",

        # EXE adı
        f"--output-filename={APP_NAME}",

        MAIN_SCRIPT,
    ]

    print(f"\n{'='*60}")
    print(f"  {APP_NAME} v{APP_VERSION} — Nuitka Derleme Başladı")
    print(f"  Çıktı: {DIST_DIR}")
    print(f"{'='*60}\n")

    result = subprocess.run(args, cwd=str(PROJECT_DIR))

    if result.returncode != 0:
        print("\n❌ Derleme başarısız!")
        sys.exit(result.returncode)

    print("\n✅ Derleme tamamlandı!")


def copy_tesseract():
    """Tesseract portable'ı dist klasörüne kopyalar.

    Öncelik sırası:
        1. Proje kökünde tesseract/ varsa oradan kopyala.
        2. Yoksa sistem kurulumundan (Program Files\\Tesseract-OCR) kopyala.
    """
    src = PROJECT_DIR / "tesseract"

    # Proje klasöründe yoksa sistem kurulumunu dene
    if not src.exists():
        system_paths = [
            Path("C:/Program Files/Tesseract-OCR"),
            Path("C:/Program Files (x86)/Tesseract-OCR"),
        ]
        for p in system_paths:
            if (p / "tesseract.exe").exists():
                src = p
                print(f"ℹ️  tesseract/ bulunamadı, sistem kurulumu kullanılıyor: {src}")
                break

    if not src.exists():
        print(
            "\n⚠️  Tesseract bulunamadı — OCR çalışmaz!\n"
            "   Çözüm A: Proje kökünde 'tesseract/' klasörü oluşturun.\n"
            "   Çözüm B: Tesseract'ı kurun: https://github.com/UB-Mannheim/tesseract/wiki"
        )
        return

    dst = DIST_DIR / "tesseract"
    if dst.exists():
        shutil.rmtree(dst)

    # TÜM Tesseract kurulumunu kopyala (pdf.ttf, configs dahil)
    shutil.copytree(src, dst)

    # Boyut optimizasyonu: gereksiz dil paketlerini sil
    keep_langs = {"eng", "tur", "osd"}
    tessdata = dst / "tessdata"
    if tessdata.exists():
        for td in tessdata.glob("*.traineddata"):
            if td.stem not in keep_langs:
                td.unlink()

    tess_size = sum(f.stat().st_size for f in dst.rglob("*") if f.is_file()) / 1_048_576
    print(f"✅ Tesseract kopyalandı: {dst} ({tess_size:.0f} MB)")


def create_shortcut() -> Path | None:
    """PDFToolKit.exe kısayolunu DIST_DIR'in üst klasörüne oluşturur.

    ZIP çıkartıldığında kullanıcı EXE aramak zorunda kalmaz.
    Kısayol, Windows'un relative path resolution sayesinde çalışır.
    """
    lnk_path = DIST_DIR.parent / f"{APP_NAME}.lnk"
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(lnk_path))
        shortcut.TargetPath = str(DIST_DIR / f"{APP_NAME}.exe")
        shortcut.WorkingDirectory = str(DIST_DIR)
        shortcut.Description = "PDFToolKit - PDF İşleme Uygulaması"
        icon_ico = DIST_DIR / "icon.ico"
        if icon_ico.exists():
            shortcut.IconLocation = str(icon_ico)
        shortcut.save()
        print(f"✅ Kısayol oluşturuldu: {lnk_path}")
        return lnk_path
    except Exception as e:
        print(f"⚠️  Kısayol oluşturulamadı: {e}")
        return None


def copy_extras():
    """README, CHANGELOG ve ikon dosyasını dist klasörüne kopyalar."""
    for filename in ("README.txt", "README.md", "CHANGELOG.txt", "CHANGELOG.md"):
        src = PROJECT_DIR / filename
        if src.exists():
            shutil.copy2(src, DIST_DIR / filename)
            print(f"✅ Kopyalandı: {filename}")

    # İkon dosyasını kopyala (kısayol ve runtime için)
    icon_src = PROJECT_DIR / "assets" / "icon.ico"
    if icon_src.exists():
        shutil.copy2(icon_src, DIST_DIR / "icon.ico")
        print("✅ Kopyalandı: icon.ico")

    # Splash logo kopyala
    for splash_name in ("splash logo.gif", "splash.gif", "splash.png"):
        splash_src = PROJECT_DIR / "assets" / splash_name
        if splash_src.exists():
            shutil.copy2(splash_src, DIST_DIR / splash_name)
            print(f"✅ Kopyalandı: {splash_name}")
            break


def create_zip():
    """Dağıtım ZIP dosyasını oluşturur."""
    zip_name = f"{APP_NAME}_v{APP_VERSION}.zip"
    zip_path = OUTPUT_DIR / zip_name

    # Kısayol oluştur (ZIP root seviyesine eklenecek)
    lnk_path = create_shortcut()

    print(f"\n📦 ZIP oluşturuluyor: {zip_path}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in DIST_DIR.rglob("*"):
            # .old yedek dosyalarını atla
            if file.suffix == ".old":
                continue
            arcname = Path(APP_NAME) / file.relative_to(DIST_DIR)
            zf.write(file, arcname)

        # Kısayolu ZIP root seviyesine ekle
        if lnk_path and lnk_path.exists():
            zf.write(lnk_path, f"{APP_NAME}.lnk")

    # Kısayol geçici dosyasını temizle
    if lnk_path and lnk_path.exists():
        lnk_path.unlink(missing_ok=True)

    size_mb = zip_path.stat().st_size / 1_048_576
    print(f"✅ ZIP hazır: {zip_path} ({size_mb:.1f} MB)")
    return zip_path


def main():
    start = datetime.now()

    # Nuitka ile derle
    run_nuitka()

    # Nuitka çıktısı: OUTPUT_DIR / MAIN_SCRIPT_STEM + ".dist" klasörü
    # (main.py -> main.dist, not PDFToolKit.dist)
    stem = Path(MAIN_SCRIPT).stem  # "main"
    nuitka_out = OUTPUT_DIR / f"{stem}.dist"
    if nuitka_out.exists():
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        DIST_DIR.parent.mkdir(parents=True, exist_ok=True)
        nuitka_out.rename(DIST_DIR)

    # Ek dosyaları kopyala
    copy_tesseract()
    copy_extras()

    # ZIP oluştur (opsiyonel — yorum satırına alın gerek yoksa)
    zip_path = create_zip()

    elapsed = (datetime.now() - start).seconds
    print(f"\n🎉 Tüm işlemler tamamlandı ({elapsed}s)")
    print(f"   EXE  : {DIST_DIR / (APP_NAME + '.exe')}")
    print(f"   ZIP  : {zip_path}")
    print(f"\n   Dağıtmadan önce VirusTotal'da tarayın:")
    print(f"   https://www.virustotal.com/gui/home/upload")


if __name__ == "__main__":
    main()
