# PDFToolKit — Proje Rehberi

> **Son güncelleme:** 9 Mart 2026 — v0.4.0  
> **Amaç:** Bu belge, projenin tüm geçmişini, mimarisini, bilinen sorunları ve geliştirme kararlarını tek bir yerde toplar. Yeni bir geliştirici veya AI aracı bu dosyayı okuyarak proje üzerinde çalışabilir seviyede bilgi edinmelidir.

---

## İÇİNDEKİLER

1. [Proje Kimliği](#1-proje-kimliği)
2. [Mimari ve Teknoloji Kararları](#2-mimari-ve-teknoloji-kararları)
3. [Dosya ve Klasör Yapısı](#3-dosya-ve-klasör-yapısı)
4. [Modül Referansı](#4-modül-referansı)
5. [GUI Bileşenleri ve Buton Haritası](#5-gui-bileşenleri-ve-buton-haritası)
6. [Paketleme ve Dağıtım](#6-paketleme-ve-dağıtım)
7. [Güncelleme Mekanizması](#7-güncelleme-mekanizması)
8. [Bilinen Sorunlar ve Çözüm Önerileri](#8-bilinen-sorunlar-ve-çözüm-önerileri)
9. [Sürüm Geçmişi](#9-sürüm-geçmişi)
10. [Geliştirme Günlüğü](#10-geliştirme-günlüğü)
11. [Gelecek Görevler](#11-gelecek-görevler)
12. [Geliştirici Notları](#12-geliştirici-notları)

---

## 1. Proje Kimliği

| Alan | Değer |
|------|-------|
| **Proje adı** | PDFToolKit |
| **Sürüm** | 0.4.0 |
| **Dil** | Python 3.12+ |
| **GUI** | PyQt6 — Catppuccin Mocha koyu tema |
| **Platform** | Windows 10/11 (x86_64) |
| **Depo** | `github.com/hobibilgisi/PDFToolKit` (private) |
| **Venv** | `.venv/` (proje kökünde) |
| **Çalışma dizinleri** | `.pdf_data/input/` ve `.pdf_data/output/` (gizli, otomatik oluşur) |
| **Paketleme** | Nuitka → standalone EXE |
| **Dağıtım** | GitHub Releases → ZIP |
| **Hedef kitle** | Yakın çevre (5–20 kişi) |

---

## 2. Mimari ve Teknoloji Kararları

### 2.1 Temel Prensipler

- **GUI ↔ Core ayrımı:** `gui/` klasörü yalnızca `core/` ve `converters/` modüllerini çağırır. `core/` ve `utils/` içinde PyQt6 import'u YOKTUR. Bu sayede gelecekte web/mobil port yapılabilir.
- **QThread Worker pattern:** Tüm PDF işlemleri `gui/worker.py` içindeki `PdfWorker` ve `BatchWorker` ile arka plan thread'inde çalışır — GUI asla donmaz.
- **Singleton Settings:** `config/settings.py` — tek `Settings` nesnesi tüm modüller tarafından paylaşılır.
- **Tek sürüm kaynağı:** `config/__init__.py` → `__version__` — `main.py` ve `build.py` bu değeri okur.

### 2.2 Teknoloji Seçimleri

| Kategori | Teknoloji | Neden |
|----------|-----------|-------|
| GUI Framework | **PyQt6** | Modern widget seti, sürükle-bırak, QThread desteği |
| PDF temel işlemler | **pypdf >= 4.0** | Birleştirme, ayırma, döndürme, şifreleme |
| PDF gelişmiş işlemler | **PyMuPDF (fitz)** | Sıkıştırma, filigran, annotation, metin arama, PDF→JPG |
| OCR | **pytesseract + Tesseract 5.4.0** | Türkçe + İngilizce metin tanıma |
| Word dönüşüm | **python-docx + pdf2docx** | PDF↔Word çift yönlü |
| Excel dönüşüm | **openpyxl + fpdf2** | Tablo okuma/yazma |
| Word/Excel→PDF (birebir) | **pywin32 COM** | Microsoft Office varsa birebir dönüşüm, yoksa fpdf2 fallback |
| Görsel işleme | **Pillow** | Resim dönüştürme, splash ekranı |
| Paketleme | **Nuitka** | Python→C→native EXE, antivirüs dostu |
| Dosya silme | **send2trash** | Geri dönüşüm kutusuna gönderir |

> **Eski kararlar:** PyPDF2 → pypdf'e migrate edildi (v0.2.0). Poppler bağımlılığı tamamen kaldırıldı (PyMuPDF ile değiştirildi).

### 2.3 Dış Bağımlılıklar (Python Dışı)

| Bağımlılık | Gereklilik | Not |
|------------|------------|-----|
| **Tesseract OCR 5.4.0** | Sadece OCR için | EXE paketine gömülü, kullanıcı kurulum yapmaz |
| **Microsoft Office** | Word/Excel→PDF COM dönüşümü | Yoksa fpdf2 ile fallback çalışır |
| **Arial font** | Filigran + numaralandırma | Windows'ta varsayılan, yoksa Helvetica fallback |

---

## 3. Dosya ve Klasör Yapısı

```
PDFToolKit/
├── main.py                 # Uygulama giriş noktası (QApplication + MainWindow)
├── build.py                # Nuitka derleme scripti (EXE + ZIP üretir)
├── requirements.txt        # Python bağımlılıkları
├── README.md               # Kullanma kılavuzu
├── .env.example            # Ortam değişkenleri şablonu
├── .gitignore
│
├── assets/                 # Statik dosyalar
│   ├── icon.ico            # Uygulama ikonu (pencere + görev çubuğu)
│   ├── icon.png            # İkon PNG versiyonu
│   └── splash logo.gif     # Açılış animasyonu
│
├── config/                 # Ayarlar
│   ├── __init__.py         # __version__ = "0.4.0"
│   └── settings.py         # Singleton Settings sınıfı
│                             (input/output dizinleri, Tesseract yolu, log seviyesi)
│
├── core/                   # Çekirdek PDF işleme (GUI'den bağımsız)
│   ├── pdf_merger.py       # merge_pdfs(), insert_pdf()
│   ├── pdf_splitter.py     # split_all_pages(), extract_pages()
│   ├── pdf_page_manager.py # delete_pages(), rotate_pages(), get_page_count()
│   ├── pdf_ocr.py          # apply_ocr() — Tesseract ile metin katmanı
│   ├── pdf_compressor.py   # compress_pdf() — 3 kalite seviyesi
│   ├── pdf_encryptor.py    # encrypt_pdf(), decrypt_pdf()
│   ├── pdf_watermark.py    # add_watermark(), stamp_order_number()
│   ├── pdf_annotator.py    # add_annotation(), highlight_text()
│   └── pdf_metadata.py     # get_metadata()
│
├── converters/             # Format dönüştürme
│   ├── from_pdf.py         # pdf_to_word(), pdf_to_excel(), pdf_to_jpg()
│   └── to_pdf.py           # word_to_pdf(), excel_to_pdf(), jpg_to_pdf(),
│                             images_to_pdf(), convert_and_merge(),
│                             _stamp_all_pages()
│
├── gui/                    # PyQt6 kullanıcı arayüzü
│   ├── main_window.py      # MainWindow — ana pencere, menü çubuğu, splitter
│   ├── action_panel.py     # ActionPanel — 27 işlem butonu, 4 grup
│   │                         CollapsibleGroupBox — daraltılabilir grup widget'ı
│   ├── file_list_widget.py # FileListWidget — çift bölmeli dosya tablosu
│   │                         _DragOutTable — output'tan dışarı sürükleme
│   ├── icons.py            # SVG ikon kütüphanesi (Catppuccin Mocha renkleri, 28px)
│   ├── styles.py           # Catppuccin Mocha CSS tema
│   ├── worker.py           # PdfWorker + BatchWorker (QThread arka plan işleri)
│   ├── status_bar.py       # StatusBar — renkli mesajlar + progress bar
│   ├── splash_screen.py    # SplashScreen — GIF animasyonlu açılış
│   ├── convert_mode_dialog.py  # ConvertModeDialog — "ayrı ayrı / birleştir" seçimi
│   ├── merge_options_dialog.py # MergeOptionsDialog — sıralama + numaralandırma
│   └── order_dialog.py     # OrderDialog — dosya numaralandırma diyaloğu
│
├── utils/                  # Yardımcı modüller (GUI'den bağımsız)
│   ├── page_parser.py      # parse_page_input() — "1-5,8,tümü" ayrıştırıcı
│   ├── file_utils.py       # list_files(), unique_filename(), format_size()
│   ├── logger.py           # setup_logger() — standart loglama
│   └── updater.py          # check_for_update(), apply_update() — GitHub API
│
├── tests/                  # pytest birim testleri (35 test)
│   ├── test_converters.py      # jpg_to_pdf, images_to_pdf
│   ├── test_page_parser.py     # parse_page_input (15 senaryo)
│   ├── test_pdf_merger.py      # merge_pdfs, insert_pdf
│   ├── test_pdf_page_manager.py # delete_pages, rotate_pages, get_page_count
│   └── test_pdf_splitter.py    # split_all_pages, extract_pages
│
├── tesseract/              # Gömülü Tesseract OCR (EXE paketine dahil)
│   ├── tesseract.exe
│   └── tessdata/
│       ├── eng.traineddata
│       ├── tur.traineddata
│       ├── osd.traineddata
│       └── configs/
│
└── docs/                   # Proje dokumantasyon klasoru
    ├── PROJECT_GUIDE.md    # Proje rehberi
    ├── WORK_LOG.md         # Gerceklesen islemlerin kurumsal kaydi
    └── yapılacaklar.md     # Planlanan degisiklik listesi
```

---

## 4. Modül Referansı

### 4.1 Çekirdek Modüller (`core/`)

| Modül | Fonksiyonlar | Bağımlılık | Notlar |
|-------|-------------|------------|--------|
| `pdf_merger.py` | `merge_pdfs(file_list, output_path)`, `insert_pdf(base, insert, after_page, output)` | pypdf | `file_list`: `[{"path": str, "pages": list|None}]` |
| `pdf_splitter.py` | `split_all_pages(path, output_dir)`, `extract_pages(path, pages, output)` | pypdf | pages: 1-indexed liste |
| `pdf_page_manager.py` | `delete_pages(path, pages, output)`, `rotate_pages(path, pages, angle, output)`, `get_page_count(path)` | pypdf | angle: 90, 180, 270 |
| `pdf_ocr.py` | `apply_ocr(path, output, lang)` | pytesseract, PyMuPDF | lang: `"tur+eng"` varsayılan |
| `pdf_compressor.py` | `compress_pdf(path, output, quality)` | PyMuPDF | quality: `"low"`, `"medium"`, `"high"` |
| `pdf_encryptor.py` | `encrypt_pdf(path, output, user_pw, owner_pw)`, `decrypt_pdf(path, output, password)` | pypdf | |
| `pdf_watermark.py` | `add_watermark(path, text, output, opacity, fontsize, angle)`, `stamp_order_number(path, number, output)` | PyMuPDF | stamp: 20pt kırmızı, sağ üst köşe |
| `pdf_annotator.py` | `add_annotation(path, page, text, output)`, `highlight_text(path, search_text, pages, output)` | PyMuPDF | |
| `pdf_metadata.py` | `get_metadata(path)` | pypdf | dict döner: title, author, pages, size |

### 4.2 Dönüştürme Modülleri (`converters/`)

| Fonksiyon | Açıklama | Mekanizma |
|-----------|----------|-----------|
| `pdf_to_word(path, output)` | PDF → Word (.docx) | pdf2docx |
| `pdf_to_excel(path, output)` | PDF → Excel (.xlsx) | PyMuPDF tablo algılama + openpyxl |
| `pdf_to_jpg(path, output_dir)` | PDF → JPG (sayfa başına) | PyMuPDF |
| `word_to_pdf(path, output)` | Word → PDF | pywin32 COM (Office varsa), aksi hâlde fpdf2 |
| `excel_to_pdf(path, output)` | Excel → PDF | pywin32 COM, aksi hâlde fpdf2 |
| `jpg_to_pdf(path, output)` | Tek görsel → PDF | PyMuPDF |
| `images_to_pdf(paths, output)` | Çoklu görsel → tek PDF | PyMuPDF |
| `convert_and_merge(files, output, ...)` | Dönüştür → birleştir → numaralandır | Üst fonksiyon |
| `_stamp_all_pages(path, start, mode, page_counts)` | Sayfa numarası damgala | PyMuPDF, 20pt Bold kırmızı |

**`_stamp_all_pages` parametre detayı:**
- `mode="sequential"` → ardışık: 1, 2, 3, 4 …
- `mode="per_document"` + `page_counts=[2,3]` → dosya bazlı: 1,1,2,2,2
- Font: Arial Bold (`arialbd.ttf`), 20pt, kırmızı `(1.0, 0.0, 0.0)`
- Konum: sağ üst köşe, `Rect(width-80, 8, width-10, 38)`

### 4.3 GUI Sinyal Akışı

```
ActionPanel (buton tıklanır)
    │
    ├─► _run_worker(func, *args)       ← tek dosya işlemi
    │       PdfWorker.start()
    │           ├─► finished → operation_completed sinyal
    │           └─► error    → operation_failed sinyal
    │
    └─► _run_batch_worker(func, paths)  ← toplu işlem
            BatchWorker.start()
                ├─► progress → operation_progress sinyal → StatusBar progress bar
                ├─► finished → operation_completed sinyal
                └─► error    → operation_failed sinyal

MainWindow dinler:
    operation_completed → StatusBar.show_success() + dosya listelerini yenile
    operation_failed    → StatusBar.show_error()
    operation_progress  → StatusBar.show_progress()
```

### 4.4 Worker ve COM Thread Güvenliği

`gui/worker.py` içinde pywin32 COM kullanılıyorsa thread başında `pythoncom.CoInitialize()` çağrılır:

```python
def _com_init(self):
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except ImportError:
        pass

def _com_uninit(self):
    try:
        import pythoncom
        pythoncom.CoUninitialize()
    except ImportError:
        pass
```

> **DİKKAT:** `_com_uninit()` mutlaka `finally` bloğu içinde çağrılmalı (bkz. Bilinen Sorunlar #5).

---

## 5. GUI Bileşenleri ve Buton Haritası

### 5.1 Ana Pencere Düzeni

```
┌─────────────────────────────────────────────────────┐
│  Menü Çubuğu  [Dosya]  [Düzen]  [Yardım]  [🔄]     │
├───────────────────────────┬─────────────────────────┤
│  Sol Panel (Splitter)     │  Sağ Panel              │
│  ┌───────────────────┐    │  ┌───────────────────┐  │
│  │  Input Tablosu    │    │  │  PDF İşlemleri    │  │
│  │  (FileListWidget) │    │  │  (9 buton)        │  │
│  │  - ☑ Dosya adı    │    │  │  Dönüştürme ▶    │  │
│  │  - Sayfa sayısı   │    │  │  (6 buton)        │  │
│  │  - Boyut          │    │  │  İşlemler ▶      │  │
│  │  - Sayfa seçimi   │    │  │  (7 buton)        │  │
│  ├───────────────────┤    │  │  Dosya Yönetimi   │  │
│  │  Output Tablosu   │    │  │  (4 buton)        │  │
│  │  (_DragOutTable)  │    │  └───────────────────┘  │
│  └───────────────────┘    │                         │
├───────────────────────────┴─────────────────────────┤
│  StatusBar  [Mesaj]  [Progress]  [PDFToolKit v0.4.0]│
└─────────────────────────────────────────────────────┘
```

### 5.2 Buton Grupları ve Bağlantıları

#### PDF İşlemleri (sabit açık)
| Buton | Handler | Modül Çağrısı |
|-------|---------|---------------|
| Birleştir | `_on_merge()` | `MergeOptionsDialog` → `merge_pdfs()` → `_stamp_all_pages()` |
| Sayfalarına Ayır | `_on_split()` | `split_all_pages()` |
| Seçili Sayfaları Çıkar | `_on_extract()` | `extract_pages()` |
| Sayfa Sil | `_on_delete()` | `delete_pages()` |
| Yatay / Dikey Yap | `_on_orientation()` | `rotate_pages()` |
| PDF Ekle | `_on_insert()` | `insert_pdf()` |
| Alfabetik Sırala | `_on_sort_alpha()` | Tablo içi sıralama |
| Adını Değiştir | `_on_rename()` | `Path.rename()` |
| Numaralandır / Sırala | `_on_order_number()` | `OrderDialog` → `stamp_order_number()` |

#### Dönüştürme (daraltılabilir, varsayılan kapalı)
| Buton | Handler | Modül Çağrısı |
|-------|---------|---------------|
| PDF → Word | `_on_pdf_to_word()` | `pdf_to_word()` |
| PDF → Excel | `_on_pdf_to_excel()` | `pdf_to_excel()` |
| PDF → JPG | `_on_pdf_to_jpg()` | `pdf_to_jpg()` |
| Word → PDF | `_on_word_to_pdf()` | `ConvertModeDialog` → `word_to_pdf()` |
| Excel → PDF | `_on_excel_to_pdf()` | `ConvertModeDialog` → `excel_to_pdf()` |
| JPG → PDF | `_on_jpg_to_pdf()` | `ConvertModeDialog` → `jpg_to_pdf()` / `images_to_pdf()` |

#### İşlemler (daraltılabilir, varsayılan kapalı)
| Buton | Handler | Modül Çağrısı |
|-------|---------|---------------|
| OCR Uygula | `_on_ocr()` | `apply_ocr()` (BatchWorker) |
| Sıkıştır | `_on_compress()` | `compress_pdf()` (BatchWorker) |
| Şifrele | `_on_encrypt()` | `encrypt_pdf()` (BatchWorker) |
| Şifre Çöz | `_on_decrypt()` | `decrypt_pdf()` |
| Filigran Ekle | `_on_watermark()` | `add_watermark()` (BatchWorker) |
| Not Ekle | `_on_annotate()` | `add_annotation()` |
| Metin Vurgula | `_on_highlight()` | `highlight_text()` |

#### Dosya Yönetimi (sabit açık)
| Buton | Handler |
|-------|---------|
| Input Klasörünü Aç | `_on_open_input()` |
| Output Klasörünü Aç | `_on_open_output()` |
| Seçileni Farklı Kaydet | `_on_save_as()` |
| Seçilileri Sil | `_on_delete_selected()` → `send2trash` |

### 5.3 Diyalog Pencereleri

| Diyalog | Dosya | Kullanım | Getter Metotları |
|---------|-------|----------|------------------|
| `MergeOptionsDialog` | `gui/merge_options_dialog.py` | Birleştirme öncesi sıralama + numaralandırma | `get_ordered_files()`, `should_add_page_numbers()`, `get_start_number()`, `get_numbering_mode()` |
| `ConvertModeDialog` | `gui/convert_mode_dialog.py` | Çoklu dönüştürmede "ayrı/birleştir" | `get_mode()`, `get_ordered_files()`, `should_add_page_numbers()`, `get_start_number()` |
| `OrderDialog` | `gui/order_dialog.py` | Dosya numaralandırma sıra girişi | `get_order()` |

---

## 6. Paketleme ve Dağıtım

### 6.1 Neden Nuitka?

PyInstaller bytecode arşivler → antivirüs false positive yüksek. Nuitka Python→C→native EXE derler → antivirüs dostu.

### 6.2 Derleme Komutu

```bash
python build.py
```

**Çıktı dizini:** `C:\Build\PDFToolKit\` (OneDrive dışında, çünkü Nuitka binlerce dosya üretir ve OneDrive senkronizasyonu sorun çıkarır)

**ZIP yapısı:**
```
PDFToolKit_v0.4.0.zip
└── PDFToolKit/
    ├── PDFToolKit.exe
    ├── PDFToolKit.lnk      ← ZIP kısayolu
    ├── tesseract/           ← gömülü OCR motoru
    ├── *.dll, *.pyd         ← Nuitka standalone bağımlılıkları
    └── ...
```

### 6.3 Antivirüs Stratejisi (Ücretsiz)

1. **Nuitka** native EXE üretir — false positive dramatik şekilde azalır
2. **VirusTotal'a gönder** — 72 antivirüs tarar, sorunlu olanlar için false positive formu doldur
3. **Microsoft Security Intelligence'a başvur** — Windows Defender whitelist (ücretsiz)
4. **README'de kullanıcıyı bilgilendir** — SmartScreen "bilinmeyen yayıncı" uyarısı normal

### 6.4 Tesseract Gömme

`build.py` içindeki `copy_tesseract()` fonksiyonu Tesseract'ı `dist/` altına kopyalar. `settings.py` EXE modunda yanındaki `tesseract/` klasörünü otomatik bulur ve `TESSDATA_PREFIX` ayarlar.

---

## 7. Güncelleme Mekanizması

### 7.1 Akış

```
Uygulama açılır
  → Arka plan thread'inde GitHub API sorgusu:
    GET https://api.github.com/repos/hobibilgisi/PDFToolKit/releases/latest
  → Mevcut sürüm < yeni sürüm?
    EVET → Menü çubuğunda "Yeni sürüm v0.X.0 — Güncelle" butonu
    HAYIR → sessiz
  → Kullanıcı tıklar:
    1. ZIP indir (progress bar)
    2. Eski EXE'yi yedekle (.old)
    3. Yeni dosyaları kopyala
    4. "Yeniden başlatın" mesajı
```

### 7.2 Kapsam

- Güncellenen: EXE + DLL'ler + pyd dosyaları
- Güncellenmeyenler: `tesseract/`, `.pdf_data/` (kullanıcı dosyaları korunur)
- draft/prerelease sürümler filtrelenir

### 7.3 Kullanıcı Kontrolleri

- "Bu sürümü atla" → `.env`'e `SKIPPED_UPDATE_VERSION` yazar
- "Sonra hatırlat" → sadece o oturum boyunca gizler
- İnternet yoksa → sessizce geçer

---

## 8. Bilinen Sorunlar ve Çözüm Önerileri

### KRİTİK SEVİYE

#### KS-1: `build.py` — Tesseract eksik dosya kopyalıyor

**Durum:** v0.2.0'da tespit edildi, çözüm kodu yazıldı ama uygulanıp uygulanmadığı doğrulanmalı.

**Sorun:** Mevcut `copy_tesseract()` sadece `tesseract.exe`, `*.dll` ve 3 traineddata dosyasını kopyalıyor. `tessdata/pdf.ttf` ve `tessdata/configs/` klasörü eksik kalıyor → OCR'ın PDF çıktısı üretemez.

**Çözüm:** `copy_tesseract()` içinde `shutil.copytree()` ile TÜM Tesseract kurulumunu kopyala, sonra gereksiz dil paketlerini sil:
```python
shutil.copytree(src, dst)
keep_langs = {"eng", "tur", "osd"}
for td in (dst / "tessdata").glob("*.traineddata"):
    if td.stem not in keep_langs:
        td.unlink()
```

#### KS-2: `updater.py` — Güncelleme sadece EXE'yi değiştiriyor

**Sorun:** `apply_update()` ZIP'ten sadece EXE çıkarıyor. Nuitka standalone yüzlerce DLL içerir — yeni sürümde paket güncellenirse eski DLL + yeni EXE = crash.

**Çözüm:** `tesseract/` ve `.pdf_data/` HARİÇ tüm dosyaları güncelle. Batch script ile çalışan EXE'nin kilidini aş.

#### KS-3: `worker.py` — BatchWorker hata durumunda sonuçları kaybediyor

**Sorun:** Toplu işlemde bazı dosyalar başarılı, bazıları başarısız olunca `error` sinyali gönderiliyor ama `finished` sinyali ATIN — başarılı sonuçlar kaybolur.

**Çözüm:** Her iki sinyali de gönder: başarılı olanlar `finished`, hatalar `error` ile.

### YÜKSEK SEVİYE

#### YS-1: `settings.py` — Sistem PATH'teki Tesseract bulunamıyor

Kaynak koddan çalıştırırken sistem PATH'teki Tesseract algılanmıyor. `shutil.which("tesseract")` fallback eklenebilir.

#### YS-2: `worker.py` — COM `_com_uninit()` finally bloğu dışında

Exception olursa COM initialization leak oluşabilir. `_com_uninit()` mutlaka `try/finally` içinde olmalı.

#### YS-3: `file_list_widget.py` — ↑↓ buton lambda stale referansı

Hızlı çift tıklamada yanlış satır taşınabilir. Lambda'lar dinamik row index almalı.

### ORTA SEVİYE

| # | Sorun | Dosya |
|---|-------|-------|
| 1 | `pdf_to_excel`: Tablo bulunamazsa kullanıcıya uyarı yok | `converters/from_pdf.py` |
| 2 | `decrypt_pdf`: pypdf 4.x'te `reader.decrypt()` enum döndürüyor, `== 0` hatalı | `core/pdf_encryptor.py` |
| 3 | Watermark ölçüm döngüsünde uncommitted shape riski | `core/pdf_watermark.py` |
| 4 | Arial font path hardcoded (`C:/Windows/Fonts/arial.ttf`) | `core/pdf_watermark.py`, `converters/to_pdf.py` |
| 5 | GitHub API rate limit (60/saat unauthenticated) | `utils/updater.py` |

### DÜŞÜK SEVİYE

| # | Sorun | Dosya |
|---|-------|-------|
| 1 | `osd.traineddata` varlık kontrolü yok | `core/pdf_ocr.py` |
| 2 | `images_to_pdf` dosya uzantısı kontrolü yok | `converters/to_pdf.py` |
| 3 | `create_zip` sadece `.old` dosyalarını atlıyor | `build.py` |
| 4 | `.env` EXE modunda otomatik oluşturulmuyor | `config/settings.py` |

---

## 9. Sürüm Geçmişi

### v0.4.0 (2026-03-09)

**Tema: Görsel modernizasyon + birleştirme iyileştirmeleri + proje temizliği**

- SVG ikon sistemi (27 buton, Catppuccin Mocha renkleri, 28px)
- Uygulama ikonu (PDF + dişli rozet)
- Splash ekranı (şeffaf GIF animasyonu)
- Dönüştürme modu diyaloğu: çoklu dosya → "ayrı ayrı / birleştir"
- Birleştirme diyaloğu: sıralama + numaralandırma modu seçimi
- Numaralandırma: ardışık (1,2,3,4) veya dosya bazlı (1,1,2,2)
- Sayfa numara fontu: 20pt kalın kırmızı (Arial Bold)
- Çoklu dosya seçimi: Word/Excel → PDF
- Proje temizliği: gereksiz dosyalar, __pycache__, eski dökümanlar silindi
- README kapsamlı kullanma kılavuzu olarak yeniden yazıldı

### v0.3.0 (2026-03-08)

**Tema: Arayüz modernizasyonu + dosya yönetimi + paketleme iyileştirmeleri**

- Daraltılabilir buton grupları (CollapsibleGroupBox)
- Output sürükle-bırak (_DragOutTable)
- Input/Output Klasörünü Aç, Seçileni Farklı Kaydet butonları
- Alfabetik Sırala, Adını Değiştir butonları
- Numaralandır / Sırala: dosya adı 001_ad.pdf + sayfa damgası
- Uzun dosya yolu (255+) algılama ve yeniden adlandırma diyaloğu
- Sürüm bilgisi durum çubuğunda, güncelleme detay gösterimi
- Tek sürüm kaynağı (`config/__init__.py`)
- ZIP kısayolu (.lnk) ve güncelleme batch mekanizması
- Güncelleme: draft/prerelease filtreleme

### v0.2.0 (2026-02-21)

**Tema: Performans + thread güvenliği + toplu işlem**

- QThread Worker sistemi (PdfWorker, BatchWorker)
- Progress bar entegrasyonu
- Buton kilitleme (işlem sırasında)
- Toplu işlem: OCR, sıkıştırma, şifreleme, filigran
- PyPDF2 → pypdf migrasyonu
- Kod tekrarı azaltma (_run_worker, _run_batch_worker)

### v0.1.0 (2026-02-20)

**Tema: Temel altyapı + 9 çekirdek modül + GUI**

- 9 çekirdek PDF işleme modülü
- 6 dönüştürme fonksiyonu (PDF↔Word/Excel/JPG)
- PyQt6 GUI: koyu tema, sürükle-bırak, çift dosya listesi
- Sayfa seçimi ayrıştırıcı ("1-5,8,tümü")
- 5 test dosyası, kapsamlı birim testleri
- Tesseract OCR (Türkçe+İngilizce)
- Hata düzeltmeleri: watermark opacity, Türkçe karakter, unicode log

---

## 10. Geliştirme Günlüğü

### Oturum: 2026-03-09 (v0.4.0)

1. **Birleştirme numaralandırma modu eklendi:**
   - `gui/merge_options_dialog.py` — Ardışık / dosya bazlı radio butonlar
   - `converters/to_pdf.py` — `_stamp_all_pages()` güncellendi: mode + page_counts parametreleri, 20pt Bold kırmızı
   - `gui/action_panel.py` — `_on_merge()` güncellendi: mode ve page_counts aktarımı

2. **Proje temizliği yapıldı:**
   - `__pycache__/` dizinleri silindi
   - `assets/` araç scriptleri silindi (`_analyze_gif.py`, `generate_icon.py`)
   - `docs/` sadeleştirildi: `antigravity_talks/`, `implementation_plan.md`, `PAKETLEME_OTURUMU.md`, `task.md` silindi

3. **Dokümantasyon güncellendi:**
    - README.md → kapsamlı kullanma kılavuzuna dönüştürüldü
    - sürüm geçmişi daha sonra WORK_LOG içine taşınacak şekilde toparlandı
    - Sürüm → 0.4.0

### Oturum: 2026-03-08 (v0.3.0)

| Konu | Açıklama | Değiştirilen Dosyalar |
|------|----------|----------------------|
| KONU 1 | Output sürükle-bırak + Input/Output Aç + Farklı Kaydet | `file_list_widget.py`, `main_window.py`, `action_panel.py` |
| KONU 2 | Alfabetik Sırala butonu | `action_panel.py` |
| KONU 3 | Adını Değiştir butonu | `action_panel.py` |
| KONU 4 | Numaralandır / Sırala diyaloğu + stamp | `gui/order_dialog.py`, `core/pdf_watermark.py`, `action_panel.py` |
| KONU 5 | Güncelleme kontrolü analizi + draft/prerelease filtre | `utils/updater.py` |
| KONU 6 | Daraltılabilir buton grupları (CollapsibleGroupBox) | `action_panel.py`, `styles.py` |

### Önceki oturumlar (v0.3.0 devamı, tarih yok)

- Modern SVG ikon sistemi oluşturuldu (`gui/icons.py`, 27 ikon)
- Tüm butonlardan emoji kaldırıldı, SVG ikonlar eklendi
- Birleştirme ikonu görünmüyordu → renk `_BLUE` → `_PEACH` değiştirildi
- İkon boyutu 20→24→28px artırıldı
- Splash ekranı eklendi (`gui/splash_screen.py`) — Pillow + numpy ile GIF transparanlık
- Dönüştürme modu diyaloğu eklendi (`gui/convert_mode_dialog.py`)
- Birleştirme seçenekleri diyaloğu eklendi (`gui/merge_options_dialog.py`)
- Word/Excel→PDF çoklu dosya seçimi (`getOpenFileNames`)

---

## 11. Gelecek Görevler

### Öncelikli (Bilinen sorun düzeltmeleri)

- [ ] `build.py`: `copy_tesseract()` → `shutil.copytree` ile tam kopyalama (KS-1)
- [ ] `updater.py`: `apply_update()` → tesseract/data hariç tüm dosyaları güncelle (KS-2)
- [ ] `worker.py`: `BatchWorker` → başarılı sonuçları da gönder (KS-3)
- [ ] `worker.py`: `_com_uninit()` → `finally` bloğuna al (YS-2)
- [ ] `settings.py`: Sistem PATH Tesseract fallback (YS-1)

### Yeni özellikler

- [ ] PDF önizleme (dosyayı açmadan sayfa görüntüleme)
- [ ] Son kullanılan klasörü hatırlama (QSettings)
- [ ] Geri alma (undo) mekanizması
- [ ] Eksik testler: OCR, compressor, encryptor, watermark, annotator, metadata

---

## 12. Geliştirici Notları

### Bu dosyayı kullanan AI için hızlı başlangıç

1. **Ilk okuma:** once `docs/yapılacaklar.md`, sonra `docs/WORK_LOG.md` dosyasini oku
2. **Bu rehberi ne zaman oku:** mimari, paketleme, dagitim veya genis kapsamli davranis degisikligi varsa bu dosyaya gec
3. **Sürüm:** `config/__init__.py` → `__version__` (tek kaynak)
4. **Test:** `python -m pytest tests/ -v` (35 test, <1 saniye)
5. **Import kontrolü:** `python -c "from gui.action_panel import ActionPanel; print('OK')"`
6. **Uygulama başlatma:** `python main.py` (`.venv` aktif olmalı)
7. **GUI yapısı:** `action_panel.py` tüm buton handler'larını, `main_window.py` ana pencereyi yönetir
8. **Değişiklik yaparken:**
   - `core/` ve `utils/` içine PyQt6 import'u ekleme
   - `_run_worker()` pattern'ini kullan, try/except yazma
   - Yeni buton eklerken `gui/icons.py`'ye ikon ekle
    - kullanıcıya yansıyan önemli değişikliklerde `docs/WORK_LOG.md` icindeki surum gecmisini guncelle
   - `config/__init__.py`'de sürümü artır

### Kullanıcı talimatları

> Adimlarla ilerle, onay alarak ilerle, kontroller yaparak ilerle. Her goreve docs/yapılacaklar.md ve docs/WORK_LOG.md okuyarak basla. Testleri tests/ klasorune kaydet. Programin mevcut islerligini bozma. Ilerlemeyi log dosyasina kaydet.

### Önemli dosya ilişkileri

```
config/__init__.py ──► main.py (pencere başlığı, sürüm gösterimi)
                   ──► build.py (ZIP adı, tag)
                   ──► gui/status_bar.py (durum çubuğu)

gui/action_panel.py ──► core/*.py (tüm PDF işlemleri)
                    ──► converters/*.py (format dönüşümleri)
                    ──► gui/worker.py (arka plan çalıştırma)
                    ──► gui/*_dialog.py (diyalog pencereleri)

gui/main_window.py ──► gui/action_panel.py (sinyal bağlantıları)
                   ──► gui/file_list_widget.py (dosya tabloları)
                   ──► gui/status_bar.py
                   ──► gui/splash_screen.py
                   ──► utils/updater.py (güncelleme kontrolü)

gui/icons.py ──► gui/action_panel.py (tüm buton ikonları)
             ──► gui/merge_options_dialog.py (birleştir ikonu)

config/settings.py ──► Tüm modüller (input/output dizini, tesseract yolu)
```
