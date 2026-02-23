"""
PDFToolKit - PDF Sıkıştırma Modülü

PDF dosya boyutunu küçültür. PyMuPDF (fitz) kullanır.
"""

from pathlib import Path
import fitz  # PyMuPDF

from utils.logger import get_logger
from utils.file_utils import generate_output_filename, get_file_size_str

logger = get_logger(__name__)


def compress_pdf(
    pdf_path: str | Path,
    output_path: str | Path | None = None,
    quality: str = "medium"
) -> Path:
    """
    PDF dosyasını sıkıştırarak boyutunu küçültür.

    Args:
        pdf_path: Kaynak PDF dosyası.
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.
        quality: Sıkıştırma kalitesi.
            - "low": Agresif sıkıştırma (en küçük boyut, düşük kalite)
            - "medium": Dengeli sıkıştırma (varsayılan)
            - "high": Hafif sıkıştırma (kalite korunur)

    Returns:
        Oluşturulan PDF'nin Path nesnesi.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    quality_settings = {
        "low": {"garbage": 4, "deflate": True, "clean": True},
        "medium": {"garbage": 3, "deflate": True, "clean": True},
        "high": {"garbage": 2, "deflate": True},
    }

    if quality not in quality_settings:
        raise ValueError(
            f"Geçersiz kalite: '{quality}'. "
            "Seçenekler: 'low', 'medium', 'high'"
        )

    settings_dict = quality_settings[quality]

    original_size = get_file_size_str(pdf_path)
    doc = fitz.open(str(pdf_path))

    # Çıktı yolu
    if output_path is None:
        output_path = generate_output_filename(pdf_path.stem, " (sıkıştırılmış)")
    else:
        output_path = Path(output_path)

    doc.save(str(output_path), **settings_dict)
    doc.close()

    compressed_size = get_file_size_str(output_path)
    logger.info(
        f"'{pdf_path.name}' sıkıştırıldı: {original_size} → {compressed_size} "
        f"(kalite: {quality}) → {output_path}"
    )
    return output_path
