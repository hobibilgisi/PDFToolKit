"""
PDFToolKit — Splash Screen

Uygulama açılışında logoyu (PNG veya animasyonlu GIF) gösterir,
ardından 0.5 sn içinde saydamlaşarak kaybolur.

GIF: Pillow ile her kare RGBA'ya çevrilir (beyaz arka plan → saydam).
     Animasyon bitince fade-out.
PNG: 2.5 sn gösterilir, ardından fade-out.
"""

from pathlib import Path
import sys

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QPainter, QImage, QColor


def _load_gif_frames(path: Path, white_threshold: int = 245):
    """Pillow ile GIF karelerini RGBA QPixmap listesine çevirir.

    Beyaz / beyaza yakın (#F5F5F5+) pikselleri saydam yapar.
    Döndürür: (frames: list[QPixmap], durations: list[int ms])
    """
    from PIL import Image
    import numpy as np

    gif = Image.open(str(path))
    frames: list[QPixmap] = []
    durations: list[int] = []

    for i in range(gif.n_frames):
        gif.seek(i)
        rgba = gif.convert("RGBA")
        arr = np.array(rgba)

        # Beyaz/beyaza yakın pikselleri saydam yap
        r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
        white_mask = (r >= white_threshold) & (g >= white_threshold) & (b >= white_threshold)
        arr[white_mask, 3] = 0  # alfa → 0

        h, w, _ = arr.shape
        qimg = QImage(arr.data, w, h, w * 4, QImage.Format.Format_RGBA8888).copy()
        frames.append(QPixmap.fromImage(qimg))
        durations.append(gif.info.get("duration", 30))

    return frames, durations


class SplashScreen(QWidget):
    """Frameless, ekran ortasında logo gösteren splash penceresi."""

    # Süre ayarları (ms)
    DISPLAY_MS = 2500      # statik logo ekranda kalma süresi (GIF'te kullanılmaz)
    FADE_OUT_MS = 500      # saydamlaşarak kaybolma süresi

    def __init__(self, logo_path: str | Path | None = None):
        super().__init__()

        # Frameless + her zaman üstte + transparan arka plan
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        self._frames: list[QPixmap] = []
        self._durations: list[int] = []
        self._frame_idx: int = 0
        self._frame_timer: QTimer | None = None
        self._current_pixmap: QPixmap | None = None
        self._on_finished = None

        # Logo dosyasını bul
        resolved = self._resolve_logo(logo_path)

        if resolved and resolved.suffix.lower() == ".gif":
            self._setup_gif(resolved)
        else:
            self._setup_static(resolved)

        self._center_on_screen()

    # ── Logo dosyası arama ──────────────────────────────────────────────
    def _resolve_logo(self, logo_path) -> Path | None:
        if logo_path:
            p = Path(logo_path)
            if p.exists():
                return p

        assets = Path(__file__).parent.parent / "assets"
        candidates = [
            assets / "splash logo.gif",
            assets / "splash.gif",
            assets / "splash.png",
            assets / "icon.png",
        ]
        if getattr(sys, "frozen", False):
            exe_dir = Path(sys.executable).parent
            candidates = [
                exe_dir / "splash logo.gif",
                exe_dir / "splash.gif",
                exe_dir / "splash.png",
                exe_dir / "icon.png",
            ] + candidates

        for c in candidates:
            if c.exists():
                return c
        return None

    # ── GIF (animasyonlu — Pillow ile RGBA) ────────────────────────────
    def _setup_gif(self, path: Path):
        self._frames, self._durations = _load_gif_frames(path)
        if not self._frames:
            self._setup_static(path)
            return

        self.setFixedSize(self._frames[0].size())
        self._current_pixmap = self._frames[0]
        self._frame_idx = 0

    # ── Statik resim (PNG / JPG / vb.) ──────────────────────────────────
    def _setup_static(self, path: Path | None):
        pixmap = QPixmap()
        if path and path.exists():
            pixmap.load(str(path))

        if pixmap.isNull():
            self.setFixedSize(512, 512)
        else:
            self.setFixedSize(pixmap.size())

        self._current_pixmap = pixmap

    # ── Ekran ortası ────────────────────────────────────────────────────
    def _center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + (geo.height() - self.height()) // 2
            self.move(x, y)

    # ── Paint — şeffaf arka plan ile çiz ────────────────────────────────
    def paintEvent(self, event):
        if not self._current_pixmap or self._current_pixmap.isNull():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.drawPixmap(self.rect(), self._current_pixmap)
        painter.end()

    # ── Başlat ──────────────────────────────────────────────────────────
    def start(self, on_finished=None):
        """Splash'ı göster → bekle/oynat → fade-out → callback çağır."""
        self._on_finished = on_finished
        self.setWindowOpacity(1.0)
        self.show()

        if self._frames:
            # GIF: kare kare oynat
            self._frame_idx = 0
            self._frame_timer = QTimer(self)
            self._frame_timer.timeout.connect(self._next_frame)
            self._frame_timer.start(self._durations[0])
        else:
            # Statik: 2.5 sn sonra fade-out
            QTimer.singleShot(self.DISPLAY_MS, self._fade_out)

    def _next_frame(self):
        self._frame_idx += 1
        if self._frame_idx >= len(self._frames):
            # Animasyon bitti → fade-out
            self._frame_timer.stop()
            self._fade_out()
            return

        self._current_pixmap = self._frames[self._frame_idx]
        self.update()

        # Sonraki kare için süreyi ayarla
        self._frame_timer.setInterval(self._durations[self._frame_idx])

    # ── Fade-out ────────────────────────────────────────────────────────
    def _fade_out(self):
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(self.FADE_OUT_MS)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.Type.InQuad)
        self._anim.finished.connect(self._on_fade_done)
        self._anim.start()

    def _on_fade_done(self):
        self.close()
        if self._on_finished:
            self._on_finished()
