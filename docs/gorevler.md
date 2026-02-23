# PDF Manipulator - Proje Geçmişi ve Görev Planı

Bu belge, "PDF Manipulator" projesinin başlangıcından itibaren alınan tüm kararları, uygulanan mimariyi, tamamlanan görevleri ve planlanan yeni özellikleri tek bir yerde tutmak amacıyla oluşturulmuştur.

---

## 🏗️ 1. Mimari Tasarım ve Kararlar (Faz 1)

Projenin başlangıcında aşağıdaki teknolojiler ve kütüphaneler seçilmiştir:
- **Dil:** Python 3.11+ (Zengin PDF kütüphaneleri ve hızlı geliştirme için)
- **GUI:** PyQt6 (Modern widget seti, sürükle-bırak (drag-drop) desteği için)
- **PDF Temel İşlemler:** pypdf (Birleştirme, ayırma, döndürme, sayfa yönetimi)
- **PDF Gelişmiş İşlemler:** PyMuPDF / fitz (Not alma, sıkıştırma, filigran, şifreleme)
- **OCR:** pytesseract + pdf2image (Görüntü tabanlı PDF'leri seçilebilir metne çevirmek için)
- **Office / Görsel Dönüşümleri:** 
  - Word: python-docx, pdf2docx
  - Excel: openpyxl, fpdf2
  - Resim: Pillow, pdf2image
- **Ortam Değişkenleri:** python-dotenv (Tesseract ve Poppler dizin yollarını saklamak için)

### Klasör Yapısı (Modüler Tasarım)
Proje modüler (OOP) bir yaklaşımla, arayüz (GUI) kodlarının çekirdek mantıktan (Core) tamamen ayrılacağı şekilde tasarlanmıştır:
- `core/`: Çekirdek PDF işleme mantıkları (GUI'den bağımsız).
- `converters/`: Format dönüştürme fonksiyonları.
- `gui/`: Kullanıcı arayüzü ve bileşenleri (Sadece `core/` ve `converters/` modüllerini çağırır).
- `utils/`: Loglama, dosya işlemleri ve yardımcı fonksiyonlar.
- `islenecek_pdfs/` ve `islenmis_pdfs/`: PDF'lerin okunduğu ve kaydedildiği statik dizinler.

---

## ✅ 2. Tamamlanan Görevler ve Modüller (Faz 2 & 3)

### Çekirdek PDF Modülleri (`core/`)
- [x] **`pdf_merger.py`**: PDF ve belirli sayfaları birleştirme, PDF arasına dosya ekleme.
- [x] **`pdf_splitter.py`**: PDF'i tekil sayfalara ayırma veya belirli aralıktaki sayfaları dışa aktarma.
- [x] **`pdf_page_manager.py`**: İstenen sayfaları silme, sayfaları (90°, 180°, 270°) döndürme.
- [x] **`pdf_ocr.py`**: OCR (Tesseract) ile görsel ağırlıklı PDF'lerde metinleri seçilebilir yapma.
- [x] **`pdf_metadata.py`**: Dosyalardaki sayfa sayısı, boyut ve meta verileri okuma.
- [x] **`pdf_annotator.py`**: İstenen sayfalara metin notları (annotation) ekleme.
- [x] **`pdf_compressor.py`**: Yüksek/Düşük/Orta kalite seçenekleriyle PDF boyutunu küçültme.
- [x] **`pdf_encryptor.py`**: PDF şifreleme (Parola koyma) ve şifre çözme.
- [x] **`pdf_watermark.py`**: Belgelere filigran (su damgası) ekleme.

### Dönüştürücü Modüller (`converters/`)
- [x] **`from_pdf.py`**: PDF -> Word (.docx), PDF -> Excel (.xlsx), PDF -> JPG formatlarına dönüştürme.
- [x] **`to_pdf.py`**: Word (.docx) -> PDF, Excel (.xlsx) -> PDF, JPG/JPEG -> PDF (Tekli ve çoklu görsel desteği) dönüşümleri.

---

## 🖥️ 3. GUI ve Arayüz Geliştirmeleri (Faz 4)

- [x] Karanlık Tema (Dark Theme) destekli `main_window.py` oluşturuldu.
- [x] PDF işlem butonları tek bir işlem panelinde gruplandırıldı (`action_panel.py`).
- [x] Özel dosya listesi tablosu (`file_list_widget.py`) oluşturuldu:
  - [x] Satırların sıra no değiştirilerek/butonla taşınması ve içerik sıralaması.
  - [x] Girdi menüsünde dosyanın kaç sayfa olduğunun ve dosya büyüklüğünün otomatik hesaplanması.
  - [x] Hangi sayfalar üzerinde işlem yapılacağının ("1-5, 8" veya "tümü" formatında) belirtilmesi.
- [x] Sol panel, "İşlenecek PDF'ler" (Girdi) ve "İşlenmiş PDF'ler" (Çıktı) olmak üzere çift liste yapısına çevrildi.
- [x] Dosya listelerine işletim sisteminden **Sürükle & Bırak (Drag & Drop)** ile dosya atma desteği eklendi. (Dosyalar `islenecek_pdfs` veya `islenmis_pdfs` klasörlerine kopyalanır).
- [x] Çift liste üzerinden çapraz PDF işlemleri yapabilme desteği (`action_panel` için) sağlandı.
- [x] Tüm tablodaki dosya satırlarına "Çift Tıklama" (Double Click) ile varsayılan görüntüleyicide açma işlevi atandı.
- [x] Tablo başlığına (☑ / ☐) tıklayarak tüm dosyaları (Select All) hızlıca seçme veya kaldırılması eklendi.
- [x] Tabloya eklenen "Seçilileri Sil" butonu sayesinde hem arayüzden hem de işletim sisteminden toplu dosya silme özelliği kazandırıldı.

---

## 🛠️ 4. Hata Giderimleri ve Optimizasyonlar (Faz 5)

- [x] Terminal loglarında (Windows `cp1254` kodlaması sebebiyle) yaşanan unicode (ok-> '→') yazım hatası giderildi (ASCII -> kullanıldı).
- [x] GUI tasarımı kullanıcı dönüşlerine göre rafine edildi (Gereksiz yazılı butonlar silindi, sütun başlıkları interaktif hale getirildi).
- [x] Tesseract ve Poppler gibi dış bağımlılıkların yokluğunda oluşan kilitlenmeler için uyarı ve klasör oluşturma yetenekleri eklendi.
- [x] Watermark opacity parametresi düzeltildi (`shape.finish(fill_opacity=opacity)` kullanıldı).
- [x] Ölü import (`pdf2docx.Converter`) kaldırıldı.
- [x] Türkçe karakter desteği eksikliği giderildi (Arial TTF font kaydı eklendi).
- [x] `pdf_compressor.py`: PyMuPDF `linearize` uyumsuzluğu çözüldü.
- [x] `pdf_watermark.py`: `rotate` parametresi `morph` matris dönüşümüyle değiştirildi.
- [x] StatusBar'daki `show_message()` lambda sorunu `_reset_status()` metodu ile düzeltildi.

---

## ⚡ 5. Performans ve Mimari İyileştirmeler (Faz 6)

- [x] **QThread Worker Sistemi** (`gui/worker.py`): `PdfWorker` ve `BatchWorker` sınıfları oluşturuldu. Tüm PDF işlemleri ana UI thread'inden ayrıldı — GUI donması tamamen önlendi.
- [x] **Progress Bar Entegrasyonu**: İşlem sırasında durum çubuğunda ilerleme çubuğu gösteriliyor, tamamlandığında otomatik gizleniyor.
- [x] **Buton Kilitleme**: İşlem devam ederken tüm butonlar `setEnabled(False)`, bittikten sonra tekrar aktif.
- [x] **Toplu İşlem (Batch) Desteği**: OCR, sıkıştırma, şifreleme ve filigran işlemleri artık çoklu dosya seçimiyle toplu çalışabiliyor.
- [x] **Kod Temizliği**: Tüm işlem handler'larındaki try/except blokları kaldırılıp `_run_worker()` / `_run_batch_worker()` pattern'ine taşındı.
- [x] **CHANGELOG.md** tüm proje geçmişiyle güncellendi (v0.1.0 ve v0.2.0).

---

## 🚀 6. Mevcut ve Gelecek Görevler (Faz 7)

Sonraki ana hedefler, uygulamayı bir masaüstü paketine dönüştürmektir.

- [ ] **Uygulamayı Paketleme (.exe oluşturma)**
  - [ ] PyInstaller yapılandırması (spec dosyası yazımı).
  - [ ] Bağımlılıkların (Poppler, Tesseract klasörleri) EXE paketinin içerisine gömülmesi veya relative path kullanılarak exe dışından okunacak şekilde ayarlanması.
  - [ ] İkon eklenmesi.
- [ ] PDF önizleme özelliği (dosyayı açmadan sayfa görüntüleme).
- [ ] Son kullanılan dizin hatırlama (QSettings).
- [ ] İşlem geri alma (undo) mekanizması.

---

## 📋 6. Proje Yönetim ve Dokümantasyon Kuralları

Bu proje kapsamında verimliliği ve takibi artırmak için aşağıdaki kurallar uygulanır:
- **Otomatik Dokümantasyon:** Her yeni görevde `docs/task.md` ve `docs/implementation_plan.md` dosyaları oluşturulur/güncellenir.
- **Süreç Takibi:** Tamamlanan her iş, bu dosya (`docs/gorevler.md`) üzerinde ilgili faza veya yeni bir maddeye eklenerek kayıt altına alınır.
- **Workflow Kullanımı:** Geliştirme sürecinde `.agent/workflows/update-docs.md` rehber olarak kullanılır.
