"""
PDFToolKit - OCR Modülü

Görüntü tabanlı (taranmış) PDF'lere metin katmanı ekleyerek
seçilebilir/aranabilir hale getirir.

Gereksinimler:
    - Tesseract OCR sisteme kurulu olmalı
    - PyMuPDF (fitz) zaten yüklü (Poppler gerekmez)
"""

from pathlib import Path

from utils.logger import get_logger
from utils.file_utils import generate_output_filename
from config.settings import settings

logger = get_logger(__name__)


def ocr_pdf(
    pdf_path: str | Path,
    output_path: str | Path | None = None,
    lang: str = "tur+eng"
) -> Path:
    """
    PDF'yi OCR ile işler ve seçilebilir metin katmanı ekler.

    PyMuPDF ile PDF sayfalarını görsele çevirir (Poppler gerekmez),
    ardından Tesseract ile metin tanıma uygular.

    Args:
        pdf_path: Kaynak PDF dosyası.
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.
        lang: OCR dili. Varsayılan "tur+eng" (Türkçe + İngilizce).

    Returns:
        Oluşturulan PDF'nin Path nesnesi.

    Raises:
        RuntimeError: Tesseract bulunamazsa.
    """
    try:
        import pytesseract
        import fitz  # PyMuPDF
        from PIL import Image
    except ImportError as e:
        raise RuntimeError(
            f"OCR için gerekli kütüphane eksik: {e}. "
            "pip install pytesseract PyMuPDF Pillow"
        )

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    # Tesseract yolu
    if settings.tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path

    logger.info(f"OCR başlatılıyor: '{pdf_path.name}' (dil: {lang})")

    # PDF → görsellere dönüştür (PyMuPDF ile — Poppler gerekmez)
    doc = fitz.open(str(pdf_path))
    zoom = 300 / 72  # 300 DPI
    matrix = fitz.Matrix(zoom, zoom)

    # Her görselden OCR ile PDF sayfası oluştur
    pdf_pages = []

    for i, page in enumerate(doc, start=1):
        logger.info(f"  Sayfa {i}/{len(doc)} işleniyor...")

        pix = page.get_pixmap(matrix=matrix)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        try:
            pdf_data = pytesseract.image_to_pdf_or_hocr(
                image,
                lang=lang,
                extension="pdf"
            )
        except Exception as e:
            raise RuntimeError(
                f"OCR hatası (sayfa {i}): {e}. "
                "Tesseract kurulu ve TESSERACT_PATH ayarlı mı?"
            )

        pdf_pages.append(pdf_data)

    doc.close()

    # OCR sonuçlarını birleştir
    from pypdf import PdfReader, PdfWriter
    import io

    writer = PdfWriter()
    for pdf_data in pdf_pages:
        reader = PdfReader(io.BytesIO(pdf_data))
        for page in reader.pages:
            writer.add_page(page)

    # Çıktı yolu
    if output_path is None:
        output_path = generate_output_filename(pdf_path.stem, " (OCR uygulandı)")
    else:
        output_path = Path(output_path)

    with open(output_path, "wb") as f:
        writer.write(f)

    logger.info(f"OCR tamamlandı → {output_path}")
    return output_path
