"""
PDFToolKit - Dosya İşlemleri Yardımcı Fonksiyonları

PDF dosya listeleme, çıktı dizini oluşturma, dosya adı üretme
gibi ortak dosya işlemlerini sağlar.
"""

import os
from pathlib import Path
from config.settings import settings

# Desteklenen dosya uzantıları
SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls",
    ".jpg", ".jpeg", ".png", ".bmp", ".tiff",
}

# Uzantı → tür etiketleri (UI'da ikon gösterimi için)
EXTENSION_LABELS = {
    ".pdf": "PDF",
    ".docx": "Word", ".doc": "Word",
    ".xlsx": "Excel", ".xls": "Excel",
    ".jpg": "JPG", ".jpeg": "JPG",
    ".png": "PNG", ".bmp": "BMP", ".tiff": "TIFF",
}


def list_pdf_files(directory: str | Path | None = None) -> list[Path]:
    """
    Belirtilen dizindeki PDF dosyalarını listeler.

    Dosyalar değişiklik tarihine göre sıralanır (en eski → en yeni).
    Böylece en son oluşturulan dosya listenin sonunda görünür.

    Args:
        directory: Taranacak dizin yolu. None ise settings.input_dir kullanılır.

    Returns:
        PDF dosyalarının Path nesneleri listesi (tarihe göre sıralı).
    """
    if directory is None:
        directory = settings.input_dir
    else:
        directory = Path(directory)

    if not directory.exists():
        return []

    pdf_files = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() == ".pdf"
    ]

    return sorted(pdf_files, key=lambda f: f.stat().st_mtime)


def list_all_files(directory: str | Path | None = None) -> list[Path]:
    """
    Belirtilen dizindeki tüm desteklenen dosyaları listeler.

    PDF, Word, Excel, görsel dosyalarını dahil eder.
    Dosyalar değişiklik tarihine göre sıralanır (en eski → en yeni).

    Args:
        directory: Taranacak dizin yolu. None ise settings.output_dir kullanılır.

    Returns:
        Desteklenen dosyaların Path nesneleri listesi (tarihe göre sıralı).
    """
    if directory is None:
        directory = settings.output_dir
    else:
        directory = Path(directory)

    if not directory.exists():
        return []

    all_files = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    return sorted(all_files, key=lambda f: f.stat().st_mtime)


def ensure_output_dir(path: str | Path | None = None) -> Path:
    """
    Çıktı dizininin var olduğundan emin olur, yoksa oluşturur.

    Args:
        path: Oluşturulacak dizin yolu. None ise settings.output_dir kullanılır.

    Returns:
        Oluşturulan/mevcut dizinin Path nesnesi.
    """
    if path is None:
        path = settings.output_dir
    else:
        path = Path(path)

    path.mkdir(parents=True, exist_ok=True)
    return path


def format_pages_description(pages: list[int], max_display: int = 5) -> str:
    """
    Sayfa listesini okunabilir açıklama metnine çevirir.

    Args:
        pages: Sayfa numaraları listesi (1-indexed).
        max_display: Gösterilecek maksimum sayfa sayısı.

    Returns:
        Açıklama metni. Örn: "2. sayfa", "1,3,5. sayfalar"
    """
    sorted_pages = sorted(set(pages))
    if len(sorted_pages) == 0:
        return ""
    if len(sorted_pages) == 1:
        return f"{sorted_pages[0]}. sayfa"
    if len(sorted_pages) <= max_display:
        page_str = ",".join(str(p) for p in sorted_pages)
    else:
        shown = ",".join(str(p) for p in sorted_pages[:max_display])
        page_str = f"{shown}..."
    return f"{page_str}. sayfalar"


def generate_output_filename(
    base_name: str,
    suffix: str = "",
    extension: str = ".pdf",
    output_dir: str | Path | None = None
) -> Path:
    """
    Çıktı dosya adı üretir. Aynı isimde dosya varsa numara ekler.

    Args:
        base_name: Temel dosya adı (uzantısız).
        suffix: Dosya adına eklenecek sonek (ör: "_birlesik", "_sayfa1").
        extension: Dosya uzantısı (varsayılan: ".pdf").
        output_dir: Çıktı dizini. None ise settings.output_dir kullanılır.

    Returns:
        Benzersiz çıktı dosya yolunun Path nesnesi.

    Örnek:
        generate_output_filename("rapor", "_birlesik")
        → output/rapor_birlesik.pdf
        Eğer varsa: output/rapor_birlesik_2.pdf
    """
    if output_dir is None:
        output_dir = ensure_output_dir()
    else:
        output_dir = ensure_output_dir(output_dir)

    # Uzantıyı normalize et
    if not extension.startswith("."):
        extension = f".{extension}"

    # Temel dosya adından uzantıyı kaldır
    base_name = Path(base_name).stem

    filename = f"{base_name}{suffix}{extension}"
    output_path = output_dir / filename

    # Aynı isimde dosya varsa numara ekle
    counter = 2
    while output_path.exists():
        filename = f"{base_name}{suffix}_{counter}{extension}"
        output_path = output_dir / filename
        counter += 1

    return output_path


def get_file_size_str(file_path: str | Path) -> str:
    """
    Dosya boyutunu insan okunabilir formatta döndürür.

    Args:
        file_path: Dosya yolu.

    Returns:
        Boyut metni (ör: "2.3 MB", "456 KB").
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return "—"

    size_bytes = file_path.stat().st_size

    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
