# Changelog

Tüm önemli değişiklikler bu dosyada belgelenecektir.

## [0.4.2] - 2026-03-16

### Düzeltildi
- **Splash ekranı paketlenmiş uygulamada açılmıyor** — Logo dosyası arama mantığı düzeltildi; Nuitka standalone modunda exe dizini her zaman kontrol ediliyor
- **GIF yükleme hatasında çökme** — Pillow/numpy hatası olduğunda statik logo moduna düşüyor

---

## [0.4.1] - 2026-03-09

### Değiştirildi
- **Yeni uygulama ikonu** — 3D PDF Tool Kit tasarımı (EXE, görev çubuğu, masaüstü kısayolu)

---

## [0.4.0] - 2026-03-09

### Eklendi
- **Modern SVG ikon sistemi** — Tüm 27 buton için Catppuccin Mocha renk paletinde vektör ikonlar (`gui/icons.py`)
- **Uygulama ikonu** — PDF döküman + dişli rozet tasarımlı pencere/görev çubuğu ikonu
- **Splash ekranı** — Uygulama açılışında şeffaf GIF animasyonlu karşılama ekranı (`gui/splash_screen.py`)
- **Dönüştürme modu diyaloğu** — Çoklu dosya dönüştürmede "ayrı ayrı" veya "birleştirerek" seçimi (`gui/convert_mode_dialog.py`)
  - Sürükle-bırak ile dosya sıralaması
  - Opsiyonel sayfa numaralandırma
- **Birleştirme seçenekleri diyaloğu** — PDF birleştirme öncesi sıralama ve numaralandırma diyaloğu (`gui/merge_options_dialog.py`)
  - Sürükle-bırak veya ▲/▼ ile dosya sıralaması
  - Ardışık veya dosya bazlı numaralandırma modu seçimi
- **Numaralandırma modu** — PDF birleştirmede iki seçenek:
  - Ardışık numaralandırma (1, 2, 3, 4 …)
  - Dosya bazlı numaralandırma (dosya 1 → 1, dosya 2 → 2 …)
- **Çoklu dosya seçimi** — Word → PDF ve Excel → PDF dönüştürmeleri artık birden fazla dosya kabul ediyor

### Değiştirildi
- Tüm butonlardan emoji prefix'leri kaldırıldı — yerine SVG ikonlar eklendi
- İkon boyutu 28px olarak ayarlandı (okunabilirlik ve tutarlılık)
- Birleştirme ikonu rengi mavi → şeftali (`_PEACH`) — koyu tema üzerinde daha iyi görünürlük
- Sayfa numarası fontu: 16pt gri → **20pt kalın kırmızı** (Arial Bold, `color=(1.0, 0.0, 0.0)`)
- `_stamp_all_pages` fonksiyonu genişletildi: `mode` ve `page_counts` parametreleri eklendi

### Düzeltildi
- Çoklu JPG → PDF dönüştürmede otomatik birleştirme sorunu — artık kullanıcıya soruluyor
- Birleştirme ikonu koyu tema üzerinde görünmüyor — renk değiştirildi

### Proje Temizliği
- `__pycache__/` dizinleri temizlendi
- `assets/` klasöründen tek kullanımlık yardımcı scriptler kaldırıldı (`_analyze_gif.py`, `generate_icon.py`)
- `docs/` klasörü sadeleştirildi: eski sohbet geçmişleri (`antigravity_talks/`), tamamlanmış planlar ve güncelliğini yitirmiş oturum dosyaları kaldırıldı
- README.md kapsamlı kullanma kılavuzu olarak yeniden yazıldı
- CHANGELOG.md tüm sürüm geçmişiyle güncellendi

## [0.2.0] - 2026-02-21

### Eklendi
- **QThread Worker sistemi** (`gui/worker.py`): Tüm PDF işlemleri artık arka plan thread'inde çalışıyor, GUI donması tamamen önlendi
- **BatchWorker**: Birden fazla dosyaya aynı anda sıkıştırma/OCR/filigran/şifreleme uygulama desteği (toplu işlem)
- **Progress Bar entegrasyonu**: İşlem sırasında durum çubuğunda ilerleme çubuğu görünüyor
- **Buton kilitleme**: İşlem devam ederken tüm butonlar devre dışı, bittikten sonra tekrar aktif
- **operation_progress sinyali**: ActionPanel → MainWindow → StatusBar ilerleme akışı

