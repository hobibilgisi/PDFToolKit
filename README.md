# PDFToolKit

Kapsamlı bir masaüstü PDF işleme uygulaması. PyQt6 tabanlı modern arayüz ile PDF birleştirme, ayırma, dönüştürme ve daha fazlası.

## Özellikler

- **PDF Birleştirme** — Birden fazla PDF'yi sıralı birleştir
- **PDF Ayırma** — Sayfalarına ayır veya belirli sayfaları çıkar
- **Sayfa Yönetimi** — Sayfa silme, ekleme, döndürme
- **OCR** — Görüntü tabanlı PDF'lerde metin seçilebilir yapma
- **Format Dönüştürme** — Word, Excel, JPG ↔ PDF
- **Not Ekleme** — Metin notu, vurgulama
- **Sıkıştırma** — PDF dosya boyutunu küçültme
- **Şifreleme** — PDF'yi parola ile koruma
- **Filigran** — Metin filigranı ekleme

## Kurulum

### Python Bağımlılıkları

```bash
pip install -r requirements.txt
```

### Harici Bağımlılıklar

#### Tesseract OCR (OCR özelliği için)
1. [Tesseract indirme sayfası](https://github.com/UB-Mannheim/tesseract/wiki) adresinden indirin
2. Kurulumda "Add to PATH" seçeneğini işaretleyin
3. `.env` dosyasındaki `TESSERACT_PATH` değerini güncelleyin

#### Poppler (PDF→JPG dönüştürme için)
1. [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) adresinden indirin
2. Arşivi bir klasöre çıkarın
3. `.env` dosyasındaki `POPPLER_PATH` değerini `bin` klasörüne yönlendirin

## Kullanım

```bash
python main.py
```

1. Uygulamayı çalıştırın
2. Dosyaları Input paneline sürükle-bırak ile ekleyin (PDF, Word, Excel, JPG, PNG)
3. Dosya listesinden seçim yapın ve istediğiniz işlemi uygulayın
4. Sonuçlar Output panelinde görünür

## Klasör Yapısı

```
.pdf_data/input/   → Giriş dosyaları (gizli klasör)
.pdf_data/output/  → İşlem sonuçları (gizli klasör)
```

## Konfigürasyon

`.env` dosyasını düzenleyerek ayarları değiştirin:

| Değişken | Açıklama | Varsayılan |
|----------|----------|------------|
| PDF_INPUT_DIR | Giriş klasörü | input |
| PDF_OUTPUT_DIR | Çıkış klasörü | output |
| LOG_LEVEL | Loglama seviyesi | INFO |
| TESSERACT_PATH | Tesseract yolu | (boş) |

## Testler

```bash
python -m pytest tests/ -v
```

## Teknolojiler

Python 3.11+ | PyQt6 | pypdf | PyMuPDF | pytesseract | pdf2image | python-docx | pdf2docx | openpyxl | fpdf2 | Pillow

## Lisans

MIT
