# Görev Listesi

## Tamamlanan Görev: Sayfa Seçimi Kullanıcı Deneyimi İyileştirmesi (UX Refinement)
- [x] Sayfa Seçimi (`QLineEdit`) için daha modern ve kompakt bir tasarım planla
- [x] `gui/styles.py` dosyasında tablo ve input stillerini güncelle
- [x] `file_list_widget.py` dosyasında input alanının davranışını (validation, placeholder) iyileştir

---

## Mevcut Görev: Hata Düzeltmeleri ve Kod Kalitesi İyileştirmesi (Bug Fixes & Code Quality)

### Bug #1 — Watermark opacity parametresi uygulanmıyor ✅
- **Dosya:** `core/pdf_watermark.py`
- **Sorun:** `opacity` parametresi kabul ediliyor ancak `insert_text()` çağrısına geçirilmiyor, filigran %100 opaklıkta çıkıyor
- [x] `insert_text()` yerine Shape API kullanıldı: `shape.finish(fill_opacity=opacity)` ile şeffaflık uygulandı

### Bug #2 — Ölü import (Dead Import) ✅
- **Dosya:** `converters/to_pdf.py`
- **Sorun:** `word_to_pdf()` içinde `pdf2docx.Converter` import ediliyor ancak hiç kullanılmıyor
- [x] `from pdf2docx import Converter as Pdf2DocxConverter` satırı kaldırıldı (pdf2docx sadece `from_pdf.py`'de PDF→Word için kullanılıyor)

### Bug #3 — Türkçe karakter desteği eksik ✅
- **Dosya:** `converters/to_pdf.py`
- **Sorun:** `fpdf2` Helvetica fontu Türkçe karakterleri (ş,ç,ğ,ı,ö,ü) desteklemiyor
- [x] `_register_arial_font()` yardımcı fonksiyonu eklendi — Windows Arial TTF fontunu FPDF'e kaydeder
- [x] `word_to_pdf()`: Helvetica → Arial TTF değiştirildi, Unicode desteği sağlandı
- [x] `excel_to_pdf()`: Helvetica → Arial TTF değiştirildi, Unicode desteği sağlandı
- [x] Arial bulunamazsa Helvetica'ya graceful fallback eklendi

### Bug #4 — Highlight fonksiyonu GUI'den erişilemiyor ✅
- **Dosya:** `core/pdf_annotator.py`, `gui/action_panel.py`
- **Sorun:** `add_highlight()` fonksiyonu tanımlı ama GUI'de butonu yok
- [x] `highlight_text()` fonksiyonu eklendi — `page.search_for()` ile metin arayıp bulunan yerleri vurgular
- [x] GUI'ye "🖍️ Metin Vurgula" butonu eklendi, sayfa seçimi desteğiyle entegre edildi
- [x] Kullanıcı metin girer, PDF'te otomatik aranıp sarıyla vurgulanır

### Bug #5 — Eksik birim testleri ✅
- **Dosyalar:** `tests/` klasörü
- **Sorun:** OCR, compress, encrypt, watermark, annotate, metadata ve dönüştürme testleri eksik
- [x] 5 yeni test dosyası oluşturuldu (compressor, encryptor, watermark, annotator, metadata)
- [x] 65/65 test geçti — testler sırasında 2 ek gerçek hata tespit edildi:
  - `pdf_compressor.py`: PyMuPDF `linearize` artık desteklenmiyor → `"linear": True` kaldırıldı
  - `pdf_watermark.py`: `shape.insert_text(rotate=45)` hatası → `morph` matris dönüşümüyle düzeltildi
- [x] Geçici test dosyaları silindi (doğrulama tamamlandı)

### Bug #6 — StatusBar'da kırılgan lambda kullanımı ✅
- **Dosya:** `gui/status_bar.py`
- **Sorun:** `QTimer.singleShot` lambda'larında tuple yan etki `(a, b)` kullanımı — çalışıyor ama kırılgan
- [x] Tuple-lambda kalıbı kaldırıldı, `_reset_status()` private metodu oluşturuldu
- [x] `show_error()` ve `show_success()` metotları temiz çağrıya (`self._reset_status`) dönüştürüldü

---

## Gelecek Görevler: Paketleme ve Dağıtım (Faz 6)
- [ ] Uygulamayı Paketleme (.exe oluşturma)
  - [ ] PyInstaller yapılandırması (spec dosyası yazımı)
  - [ ] Bağımlılıkların (Poppler, Tesseract) yönetimi
  - [ ] İkon eklenmesi
- [ ] Versiyon notlarının (`CHANGELOG.md`) tamamlanması
- [ ] `README.md` dosyasının son kullanıcı için güncellenmesi
