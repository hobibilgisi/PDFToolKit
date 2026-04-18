# PDFToolKit

Kapsamlı bir masaüstü PDF işleme uygulaması. PyQt6 tabanlı modern koyu tema arayüzü ile PDF birleştirme, ayırma, dönüştürme, numaralandırma ve daha fazlası.

**Sürüm:** 0.4.0 | **Platform:** Windows 10/11 | **Lisans:** MIT

---

## Özellikler

### PDF İşlemleri
| İşlem | Açıklama |
|-------|----------|
| **Birleştir** | Birden fazla PDF'yi tek dosyada birleştirir. Sıralama diyaloğu ile dosya sırasını belirleyin. Ardışık veya dosya bazlı numaralandırma seçeneği. |
| **Sayfalarına Ayır** | PDF'nin her sayfasını ayrı birer PDF dosyasına ayırır. |
| **Seçili Sayfaları Çıkar** | Belirtilen sayfaları çıkarıp yeni bir PDF oluşturur (ör: `1,3,5-8`). |
| **Sayfa Sil** | Belirtilen sayfaları siler, yeni dosya oluşturur. Orijinal dosyaya dokunulmaz. |
| **Yatay / Dikey Yap** | Sayfaları yatay (landscape) veya dikey (portrait) yöne çevirir. |
| **PDF Ekle** | Bir PDF'yi başka bir PDF'nin belirli sayfasından sonra ekler. |
| **Alfabetik Sırala** | Seçili dosyaları dosya adına göre A→Z sıralar. |
| **Adını Değiştir** | Seçili dosyanın adını değiştirir (uzantı korunur, geçersiz karakter kontrolü). |
| **Numaralandır / Sırala** | PDF'lere sıra numarası atar (dosya adı `001_ad.pdf` formatına güncellenir, her sayfaya kırmızı damga). |

### Dönüştürme
| İşlem | Açıklama |
|-------|----------|
| **PDF → Word** | PDF dosyasını düzenlenebilir Word (.docx) formatına çevirir. |
| **PDF → Excel** | PDF içindeki tablo verilerini Excel (.xlsx) formatına çevirir. |
| **PDF → JPG** | PDF'nin her sayfasını ayrı JPG görsel dosyasına çevirir. |
| **Word → PDF** | Word (.docx) dosyalarını PDF'e çevirir. Çoklu dosya seçimi ve birleştirme destekler. |
| **Excel → PDF** | Excel (.xlsx) dosyalarını PDF'e çevirir. Çoklu dosya seçimi ve birleştirme destekler. |
| **JPG → PDF** | Görselleri (JPG, PNG, BMP, TIFF) PDF'e çevirir. Ayrı ayrı veya birleştirerek dönüştürme seçeneği. |

### İşlemler
| İşlem | Açıklama |
|-------|----------|
| **OCR Uygula** | Taranmış PDF'lere metin tanıma uygular (Türkçe + İngilizce). Toplu işlem destekler. |
| **Sıkıştır** | PDF boyutunu küçültür — Hafif / Dengeli / Agresif kalite seçenekleri. |
| **Şifrele** | PDF'ye parola koruması ekler. Toplu şifreleme destekler. |
| **Şifre Çöz** | Şifreli PDF'nin parolasını girerek korumayı kaldırır. |
| **Filigran Ekle** | Sayfalarına çapraz filigran metni ekler. Toplu işlem destekler. |
| **Not Ekle** | Belirtilen sayfaya yapışkan not (annotation) ekler. |
| **Metin Vurgula** | PDF içinde metin arar ve bulduğu yerleri sarı ile vurgular. |

### Dosya Yönetimi
| İşlem | Açıklama |
|-------|----------|
| **Input/Output Klasörünü Aç** | İlgili klasörü dosya gezgininde açar. |
| **Seçileni Farklı Kaydet** | Seçili dosyaları istediğiniz konuma kaydeder. |
| **Seçilileri Sil** | Seçili dosyaları geri dönüşüm kutusuna gönderir. |

---

## Kullanma Kılavuzu

### Başlangıç

1. Uygulamayı çalıştırın (`PDFToolKit.exe` veya `python main.py`)
2. Dosyaları **Input** paneline sürükle-bırak ile ekleyin (PDF, Word, Excel, JPG, PNG desteklenir)
3. Dosya listesinden işlem yapmak istediğiniz dosyaları seçin (☑ onay kutusu)
4. Sağ paneldeki butonlardan istediğiniz işlemi tıklayın
5. Sonuçlar **Output** panelinde görünür

### Sayfa Seçimi

Birçok işlem belirli sayfalar üzerinde çalışabilir. **Sayfa Seçimi** alanına şu formatlardan birini yazın:

| Format | Örnek | Açıklama |
|--------|-------|----------|
| Tek sayfa | `3` | Sadece 3. sayfa |
| Aralık | `1-5` | 1'den 5'e kadar |
| Virgülle ayırma | `1,3,5` | 1, 3 ve 5. sayfalar |
| Karışık | `1-3,5,7-9` | 1-3, 5 ve 7-9. sayfalar |
| Tümü | boş bırakın veya `tümü` | Tüm sayfalar |

### PDF Birleştirme

