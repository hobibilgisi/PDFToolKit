"""
PDFToolKit - Filigran Modülü

PDF dosyalarına metin filigranı (watermark) ekler.
PyMuPDF (fitz) kullanır. Arial TTF ile Türkçe karakter desteği.
"""

from pathlib import Path
import math
import fitz  # PyMuPDF

from utils.logger import get_logger
from utils.file_utils import generate_output_filename

logger = get_logger(__name__)

# Windows Arial font (Unicode/Türkçe karakter desteği)
_ARIAL_FONT = Path("C:/Windows/Fonts/arial.ttf")


def add_watermark(
    pdf_path: str | Path,
    watermark_text: str,
    output_path: str | Path | None = None,
    font_size: int = 60,
    opacity: float = 0.3,
    color: tuple[float, float, float] = (0.5, 0.5, 0.5),
    angle: float = 45.0
) -> Path:
    """
    PDF'nin tüm sayfalarına şeffaf metin filigranı ekler.

    Arial TTF fontu kullanarak Türkçe karakterleri (ğ, ı, ş, ç, ö, ü)
    doğru şekilde gösterir.

    Args:
        pdf_path: Kaynak PDF dosyası.
        watermark_text: Filigran metni.
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.
        font_size: Font boyutu (varsayılan: 60).
        opacity: Saydamlık 0.0-1.0 (varsayılan: 0.3).
        color: Metin rengi (R, G, B) 0.0-1.0. Varsayılan gri.
        angle: Döndürme açısı derece cinsinden (varsayılan: 45°).

    Returns:
        Oluşturulan PDF'nin Path nesnesi.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    if not watermark_text.strip():
        raise ValueError("Filigran metni boş olamaz")

    # Font dosyasını belirle (Türkçe karakter desteği için Arial TTF)
    fontfile = str(_ARIAL_FONT) if _ARIAL_FONT.exists() else None
    fontname = "arial" if fontfile else "helv"

    if not fontfile:
        logger.warning(
            "Arial font bulunamadı — Helvetica kullanılacak "
            "(Türkçe karakterler eksik olabilir)"
        )

    doc = fitz.open(str(pdf_path))

    for page in doc:
        rect = page.rect
        cx, cy = rect.width / 2, rect.height / 2

        # Döndürme açısına göre sayfa içinde kalacak max genişliği hesapla
        rad = math.radians(angle)
        cos_a, sin_a = abs(math.cos(rad)), abs(math.sin(rad))

        if cos_a < 0.01:
            max_line = rect.height
        elif sin_a < 0.01:
            max_line = rect.width
        else:
            max_line = min(rect.height / sin_a, rect.width / cos_a)

        max_width = max_line * 0.80
        trial_h = font_size * 20          # büyük deneme kutusu

        # ── 1) Deneme kutusuyla gerçek yüksekliği ölç + font küçült ──
        actual_fs = font_size
        measured_h = trial_h

        while actual_fs >= 12:
            trial_rect = fitz.Rect(0, 0, max_width, trial_h)
            trial_shape = page.new_shape()
            rc = trial_shape.insert_textbox(
                trial_rect,
                watermark_text,
                fontname=fontname,
                fontfile=fontfile,
                fontsize=actual_fs,
                align=fitz.TEXT_ALIGN_CENTER,
            )
            # Shape'i commit etmiyoruz — sadece ölçüm
            if rc >= 0:
                measured_h = trial_h - rc        # metnin kapladığı gerçek yükseklik
                break
            actual_fs -= 4

        # ── 2) Gerçek ortalanmış kutuyu oluştur ──
        half_w = max_width / 2
        half_h = measured_h / 2
        text_rect = fitz.Rect(
            cx - half_w, cy - half_h,
            cx + half_w, cy + half_h,
        )
        pivot = fitz.Point(cx, cy)

        rotation_matrix = fitz.Matrix(
            math.cos(rad), math.sin(rad),
            -math.sin(rad), math.cos(rad),
            0, 0,
        )

        # ── 3) Asıl filigranı yaz ──
        shape = page.new_shape()
        shape.insert_textbox(
            text_rect,
            watermark_text,
            fontname=fontname,
            fontfile=fontfile,
            fontsize=actual_fs,
            color=color,
            render_mode=0,
            align=fitz.TEXT_ALIGN_CENTER,
            morph=(pivot, rotation_matrix),
        )
        shape.finish(fill_opacity=opacity)
        shape.commit(overlay=True)

    # Çıktı yolu
    if output_path is None:
        output_path = generate_output_filename(pdf_path.stem, " (filigranlı)")
    else:
        output_path = Path(output_path)

    doc.save(str(output_path))
    doc.close()

    logger.info(
        f"'{pdf_path.name}' → filigran eklendi '{watermark_text}' → {output_path}"
    )
    return output_path
