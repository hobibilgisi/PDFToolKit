"""
PDFToolKit - Dosya Listesi Bileşeni

Dosyaları tablo şeklinde listeler.
Sürükle-bırak, sıra numarası ve ↑↓ butonlarıyla sıralama desteği.
Dışarıdan dosyaları sürükle-bırak ile klasöre eklemeyi destekler.
Input: PDF + Word + Excel + görsel dosyaları kabul eder.
Output: Tüm desteklenen formatları listeler.
"""

from pathlib import Path
import shutil
import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QAbstractItemView, QLineEdit, QCheckBox,
    QLabel, QMessageBox, QDialog, QDialogButtonBox, QScrollArea, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDrag

from core.pdf_metadata import get_metadata
from utils.file_utils import (
    list_pdf_files, list_all_files, get_file_size_str,
    SUPPORTED_EXTENSIONS, EXTENSION_LABELS,
)
from config.settings import settings


class _DragOutTable(QTableWidget):
    """Dosyaları dışarıya sürükle-bırak ile taşımayı destekleyen tablo."""

    def startDrag(self, supportedActions):
        urls = []
        seen = set()
        for index in self.selectedIndexes():
            row = index.row()
            if row in seen:
                continue
            seen.add(row)
            item = self.item(row, 2)  # Dosya Adı sütunu
            if item:
                path = item.data(Qt.ItemDataRole.UserRole)
                if path and Path(path).exists():
                    urls.append(QUrl.fromLocalFile(path))

        if urls:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setUrls(urls)
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.CopyAction)