### Düzeltildi
- **StatusBar lambda sorunu**: `show_message()` içindeki kırılgan `lambda` kullanımı `_reset_status()` metodu ile değiştirildi
- **Progress bar hata durumunda gizlenmiyor**: `show_error()` artık progress bar'ı otomatik gizliyor

### İyileştirildi
- Tüm PDF işlem handler'ları (`_on_merge`, `_on_split`, `_on_compress` vb.) try/except bloklarından kurtarılıp worker pattern'ine taşındı
- OCR, sıkıştırma, şifreleme ve filigran işlemleri artık çoklu dosya seçimiyle toplu çalışıyor
- **PyPDF2 → pypdf migrasyonu**: Tüm modüller, testler ve dökümantasyon güncellendi (deprecated PyPDF2 kaldırıldı, pypdf>=4.0 eklendi)
- Kod tekrarı azaltıldı: `_run_worker()` ve `_run_batch_worker()` yardımcı metotları eklendi

## [0.1.0] - 2026-02-20

### Eklendi (Faz 1-5 tamamlandı)
- Proje altyapısı: `.env`, `requirements.txt`, `config/settings.py` (Singleton)
- **9 çekirdek modül** (`core/`):
  - `pdf_merger.py` — PDF birleştirme + belirli sayfaları birleştirme + PDF ekleme
  - `pdf_splitter.py` — Tüm sayfaları ayırma + belirli sayfaları çıkarma
  - `pdf_page_manager.py` — Sayfa silme, döndürme (90°/180°/270°), sayfa sayısı sorgulama
  - `pdf_ocr.py` — Tesseract OCR ile metin katmanı ekleme (Türkçe+İngilizce)
  - `pdf_metadata.py` — PDF meta bilgilerini okuma
  - `pdf_annotator.py` — Metin notu ekleme + metin arama ve vurgulama
  - `pdf_compressor.py` — 3 kalite seviyesinde PDF sıkıştırma (PyMuPDF)
  - `pdf_encryptor.py` — PDF şifreleme (kullanıcı+sahip parolası) ve şifre çözme
  - `pdf_watermark.py` — Şeffaf metin filigranı (açı, boyut, opaklık ayarlı)
- **Dönüştürme modülleri** (`converters/`):
  - `from_pdf.py` — PDF → Word (pdf2docx), PDF → Excel (tablo algılama), PDF → JPG
  - `to_pdf.py` — Word → PDF, Excel → PDF, JPG → PDF, çoklu görsel → PDF
  - Türkçe karakter desteği (Arial TTF ile Unicode)
- **GUI** (`gui/`):
  - `main_window.py` — Koyu tema, splitter panel düzeni, menü çubuğu
  - `file_list_widget.py` — İki bölmeli dosya listesi (İşlenecek/İşlenmiş)
  - `action_panel.py` — 16 işlem butonu 3 grup halinde
  - `status_bar.py` — Renkli durum mesajları + dosya sayacı
  - `styles.py` — Catppuccin Mocha temalı tam CSS
  - Sürükle-bırak (Drag & Drop) ile dosya ekleme
  - Çift tıklama ile PDF açma
  - Tümünü seç/kaldır (☑/☐ sütun başlığı)
  - Seçilileri silme butonu (kalıcı dosya silme)
  - ↑↓ butonlarıyla sıra değiştirme
- **Yardımcı modüller** (`utils/`):
  - `page_parser.py` — Esnek sayfa numarası ayrıştırma ("1-5,8", "tümü" vb.)
  - `file_utils.py` — Dosya listeleme, benzersiz dosya adı üretme, boyut formatlama
  - `logger.py` — Standart loglama yapılandırması
- **Birim testleri** (`tests/`): 5 test dosyası, tüm çekirdek modüller için kapsamlı testler

### Düzeltildi
- Watermark opacity parametresi artık uygulanıyor (`shape.finish(fill_opacity=opacity)`)
- Ölü import (`pdf2docx.Converter`) kaldırıldı
- `pdf_compressor.py`: PyMuPDF `linearize` uyumsuzluğu giderildi
- `pdf_watermark.py`: `shape.insert_text(rotate=45)` hatası `morph` matris dönüşümüyle düzeltildi
- Terminal loglarında Windows `cp1254` unicode hatası giderildi
