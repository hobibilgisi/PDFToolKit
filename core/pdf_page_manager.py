"""
PDFToolKit - Sayfa Yönetimi Modülü

PDF sayfalarını silme, döndürme ve sayfa sayısı sorgulama.
"""

from pathlib import Path
from pypdf import PdfReader, PdfWriter

from utils.logger import get_logger
from utils.file_utils import generate_output_filename, format_pages_description

logger = get_logger(__name__)


def delete_pages(
    pdf_path: str | Path,
    pages_to_delete: list[int],
    output_path: str | Path | None = None
) -> Path:
    """
    PDF'den belirli sayfaları siler.

    Args:
        pdf_path: Kaynak PDF dosyası.
        pages_to_delete: Silinecek sayfa numaraları (1-indexed).
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.

    Returns:
        Oluşturulan PDF'nin Path nesnesi.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    if not pages_to_delete:
        raise ValueError("Silinecek sayfa listesi boş")

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    delete_set = set(pages_to_delete)

    pages_kept = 0
    for i, page in enumerate(reader.pages, start=1):
        if i not in delete_set:
            writer.add_page(page)
            pages_kept += 1

    if pages_kept == 0:
        raise ValueError("Tüm sayfalar silinmiş olur, en az bir sayfa kalmalı")

    # Çıktı yolu
    if output_path is None:
        desc = format_pages_description(pages_to_delete)
        output_path = generate_output_filename(
            pdf_path.stem, f" ({desc} silindi)"
        )
    else:
        output_path = Path(output_path)

    with open(output_path, "wb") as f:
        writer.write(f)

    deleted_count = len(reader.pages) - pages_kept
    logger.info(
        f"'{pdf_path.name}' → {deleted_count} sayfa silindi, "
        f"{pages_kept} sayfa kaldı → {output_path}"
    )
    return output_path


def rotate_pages(
    pdf_path: str | Path,
    pages: list[int],
    angle: int,
    output_path: str | Path | None = None
) -> Path:
    """
    Belirli sayfaları saat yönünde döndürür.

    Args:
        pdf_path: Kaynak PDF dosyası.
        pages: Döndürülecek sayfa numaraları (1-indexed).
        angle: Döndürme açısı (90, 180, 270).
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.

    Returns:
        Oluşturulan PDF'nin Path nesnesi.

    Raises:
        ValueError: Geçersiz açı değeri.
    """
    if angle not in (90, 180, 270):
        raise ValueError(f"Geçersiz döndürme açısı: {angle}. 90, 180 veya 270 olmalı")

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    rotate_set = set(pages)

    for i, page in enumerate(reader.pages, start=1):
        if i in rotate_set:
            page.rotate(angle)
        writer.add_page(page)

    # Çıktı yolu
    if output_path is None:
        desc = format_pages_description(pages)
        output_path = generate_output_filename(
            pdf_path.stem, f" ({desc} {angle}° döndürüldü)"
        )
    else:
        output_path = Path(output_path)

    with open(output_path, "wb") as f:
        writer.write(f)

    logger.info(
        f"'{pdf_path.name}' → {len(rotate_set)} sayfa {angle}° döndürüldü → {output_path}"
    )
    return output_path


def set_page_orientation(
    pdf_path: str | Path,
    pages: list[int],
    orientation: str = "landscape",
    output_path: str | Path | None = None
) -> Path:
    """
    Belirli sayfaları yatay (landscape) veya dikey (portrait) yapar.

    Sayfanın mevcut yönünü algılar ve gerekiyorsa 90° döndürerek
    istenen yöne çevirir. Zaten doğru yöndeyse dokunmaz.

    Args:
        pdf_path: Kaynak PDF dosyası.
        pages: Yön değiştirilecek sayfa numaraları (1-indexed).
        orientation: "landscape" (yatay) veya "portrait" (dikey).
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.

    Returns:
        Oluşturulan PDF'nin Path nesnesi.
    """
    if orientation not in ("landscape", "portrait"):
        raise ValueError(
            f"Geçersiz yön: '{orientation}'. 'landscape' veya 'portrait' olmalı"
        )

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    target_set = set(pages)
    changed_count = 0

    for i, page in enumerate(reader.pages, start=1):
        if i in target_set:
            # Sayfanın mevcut boyutlarını al (rotation hesaba katılarak)
            rotation = page.get("/Rotate", 0) or 0
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)

            # Mevcut rotation 90/270 ise gerçek görüntü boyutları ters
            if rotation in (90, 270):
                width, height = height, width

            is_landscape = width > height

            if orientation == "landscape" and not is_landscape:
                page.rotate(90)   # saat yönünde
                changed_count += 1
            elif orientation == "portrait" and is_landscape:
                page.rotate(270)  # saat yönü tersine
                changed_count += 1

        writer.add_page(page)

    # Çıktı yolu
    yon_str = "yatay yapıldı" if orientation == "landscape" else "dikey yapıldı"
    if output_path is None:
        desc = format_pages_description(pages)
        output_path = generate_output_filename(
            pdf_path.stem, f" ({desc} {yon_str})"
        )
    else:
        output_path = Path(output_path)

    with open(output_path, "wb") as f:
        writer.write(f)

    yon_str = "yatay" if orientation == "landscape" else "dikey"
    logger.info(
        f"'{pdf_path.name}' → {changed_count}/{len(target_set)} sayfa {yon_str} yapıldı → {output_path}"
    )
    return output_path


def get_page_count(pdf_path: str | Path) -> int:
    """
    PDF dosyasının sayfa sayısını döndürür.

    Args:
        pdf_path: PDF dosya yolu.

    Returns:
        Sayfa sayısı.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    return len(reader.pages)
