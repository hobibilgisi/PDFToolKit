"""
PDFToolKit - İşlem Paneli Bileşeni

PDF işlem butonlarını gruplar halinde sunar.
Her buton tıklandığında ilgili core/converters fonksiyonunu çağırır.
Tüm işlemler QThread worker ile arka planda çalışarak GUI donmasını önler.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton,
    QInputDialog, QMessageBox, QFileDialog, QComboBox, QLabel
)
from PyQt6.QtCore import pyqtSignal
from send2trash import send2trash

from gui.worker import PdfWorker, BatchWorker
from utils.page_parser import parse_page_input
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class ActionPanel(QWidget):
    """İşlem butonları paneli."""

    # Sinyal: işlem tamamlandığında
    operation_completed = pyqtSignal(str)  # başarı mesajı
    operation_failed = pyqtSignal(str)     # hata mesajı
    operation_progress = pyqtSignal(int, str)  # ilerleme (yüzde, mesaj)

    def __init__(self, file_lists, parent=None):
        super().__init__(parent)
        # file_lists artık liste kabul ediyor [input_list, output_list] vb.
        self.file_lists = file_lists if isinstance(file_lists, list) else [file_lists]
        self._active_worker = None  # Aktif worker referansı (GC koruması)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ===== PDF İşlemleri =====
        pdf_group = QGroupBox("📄 PDF İşlemleri")
        pdf_layout = QVBoxLayout(pdf_group)

        self.merge_btn = QPushButton("🔗 Birleştir")
        self.merge_btn.setObjectName("primaryButton")
        self.merge_btn.setToolTip("Seçili PDF dosyalarını sırasıyla tek bir PDF'de birleştirir.\nEn az 2 dosya seçin. Sayfa seçimi yapabilirsiniz.")
        self.merge_btn.clicked.connect(self._on_merge)
        pdf_layout.addWidget(self.merge_btn)

        self.split_btn = QPushButton("✂️ Sayfalarına Ayır")
        self.split_btn.setToolTip("PDF'nin her sayfasını ayrı birer PDF dosyasına ayırır.")
        self.split_btn.clicked.connect(self._on_split)
        pdf_layout.addWidget(self.split_btn)

        self.extract_btn = QPushButton("📋 Seçili Sayfaları Çıkar")
        self.extract_btn.setToolTip("Belirtilen sayfaları çıkarıp yeni bir PDF oluşturur.\nSayfa Seçimi alanına sayfaları yazın (ör: 1,3,5-8).")
        self.extract_btn.clicked.connect(self._on_extract)
        pdf_layout.addWidget(self.extract_btn)

        self.delete_btn = QPushButton("🗑️ Sayfa Sil")
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.setToolTip("Belirtilen sayfaları siler, yeni dosya oluşturur.\nOrijinal dosyaya dokunulmaz.")
        self.delete_btn.clicked.connect(self._on_delete)
        pdf_layout.addWidget(self.delete_btn)

        self.orientation_btn = QPushButton("📐 Yatay / Dikey Yap")
        self.orientation_btn.setToolTip("Sayfaları yatay (landscape) veya dikey (portrait) yöne çevirir.\nZaten doğru yöndeki sayfalar değiştirilmez.")
        self.orientation_btn.clicked.connect(self._on_orientation)
        pdf_layout.addWidget(self.orientation_btn)

        self.insert_btn = QPushButton("📥 PDF Ekle")
        self.insert_btn.setToolTip("Bir PDF'yi başka bir PDF'nin belirli sayfasından sonra ekler.\n0 girerseniz en başa eklenir.")
        self.insert_btn.clicked.connect(self._on_insert)
        pdf_layout.addWidget(self.insert_btn)

        self.remove_selected_btn = QPushButton("🗑️ Seçilileri Sil")
        self.remove_selected_btn.setObjectName("dangerButton")
        self.remove_selected_btn.setToolTip("İşaretli dosyaları geri dönüşüm kutusuna gönderir.\nDosyalar geri dönüşüm kutusundan geri alınabilir.")
        self.remove_selected_btn.clicked.connect(self._on_remove_selected)
        pdf_layout.addWidget(self.remove_selected_btn)

        layout.addWidget(pdf_group)

        # ===== Dönüştürme =====
        convert_group = QGroupBox("🔄 Dönüştürme")
        convert_layout = QVBoxLayout(convert_group)

        self.pdf_to_word_btn = QPushButton("📝 PDF → Word")
        self.pdf_to_word_btn.setToolTip("PDF dosyasını düzenlenebilir Word (.docx) formatına çevirir.")
        self.pdf_to_word_btn.clicked.connect(self._on_pdf_to_word)
        convert_layout.addWidget(self.pdf_to_word_btn)

        self.pdf_to_excel_btn = QPushButton("📊 PDF → Excel")
        self.pdf_to_excel_btn.setToolTip("PDF içindeki tablo verilerini Excel (.xlsx) formatına çevirir.")
        self.pdf_to_excel_btn.clicked.connect(self._on_pdf_to_excel)
        convert_layout.addWidget(self.pdf_to_excel_btn)

        self.pdf_to_jpg_btn = QPushButton("🖼️ PDF → JPG")
        self.pdf_to_jpg_btn.setToolTip("PDF'nin her sayfasını ayrı JPG görsel dosyasına çevirir.\nPyMuPDF kullanır — harici kurulum gerektirmez.")
        self.pdf_to_jpg_btn.clicked.connect(self._on_pdf_to_jpg)
        convert_layout.addWidget(self.pdf_to_jpg_btn)

        self.word_to_pdf_btn = QPushButton("📄 Word → PDF")
        self.word_to_pdf_btn.setToolTip("Word (.docx) dosyasını PDF formatına çevirir.\nDosya seçme diyaloğu açılır.")
        self.word_to_pdf_btn.clicked.connect(self._on_word_to_pdf)
        convert_layout.addWidget(self.word_to_pdf_btn)

        self.excel_to_pdf_btn = QPushButton("📄 Excel → PDF")
        self.excel_to_pdf_btn.setToolTip("Excel (.xlsx) dosyasını PDF formatına çevirir.\nDosya seçme diyaloğu açılır.")
        self.excel_to_pdf_btn.clicked.connect(self._on_excel_to_pdf)
        convert_layout.addWidget(self.excel_to_pdf_btn)

        self.jpg_to_pdf_btn = QPushButton("📄 JPG → PDF")
        self.jpg_to_pdf_btn.setToolTip("Bir veya birden fazla görseli (JPG, PNG, BMP, TIFF)\ntek bir PDF dosyasına dönüştürür.")
        self.jpg_to_pdf_btn.clicked.connect(self._on_jpg_to_pdf)
        convert_layout.addWidget(self.jpg_to_pdf_btn)

        layout.addWidget(convert_group)

        # ===== Araçlar =====
        tools_group = QGroupBox("🛠️ Araçlar")
        tools_layout = QVBoxLayout(tools_group)

        self.ocr_btn = QPushButton("🔍 OCR Uygula")
        self.ocr_btn.setToolTip("Taranmış (görsel tabanlı) PDF'lere metin tanıma uygular.\nTesseract OCR kurulu olmalıdır. Toplu işlem destekler.")
        self.ocr_btn.clicked.connect(self._on_ocr)
        tools_layout.addWidget(self.ocr_btn)

        self.compress_btn = QPushButton("📦 Sıkıştır")
        self.compress_btn.setToolTip("PDF dosya boyutunu küçültür.\nHafif / Dengeli / Agresif kalite seçenekleri. Toplu işlem destekler.")
        self.compress_btn.clicked.connect(self._on_compress)
        tools_layout.addWidget(self.compress_btn)

        self.encrypt_btn = QPushButton("🔒 Şifrele")
        self.encrypt_btn.setToolTip("PDF'ye parola koruması ekler.\nBirden fazla dosya seçerek toplu şifreleme yapabilirsiniz.")
        self.encrypt_btn.clicked.connect(self._on_encrypt)
        tools_layout.addWidget(self.encrypt_btn)

        self.decrypt_btn = QPushButton("🔓 Şifre Çöz")
        self.decrypt_btn.setToolTip("Şifreli PDF'nin parolasını girerek korumayı kaldırır.")
        self.decrypt_btn.clicked.connect(self._on_decrypt)
        tools_layout.addWidget(self.decrypt_btn)

        self.watermark_btn = QPushButton("💧 Filigran Ekle")
        self.watermark_btn.setToolTip("PDF sayfalarına çapraz filigran metni ekler.\nToplu işlem destekler.")
        self.watermark_btn.clicked.connect(self._on_watermark)
        tools_layout.addWidget(self.watermark_btn)

        self.annotate_btn = QPushButton("📝 Not Ekle")
        self.annotate_btn.setToolTip("Belirtilen sayfaya yapışkan not (annotation) ekler.")
        self.annotate_btn.clicked.connect(self._on_annotate)
        tools_layout.addWidget(self.annotate_btn)
        self.highlight_btn = QPushButton("🖍️ Metin Vurgula")
        self.highlight_btn.setToolTip("PDF içinde metin arar ve bulduğu yerleri sarı ile vurgular.\nSayfa seçimi yaparsanız sadece o sayfalarda arar.")
        self.highlight_btn.clicked.connect(self._on_highlight)
        tools_layout.addWidget(self.highlight_btn)
        layout.addWidget(tools_group)

        layout.addStretch()

    # ========== Yardımcı Fonksiyonlar ==========

    def _get_selected_files(self):
        """Birden fazla listeden seçili dosyaları alır, yoksa uyarı gösterir."""
        files = []
        for file_list in self.file_lists:
             files.extend(file_list.get_selected_files())
        
        if not files:
            self.operation_failed.emit("Lütfen en az bir dosya seçin")
            return None
        return files

    def _get_first_file(self):
        """İlk seçili dosyayı alır."""
        files = self._get_selected_files()
        if not files:
            return None
        return files[0]

    def _parse_pages(self, page_str: str, pdf_path: str) -> list[int] | None:
        """Sayfa girdisini ayrıştırır."""
        from core.pdf_page_manager import get_page_count
        try:
            max_pages = get_page_count(pdf_path)
            if not page_str:
                return list(range(1, max_pages + 1))
            return parse_page_input(page_str, max_pages)
        except Exception as e:
            self.operation_failed.emit(str(e))
            return None

    def _set_buttons_enabled(self, enabled: bool):
        """Tüm işlem butonlarını etkinleştirir/devre dışı bırakır."""
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(enabled)

    def _run_worker(self, func, *args, success_msg_func=None, **kwargs):
        """
        Verilen fonksiyonu PdfWorker ile arka planda çalıştırır.

        Args:
            func: Çalıştırılacak fonksiyon.
            *args: Fonksiyon argümanları.
            success_msg_func: Sonuçtan başarı mesajı üreten callable. 
                              None ise varsayılan mesaj kullanılır.
            **kwargs: Fonksiyon keyword argümanları.
        """
        self._set_buttons_enabled(False)

        worker = PdfWorker(func, *args, **kwargs)
        worker.progress.connect(self._on_worker_progress)
        worker.finished.connect(lambda result: self._on_worker_finished(result, success_msg_func))
        worker.error.connect(self._on_worker_error)
        worker.start()
        
        # Worker referansını tut (GC tarafından silinmesini önle)
        self._active_worker = worker

    def _run_batch_worker(self, func, file_args_list, success_msg="Toplu işlem tamamlandı"):
        """
        Birden fazla dosya üzerinde aynı işlemi BatchWorker ile çalıştırır.

        Args:
            func: Her dosya için çalıştırılacak fonksiyon.
            file_args_list: [{"args": tuple, "kwargs": dict, "label": str}, ...]
            success_msg: Tamamlandığında gösterilecek mesaj.
        """
        self._set_buttons_enabled(False)

        worker = BatchWorker(func, file_args_list)
        worker.progress.connect(self._on_worker_progress)
        worker.finished.connect(
            lambda results: self._on_batch_finished(results, success_msg)
        )
        worker.error.connect(self._on_worker_error)
        worker.start()
        
        self._active_worker = worker

    def _on_worker_progress(self, percent, message):
        """Worker ilerleme sinyali."""
        self.operation_progress.emit(percent, message)

    def _on_worker_finished(self, result, success_msg_func=None):
        """Worker başarıyla tamamlandığında."""
        self._set_buttons_enabled(True)
        self._active_worker = None

        if success_msg_func and result is not None:
            msg = success_msg_func(result)
        elif hasattr(result, 'name'):
            msg = f"İşlem tamamlandı: {result.name}"
        elif isinstance(result, list):
            msg = f"İşlem tamamlandı: {len(result)} dosya oluşturuldu"
        else:
            msg = "İşlem tamamlandı"

        self.operation_completed.emit(msg)

    def _on_batch_finished(self, results, success_msg):
        """Batch worker tamamlandığında."""
        self._set_buttons_enabled(True)
        self._active_worker = None
        self.operation_completed.emit(f"{success_msg}: {len(results)} dosya işlendi")

    def _on_worker_error(self, error_msg):
        """Worker hata sinyali."""
        self._set_buttons_enabled(True)
        self._active_worker = None
        self.operation_failed.emit(error_msg)

    # ========== PDF İşlemleri ==========

    def _on_remove_selected(self):
        """Seçili dosyaları tüm listelerden toplayıp geri dönüşüm kutusuna gönderir."""
        all_paths: list[Path] = []
        for file_list in self.file_lists:
            selected = file_list.get_selected_files()
            for f in selected:
                p = Path(f["path"])
                if p not in all_paths:
                    all_paths.append(p)

        if not all_paths:
            self.operation_failed.emit("Silinecek dosya seçilmedi.")
            return

        reply = QMessageBox.question(
            self,
            "Silme Onayı",
            f"Seçilen {len(all_paths)} dosya geri dönüşüm kutusuna gönderilecek.\nDevam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        deleted = 0
        errors: list[str] = []
        for p in all_paths:
            try:
                if p.exists():
                    send2trash(str(p))
                    deleted += 1
            except Exception as e:
                errors.append(f"{p.name}: {e}")

        # Listeleri güncelle
        for file_list in self.file_lists:
            file_list.refresh_files()

        if errors:
            self.operation_failed.emit(
                f"{deleted} dosya silindi, {len(errors)} hata:\n" + "\n".join(errors)
            )
        else:
            self.operation_completed.emit(
                f"{deleted} dosya geri dönüşüm kutusuna gönderildi."
            )

    def _on_merge(self):
        """PDF birleştirme."""
        files = self._get_selected_files()
        if not files or len(files) < 2:
            self.operation_failed.emit("Birleştirmek için en az 2 dosya seçin")
            return

        from core.pdf_merger import merge_pdfs

        file_list = []
        for f in files:
            pages = self._parse_pages(f["pages"], f["path"])
            if pages is None:
                return
            file_list.append({"path": f["path"], "pages": pages if f["pages"] else None})

        self._run_worker(
            merge_pdfs, file_list,
            success_msg_func=lambda r: f"Birleştirme tamamlandı: {r.name}"
        )

    def _on_split(self):
        """PDF sayfalarına ayırma."""
        file_info = self._get_first_file()
        if not file_info:
            return

        from core.pdf_splitter import split_all_pages
        self._run_worker(
            split_all_pages, file_info["path"],
            success_msg_func=lambda r: f"{len(r)} sayfaya ayrıldı"
        )

    def _on_extract(self):
        """Seçili sayfaları çıkarma."""
        file_info = self._get_first_file()
        if not file_info:
            return

        if not file_info["pages"]:
            self.operation_failed.emit("Lütfen çıkarılacak sayfaları belirtin")
            return

        from core.pdf_splitter import extract_pages
        pages = self._parse_pages(file_info["pages"], file_info["path"])
        if pages is None:
            return
        self._run_worker(
            extract_pages, file_info["path"], pages,
            success_msg_func=lambda r: f"Sayfalar çıkarıldı: {r.name}"
        )

    def _on_delete(self):
        """Sayfa silme."""
        file_info = self._get_first_file()
        if not file_info:
            return

        if not file_info["pages"]:
            self.operation_failed.emit("Lütfen silinecek sayfaları belirtin")
            return

        from core.pdf_page_manager import delete_pages
        pages = self._parse_pages(file_info["pages"], file_info["path"])
        if pages is None:
            return
        self._run_worker(
            delete_pages, file_info["path"], pages,
            success_msg_func=lambda r: f"Sayfalar silindi: {r.name}"
        )

    def _on_orientation(self):
        """Sayfa yönü değiştirme (yatay/dikey)."""
        file_info = self._get_first_file()
        if not file_info:
            return

        orientation, ok = QInputDialog.getItem(
            self, "Sayfa Yönü",
            "Sayfaları hangi yöne çevirmek istiyorsunuz?",
            ["Yatay (Landscape)", "Dikey (Portrait)"], 0, False
        )
        if not ok:
            return

        orient_val = "landscape" if "Yatay" in orientation else "portrait"

        from core.pdf_page_manager import set_page_orientation
        pages = self._parse_pages(file_info["pages"], file_info["path"])
        if pages is None:
            return

        yon_str = "yatay" if orient_val == "landscape" else "dikey"
        self._run_worker(
            set_page_orientation, file_info["path"], pages, orient_val,
            success_msg_func=lambda r: f"Sayfalar {yon_str} yapıldı: {r.name}"
        )

    def _on_insert(self):
        """PDF ekleme."""
        file_info = self._get_first_file()
        if not file_info:
            return

        source_path, _ = QFileDialog.getOpenFileName(
            self, "Eklenecek PDF'yi Seçin", "", "PDF Dosyaları (*.pdf)"
        )
        if not source_path:
            return

        page_num, ok = QInputDialog.getInt(
            self, "Ekleme Noktası",
            "Hangi sayfadan sonra eklensin (0 = en başa):",
            0, 0, 9999
        )
        if not ok:
            return

        from core.pdf_merger import insert_pdf
        self._run_worker(
            insert_pdf, file_info["path"], source_path, page_num,
            success_msg_func=lambda r: f"PDF eklendi: {r.name}"
        )

    # ========== Dönüştürme ==========

    def _on_pdf_to_word(self):
        file_info = self._get_first_file()
        if not file_info:
            return
        from converters.from_pdf import pdf_to_word
        self._run_worker(
            pdf_to_word, file_info["path"],
            success_msg_func=lambda r: f"PDF -> Word: {r.name}"
        )

    def _on_pdf_to_excel(self):
        file_info = self._get_first_file()
        if not file_info:
            return
        from converters.from_pdf import pdf_to_excel
        self._run_worker(
            pdf_to_excel, file_info["path"],
            success_msg_func=lambda r: f"PDF -> Excel: {r.name}"
        )

    def _on_pdf_to_jpg(self):
        file_info = self._get_first_file()
        if not file_info:
            return
        from converters.from_pdf import pdf_to_jpg
        self._run_worker(
            pdf_to_jpg, file_info["path"],
            success_msg_func=lambda r: f"PDF -> JPG: {len(r)} gorsel"
        )

    def _on_word_to_pdf(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Word Dosyası Seçin", "",
            "Word Dosyaları (*.docx *.doc)"
        )
        if not path:
            return
        from converters.to_pdf import word_to_pdf
        self._run_worker(
            word_to_pdf, path,
            success_msg_func=lambda r: f"Word -> PDF: {r.name}"
        )

    def _on_excel_to_pdf(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seçin", "",
            "Excel Dosyaları (*.xlsx *.xls)"
        )
        if not path:
            return
        from converters.to_pdf import excel_to_pdf
        self._run_worker(
            excel_to_pdf, path,
            success_msg_func=lambda r: f"Excel -> PDF: {r.name}"
        )

    def _on_jpg_to_pdf(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Görsel Dosyaları Seçin", "",
            "Görseller (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        if not paths:
            return
        if len(paths) == 1:
            from converters.to_pdf import jpg_to_pdf
            self._run_worker(
                jpg_to_pdf, paths[0],
                success_msg_func=lambda r: f"JPG -> PDF: {r.name}"
            )
        else:
            from converters.to_pdf import images_to_pdf
            self._run_worker(
                images_to_pdf, paths,
                success_msg_func=lambda r: f"JPG -> PDF: {r.name}"
            )

    # ========== Araçlar ==========

    def _on_ocr(self):
        """OCR — tek veya toplu dosya desteği."""
        files = self._get_selected_files()
        if not files:
            return

        from core.pdf_ocr import ocr_pdf

        if len(files) == 1:
            self._run_worker(
                ocr_pdf, files[0]["path"],
                success_msg_func=lambda r: f"OCR tamamlandı: {r.name}"
            )
        else:
            file_args = [
                {"args": (f["path"],), "kwargs": {}, "label": Path(f["path"]).name}
                for f in files
            ]
            self._run_batch_worker(ocr_pdf, file_args, "OCR tamamlandı")

    def _on_compress(self):
        """Sıkıştırma — tek veya toplu dosya desteği."""
        files = self._get_selected_files()
        if not files:
            return

        quality, ok = QInputDialog.getItem(
            self, "Sıkıştırma Kalitesi",
            "Kalite seçin:",
            ["high (Hafif)", "medium (Dengeli)", "low (Agresif)"], 1, False
        )
        if not ok:
            return

        quality_val = quality.split(" ")[0]
        from core.pdf_compressor import compress_pdf

        if len(files) == 1:
            self._run_worker(
                compress_pdf, files[0]["path"], quality=quality_val,
                success_msg_func=lambda r: f"Sıkıştırma tamamlandı: {r.name}"
            )
        else:
            file_args = [
                {"args": (f["path"],), "kwargs": {"quality": quality_val},
                 "label": Path(f["path"]).name}
                for f in files
            ]
            self._run_batch_worker(compress_pdf, file_args, "Toplu sıkıştırma tamamlandı")

    def _on_encrypt(self):
        """Şifreleme — tek veya toplu dosya desteği."""
        files = self._get_selected_files()
        if not files:
            return

        password, ok = QInputDialog.getText(
            self, "PDF Sifreleme", "Parola girin:"
        )
        if not ok or not password:
            return

        from core.pdf_encryptor import encrypt_pdf

        if len(files) == 1:
            self._run_worker(
                encrypt_pdf, files[0]["path"], password,
                success_msg_func=lambda r: f"Şifreleme tamamlandı: {r.name}"
            )
        else:
            file_args = [
                {"args": (f["path"], password), "kwargs": {},
                 "label": Path(f["path"]).name}
                for f in files
            ]
            self._run_batch_worker(encrypt_pdf, file_args, "Toplu şifreleme tamamlandı")

    def _on_decrypt(self):
        file_info = self._get_first_file()
        if not file_info:
            return

        password, ok = QInputDialog.getText(
            self, "Şifre Çözme", "Parola girin:"
        )
        if not ok or not password:
            return

        from core.pdf_encryptor import decrypt_pdf
        self._run_worker(
            decrypt_pdf, file_info["path"], password,
            success_msg_func=lambda r: f"Şifre çözüldü: {r.name}"
        )

    def _on_watermark(self):
        """Filigran — tek veya toplu dosya desteği."""
        files = self._get_selected_files()
        if not files:
            return

        text, ok = QInputDialog.getText(
            self, "Filigran", "Filigran metnini girin:"
        )
        if not ok or not text:
            return

        from core.pdf_watermark import add_watermark

        if len(files) == 1:
            self._run_worker(
                add_watermark, files[0]["path"], text,
                success_msg_func=lambda r: f"Filigran eklendi: {r.name}"
            )
        else:
            file_args = [
                {"args": (f["path"], text), "kwargs": {},
                 "label": Path(f["path"]).name}
                for f in files
            ]
            self._run_batch_worker(add_watermark, file_args, "Toplu filigran eklendi")

    def _on_annotate(self):
        file_info = self._get_first_file()
        if not file_info:
            return

        text, ok = QInputDialog.getText(
            self, "Not Ekleme", "Not metnini girin:"
        )
        if not ok or not text:
            return

        page_num, ok = QInputDialog.getInt(
            self, "Sayfa Seçimi",
            "Hangi sayfaya not eklensin:",
            1, 1, 9999
        )
        if not ok:
            return

        from core.pdf_annotator import add_text_annotation
        self._run_worker(
            add_text_annotation, file_info["path"], page_num, text,
            success_msg_func=lambda r: f"Not eklendi: {r.name}"
        )

    def _on_highlight(self):
        """Metin arama ve vurgulama."""
        file_info = self._get_first_file()
        if not file_info:
            return

        text, ok = QInputDialog.getText(
            self, "Metin Vurgulama",
            "Vurgulanacak metni girin:"
        )
        if not ok or not text:
            return

        from core.pdf_annotator import highlight_text

        # Sayfa secimi varsa sadece o sayfalarda ara
        pages = None
        if file_info["pages"]:
            pages = self._parse_pages(file_info["pages"], file_info["path"])
            if pages is None:
                return

        self._run_worker(
            highlight_text, file_info["path"], text, pages=pages,
            success_msg_func=lambda r: f"Metin vurgulandı: {r.name}"
        )