1. En az 2 PDF dosyasını seçin
2. **Birleştir** butonuna tıklayın
3. Diyalog penceresinde:
   - Dosyaları sürükle-bırak veya ▲/▼ ile sıralayın
   - İsterseniz **"Sayfalara numara ekle"** seçeneğini işaretleyin
   - Numaralandırma modu seçin:
     - **Ardışık** (1, 2, 3, 4 …) — her sayfaya sırayla numara verir
     - **Dosya bazlı** — aynı kaynak dosyanın tüm sayfalarına aynı numara verir
4. **Birleştir** butonuna tıklayın

### Dönüştürme (Çoklu Dosya)

Word/Excel/JPG → PDF dönüştürmelerinde birden fazla dosya seçtiğinizde:
- **Ayrı ayrı dönüştür** — her dosya ayrı bir PDF olur
- **Birleştirerek dönüştür** — tüm dosyalar tek PDF'de birleştirilir
  - Dosya sırasını belirleyebilir ve sayfa numarası ekleyebilirsiniz

### Sürükle-Bırak

- **Input paneline** dosya sürükle-bırak ile dosya ekleyebilirsiniz
- **Output panelinden** dosyaları dışarı sürükleyerek başka bir konuma taşıyabilirsiniz

### Güncelleme

Uygulama başlangıçta yeni sürüm kontrolü yapar. Güncelleme varsa menü çubuğunda bildirim görünür. Tek tıkla güncelleme yapılabilir.

---

## Kurulum (Geliştirici)

### Python ile Çalıştırma

```bash
# Python 3.11+ gerekli
pip install -r requirements.txt
python main.py
```

### Harici Bağımlılıklar

| Bağımlılık | Gerekli | Not |
|------------|---------|-----|
| **Tesseract OCR** | Sadece OCR için | Uygulamayla birlikte gelir (EXE paketinde) |
| **Microsoft Office** | Word/Excel → PDF COM dönüşümü | Yoksa fpdf2 fallback devreye girer |

### EXE Derleme

```bash
python build.py
```

Nuitka ile standalone EXE oluşturur. Çıktı: `C:\Build\PDFToolKit\`

---

## Klasör Yapısı

```
PDFToolKit/
├── main.py                 # Uygulama giriş noktası
├── build.py                # Nuitka derleme scripti
├── requirements.txt        # Python bağımlılıkları
├── assets/                 # İkon ve görsel dosyalar
│   ├── icon.ico
│   ├── icon.png
│   └── splash logo.gif
├── config/                 # Ayarlar ve sürüm bilgisi
│   ├── __init__.py         # __version__ tanımı
│   └── settings.py         # Singleton ayar yöneticisi
├── core/                   # Çekirdek PDF işleme modülleri
│   ├── pdf_merger.py       # Birleştirme
│   ├── pdf_splitter.py     # Ayırma
│   ├── pdf_page_manager.py # Sayfa yönetimi
│   ├── pdf_ocr.py          # OCR
│   ├── pdf_compressor.py   # Sıkıştırma
│   ├── pdf_encryptor.py    # Şifreleme
│   ├── pdf_watermark.py    # Filigran
│   ├── pdf_annotator.py    # Not ekleme
│   └── pdf_metadata.py     # Meta bilgi okuma
├── converters/             # Format dönüştürme
│   ├── from_pdf.py         # PDF → Word/Excel/JPG
│   └── to_pdf.py           # Word/Excel/JPG → PDF
├── gui/                    # Kullanıcı arayüzü
│   ├── main_window.py      # Ana pencere
│   ├── action_panel.py     # İşlem butonları paneli
│   ├── file_list_widget.py # Dosya listesi tablosu
│   ├── icons.py            # SVG ikon kütüphanesi
│   ├── styles.py           # Catppuccin Mocha tema CSS
│   ├── worker.py           # QThread arka plan işleri
│   ├── status_bar.py       # Durum çubuğu
│   ├── splash_screen.py    # Açılış ekranı
│   ├── convert_mode_dialog.py    # Dönüştürme modu diyaloğu
│   ├── merge_options_dialog.py   # Birleştirme seçenekleri
│   └── order_dialog.py     # Numaralandırma diyaloğu
├── utils/                  # Yardımcı modüller
│   ├── page_parser.py      # Sayfa numarası ayrıştırıcı
│   ├── file_utils.py       # Dosya yardımcıları
│   ├── logger.py           # Loglama yapılandırması
│   └── updater.py          # Otomatik güncelleme
├── tests/                  # Birim testleri
│   ├── test_converters.py
│   ├── test_page_parser.py
│   ├── test_pdf_merger.py
│   ├── test_pdf_page_manager.py
│   └── test_pdf_splitter.py
└── tesseract/              # Gömülü Tesseract OCR
    ├── tesseract.exe
    └── tessdata/
```

### Çalışma Dizinleri

```
.pdf_data/input/   → Giriş dosyaları (gizli klasör)
.pdf_data/output/  → İşlem sonuçları (gizli klasör)
```

---

## Testler

```bash
python -m pytest tests/ -v
```

---

## Teknolojiler

| Kategori | Teknoloji |
|----------|-----------|
| GUI | PyQt6 (Catppuccin Mocha koyu tema) |
| PDF temel | pypdf >= 4.0 |
| PDF gelişmiş | PyMuPDF (fitz) |
| OCR | pytesseract + Tesseract 5.4.0 |
| Office dönüşüm | python-docx, pdf2docx, openpyxl, fpdf2, pywin32 |
| Görsel | Pillow |
| Paketleme | Nuitka |

---

## Lisans

MIT