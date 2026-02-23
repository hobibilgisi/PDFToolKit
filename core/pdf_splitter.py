"""
PDFToolKit - PDF Ayırma Modülü

PDF'yi sayfalarına ayırır veya belirli sayfaları ayrı dosya olarak çıkarır.
"""

from pathlib import Path
from pypdf import PdfReader, PdfWriter

from utils.logger import get_logger
from utils.file_utils import ensure_output_dir

logger = get_logger(__name__)


def split_all_pages(
    pdf_path: str | Path,
    output_dir: str | Path | None = None
) -> list[Path]:
    """
    PDF'nin her sayfasını ayrı birer PDF dosyasına ayırır.

    Args:
        pdf_path: Kaynak PDF dosyası.
        output_dir: Çıktı dizini. None ise varsayılan çıktı dizini kullanılır.

    Returns:
        Oluşturulan PDF dosyalarının Path listesi.

    Dosya adlandırma: "{orijinal_isim}_sayfa{numara}.pdf"
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)

    if total_pages == 0:
        logger.warning(f"'{pdf_path.name}' boş bir PDF")
        return []

    output_dir = ensure_output_dir(output_dir)
    created_files = []

    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)

        output_file = output_dir / f"{pdf_path.stem}_sayfa{i}.pdf"
        with open(output_file, "wb") as f:
            writer.write(f)

        created_files.append(output_file)

    logger.info(
        f"'{pdf_path.name}' → {total_pages} sayfaya ayrıldı → {output_dir}"
    )
    return created_files


def extract_pages(
    pdf_path: str | Path,
    pages: list[int],
    output_path: str | Path | None = None
) -> Path:
    """
    PDF'den belirli sayfaları çıkarıp yeni bir PDF oluşturur.

    Args:
        pdf_path: Kaynak PDF dosyası.
        pages: Çıkarılacak sayfa numaraları listesi (1-indexed).
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.

    Returns:
        Oluşturulan PDF'nin Path nesnesi.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    if not pages:
        raise ValueError("Çıkarılacak sayfa listesi boş")

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()

    for page_num in sorted(pages):
        idx = page_num - 1
        if 0 <= idx < len(reader.pages):
            writer.add_page(reader.pages[idx])
        else:
            logger.warning(
                f"Sayfa {page_num} atlandı "
                f"(toplam {len(reader.pages)} sayfa)"
            )

    if len(writer.pages) == 0:
        raise ValueError("Hiçbir geçerli sayfa çıkarılamadı")

    # Çıktı yolu
    if output_path is None:
        from utils.file_utils import generate_output_filename, format_pages_description
        desc = format_pages_description(pages)
        output_path = generate_output_filename(
            pdf_path.stem, f" (çıkarılan {desc})"
        )
    else:
        output_path = Path(output_path)

    with open(output_path, "wb") as f:
        writer.write(f)

    logger.info(
        f"'{pdf_path.name}' → {len(writer.pages)} sayfa çıkarıldı → {output_path}"
    )
    return output_path
