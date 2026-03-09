"""
PDFToolKit — SVG İkon Kütüphanesi

Tüm buton ve uygulama ikonları inline SVG olarak tanımlıdır.
Catppuccin Mocha renk paletine uyumlu, Lucide-benzeri minimalist tasarım.

Kullanım:
    from gui.icons import icon
    btn.setIcon(icon("merge"))
"""

from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtCore import QSize, QByteArray, Qt
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter

# ── Catppuccin Mocha Renkleri ───────────────────────────────────────────
_TEXT = "#cdd6f4"
_BLUE = "#89b4fa"
_GREEN = "#a6e3a1"
_RED = "#f38ba8"
_YELLOW = "#f9e2af"
_LAVENDER = "#b4befe"
_MAUVE = "#cba6f7"
_TEAL = "#94e2d5"
_PEACH = "#fab387"
_SUBTEXT = "#a6adc8"

# ── SVG Şablonları ──────────────────────────────────────────────────────
def _svg(inner: str, color: str = _TEXT, size: int = 24) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )


_ICONS: dict[str, str] = {}

# ===== PDF İşlemleri =====

# Birleştir — iki sayfa birleşen ok
_ICONS["merge"] = _svg(
    '<path d="M5 4v5l7 5 7-5V4"/>'
    '<line x1="12" y1="14" x2="12" y2="21"/>'
    '<polyline points="9,18 12,21 15,18"/>',
    _PEACH
)

# Sayfalarına Ayır — makas
_ICONS["split"] = _svg(
    '<circle cx="6" cy="6" r="2.5"/>'
    '<circle cx="6" cy="18" r="2.5"/>'
    '<line x1="20" y1="4" x2="8.2" y2="15.8"/>'
    '<line x1="14.5" y1="13" x2="20" y2="20"/>'
    '<line x1="8.2" y1="8.2" x2="12" y2="12"/>',
    _PEACH
)

# Seçili Sayfaları Çıkar — dosyadan dışarı ok
_ICONS["extract"] = _svg(
    '<rect x="4" y="2" width="11" height="16" rx="2"/>'
    '<line x1="14" y1="10" x2="22" y2="10"/>'
    '<polyline points="19,7 22,10 19,13"/>',
    _GREEN
)

# Sayfa Sil — dosya üzerinde X
_ICONS["delete_page"] = _svg(
    '<rect x="4" y="2" width="14" height="18" rx="2"/>'
    '<line x1="9" y1="8" x2="15" y2="14"/>'
    '<line x1="15" y1="8" x2="9" y2="14"/>',
    _SUBTEXT
)

# Yatay / Dikey Yap — döndürme oku
_ICONS["orientation"] = _svg(
    '<rect x="3" y="6" width="10" height="14" rx="1.5" stroke-dasharray="3,2"/>'
    '<rect x="7" y="3" width="14" height="10" rx="1.5"/>'
    '<path d="M17 16l2.5-2.5L17 11"/>',
    _LAVENDER
)

# PDF Ekle — dosya ile artı
_ICONS["insert"] = _svg(
    '<rect x="4" y="2" width="11" height="16" rx="2"/>'
    '<line x1="19" y1="14" x2="19" y2="22"/>'
    '<line x1="15" y1="18" x2="23" y2="18"/>',
    _TEAL
)

# Alfabetik Sırala — A-Z çubuklar
_ICONS["sort_alpha"] = _svg(
    '<line x1="4" y1="6" x2="14" y2="6"/>'
    '<line x1="4" y1="12" x2="11" y2="12"/>'
    '<line x1="4" y1="18" x2="8" y2="18"/>'
    '<path d="M18 5l2.5 6h-5l2.5-6z" fill="{c}"/>'
    '<line x1="20" y1="15" x2="20" y2="21"/>'
    '<polyline points="17,18.5 20,21 23,18.5"/>'.format(c=_YELLOW),
    _YELLOW
)

# Adını Değiştir — kalem
_ICONS["rename"] = _svg(
    '<path d="M17 3l4 4L8 20H4v-4L17 3z"/>'
    '<line x1="14" y1="6" x2="18" y2="10"/>',
    _MAUVE
)

