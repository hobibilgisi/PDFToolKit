"""
PDFToolKit - PDF Not Ekleme Modülü

PDF dosyalarına metin notu (annotation) ve vurgulama (highlight) ekler.
PyMuPDF (fitz) kullanır.
"""

from pathlib import Path
import fitz  # PyMuPDF

from utils.logger import get_logger
from utils.file_utils import generate_output_filename

logger = get_logger(__name__)


def add_text_annotation(
    pdf_path: str | Path,
    page_num: int,
    text: str,
    position: tuple[float, float] = (72, 72),
    output_path: str | Path | None = None
) -> Path:
    """
    PDF'nin belirli bir sayfasına metin notu ekler.

    Args:
        pdf_path: Kaynak PDF dosyası.
        page_num: Not eklenecek sayfa numarası (1-indexed).
        text: Not metni.
        position: Notun konumu (x, y) piksel cinsinden. Varsayılan sol üst.
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.

    Returns:
        Oluşturulan PDF'nin Path nesnesi.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    doc = fitz.open(str(pdf_path))

    idx = page_num - 1
    if idx < 0 or idx >= len(doc):
        doc.close()
        raise ValueError(
            f"Geçersiz sayfa numarası: {page_num} "
            f"(toplam {len(doc)} sayfa)"
        )

    page = doc[idx]
    point = fitz.Point(position[0], position[1])
    page.add_text_annot(point, text)

    # Çıktı yolu
    if output_path is None:
        output_path = generate_output_filename(
            pdf_path.stem, f" ({page_num}. sayfaya not eklendi)"
        )
    else:
        output_path = Path(output_path)

    doc.save(str(output_path))
    doc.close()

    logger.info(
        f"'{pdf_path.name}' sayfa {page_num} → metin notu eklendi → {output_path}"
    )
    return output_path


def add_highlight(
    pdf_path: str | Path,
    page_num: int,
    rect: tuple[float, float, float, float],
    color: tuple[float, float, float] = (1.0, 1.0, 0.0),
    output_path: str | Path | None = None
) -> Path:
    """
    PDF'nin belirli bir sayfasındaki alana vurgulama ekler.

    Args:
        pdf_path: Kaynak PDF dosyası.
        page_num: Vurgulama yapılacak sayfa numarası (1-indexed).
        rect: Vurgulanacak alan (x0, y0, x1, y1) piksel cinsinden.
        color: Vurgulama rengi (R, G, B) 0.0-1.0 arası. Varsayılan sarı.
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.

    Returns:
        Oluşturulan PDF'nin Path nesnesi.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    doc = fitz.open(str(pdf_path))

    idx = page_num - 1
    if idx < 0 or idx >= len(doc):
        doc.close()
        raise ValueError(
            f"Geçersiz sayfa numarası: {page_num} "
            f"(toplam {len(doc)} sayfa)"
        )

    page = doc[idx]
    highlight_rect = fitz.Rect(rect)
    annot = page.add_highlight_annot(highlight_rect)
    annot.set_colors(stroke=color)
    annot.update()

    # Çıktı yolu
    if output_path is None:
        output_path = generate_output_filename(
            pdf_path.stem, f" ({page_num}. sayfa vurgulandı)"
        )
    else:
        output_path = Path(output_path)

    doc.save(str(output_path))
    doc.close()

    logger.info(
        f"'{pdf_path.name}' sayfa {page_num} → vurgulama eklendi → {output_path}"
    )
    return output_path

def highlight_text(
    pdf_path: str | Path,
    search_text: str,
    pages: list[int] | None = None,
    color: tuple[float, float, float] = (1.0, 1.0, 0.0),
    output_path: str | Path | None = None
) -> Path:
    """
    PDF'te belirtilen metni arayarak buldu\u011fu yerleri vurgular.

    Args:
        pdf_path: Kaynak PDF dosyas\u0131.
        search_text: Aranacak ve vurgulanacak metin.
        pages: Aranacak sayfa numaralar\u0131 (1-indexed). None ise t\u00fcm sayfalar.
        color: Vurgulama rengi (R, G, B) 0.0-1.0 aras\u0131. Varsay\u0131lan sar\u0131.
        output_path: \u00c7\u0131kt\u0131 dosya yolu. None ise otomatik \u00fcretilir.

    Returns:
        Olu\u015fturulan PDF'nin Path nesnesi.

    Raises:
        FileNotFoundError: Dosya bulunamazsa.
        ValueError: Metin bo\u015fsa veya hi\u00e7 e\u015fle\u015fme bulunamazsa.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamad\u0131: {pdf_path}")

    if not search_text.strip():
        raise ValueError("Aranacak metin bo\u015f olamaz")

    doc = fitz.open(str(pdf_path))
    total_highlights = 0

    # Aranacak sayfa indekslerini belirle
    if pages is None:
        page_indices = range(len(doc))
    else:
        page_indices = [p - 1 for p in pages if 0 < p <= len(doc)]

    for idx in page_indices:
        page = doc[idx]
        text_instances = page.search_for(search_text)

        for inst in text_instances:
            annot = page.add_highlight_annot(inst)
            annot.set_colors(stroke=color)
            annot.update()
            total_highlights += 1

    if total_highlights == 0:
        doc.close()
        raise ValueError(
            f"'{search_text}' metni PDF'te bulunamad\u0131"
        )

    # \u00c7\u0131kt\u0131 yolu
    if output_path is None:
        # Arama metnini kısalt (dosya adı çok uzamasın)
        short_text = search_text[:20] + ("..." if len(search_text) > 20 else "")
        output_path = generate_output_filename(
            pdf_path.stem, f" ({short_text} vurgulandı)"
        )
    else:
        output_path = Path(output_path)

    doc.save(str(output_path))
    doc.close()

    logger.info(
        f"'{pdf_path.name}' \u2192 '{search_text}' metni {total_highlights} yerde "
        f"vurguland\u0131 \u2192 {output_path}"
    )
    return output_path