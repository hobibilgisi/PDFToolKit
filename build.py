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
APP_VERSION = "0.2.0"
MAIN_SCRIPT = "main.py"

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

        # PyQt6 plugin'i — Qt bileşenlerini dahil etmek için zorunlu
        "--enable-plugin=pyqt6",

        # Konsol penceresi çıkmasın (GUI uygulaması)
        "--windows-console-mode=disable",

        # Uygulama ikonu (varsa)
        # "--windows-icon-from-ico=assets/icon.ico",

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
        "--include-package=fpdf2",
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

    # Yalnızca gereken dosyaları kopyala: tesseract.exe, DLL'ler, tessdata
    dst.mkdir(parents=True)
    (dst / "tessdata").mkdir()
    # EXE
    shutil.copy2(src / "tesseract.exe", dst / "tesseract.exe")
    # DLL'ler
    for dll in src.glob("*.dll"):
        shutil.copy2(dll, dst / dll.name)
    # Dil paketleri (sadece eng + tur + osd)
    for lang in ("eng", "tur", "osd"):
        td = src / "tessdata" / f"{lang}.traineddata"
        if td.exists():
            shutil.copy2(td, dst / "tessdata" / td.name)

    tess_size = sum(f.stat().st_size for f in dst.rglob("*") if f.is_file()) / 1_048_576
    print(f"✅ Tesseract kopyalandı: {dst} ({tess_size:.0f} MB)")


def copy_extras():
    """README ve CHANGELOG'u dist klasörüne kopyalar."""
    for filename in ("README.txt", "README.md", "CHANGELOG.txt", "CHANGELOG.md"):
        src = PROJECT_DIR / filename
        if src.exists():
            shutil.copy2(src, DIST_DIR / filename)
            print(f"✅ Kopyalandı: {filename}")


def create_zip():
    """Dağıtım ZIP dosyasını oluşturur."""
    zip_name = f"{APP_NAME}_v{APP_VERSION}.zip"
    zip_path = OUTPUT_DIR / zip_name

    print(f"\n📦 ZIP oluşturuluyor: {zip_path}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in DIST_DIR.rglob("*"):
            # .old yedek dosyalarını atla
            if file.suffix == ".old":
                continue
            arcname = Path(APP_NAME) / file.relative_to(DIST_DIR)
            zf.write(file, arcname)

    size_mb = zip_path.stat().st_size / 1_048_576
    print(f"✅ ZIP hazır: {zip_path} ({size_mb:.1f} MB)")
    return zip_path


def main():
    start = datetime.now()

    # Nuitka ile derle
    run_nuitka()

    # Nuitka çıktısı: OUTPUT_DIR / APP_NAME + ".dist" klasörü
    nuitka_out = OUTPUT_DIR / f"{APP_NAME}.dist"
    if nuitka_out.exists() and not DIST_DIR.exists():
        nuitka_out.rename(DIST_DIR)
    elif nuitka_out.exists():
        # Her iki klasör de varsa, yenisiyle değiştir
        shutil.rmtree(DIST_DIR)
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