# Numaralandır / Sırala — sayı listesi
_ICONS["order_number"] = _svg(
    '<text x="3" y="8" font-size="7" font-weight="bold" fill="{c}" stroke="none" font-family="sans-serif">1</text>'
    '<line x1="10" y1="6" x2="21" y2="6"/>'
    '<text x="3" y="15" font-size="7" font-weight="bold" fill="{c}" stroke="none" font-family="sans-serif">2</text>'
    '<line x1="10" y1="13" x2="21" y2="13"/>'
    '<text x="3" y="22" font-size="7" font-weight="bold" fill="{c}" stroke="none" font-family="sans-serif">3</text>'
    '<line x1="10" y1="20" x2="21" y2="20"/>'.format(c=_PEACH),
    _PEACH
)

# ===== Dönüştürme =====

# PDF → Word
_ICONS["pdf_to_word"] = _svg(
    '<rect x="2" y="4" width="9" height="12" rx="1.5"/>'
    '<text x="4" y="12.5" font-size="5.5" fill="{bl}" stroke="none" font-weight="bold" font-family="sans-serif">P</text>'
    '<polyline points="13,10 16,10"/>'
    '<polyline points="14.5,8 16.5,10 14.5,12"/>'
    '<rect x="17" y="4" width="5" height="12" rx="1.5" stroke="{bl}"/>'
    '<text x="17.8" y="12.5" font-size="5" fill="{bl}" stroke="none" font-weight="bold" font-family="sans-serif">W</text>'.format(bl=_BLUE),
    _TEXT
)

# PDF → Excel
_ICONS["pdf_to_excel"] = _svg(
    '<rect x="2" y="4" width="9" height="12" rx="1.5"/>'
    '<text x="4" y="12.5" font-size="5.5" fill="{g}" stroke="none" font-weight="bold" font-family="sans-serif">P</text>'
    '<polyline points="13,10 16,10"/>'
    '<polyline points="14.5,8 16.5,10 14.5,12"/>'
    '<rect x="17" y="4" width="5" height="12" rx="1.5" stroke="{g}"/>'
    '<text x="18" y="12.5" font-size="5" fill="{g}" stroke="none" font-weight="bold" font-family="sans-serif">X</text>'.format(g=_GREEN),
    _TEXT
)

# PDF → JPG
_ICONS["pdf_to_jpg"] = _svg(
    '<rect x="2" y="4" width="9" height="12" rx="1.5"/>'
    '<text x="4" y="12.5" font-size="5.5" fill="{p}" stroke="none" font-weight="bold" font-family="sans-serif">P</text>'
    '<polyline points="13,10 16,10"/>'
    '<polyline points="14.5,8 16.5,10 14.5,12"/>'
    '<rect x="16" y="4" width="7" height="12" rx="1.5" stroke="{p}"/>'
    '<circle cx="18.5" cy="8" r="1.2" fill="{p}" stroke="none"/>'
    '<polyline points="16,14 18.5,10.5 21,13 23,11.5" stroke="{p}" fill="none"/>'.format(p=_PEACH),
    _TEXT
)

# Word → PDF
_ICONS["word_to_pdf"] = _svg(
    '<rect x="2" y="4" width="5" height="12" rx="1.5" stroke="{bl}"/>'
    '<text x="2.5" y="12.5" font-size="5" fill="{bl}" stroke="none" font-weight="bold" font-family="sans-serif">W</text>'
    '<polyline points="9,10 12,10"/>'
    '<polyline points="10.5,8 12.5,10 10.5,12"/>'
    '<rect x="13" y="4" width="9" height="12" rx="1.5"/>'
    '<text x="15" y="12.5" font-size="5.5" fill="{r}" stroke="none" font-weight="bold" font-family="sans-serif">P</text>'.format(bl=_BLUE, r=_RED),
    _TEXT
)

# Excel → PDF
_ICONS["excel_to_pdf"] = _svg(
    '<rect x="2" y="4" width="5" height="12" rx="1.5" stroke="{g}"/>'
    '<text x="2.8" y="12.5" font-size="5" fill="{g}" stroke="none" font-weight="bold" font-family="sans-serif">X</text>'
    '<polyline points="9,10 12,10"/>'
    '<polyline points="10.5,8 12.5,10 10.5,12"/>'
    '<rect x="13" y="4" width="9" height="12" rx="1.5"/>'
    '<text x="15" y="12.5" font-size="5.5" fill="{r}" stroke="none" font-weight="bold" font-family="sans-serif">P</text>'.format(g=_GREEN, r=_RED),
    _TEXT
)

