"""
PDFToolKit - PDF Birleştirme Modülü

Birden fazla PDF dosyasını sıralı olarak birleştirir.
Belirli sayfaları seçerek birleştirme ve bir PDF'yi
başka bir PDF'nin belirli sayfasına ekleme desteği.
"""

from pathlib import Path
from pypdf import PdfReader, PdfWriter

from utils.logger import get_logger
from utils.file_utils import generate_output_filename

logger = get_logger(__name__)


def merge_pdfs(
    file_list: list[dict],
    output_path: str | Path | None = None
) -> Path:
    """
    Birden fazla PDF'yi belirtilen sırayla birleştirir.

    Args:
        file_list: Birleştirilecek dosya bilgileri listesi.
            Her eleman bir dict: {"path": str|Path, "pages": list[int] | None}
            pages None ise tüm sayfalar alınır. Sayfa numaraları 1-indexed.
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.

    Returns:
        Oluşturulan birleştirilmiş PDF'nin Path nesnesi.

    Raises:
        FileNotFoundError: Dosya bulunamazsa.
        ValueError: file_list boşsa.
    """
    if not file_list:
        raise ValueError("Birleştirilecek dosya listesi boş")

    writer = PdfWriter()

    for item in file_list:
        pdf_path = Path(item["path"])

        if not pdf_path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

        reader = PdfReader(str(pdf_path))
        pages = item.get("pages")  # None → tüm sayfalar

        if pages is None:
            # Tüm sayfaları ekle
            for page in reader.pages:
                writer.add_page(page)
            logger.info(
                f"'{pdf_path.name}' : tüm sayfalar eklendi "
                f"({len(reader.pages)} sayfa)"
            )
        else:
            # Belirli sayfaları ekle (1-indexed → 0-indexed)
            for page_num in pages:
                idx = page_num - 1
                if 0 <= idx < len(reader.pages):
                    writer.add_page(reader.pages[idx])
                else:
                    logger.warning(
                        f"'{pdf_path.name}' : sayfa {page_num} atlandı "
                        f"(toplam {len(reader.pages)} sayfa)"
                    )
            logger.info(
                f"'{pdf_path.name}' : {len(pages)} sayfa eklendi"
            )

    # Çıktı yolu
    if output_path is None:
        names = [Path(item["path"]).stem for item in file_list[:3]]
        names_str = ", ".join(names)
        if len(file_list) > 3:
            names_str += "..."
        output_path = generate_output_filename(
            "birlesik", f" ({names_str})"
        )
    else:
        output_path = Path(output_path)

    with open(output_path, "wb") as f:
        writer.write(f)

    logger.info(f"Birleştirme tamamlandı -> {output_path}")
    return output_path


def insert_pdf(
    target_path: str | Path,
    source_path: str | Path,
    insert_after_page: int,
    output_path: str | Path | None = None
) -> Path:
    """
    Bir PDF'yi başka bir PDF'nin belirli sayfasından sonra ekler.

    Args:
        target_path: Hedef PDF dosyası.
        source_path: Eklenecek kaynak PDF dosyası.
        insert_after_page: Kaynağın ekleneceği sayfa numarası (1-indexed).
            0 = en başa ekle.
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.

    Returns:
        Oluşturulan PDF'nin Path nesnesi.
    """
    target_path = Path(target_path)
    source_path = Path(source_path)

    if not target_path.exists():
        raise FileNotFoundError(f"Hedef dosya bulunamadı: {target_path}")
    if not source_path.exists():
        raise FileNotFoundError(f"Kaynak dosya bulunamadı: {source_path}")

    target_reader = PdfReader(str(target_path))
    source_reader = PdfReader(str(source_path))
    writer = PdfWriter()

    # insert_after_page öncesi sayfalar
    for i in range(min(insert_after_page, len(target_reader.pages))):
        writer.add_page(target_reader.pages[i])

    # Kaynak sayfaları ekle
    for page in source_reader.pages:
        writer.add_page(page)

    # insert_after_page sonrası sayfalar
    for i in range(insert_after_page, len(target_reader.pages)):
        writer.add_page(target_reader.pages[i])

    # Çıktı yolu
    if output_path is None:
        output_path = generate_output_filename(
            target_path.stem,
            f" ({source_path.stem} sayfa {insert_after_page} sonrasına eklendi)"
        )
    else:
        output_path = Path(output_path)

    with open(output_path, "wb") as f:
        writer.write(f)

    logger.info(
        f"'{source_path.name}' -> '{target_path.name}' "
        f"sayfa {insert_after_page} sonrasına eklendi -> {output_path}"
    )
    return output_path
