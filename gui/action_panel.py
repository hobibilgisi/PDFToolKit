"""
PDFToolKit - İşlem Paneli Bileşeni

PDF işlem butonlarını gruplar halinde sunar.
Her buton tıklandığında ilgili core/converters fonksiyonunu çağırır.
Tüm işlemler QThread worker ile arka planda çalışarak GUI donmasını önler.
"""

import os
import sys
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton,
    QInputDialog, QMessageBox, QFileDialog, QComboBox, QLabel,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve
from send2trash import send2trash


class CollapsibleGroupBox(QWidget):
    """Daraltılabilir grup kutusu. Başlığa tıklanınca içerik açılır/kapanır."""

    def __init__(self, title: str, collapsed: bool = True, parent=None):
        super().__init__(parent)
        self._collapsed = collapsed

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Başlık butonu
        self._toggle_btn = QPushButton()
        self._toggle_btn.setObjectName("collapsibleToggle")
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setChecked(not collapsed)
        self._toggle_btn.clicked.connect(self._on_toggle)
        layout.addWidget(self._toggle_btn)

        # İçerik alanı
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 4, 0, 0)
        self._content_layout.setSpacing(4)
        self._content.setVisible(not collapsed)
        layout.addWidget(self._content)

        self._title = title
        self._update_title()

    def _update_title(self):
        arrow = "▼" if not self._collapsed else "▶"
        self._toggle_btn.setText(f"{arrow}  {self._title}")

    def _on_toggle(self):
        self._collapsed = not self._collapsed
        self._content.setVisible(not self._collapsed)
        self._update_title()

    def content_layout(self) -> QVBoxLayout:
        """İçerik layout'unu döndürür — butonları buraya ekleyin."""
        return self._content_layout