# JPG → PDF
_ICONS["jpg_to_pdf"] = _svg(
    '<rect x="1" y="4" width="7" height="12" rx="1.5" stroke="{p}"/>'
    '<circle cx="3.5" cy="8" r="1.2" fill="{p}" stroke="none"/>'
    '<polyline points="1,14 3.5,10.5 6,13 8,11.5" stroke="{p}" fill="none"/>'
    '<polyline points="10,10 13,10"/>'
    '<polyline points="11.5,8 13.5,10 11.5,12"/>'
    '<rect x="14" y="4" width="9" height="12" rx="1.5"/>'
    '<text x="16" y="12.5" font-size="5.5" fill="{r}" stroke="none" font-weight="bold" font-family="sans-serif">P</text>'.format(p=_PEACH, r=_RED),
    _TEXT
)

# ===== İşlemler =====

# OCR — tarama/göz
_ICONS["ocr"] = _svg(
    '<circle cx="10" cy="10" r="6"/>'
    '<line x1="14.5" y1="14.5" x2="20" y2="20"/>'
    '<line x1="7" y1="8.5" x2="13" y2="8.5"/>'
    '<line x1="7" y1="11" x2="11" y2="11"/>',
    _TEAL
)

# Sıkıştır — içe bakan oklar
_ICONS["compress"] = _svg(
    '<polyline points="4,8 8,4 12,8"/>'
    '<line x1="8" y1="4" x2="8" y2="13"/>'
    '<polyline points="4,16 8,20 12,16"/>'
    '<line x1="8" y1="20" x2="8" y2="11"/>'
    '<polyline points="14,6 18,10 14,14"/>'
    '<line x1="18" y1="10" x2="13" y2="10"/>',
    _YELLOW
)

# Şifrele — kilitli kilit
_ICONS["encrypt"] = _svg(
    '<rect x="5" y="11" width="14" height="10" rx="2"/>'
    '<path d="M8 11V7a4 4 0 018 0v4"/>'
    '<circle cx="12" cy="16" r="1.5" fill="{c}" stroke="none"/>'.format(c=_RED),
    _RED
)

# Şifre Çöz — açık kilit
_ICONS["decrypt"] = _svg(
    '<rect x="5" y="11" width="14" height="10" rx="2"/>'
    '<path d="M8 11V7a4 4 0 018 0"/>'
    '<circle cx="12" cy="16" r="1.5" fill="{c}" stroke="none"/>'.format(c=_GREEN),
    _GREEN
)

# Filigran — su damlası
_ICONS["watermark"] = _svg(
    '<path d="M12 3C12 3 5 11 5 15a7 7 0 0014 0C19 11 12 3 12 3z"/>'
    '<path d="M8.5 16.5a3.5 3.5 0 003.5 3" stroke-width="1.5"/>',
    _BLUE
)

# Not Ekle — yapışkan not
_ICONS["annotate"] = _svg(
    '<rect x="3" y="3" width="18" height="18" rx="2.5"/>'
    '<line x1="7" y1="8" x2="17" y2="8"/>'
    '<line x1="7" y1="12" x2="14" y2="12"/>'
    '<line x1="7" y1="16" x2="11" y2="16"/>',
    _YELLOW
)

# Metin Vurgula — işaretleyici kalem
_ICONS["highlight"] = _svg(
    '<path d="M14.5 3.5l6 6-10 10H4.5v-6l10-10z"/>'
    '<line x1="12" y1="6" x2="18" y2="12"/>'
    '<line x1="3" y1="22" x2="9" y2="22" stroke-width="2.5"/>',
    _MAUVE
)

# ===== Dosya Yönetimi =====

# Klasör Aç
_ICONS["open_folder"] = _svg(
    '<path d="M3 6V19a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-3H5a2 2 0 00-2 2z"/>',
    _YELLOW
)

# Farklı Kaydet — disket
_ICONS["save_as"] = _svg(
    '<path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/>'
    '<polyline points="17,21 17,13 7,13 7,21"/>'
    '<polyline points="7,3 7,8 15,8"/>',
    _BLUE
)

# Sil — çöp kutusu
_ICONS["delete"] = _svg(
    '<polyline points="3,6 5,6 21,6"/>'
    '<path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>'
    '<path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>',
    _RED
)


# ── İkon Oluşturma ──────────────────────────────────────────────────────
_cache: dict[str, QIcon] = {}


def icon(name: str, size: int = 28) -> QIcon:
    """Adına göre SVG ikonu QIcon olarak döndürür. Sonuçlar cache'lenir."""
    key = f"{name}_{size}"
    if key in _cache:
        return _cache[key]

    svg_data = _ICONS.get(name)
    if not svg_data:
        return QIcon()

    renderer = QSvgRenderer(QByteArray(svg_data.encode()))
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    qicon = QIcon(pixmap)
    _cache[key] = qicon
    return qicon
