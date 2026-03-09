"""
PDFToolKit - Ana Pencere

Uygulamanın ana penceresi: sol panel (dosya listeleri) + sağ panel (işlem butonları).
"""

from pathlib import Path
import sys

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QScrollArea, QMenuBar, QMenu, QDialog,
    QTextBrowser, QDialogButtonBox, QMessageBox, QPushButton, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon

from gui.file_list_widget import FileListWidget
from gui.action_panel import ActionPanel
from gui.status_bar import StatusBar
from gui.styles import DARK_THEME
from config.settings import settings
from utils.updater import (
    UpdateChecker, UpdateDownloader, apply_update, cleanup_old_exe
)

class MainWindow(QMainWindow):
    """PDFToolKit ana penceresi."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDFToolKit")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)

        # Uygulama ikonu
        icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
        if not icon_path.exists():
            # EXE dağıtımında icon.ico, exe ile aynı klasörde
            icon_path = Path(sys.executable).parent / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Önceki güncelleme dosyasını temizle (.exe.old)
        cleanup_old_exe()

        # Güncelleme ile ilgili state
        self._pending_update_version: str = ""
        self._pending_update_url: str = ""
        self._update_downloader: UpdateDownloader | None = None

        # Koyu tema uygula
        self.setStyleSheet(DARK_THEME)

        self._setup_menu()
        self._setup_ui()
        self._connect_signals()

    def _setup_menu(self):
        """Menü çubuğunu oluşturur."""
        menubar = self.menuBar()

        # Dosya menüsü
        file_menu = menubar.addMenu("Dosya")

        exit_action = QAction("Çıkış", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Yardım menüsü
        help_menu = menubar.addMenu("Yardım")

        guide_action = QAction("📖 Kullanım Kılavuzu", self)
        guide_action.setShortcut("F1")
        guide_action.triggered.connect(self._on_guide)
        help_menu.addAction(guide_action)

        requirements_action = QAction("⚙️ Sistem Gereksinimleri", self)
        requirements_action.triggered.connect(self._on_requirements)
        help_menu.addAction(requirements_action)

        help_menu.addSeparator()

        about_action = QAction("ℹ️ Hakkında", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

        # Menü çubuğuna doğrudan Yenile butonu
        refresh_menu_action = QAction("🔄 Yenile", self)
        refresh_menu_action.setShortcut("F5")
        refresh_menu_action.setToolTip("Dosya listelerini yenile (F5)")
        refresh_menu_action.triggered.connect(self._on_refresh)
        menubar.addAction(refresh_menu_action)

    def _setup_ui(self):
        """Ana arayüzü oluşturur."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Splitter: sol (dosya listeleri) + sağ (işlem paneli)
        splitter_main = QSplitter(Qt.Orientation.Horizontal)

        # Sol panel - İki liste (Input ve Output) alt alta
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        self.input_list = FileListWidget(
            title="📥 Input", directory=settings.input_dir, accept_all_formats=True
        )
        self.output_list = FileListWidget(
            title="📤 Output", directory=settings.output_dir, accept_all_formats=True, allow_drop=False, allow_drag_out=True
        )
        
        left_splitter.addWidget(self.input_list)
        left_splitter.addWidget(self.output_list)
        left_splitter.setSizes([350, 350])

        splitter_main.addWidget(left_splitter)

        # Sağ panel - İşlem butonları (scroll destekli)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(280)
        scroll_area.setMinimumWidth(220)

        self.action_panel = ActionPanel([self.input_list, self.output_list])
        scroll_area.setWidget(self.action_panel)

        splitter_main.addWidget(scroll_area)

        # Splitter oranları: %75 sol, %25 sağ
        splitter_main.setSizes([800, 280])

        main_layout.addWidget(splitter_main)

        # Durum çubuğu
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        # Mevcut sürüm etiketi (durum çubuğunda kalıcı)
        from PyQt6.QtWidgets import QLabel
        current_ver = QApplication.applicationVersion()
        self._version_label = QLabel(f"PDFToolKit v{current_ver}")
        self._version_label.setStyleSheet("color: #6c7086; font-size: 11px; padding: 0 6px;")
        self.status_bar.addPermanentWidget(self._version_label)

        # Güncelleme bildirimi butonu (başlangıçta gizli)
        self._update_btn = QPushButton("")
        self._update_btn.setVisible(False)
        self._update_btn.setStyleSheet(
            "QPushButton { background: #313244; color: #a6e3a1; "
            "border: 1px solid #a6e3a1; border-radius: 4px; "
            "padding: 2px 10px; font-size: 12px; } "
            "QPushButton:hover { background: #45475a; }"
        )
        self._update_btn.clicked.connect(self._on_update_btn_clicked)
        self.status_bar.addPermanentWidget(self._update_btn)

    def _connect_signals(self):
        """Sinyal-slot bağlantıları."""
        # İşlem sonuçları → durum çubuğu
        self.action_panel.operation_completed.connect(
            self._on_operation_completed
        )
        self.action_panel.operation_failed.connect(
            self.status_bar.show_error
        )
        # İlerleme sinyali → progress bar
        self.action_panel.operation_progress.connect(
            self._on_operation_progress
        )

        # Dosya listesi değişiklikleri
        self.input_list.files_changed.connect(self._on_files_changed)
        self.output_list.files_changed.connect(self._on_files_changed)

        # İlk yükleme
        self._on_files_changed()

        # Güncelleme kontrolcüsü — arka planda, uygulama açılışını yavaşlatmaz
        QTimer.singleShot(2000, self._start_update_check)

    def _on_operation_completed(self, message):
        """Bir işlem başarıyla tamamlandığında çıktı listesini yeniler."""
        self.status_bar.show_success(message)
        self.status_bar.hide_progress()
        self.output_list.refresh_files()
        self.output_list.scroll_to_bottom()

    def _on_operation_progress(self, percent, message):
        """İlerleme güncellemesi geldiğinde progress bar'ı gösterir."""
        self.status_bar.show_progress(percent)
        self.status_bar.show_message(message, timeout_ms=0)

    def _on_files_changed(self):
        """Dosya listesi değiştiğinde çağrılır."""
        count = self.input_list.get_file_count() + self.output_list.get_file_count()
        self.status_bar.update_file_count(count)

    def _on_refresh(self):
        """Dosya listelerini yeniler."""
        self.input_list.refresh_files()
        self.output_list.refresh_files()
        self.status_bar.show_message("Dosya listeleri yenilendi")

    # ─── Güncelleme ─────────────────────────────────────────────────────────

    def _start_update_check(self):
        """Uygulama açıldıktan 2 saniye sonra arka planda güncelleme kontrolü başlatır."""
        checker = UpdateChecker(
            current_version=QApplication.applicationVersion(),
            skipped_version=settings.skipped_update_version,
            parent=self
        )
        checker.update_available.connect(self._on_update_available)
        checker.start()

    def _on_update_available(self, version: str, url: str, release_name: str):
        """Yeni sürüm bulununca durum çubuğuna bildirim düğmesi gösterir."""
        self._pending_update_version = version
        self._pending_update_url = url
        self._pending_release_name = release_name
        current_ver = QApplication.applicationVersion()
        btn_text = f"v{current_ver} → v{version}"
        if release_name:
            btn_text += f" ({release_name})"
        btn_text += " — Güncelle"
        self._update_btn.setText(f"🔄 {btn_text}")
        self._update_btn.setVisible(True)

    def _on_update_btn_clicked(self):
        """Güncelle düğmesine tıklandığında seçenek diyaloğu gösterir."""
        reply = QMessageBox.question(
            self,
            "Güncelleme Mevcut",
            f"<b>PDFToolKit v{self._pending_update_version}</b> yayınlandı.<br><br>"
            "Şimdi güncellemek ister misiniz?<br>"
            "<small>Güncelleme sırasında uygulama kapanmayacak; "
            "indirme tamamlanınca yeniden başlatmanız istenecek.</small>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ignore,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._start_download()
        elif reply == QMessageBox.StandardButton.Ignore:
            # "Bu sürümü atla" — bir daha sorma
            settings.set_skipped_version(self._pending_update_version)
            self._update_btn.setVisible(False)
        # No: düğme yerinde kalır, kullanıcı daha sonra tıklayabilir

    def _start_download(self):
        """Güncelleme ZIP'ini arka planda indirir."""
        self._update_btn.setEnabled(False)
        self._update_btn.setText("⬇️ İndiriliyor...")
        self.status_bar.show_message("Güncelleme indiriliyor...", timeout_ms=0)

        self._update_downloader = UpdateDownloader(self._pending_update_url, parent=self)
        self._update_downloader.progress.connect(self._on_download_progress)
        self._update_downloader.finished.connect(self._on_download_finished)
        self._update_downloader.start()

    def _on_download_progress(self, downloaded: int, total: int):
        if total > 0:
            pct = int((downloaded / total) * 100)
            self.status_bar.show_progress(pct)
            mb_d = downloaded / 1_048_576
            mb_t = total / 1_048_576
            self.status_bar.show_message(
                f"İndiriliyor: {mb_d:.1f} / {mb_t:.1f} MB", timeout_ms=0
            )

    def _on_download_finished(self, success: bool):
        self.status_bar.hide_progress()
        if not success:
            self.status_bar.show_error("İndirme başarısız. İnternet bağlantısını kontrol edin.")
            self._update_btn.setEnabled(True)
            self._update_btn.setText(f"🔄 Yeni sürüm: v{self._pending_update_version} — Tekrar dene")
            return

        zip_path = self._update_downloader.zip_path
        ok = apply_update(zip_path)

        if ok:
            QMessageBox.information(
                self,
                "Güncelleme Başlatıldı",
                f"<b>PDFToolKit v{self._pending_update_version}</b> güncelleme hazırlandı.<br><br>"
                "Uygulama şimdi kapanacak ve güncelleme uygulanacak.<br>"
                "İşlem bitince uygulama otomatik olarak yeniden başlayacak."
            )
            # Uygulamayı kapat — batch script devralacak
            QApplication.quit()
        else:
            self.status_bar.show_error("Güncelleme uygulanamadı.")
            self._update_btn.setEnabled(True)

    # ─── Menü Diyalogları ────────────────────────────────────────────────────

    def _on_about(self):
        """Hakkında diyaloğu."""
        ver = QApplication.applicationVersion()
        QMessageBox.about(
            self,
            "PDFToolKit Hakkında",
            f"<h3>PDFToolKit v{ver}</h3>"
            "<p>Kapsamlı masaüstü PDF işleme uygulaması.</p>"
            "<p><b>Geliştirme:</b> Python 3.11+ | PyQt6 | pypdf</p>"
            "<p><b>Lisans:</b> MIT</p>"
        )

    def _on_guide(self):
        """Kullanım kılavuzu diyaloğu."""
        dlg = QDialog(self)
        dlg.setWindowTitle("📖 Kullanım Kılavuzu")
        dlg.resize(700, 550)
        layout = QVBoxLayout(dlg)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._get_guide_html())
        layout.addWidget(browser)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(dlg.close)
        layout.addWidget(btn_box)

        dlg.exec()

    def _on_requirements(self):
        """Sistem gereksinimleri diyaloğu."""
        dlg = QDialog(self)
        dlg.setWindowTitle("⚙️ Sistem Gereksinimleri")
        dlg.resize(600, 450)
        layout = QVBoxLayout(dlg)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._get_requirements_html())
        layout.addWidget(browser)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(dlg.close)
        layout.addWidget(btn_box)

        dlg.exec()

    @staticmethod
    def _get_guide_html() -> str:
        """Kullanım kılavuzu HTML içeriği."""
        return """
        <style>
            body { font-family: 'Segoe UI', sans-serif; }
            h2 { color: #89b4fa; border-bottom: 1px solid #45475a; padding-bottom: 4px; }
            h3 { color: #a6e3a1; margin-top: 14px; }
            .shortcut { color: #f9e2af; font-weight: bold; }
            .example { background: #313244; padding: 6px 10px; border-radius: 4px;
                       margin: 4px 0; color: #cdd6f4; }
            ul { margin: 4px 0 8px 0; }
            li { margin: 2px 0; }
        </style>

        <h2>📄 PDF İşlemleri</h2>

        <h3>🔗 Birleştir</h3>
        <p>Birden fazla PDF dosyasını tek bir PDF'de birleştirir.</p>
        <ul>
            <li>En az <b>2 dosya</b> seçin (checkbox ile işaretleyin).</li>
            <li>Dosyalar tablodaki sıraya göre birleştirilir (▲▼ ile sıra değiştirin).</li>
            <li>Sayfa seçimi yaparsanız sadece o sayfalar alınır.</li>
        </ul>
        <div class="example">Örnek: 3 PDF seçip birleştirince → <b>birlesik (a, b, c).pdf</b></div>

        <h3>✂️ Sayfalarına Ayır</h3>
        <p>PDF'nin her sayfasını ayrı birer PDF dosyasına ayırır.</p>
        <ul>
            <li>Tek dosya seçin.</li>
            <li>Her sayfa ayrı dosya olarak output klasörüne kaydedilir.</li>
        </ul>
        <div class="example">Örnek: 5 sayfalık PDF → <b>dosya_sayfa1.pdf, dosya_sayfa2.pdf...</b></div>

        <h3>📋 Seçili Sayfaları Çıkar</h3>
        <p>PDF'den belirli sayfaları çıkarıp yeni bir PDF oluşturur.</p>
        <ul>
            <li>Dosya seçin ve <b>Sayfa Seçimi</b> alanına sayfa numaralarını girin.</li>
            <li>Format: <code>1,3,5</code> veya <code>2-6</code> veya <code>1-3,7,10-12</code></li>
        </ul>
        <div class="example">Örnek: a.pdf'den 2,3 → <b>a (çıkarılan 2,3. sayfalar).pdf</b></div>

        <h3>🗑️ Sayfa Sil</h3>
        <p>PDF'den belirtilen sayfaları kalıcı olarak siler.</p>
        <ul>
            <li>Sayfa Seçimi alanına silinecek sayfaları yazın.</li>
            <li>Orijinal dosyaya dokunulmaz, yeni dosya oluşturulur.</li>
        </ul>
        <div class="example">Örnek: a.pdf'den 2. sayfa → <b>a (2. sayfa silindi).pdf</b></div>

        <h3>📐 Yatay / Dikey Yap</h3>
        <p>Sayfaları yatay (landscape) veya dikey (portrait) yöne çevirir.</p>
        <ul>
            <li>Zaten doğru yöndeki sayfalar değiştirilmez.</li>
            <li>Dikey→Yatay: Saat yönünde döner.</li>
            <li>Yatay→Dikey: Saat yönü tersine döner.</li>
        </ul>

        <h3>📥 PDF Ekle</h3>
        <p>Bir PDF'yi başka bir PDF'nin belirli sayfasından sonra ekler.</p>
        <ul>
            <li>Hedef dosyayı seçin, ardından eklenecek PDF'yi belirtin.</li>
            <li>0 girerseniz en başa eklenir.</li>
        </ul>

        <h3>🗑️ Seçilileri Sil</h3>
        <p>İşaretli dosyaları <b>geri dönüşüm kutusuna</b> gönderir. Dosyalar geri alınabilir.</p>

        <hr>
        <h2>🔄 Dönüştürme</h2>

        <h3>📝 PDF → Word</h3>
        <p>PDF dosyasını düzenlenebilir Word (.docx) formatına çevirir.</p>

        <h3>📊 PDF → Excel</h3>
        <p>PDF içindeki tablo verilerini Excel (.xlsx) formatına çevirir.</p>

        <h3>🖼️ PDF → JPG</h3>
        <p>PDF'nin her sayfasını ayrı JPG görsel dosyasına çevirir.</p>
        <ul><li>PyMuPDF kullanır — harici kurulum gerektirmez.</li></ul>

        <h3>📄 Word → PDF</h3>
        <p>Word dosyasını (.docx) PDF formatına çevirir.</p>
        <ul><li>Office kuruluysa sayfa düzeni birebir korunur (COM).</li></ul>

        <h3>📄 Excel → PDF</h3>
        <p>Excel dosyasını (.xlsx) PDF formatına çevirir.</p>
        <ul><li>Office kuruluysa hücre yapısı birebir korunur (COM).</li></ul>

        <h3>📄 JPG → PDF</h3>
        <p>Bir veya birden fazla görseli tek bir PDF'e dönüştürür.</p>

        <hr>
        <h2>🛠️ Araçlar</h2>

        <h3>🔍 OCR Uygula</h3>
        <p>Taranmış (görsel tabanlı) PDF'lere metin tanıma uygular.</p>
        <ul>
            <li>Tesseract OCR kurulu olmalıdır.</li>
            <li>Birden fazla dosya seçerek toplu OCR yapabilirsiniz.</li>
        </ul>

        <h3>📦 Sıkıştır</h3>
        <p>PDF dosya boyutunu küçültür. 3 kalite seviyesi:</p>
        <ul>
            <li><b>high</b> — Hafif sıkıştırma, kalite korunur.</li>
            <li><b>medium</b> — Dengeli (önerilen).</li>
            <li><b>low</b> — Agresif, boyut çok küçülür ama kalite düşer.</li>
        </ul>

        <h3>🔒 Şifrele</h3>
        <p>PDF'ye parola koruması ekler. Toplu şifreleme destekler.</p>

        <h3>🔓 Şifre Çöz</h3>
        <p>Şifreli PDF'nin parolasını girerek korumasını kaldırır.</p>

        <h3>💧 Filigran Ekle</h3>
        <p>PDF sayfalarına çapraz filigran metni ekler. Toplu destekler.</p>

        <h3>📝 Not Ekle</h3>
        <p>Belirtilen sayfaya yapışkan not (annotation) ekler.</p>

        <h3>🖍️ Metin Vurgula</h3>
        <p>PDF içinde metin arar ve bulunan yerleri sarı ile vurgular.</p>
        <ul><li>Sayfa seçimi yaparsanız sadece o sayfalarda arar.</li></ul>

        <hr>
        <h2>⌨️ Kısayollar</h2>
        <ul>
            <li><span class="shortcut">F5</span> — Dosya listelerini yenile</li>
            <li><span class="shortcut">F1</span> — Kullanım kılavuzu</li>
            <li><span class="shortcut">Ctrl+Q</span> — Çıkış</li>
            <li><b>Çift tıklama</b> — Dosyayı varsayılan uygulamada açar</li>
            <li><b>Sürükle-bırak</b> — Dışarıdan dosya ekler (PDF, Word, Excel, JPG, PNG)</li>
            <li><b>☑ başlığa tıkla</b> — Tümünü seç / kaldır</li>
        </ul>

        <hr>
        <h2>💡 Sayfa Seçimi Formatları</h2>
        <ul>
            <li><b>Boş bırak</b> veya <b>tümü</b> → Tüm sayfalar</li>
            <li><b>3</b> → Sadece 3. sayfa</li>
            <li><b>2-6</b> → 2'den 6'ya kadar</li>
            <li><b>1,4,7</b> → Tek tek seçim</li>
            <li><b>1-3,5,8-10</b> → Karışık</li>
        </ul>
        """

    @staticmethod
    def _get_requirements_html() -> str:
        """Sistem gereksinimleri HTML içeriği."""
        return """
        <style>
            body { font-family: 'Segoe UI', sans-serif; }
            h2 { color: #89b4fa; border-bottom: 1px solid #45475a; padding-bottom: 4px; }
            h3 { color: #a6e3a1; margin-top: 14px; }
            code { background: #313244; padding: 2px 6px; border-radius: 3px; color: #f9e2af; }
            .cmd { background: #1e1e2e; padding: 8px 12px; border-radius: 4px;
                   margin: 4px 0; color: #a6e3a1; font-family: monospace; }
        </style>

        <h2>⚙️ Sistem Gereksinimleri</h2>

        <h3>Python</h3>
        <p>Python <b>3.11</b> veya üzeri gereklidir.</p>
        <div class="cmd">python --version</div>
        <p>İndirme: <a href="https://www.python.org/downloads/">python.org/downloads</a></p>

        <h3>Python Paketleri</h3>
        <p>Tüm bağımlılıkları yüklemek için:</p>
        <div class="cmd">pip install -r requirements.txt</div>

        <table border="0" cellpadding="4" cellspacing="0">
        <tr><td><b>Paket</b></td><td><b>Amaç</b></td><td><b>Versiyon</b></td></tr>
        <tr><td>PyQt6</td><td>Arayüz</td><td>≥ 6.6</td></tr>
        <tr><td>pypdf</td><td>PDF okuma/yazma</td><td>≥ 4.0</td></tr>
        <tr><td>PyMuPDF (fitz)</td><td>PDF işleme, PDF→JPG, OCR</td><td>≥ 1.23</td></tr>
        <tr><td>pytesseract</td><td>OCR motor arayüzü</td><td>≥ 0.3</td></tr>
        <tr><td>pywin32</td><td>Office COM (Word/Excel→PDF)</td><td>≥ 306</td></tr>
        <tr><td>python-docx</td><td>Word dosya desteği</td><td>≥ 1.1</td></tr>
        <tr><td>pdf2docx</td><td>PDF → Word dönüşüm</td><td>≥ 0.5</td></tr>
        <tr><td>openpyxl</td><td>Excel dosya desteği</td><td>≥ 3.1</td></tr>
        <tr><td>fpdf2</td><td>PDF oluşturma (fallback)</td><td>≥ 2.7</td></tr>
        <tr><td>Pillow</td><td>Görsel işleme</td><td>≥ 10.0</td></tr>
        <tr><td>python-dotenv</td><td>Ortam değişkenleri</td><td>≥ 1.0</td></tr>
        </table>

        <h3>Harici Yazılımlar</h3>

        <h4>Microsoft Office (Word/Excel → PDF birebir dönüşüm)</h4>
        <p>Word ve Excel dosyalarını sayfa düzeni korunarak PDF'e dönüştürmek için
           <b>Microsoft Office</b> (Word + Excel) kurulu olmalıdır.</p>
        <p>Office kurulu değilse fpdf2 fallback yöntemi kullanılır
           (düzen tam korunamaz).</p>

        <h4>Tesseract OCR (OCR özelliği için gerekli)</h4>
        <p>OCR işlemleri için <b>Tesseract</b> kurulu olmalıdır.</p>
        <ol>
            <li><a href="https://github.com/UB-Mannheim/tesseract/wiki">
                Tesseract Windows Installer</a> sayfasından indirin.</li>
            <li>Kurulum sırasında <b>Turkish</b> dil paketini ekleyin.</li>
            <li>Kurulum yolunu (ör: <code>C:\\Program Files\\Tesseract-OCR</code>)
                sistem PATH'ine ekleyin.</li>
        </ol>
        <p>Kontrol:</p>
        <div class="cmd">tesseract --version</div>

        <hr>
        <h2>📋 Versiyon Bilgileri</h2>
        <table border="0" cellpadding="4" cellspacing="0">
        <tr><td><b>Uygulama</b></td><td>PDFToolKit v0.2.0</td></tr>
        <tr><td><b>Python</b></td><td>3.11+</td></tr>
        <tr><td><b>GUI</b></td><td>PyQt6</td></tr>
        <tr><td><b>PDF Motor</b></td><td>pypdf + PyMuPDF</td></tr>
        <tr><td><b>Platform</b></td><td>Windows 10/11</td></tr>
        </table>
        """
