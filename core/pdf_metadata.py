"""
PDFToolKit - PDF Meta Bilgi Modülü

PDF dosyalarının meta bilgilerini (sayfa sayısı, boyut, yazar vb.) okur.
"""

from pathlib import Path
from pypdf import PdfReader

from utils.logger import get_logger
from utils.file_utils import get_file_size_str

logger = get_logger(__name__)


def get_metadata(pdf_path: str | Path) -> dict:
    """
    PDF dosyasının meta bilgilerini döndürür.

    Args:
        pdf_path: PDF dosya yolu.

    Returns:
        Meta bilgiler sözlüğü:
        {
            "dosya_adi": str,
            "sayfa_sayisi": int,
            "dosya_boyutu": str,
            "dosya_boyutu_bytes": int,
            "yazar": str | None,
            "baslik": str | None,
            "konu": str | None,
            "olusturucu": str | None,
            "uretici": str | None,
            "olusturma_tarihi": str | None,
            "degistirme_tarihi": str | None,
            "sifrelenmis": bool
        }
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    info = reader.metadata

    metadata = {
        "dosya_adi": pdf_path.name,
        "sayfa_sayisi": len(reader.pages),
        "dosya_boyutu": get_file_size_str(pdf_path),
        "dosya_boyutu_bytes": pdf_path.stat().st_size,
        "sifrelenmis": reader.is_encrypted,
    }

    if info:
        metadata.update({
            "yazar": info.get("/Author"),
            "baslik": info.get("/Title"),
            "konu": info.get("/Subject"),
            "olusturucu": info.get("/Creator"),
            "uretici": info.get("/Producer"),
            "olusturma_tarihi": str(info.get("/CreationDate", "")),
            "degistirme_tarihi": str(info.get("/ModDate", "")),
        })
    else:
        metadata.update({
            "yazar": None,
            "baslik": None,
            "konu": None,
            "olusturucu": None,
            "uretici": None,
            "olusturma_tarihi": None,
            "degistirme_tarihi": None,
        })

    logger.info(f"Meta bilgi okundu: '{pdf_path.name}'")
    return metadata