from gui.worker import PdfWorker, BatchWorker
from gui.icons import icon
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

        # ===== PDF İşlemleri (Daraltılabilir) =====
        pdf_group = CollapsibleGroupBox("📄 PDF İşlemleri", collapsed=True)
        pdf_layout = pdf_group.content_layout()

        self.merge_btn = QPushButton("Birleştir")
        self.merge_btn.setIcon(icon("merge"))
        self.merge_btn.setObjectName("primaryButton")
        self.merge_btn.setToolTip("Seçili PDF dosyalarını sırasıyla tek bir PDF'de birleştirir.\nEn az 2 dosya seçin. Sayfa seçimi yapabilirsiniz.")
        self.merge_btn.clicked.connect(self._on_merge)
        pdf_layout.addWidget(self.merge_btn)

        self.split_btn = QPushButton("Sayfalarına Ayır")
        self.split_btn.setIcon(icon("split"))
        self.split_btn.setToolTip("PDF'nin her sayfasını ayrı birer PDF dosyasına ayırır.")
        self.split_btn.clicked.connect(self._on_split)
        pdf_layout.addWidget(self.split_btn)

        self.extract_btn = QPushButton("Seçili Sayfaları Çıkar")
        self.extract_btn.setIcon(icon("extract"))
        self.extract_btn.setToolTip("Belirtilen sayfaları çıkarıp yeni bir PDF oluşturur.\nSayfa Seçimi alanına sayfaları yazın (ör: 1,3,5-8).")
        self.extract_btn.clicked.connect(self._on_extract)
        pdf_layout.addWidget(self.extract_btn)

        self.delete_btn = QPushButton("Sayfa Sil")
        self.delete_btn.setIcon(icon("delete_page"))
        self.delete_btn.setToolTip("Belirtilen sayfaları siler, yeni dosya oluşturur.\nOrijinal dosyaya dokunulmaz.")
        self.delete_btn.clicked.connect(self._on_delete)
        pdf_layout.addWidget(self.delete_btn)

        self.orientation_btn = QPushButton("Yatay / Dikey Yap")
        self.orientation_btn.setIcon(icon("orientation"))
        self.orientation_btn.setToolTip("Sayfaları yatay (landscape) veya dikey (portrait) yöne çevirir.\nZaten doğru yöndeki sayfalar değiştirilmez.")
        self.orientation_btn.clicked.connect(self._on_orientation)
        pdf_layout.addWidget(self.orientation_btn)

        self.insert_btn = QPushButton("PDF Ekle")
        self.insert_btn.setIcon(icon("insert"))
        self.insert_btn.setToolTip("Bir PDF'yi başka bir PDF'nin belirli sayfasından sonra ekler.\n0 girerseniz en başa eklenir.")
        self.insert_btn.clicked.connect(self._on_insert)
        pdf_layout.addWidget(self.insert_btn)

        self.sort_alpha_btn = QPushButton("Alfabetik Sırala")
        self.sort_alpha_btn.setIcon(icon("sort_alpha"))
        self.sort_alpha_btn.setToolTip("Seçili dosyaları dosya adına göre\nalfabetik (A→Z) sıralar.")
        self.sort_alpha_btn.clicked.connect(self._on_sort_alphabetical)
        pdf_layout.addWidget(self.sort_alpha_btn)

        self.rename_btn = QPushButton("Adını Değiştir")
        self.rename_btn.setIcon(icon("rename"))
        self.rename_btn.setToolTip("Seçili dosyanın adını değiştirir.\nInput veya output'taki dosyaların adlarını değiştirebilirsiniz.")
        self.rename_btn.clicked.connect(self._on_rename_file)
        pdf_layout.addWidget(self.rename_btn)

        self.order_number_btn = QPushButton("Numaralandır / Sırala")
        self.order_number_btn.setIcon(icon("order_number"))
        self.order_number_btn.setToolTip(
            "Seçili PDF dosyalarına sıra numarası atar.\n"
            "Dosya adlarını 001_ad.pdf formatında yeniden adlandırır,\n"
            "her sayfanın sağ üst köşesine kırmızı numara yazar."
        )
        self.order_number_btn.clicked.connect(self._on_order_number)
        pdf_layout.addWidget(self.order_number_btn)

        layout.addWidget(pdf_group)

        # ===== Dönüştürme (Daraltılabilir) =====
        convert_group = CollapsibleGroupBox("🔄 Dönüştürme", collapsed=True)
        convert_layout = convert_group.content_layout()

        self.pdf_to_word_btn = QPushButton("PDF → Word")
        self.pdf_to_word_btn.setIcon(icon("pdf_to_word"))
        self.pdf_to_word_btn.setToolTip("PDF dosyasını düzenlenebilir Word (.docx) formatına çevirir.")
        self.pdf_to_word_btn.clicked.connect(self._on_pdf_to_word)
        convert_layout.addWidget(self.pdf_to_word_btn)

        self.pdf_to_excel_btn = QPushButton("PDF → Excel")
        self.pdf_to_excel_btn.setIcon(icon("pdf_to_excel"))
        self.pdf_to_excel_btn.setToolTip("PDF içindeki tablo verilerini Excel (.xlsx) formatına çevirir.")
        self.pdf_to_excel_btn.clicked.connect(self._on_pdf_to_excel)
        convert_layout.addWidget(self.pdf_to_excel_btn)

        self.pdf_to_jpg_btn = QPushButton("PDF → JPG")
        self.pdf_to_jpg_btn.setIcon(icon("pdf_to_jpg"))
        self.pdf_to_jpg_btn.setToolTip("PDF'nin her sayfasını ayrı JPG görsel dosyasına çevirir.\nPyMuPDF kullanır — harici kurulum gerektirmez.")
        self.pdf_to_jpg_btn.clicked.connect(self._on_pdf_to_jpg)
        convert_layout.addWidget(self.pdf_to_jpg_btn)

        self.word_to_pdf_btn = QPushButton("Word → PDF")
        self.word_to_pdf_btn.setIcon(icon("word_to_pdf"))
        self.word_to_pdf_btn.setToolTip("Word (.docx) dosyasını PDF formatına çevirir.\nDosya seçme diyaloğu açılır.")
        self.word_to_pdf_btn.clicked.connect(self._on_word_to_pdf)
        convert_layout.addWidget(self.word_to_pdf_btn)

        self.excel_to_pdf_btn = QPushButton("Excel → PDF")
        self.excel_to_pdf_btn.setIcon(icon("excel_to_pdf"))
        self.excel_to_pdf_btn.setToolTip("Excel (.xlsx) dosyasını PDF formatına çevirir.\nDosya seçme diyaloğu açılır.")
        self.excel_to_pdf_btn.clicked.connect(self._on_excel_to_pdf)
        convert_layout.addWidget(self.excel_to_pdf_btn)

        self.jpg_to_pdf_btn = QPushButton("JPG → PDF")
        self.jpg_to_pdf_btn.setIcon(icon("jpg_to_pdf"))
        self.jpg_to_pdf_btn.setToolTip("Bir veya birden fazla görseli (JPG, PNG, BMP, TIFF)\ntek bir PDF dosyasına dönüştürür.")
        self.jpg_to_pdf_btn.clicked.connect(self._on_jpg_to_pdf)
        convert_layout.addWidget(self.jpg_to_pdf_btn)

        layout.addWidget(convert_group)

        # ===== İşlemler (Daraltılabilir) =====
        tools_group = CollapsibleGroupBox("🛠️ İşlemler", collapsed=True)
        tools_layout = tools_group.content_layout()

        self.ocr_btn = QPushButton("OCR Uygula")
        self.ocr_btn.setIcon(icon("ocr"))
        self.ocr_btn.setToolTip("Taranmış (görsel tabanlı) PDF'lere metin tanıma uygular.\nTesseract OCR kurulu olmalıdır. Toplu işlem destekler.")
        self.ocr_btn.clicked.connect(self._on_ocr)
        tools_layout.addWidget(self.ocr_btn)

        self.compress_btn = QPushButton("Sıkıştır")
        self.compress_btn.setIcon(icon("compress"))
        self.compress_btn.setToolTip("PDF dosya boyutunu küçültür.\nHafif / Dengeli / Agresif kalite seçenekleri. Toplu işlem destekler.")
        self.compress_btn.clicked.connect(self._on_compress)
        tools_layout.addWidget(self.compress_btn)

        self.encrypt_btn = QPushButton("Şifrele")
        self.encrypt_btn.setIcon(icon("encrypt"))
        self.encrypt_btn.setToolTip("PDF'ye parola koruması ekler.\nBirden fazla dosya seçerek toplu şifreleme yapabilirsiniz.")
        self.encrypt_btn.clicked.connect(self._on_encrypt)
        tools_layout.addWidget(self.encrypt_btn)

        self.decrypt_btn = QPushButton("Şifre Çöz")
        self.decrypt_btn.setIcon(icon("decrypt"))
        self.decrypt_btn.setToolTip("Şifreli PDF'nin parolasını girerek korumayı kaldırır.")
        self.decrypt_btn.clicked.connect(self._on_decrypt)
        tools_layout.addWidget(self.decrypt_btn)

        self.watermark_btn = QPushButton("Filigran Ekle")
        self.watermark_btn.setIcon(icon("watermark"))
        self.watermark_btn.setToolTip("PDF sayfalarına çapraz filigran metni ekler.\nToplu işlem destekler.")
        self.watermark_btn.clicked.connect(self._on_watermark)
        tools_layout.addWidget(self.watermark_btn)

        self.annotate_btn = QPushButton("Not Ekle")
        self.annotate_btn.setIcon(icon("annotate"))
        self.annotate_btn.setToolTip("Belirtilen sayfaya yapışkan not (annotation) ekler.")
        self.annotate_btn.clicked.connect(self._on_annotate)
        tools_layout.addWidget(self.annotate_btn)
        self.highlight_btn = QPushButton("Metin Vurgula")
        self.highlight_btn.setIcon(icon("highlight"))
        self.highlight_btn.setToolTip("PDF içinde metin arar ve bulduğu yerleri sarı ile vurgular.\nSayfa seçimi yaparsanız sadece o sayfalarda arar.")
        self.highlight_btn.clicked.connect(self._on_highlight)
        tools_layout.addWidget(self.highlight_btn)
        layout.addWidget(tools_group)

        # ===== Dosya Yönetimi =====
        file_mgmt_group = QGroupBox("📁 Dosya Yönetimi")
        file_mgmt_layout = QVBoxLayout(file_mgmt_group)

        self.open_input_btn = QPushButton("Input Klasörünü Aç")
        self.open_input_btn.setIcon(icon("open_folder"))
        self.open_input_btn.setToolTip("Input klasörünü dosya gezgininde açar.")
        self.open_input_btn.clicked.connect(self._on_open_input_folder)
        file_mgmt_layout.addWidget(self.open_input_btn)

        self.open_output_btn = QPushButton("Output Klasörünü Aç")
        self.open_output_btn.setIcon(icon("open_folder"))
        self.open_output_btn.setToolTip("Output klasörünü dosya gezgininde açar.")
        self.open_output_btn.clicked.connect(self._on_open_output_folder)
        file_mgmt_layout.addWidget(self.open_output_btn)

        self.save_as_btn = QPushButton("Seçileni Farklı Kaydet")
        self.save_as_btn.setIcon(icon("save_as"))
        self.save_as_btn.setToolTip("Seçili dosya veya dosyaları istediğiniz konuma kaydeder.")
        self.save_as_btn.clicked.connect(self._on_save_selected_as)
        file_mgmt_layout.addWidget(self.save_as_btn)

        self.remove_selected_btn = QPushButton("Seçilileri Sil")
        self.remove_selected_btn.setIcon(icon("delete"))
        self.remove_selected_btn.setObjectName("dangerButton")
        self.remove_selected_btn.setToolTip("İşaretli dosyaları geri dönüşüm kutusuna gönderir.\nDosyalar geri dönüşüm kutusundan geri alınabilir.")
        self.remove_selected_btn.clicked.connect(self._on_remove_selected)
        file_mgmt_layout.addWidget(self.remove_selected_btn)

        layout.addWidget(file_mgmt_group)

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
        """PDF birleştirme — sıralama ve numaralandırma seçenekleriyle."""
        files = self._get_selected_files()
        if not files or len(files) < 2:
            self.operation_failed.emit("Birleştirmek için en az 2 dosya seçin")
            return

        # Sayfa ayrıştırmasını önceden yap
        prepared = []
        for f in files:
            pages = self._parse_pages(f["pages"], f["path"])
            if pages is None:
                return
            prepared.append({
                "path": f["path"],
                "pages": pages if f["pages"] else None,
            })

        # Sıralama ve numaralandırma diyaloğu
        from gui.merge_options_dialog import MergeOptionsDialog
        dialog = MergeOptionsDialog(prepared, parent=self)
        if dialog.exec() != MergeOptionsDialog.DialogCode.Accepted:
            return

        ordered = dialog.get_ordered_files()
        if not ordered:
            return

        from core.pdf_merger import merge_pdfs

        add_numbers = dialog.should_add_page_numbers()
        start_num = dialog.get_start_number()
        numbering_mode = dialog.get_numbering_mode()

        if not add_numbers:
            # Sadece birleştir
            file_list = [{"path": f["path"], "pages": f["pages"]} for f in ordered]
            self._run_worker(
                merge_pdfs, file_list,
                success_msg_func=lambda r: f"Birleştirme tamamlandı: {r.name}"
            )
        else:
            # Birleştir + numaralandır
            from converters.to_pdf import _stamp_all_pages
            from pypdf import PdfReader

            # Her dosyanın sayfa sayısını hesapla (per_document modu için)
            page_counts = []
            for f in ordered:
                reader = PdfReader(f["path"])
                page_counts.append(len(reader.pages))

            def _merge_and_number(file_list, start, mode, p_counts):
                result = merge_pdfs(file_list)
                _stamp_all_pages(result, start, mode=mode, page_counts=p_counts)
                return result

            file_list = [{"path": f["path"], "pages": f["pages"]} for f in ordered]
            self._run_worker(
                _merge_and_number, file_list, start_num, numbering_mode, page_counts,
                success_msg_func=lambda r: f"Birleştirme + numaralandırma tamamlandı: {r.name}"
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
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Word Dosyası Seçin", "",
            "Word Dosyaları (*.docx *.doc)"
        )
        if not paths:
            return
        from converters.to_pdf import word_to_pdf
        if len(paths) == 1:
            self._run_worker(
                word_to_pdf, paths[0],
                success_msg_func=lambda r: f"Word -> PDF: {r.name}"
            )
        else:
            self._handle_multi_convert(paths, word_to_pdf, "Word")

    def _on_excel_to_pdf(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Excel Dosyası Seçin", "",
            "Excel Dosyaları (*.xlsx *.xls)"
        )
        if not paths:
            return
        from converters.to_pdf import excel_to_pdf
        if len(paths) == 1:
            self._run_worker(
                excel_to_pdf, paths[0],
                success_msg_func=lambda r: f"Excel -> PDF: {r.name}"
            )
        else:
            self._handle_multi_convert(paths, excel_to_pdf, "Excel")

    def _on_jpg_to_pdf(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Görsel Dosyaları Seçin", "",
            "Görseller (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        if not paths:
            return
        from converters.to_pdf import jpg_to_pdf
        if len(paths) == 1:
            self._run_worker(
                jpg_to_pdf, paths[0],
                success_msg_func=lambda r: f"JPG -> PDF: {r.name}"
            )
        else:
            self._handle_multi_convert(paths, jpg_to_pdf, "görsel")

    def _handle_multi_convert(self, paths: list[str], converter_func, file_type_label: str):
        """
        Çoklu dosya dönüştürmede kullanıcıya ayrı/birleştir seçeneği sunar.

        Args:
            paths: Dönüştürülecek dosya yolları.
            converter_func: Tek dosya dönüştürme fonksiyonu (path, output_path) -> Path.
            file_type_label: Dosya türü etiketi (ör: "görsel", "Word", "Excel").
        """
        from gui.convert_mode_dialog import ConvertModeDialog
        from converters.to_pdf import convert_and_merge

        dialog = ConvertModeDialog(paths, file_type_label, parent=self)
        if dialog.exec() != ConvertModeDialog.DialogCode.Accepted:
            return

        mode = dialog.get_mode()
        ordered_paths = dialog.get_ordered_paths()

        if mode == ConvertModeDialog.MODE_SEPARATE:
            # Ayrı ayrı dönüştür
            file_args = [
                {"args": (p,), "kwargs": {}, "label": Path(p).name}
                for p in ordered_paths
            ]
            self._run_batch_worker(
                converter_func, file_args,
                success_msg=f"{file_type_label} → PDF dönüştürme tamamlandı"
            )
        else:
            # Tek PDF olarak birleştir
            add_numbers = dialog.should_add_page_numbers()
            start_num = dialog.get_start_number()
            self._run_worker(
                convert_and_merge,
                ordered_paths,
                converter_func,
                add_page_numbers=add_numbers,
                start_number=start_num,
                success_msg_func=lambda r: f"Birleşik PDF oluşturuldu: {r.name}"
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

    # ========== Dosya Yönetimi ==========

    def _on_open_input_folder(self):
        """Input klasörünü dosya gezgininde açar."""
        self._open_folder(settings.input_dir)

    def _on_open_output_folder(self):
        """Output klasörünü dosya gezgininde açar."""
        self._open_folder(settings.output_dir)

    def _open_folder(self, path):
        """Klasörü sistem dosya gezgininde açar."""
        try:
            folder = Path(path)
            folder.mkdir(parents=True, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(str(folder))
            elif sys.platform == "darwin":
                import subprocess
                subprocess.call(["open", str(folder)])
            else:
                import subprocess
                subprocess.call(["xdg-open", str(folder)])
        except Exception as e:
            self.operation_failed.emit(f"Klasör açılamadı: {e}")

    def _on_sort_alphabetical(self):
        """Seçili dosyaları bulundukları listeye göre alfabetik sıralar."""
        sorted_any = False
        for file_list in self.file_lists:
            selected = file_list.get_selected_files()
            if len(selected) < 2:
                continue
            # Dosya adına göre sırala (case-insensitive)
            selected_sorted = sorted(selected, key=lambda f: Path(f["path"]).name.lower())
            # Orijinal satır numaralarını bul (order 1-based)
            original_rows = sorted([f["order"] - 1 for f in selected])
            # Sıralanmış dosyaları orijinal satır konumlarına yerleştir
            for i, row in enumerate(original_rows):
                sf = selected_sorted[i]
                src_path = Path(sf["path"])
                name_item = file_list.table.item(row, 2)
                if name_item:
                    name_item.setText(src_path.name)
                    name_item.setData(Qt.ItemDataRole.UserRole, str(src_path))
                    name_item.setToolTip(src_path.name)
                # Tür
                ext = src_path.suffix.lower()
                from utils.file_utils import EXTENSION_LABELS
                type_label = EXTENSION_LABELS.get(ext, ext.upper().lstrip('.'))
                type_item = file_list.table.item(row, 3)
                if type_item:
                    type_item.setText(type_label)
                # Sayfa sayısı
                is_pdf = ext == '.pdf'
                if is_pdf:
                    try:
                        from core.pdf_metadata import get_metadata
                        metadata = get_metadata(src_path)
                        page_count = str(metadata["sayfa_sayisi"])
                        size_str = metadata["dosya_boyutu"]
                    except Exception:
                        page_count = "?"
                        from utils.file_utils import get_file_size_str
                        size_str = get_file_size_str(src_path)
                else:
                    page_count = "—"
                    from utils.file_utils import get_file_size_str
                    size_str = get_file_size_str(src_path)
                page_item = file_list.table.item(row, 4)
                if page_item:
                    page_item.setText(page_count)
                size_item = file_list.table.item(row, 6)
                if size_item:
                    size_item.setText(size_str)
            file_list._update_order_numbers()
            sorted_any = True

        if sorted_any:
            self.operation_completed.emit("Dosyalar alfabetik sıralandı")
        else:
            self.operation_failed.emit("Sıralamak için en az 2 dosya seçin")

    def _on_rename_file(self):
        """Seçili dosyanın adını değiştirir."""
        files = self._get_selected_files()
        if not files:
            return
        if len(files) > 1:
            self.operation_failed.emit("Lütfen adını değiştirmek için tek bir dosya seçin")
            return

        file_info = files[0]
        src = Path(file_info["path"])
        old_name = src.stem  # Uzantısız dosya adı

        new_name, ok = QInputDialog.getText(
            self, "Dosya Adını Değiştir",
            f"Yeni dosya adını girin (uzantı otomatik eklenir):\n\nMevcut: {src.name}",
            text=old_name
        )
        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()
        # Güvenlik: dosya adında yasak karakterler
        invalid_chars = '<>:"/\\|?*'
        if any(c in new_name for c in invalid_chars):
            self.operation_failed.emit(f"Dosya adında geçersiz karakterler var: {invalid_chars}")
            return

        new_path = src.parent / f"{new_name}{src.suffix}"
        if new_path.exists():
            self.operation_failed.emit(f"Bu isimde bir dosya zaten mevcut: {new_path.name}")
            return

        try:
            src.rename(new_path)
            # Listeleri yenile
            for file_list in self.file_lists:
                file_list.refresh_files()
            self.operation_completed.emit(f"Ad değiştirildi: {src.name} → {new_path.name}")
        except Exception as e:
            self.operation_failed.emit(f"Ad değiştirme hatası: {e}")

    def _on_save_selected_as(self):
        """Seçili dosyaları farklı bir konuma kaydeder."""
        files = self._get_selected_files()
        if not files:
            return

        if len(files) == 1:
            src = Path(files[0]["path"])
            dest, _ = QFileDialog.getSaveFileName(
                self, "Farklı Kaydet", src.name,
                f"Dosyalar (*{src.suffix});;Tüm Dosyalar (*.*)"
            )
            if not dest:
                return
            try:
                shutil.copy2(str(src), dest)
                self.operation_completed.emit(f"Dosya kaydedildi: {Path(dest).name}")
            except Exception as e:
                self.operation_failed.emit(f"Kaydetme hatası: {e}")
        else:
            dest_dir = QFileDialog.getExistingDirectory(
                self, "Kayıt Klasörünü Seçin"
            )
            if not dest_dir:
                return
            dest_path = Path(dest_dir)
            saved = 0
            errors = []
            for f in files:
                src = Path(f["path"])
                try:
                    shutil.copy2(str(src), str(dest_path / src.name))
                    saved += 1
                except Exception as e:
                    errors.append(f"{src.name}: {e}")
            if errors:
                self.operation_failed.emit(
                    f"{saved} dosya kaydedildi, {len(errors)} hata:\n" + "\n".join(errors)
                )
            else:
                self.operation_completed.emit(f"{saved} dosya kaydedildi")

    def _on_order_number(self):
        """Seçili PDF dosyalarını numaralandırır ve sıralar."""
        files = self._get_selected_files()
        if not files:
            return

        # Sadece PDF dosyalarını filtrele
        pdf_files = [f for f in files if Path(f["path"]).suffix.lower() == ".pdf"]
        if len(pdf_files) < 1:
            self.operation_failed.emit("Numaralandırmak için en az 1 PDF dosyası seçin")
            return

        from gui.order_dialog import OrderDialog

        dlg = OrderDialog(pdf_files, parent=self)
        if dlg.exec() != OrderDialog.DialogCode.Accepted:
            return

        result = dlg.get_result()
        if not result:
            return

        from core.pdf_watermark import stamp_order_number

        errors = []
        processed = 0
        for item in result:
            src = Path(item["path"])
            order_num = item["order_num"]
            prefix = str(order_num).zfill(3)

            # Mevcut prefix varsa kaldır (yeniden numaralandırma desteği)
            old_name = src.stem
            # 001_dosya formatındaki mevcut prefix'i kaldır
            import re
            cleaned_name = re.sub(r'^\d{3}_', '', old_name)
            new_name = f"{prefix}_{cleaned_name}{src.suffix}"
            new_path = src.parent / new_name

            try:
                # Aynı isimde dosya kontrolü (kendisi hariç)
                if new_path.exists() and new_path != src:
                    errors.append(f"{src.name}: '{new_name}' zaten mevcut")
                    continue

                # Önce PDF'ye numara damgala (orijinal dosya üzerine yaz)
                stamp_order_number(str(src), order_num)

                # Dosyayı yeniden adlandır
                if new_path != src:
                    src.rename(new_path)

                processed += 1
            except Exception as e:
                errors.append(f"{src.name}: {e}")

        # Listeleri yenile
        for file_list in self.file_lists:
            file_list.refresh_files()

        if errors:
            self.operation_failed.emit(
                f"{processed} dosya numaralandırıldı, {len(errors)} hata:\n" + "\n".join(errors)
            )
        else:
            self.operation_completed.emit(
                f"{processed} dosya numaralandırıldı ve sıralandı"
            )