class FileListWidget(QWidget):
    """Dosya listesi bileşeni — tablo yapısı."""

    files_changed = pyqtSignal()

    COLUMNS = ["☑", "Sıra", "Dosya Adı", "Tür", "Sayfa", "Sayfa Seçimi", "Boyut", ""]

    def __init__(self, title="📁 Dosyalar", directory=None, accept_all_formats=False, allow_drop=True, allow_drag_out=False, parent=None):
        super().__init__(parent)
        self.list_title = title
        self.directory = Path(directory) if directory else settings.input_dir
        self.accept_all_formats = accept_all_formats
        self.allow_drag_out = allow_drag_out
        self.setAcceptDrops(allow_drop)
        self.all_selected = False  # Tümünü seç durumu
        self._setup_ui()
        self.refresh_files()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Başlık satırı
        header_layout = QHBoxLayout()

        title = QLabel(self.list_title)
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Tablo
        if self.allow_drag_out:
            self.table = _DragOutTable()
        else:
            self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Tablo içi drag & drop
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(False)
        if self.allow_drag_out:
            self.table.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        else:
            self.table.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
            self.table.setDefaultDropAction(Qt.DropAction.MoveAction)

        # Sütun genişlikleri
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)      # Checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)      # Sıra
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)    # Dosya Adı
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)      # Tür
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)      # Sayfa
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)      # Sayfa Seçimi
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)      # Boyut
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)      # ↑↓

        self.table.setColumnWidth(0, 40)   # Checkbox
        self.table.setColumnWidth(1, 50)   # Sıra
        self.table.setColumnWidth(3, 55)   # Tür
        self.table.setColumnWidth(4, 60)   # Sayfa
        self.table.setColumnWidth(5, 120)  # Sayfa Seçimi
        self.table.setColumnWidth(6, 80)   # Boyut
        self.table.setColumnWidth(7, 70)   # ↑↓

        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        # Tablo başlığına tıklandığında tümünü seçmek için sinyal:
        header.sectionClicked.connect(self._on_header_clicked)

        layout.addWidget(self.table)
        
    def _on_header_clicked(self, logical_index):
        if logical_index == 0:
            self.all_selected = not self.all_selected
            new_text = "☑" if self.all_selected else "☐"
            self.table.horizontalHeaderItem(0).setText(new_text)
            self._toggle_select_all(self.all_selected)

    def _toggle_select_all(self, is_checked):
        """Tüm kutucukları işaretler veya işareti kaldırır."""
        for row in range(self.table.rowCount()):
            cb_widget = self.table.cellWidget(row, 0)
            if cb_widget:
                checkbox = cb_widget.findChild(QCheckBox)
                if checkbox:
                    # stateChanged sinyali tetiklenmesini kısa süreliğine engelle
                    checkbox.blockSignals(True)
                    checkbox.setChecked(is_checked)
                    checkbox.blockSignals(False)

    def _on_cell_double_clicked(self, row: int, col: int):
        """Çift tıklandığında PDF dosyasını sistem varsayılan uygulamasıyla açar."""
        name_item = self.table.item(row, 2)
        if name_item:
            path = name_item.data(Qt.ItemDataRole.UserRole)
            if path and Path(path).exists():
                try:
                    if sys.platform == "win32":
                        os.startfile(path)
                    elif sys.platform == "darwin":
                        import subprocess
                        subprocess.call(["open", path])
                    else:
                        import subprocess
                        subprocess.call(["xdg-open", path])
                except Exception as e:
                    QMessageBox.warning(self, "Hata", f"Dosya açılamadı:\n{str(e)}")

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Dışarıdan sürüklenen dosyaları kabul et."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_ext = Path(url.toLocalFile()).suffix.lower()
                if self.accept_all_formats:
                    # Tüm desteklenen formatları kabul et
                    if file_ext in SUPPORTED_EXTENSIONS:
                        event.acceptProposedAction()
                        return
                else:
                    # Sadece PDF dosyalarını kabul et
                    if file_ext == '.pdf':
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dragMoveEvent(self, event):
        """Sürükleme sırasındaki hareketi kontrol et."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Dosyalar bırakıldığında çalışır."""
        if event.mimeData().hasUrls():
            added_files = 0
            # Hangi uzantıları kabul edeceğimizi belirle
            accepted_exts = SUPPORTED_EXTENSIONS if self.accept_all_formats else {'.pdf'}

            for url in event.mimeData().urls():
                file_path = Path(url.toLocalFile())
                if file_path.suffix.lower() in accepted_exts:
                    # Hedef klasöre kopyala
                    try:
                        self.directory.mkdir(parents=True, exist_ok=True)
                        dest_path = self.directory / file_path.name

                        # Eğer aynı isimde dosya varsa üzerine yazma, numara ekle
                        counter = 2
                        base_name = file_path.stem
                        ext = file_path.suffix
                        while dest_path.exists():
                            # Eğer dosya zaten aynıysa kopyalamaya gerek yok
                            if dest_path.samefile(file_path):
                                break
                            dest_path = self.directory / f"{base_name}_{counter}{ext}"
                            counter += 1

                        if not dest_path.exists() or not dest_path.samefile(file_path):
                            shutil.copy2(file_path, dest_path)
                            added_files += 1

                    except Exception as e:
                        QMessageBox.warning(self, "Kopyalama Hatası", f"{file_path.name} kopyalanamadı:\n{str(e)}")

            if added_files > 0:
                self.refresh_files()
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    # Windows MAX_PATH sınırı
    _MAX_PATH = 255

    def refresh_files(self):
        """Belirtilen klasördeki dosyaları tarar ve tabloyu günceller."""
        if self.accept_all_formats:
            files = list_all_files(self.directory)
        else:
            files = list_pdf_files(self.directory)

        # Uzun yol kontrolü — kullanıcıdan ad kısaltması iste
        long_files = [f for f in files if len(str(f)) > self._MAX_PATH]
        if long_files:
            self._prompt_rename_long_paths(long_files)
            # Yeniden tara (adlar değişmiş olabilir)
            if self.accept_all_formats:
                files = list_all_files(self.directory)
            else:
                files = list_pdf_files(self.directory)

        self.table.setRowCount(len(files))

        for row, file_path in enumerate(files):
            self._populate_row(row, file_path)
            
        # Yenileme sonrasında select_all durumunu güncelle
        self.all_selected = False
        if self.table.horizontalHeaderItem(0):
            self.table.horizontalHeaderItem(0).setText("☐")

        self.files_changed.emit()

    def scroll_to_bottom(self):
        """Tabloyu en son satıra kaydırır."""
        if self.table.rowCount() > 0:
            self.table.scrollToBottom()

    def _populate_row(self, row: int, file_path: Path):
        """Bir tablo satırını doldurur."""
        is_pdf = file_path.suffix.lower() == '.pdf'

        # Checkbox
        checkbox = QCheckBox()
        is_checked = self.all_selected
        checkbox.setChecked(is_checked)
        
        # Kutucuk elle kaldırıldığında "Tümünü Seç" kutucuğunun da işaretinin kalkması için
        checkbox.stateChanged.connect(self._check_if_all_selected)
        
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, 0, checkbox_widget)

        # Sıra numarası
        order_item = QTableWidgetItem(str(row + 1))
        order_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, order_item)

        # Dosya adı
        name_item = QTableWidgetItem(file_path.name)
        name_item.setData(Qt.ItemDataRole.UserRole, str(file_path))
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        name_item.setToolTip(file_path.name)
        self.table.setItem(row, 2, name_item)

        # Tür
        ext = file_path.suffix.lower()
        type_label = EXTENSION_LABELS.get(ext, ext.upper().lstrip('.'))
        type_item = QTableWidgetItem(type_label)
        type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 3, type_item)

        # Sayfa sayısı ve boyut
        if is_pdf:
            try:
                metadata = get_metadata(file_path)
                page_count = metadata["sayfa_sayisi"]
                size_str = metadata["dosya_boyutu"]
            except Exception:
                page_count = "?"
                size_str = get_file_size_str(file_path)
        else:
            page_count = "—"
            size_str = get_file_size_str(file_path)

        page_item = QTableWidgetItem(str(page_count))
        page_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        page_item.setFlags(page_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 4, page_item)

        # Sayfa seçimi
        page_input = QLineEdit()
        page_input.setObjectName("pageInput")
        if is_pdf:
            page_input.setPlaceholderText("tümü")
        else:
            page_input.setPlaceholderText("—")
            page_input.setEnabled(False)
        page_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_input.setMaximumWidth(110)
        page_input.setMaximumHeight(24)
        if is_pdf:
            page_input.setToolTip(
                "<b>Sayfa Seçimi Formatları:</b><br><br>"
                "• <b>Boş bırak</b> → Tüm sayfalar<br>"
                "• <b>tümü</b> veya <b>all</b> → Tüm sayfalar<br>"
                "• <b>3</b> → Sadece 3. sayfa<br>"
                "• <b>2-6</b> → 2, 3, 4, 5, 6. sayfalar<br>"
                "• <b>1,4,7</b> → 1, 4 ve 7. sayfalar (tek tek seçim)<br>"
                "• <b>1-3,5,8-10</b> → 1, 2, 3, 5, 8, 9, 10. sayfalar<br><br>"
                "<i>Tekrar eden numaralar otomatik kaldırılır,<br>"
                "sonuç sıralı olarak uygulanır.</i>"
            )
        self.table.setCellWidget(row, 5, page_input)

        # Satır yüksekliğini widget'lara uygun ayarla
        self.table.setRowHeight(row, 38)

        # Boyut
        size_item = QTableWidgetItem(str(size_str))
        size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 6, size_item)

        # ↑↓ butonları
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(2, 2, 2, 2)
        btn_layout.setSpacing(2)

        up_btn = QPushButton("▲")
        up_btn.setObjectName("arrowButton")
        up_btn.setMaximumWidth(30)
        up_btn.setMaximumHeight(22)
        up_btn.clicked.connect(lambda _, r=row: self._move_row(r, -1))

        down_btn = QPushButton("▼")
        down_btn.setObjectName("arrowButton")
        down_btn.setMaximumWidth(30)
        down_btn.setMaximumHeight(22)
        down_btn.clicked.connect(lambda _, r=row: self._move_row(r, 1))

        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)

        self.table.setCellWidget(row, 7, btn_widget)

    def _check_if_all_selected(self):
        """Kullanıcı bir kutucuğu değiştirdiğinde 'Tümünü Seç'in durumunu günceller."""
        all_checked = True
        for row in range(self.table.rowCount()):
            cb_widget = self.table.cellWidget(row, 0)
            if cb_widget:
                checkbox = cb_widget.findChild(QCheckBox)
                if checkbox and not checkbox.isChecked():
                    all_checked = False
                    break
        
        self.all_selected = all_checked
        new_text = "☑" if self.all_selected else "☐"
        if self.table.horizontalHeaderItem(0):
            self.table.horizontalHeaderItem(0).setText(new_text)

    def _move_row(self, row: int, direction: int):
        """Satırı yukarı (-1) veya aşağı (+1) taşır."""
        target_row = row + direction
        if target_row < 0 or target_row >= self.table.rowCount():
            return

        # Satır verilerini al ve takas et
        self._swap_rows(row, target_row)
        self.table.selectRow(target_row)
        self._update_order_numbers()
        self.files_changed.emit()

    def _prompt_rename_long_paths(self, long_files: list[Path]):
        """Yol uzunluğu 255 karakteri aşan dosyalar için yeniden adlandırma diyaloğu açar."""
        import re

        dlg = QDialog(self)
        dlg.setWindowTitle("⚠️ Dosya Adı Çok Uzun")
        dlg.setMinimumWidth(600)
        dlg_layout = QVBoxLayout(dlg)

        info = QLabel(
            f"Aşağıdaki dosyaların yolu {self._MAX_PATH} karakteri aşıyor.\n"
            "Windows bu dosyaları işleyemeyebilir. Lütfen daha kısa ad verin."
        )
        info.setWordWrap(True)
        dlg_layout.addWidget(info)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)

        edits: list[tuple[Path, QLineEdit]] = []
        for fp in long_files:
            current_label = QLabel(f"<b>{fp.name}</b><br>"
                                   f"<small style='color:#6c7086;'>Yol: {len(str(fp))} karakter</small>")
            current_label.setWordWrap(True)
            current_label.setTextFormat(Qt.TextFormat.RichText)

            edit = QLineEdit(fp.stem)
            edit.setMinimumWidth(350)
            # Maks uzunluğu hesapla: klasör yolu + "/" + ad + uzantı <= _MAX_PATH
            dir_len = len(str(fp.parent)) + 1 + len(fp.suffix)
            max_stem = max(10, self._MAX_PATH - dir_len)
            edit.setMaxLength(max_stem)
            edit.setToolTip(f"Uzantı ({fp.suffix}) otomatik eklenir.\nMaks {max_stem} karakter.")

            form_layout.addRow(current_label, edit)
            edits.append((fp, edit))

        scroll.setWidget(form_widget)
        dlg_layout.addWidget(scroll)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        dlg_layout.addWidget(btn_box)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        # Geçersiz dosya adı karakterleri
        invalid_chars = re.compile(r'[<>:"/\\|?*]')

        for fp, edit in edits:
            new_stem = edit.text().strip()
            if not new_stem or new_stem == fp.stem:
                continue
            if invalid_chars.search(new_stem):
                QMessageBox.warning(self, "Geçersiz Karakter",
                                    f"'{new_stem}' geçersiz karakter içeriyor.\n"
                                    f"Şu karakterler kullanılamaz: < > : \" / \\ | ? *\n"
                                    f"Dosya adlandırılmadı: {fp.name}")
                continue
            new_path = fp.parent / f"{new_stem}{fp.suffix}"
            if new_path.exists():
                QMessageBox.warning(self, "Dosya Var",
                                    f"'{new_path.name}' zaten mevcut.\nDosya adlandırılmadı.")
                continue
            try:
                fp.rename(new_path)
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Yeniden adlandırılamadı:\n{e}")

    def _swap_rows(self, row1: int, row2: int):
        """İki satırın verilerini takas eder."""
        # Checkbox durumlarını takas et
        cb_w1 = self.table.cellWidget(row1, 0)
        cb_w2 = self.table.cellWidget(row2, 0)
        if cb_w1 and cb_w2:
            cb1 = cb_w1.findChild(QCheckBox)
            cb2 = cb_w2.findChild(QCheckBox)
            if cb1 and cb2:
                state1, state2 = cb1.isChecked(), cb2.isChecked()
                cb1.blockSignals(True); cb2.blockSignals(True)
                cb1.setChecked(state2); cb2.setChecked(state1)
                cb1.blockSignals(False); cb2.blockSignals(False)

        # Dosya adı ve path bilgisini takas et
        item1 = self.table.item(row1, 2)
        item2 = self.table.item(row2, 2)

        if item1 and item2:
            name1 = item1.text()
            path1 = item1.data(Qt.ItemDataRole.UserRole)
            name2 = item2.text()
            path2 = item2.data(Qt.ItemDataRole.UserRole)

            item1.setText(name2)
            item1.setData(Qt.ItemDataRole.UserRole, path2)
            item2.setText(name1)
            item2.setData(Qt.ItemDataRole.UserRole, path1)

        # Tür, Sayfa sayısı, Boyut
        for col in [3, 4, 6]:
            i1 = self.table.item(row1, col)
            i2 = self.table.item(row2, col)
            if i1 and i2:
                t1, t2 = i1.text(), i2.text()
                i1.setText(t2)
                i2.setText(t1)

        # Sayfa seçimi input
        w1 = self.table.cellWidget(row1, 5)
        w2 = self.table.cellWidget(row2, 5)
        if isinstance(w1, QLineEdit) and isinstance(w2, QLineEdit):
            t1, t2 = w1.text(), w2.text()
            w1.setText(t2)
            w2.setText(t1)

    def _update_order_numbers(self):
        """Sıra numaralarını günceller."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item:
                item.setText(str(row + 1))

    def get_selected_files(self) -> list[dict]:
        """
        Seçili (checkbox işaretli) dosyaların bilgilerini döndürür.

        Returns:
            [{"path": str, "pages": str, "order": int}, ...]
        """
        files = []
        for row in range(self.table.rowCount()):
            # Checkbox kontrolü
            cb_widget = self.table.cellWidget(row, 0)
            if cb_widget:
                checkbox = cb_widget.findChild(QCheckBox)
                if checkbox and not checkbox.isChecked():
                    continue

            # Dosya bilgisi
            name_item = self.table.item(row, 2)
            if not name_item:
                continue

            path = name_item.data(Qt.ItemDataRole.UserRole)
            if not path:
                continue

            # Sayfa seçimi
            page_widget = self.table.cellWidget(row, 5)
            page_str = ""
            if isinstance(page_widget, QLineEdit):
                page_str = page_widget.text().strip()

            files.append({
                "path": path,
                "pages": page_str,
                "order": row + 1
            })

        return files

    def get_file_count(self) -> int:
        """Tablodaki toplam dosya sayısını döndürür."""
        return self.table.rowCount()
