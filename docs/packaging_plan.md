# PDFToolKit — Paketleme Planı

> **Durum:** 📋 Planlandı — Uygulamaya hazır.  
> **Tarih:** 22 Şubat 2026  
> **Hedef:** Tek tıkla çalışan, otomatik güncellenebilen, antivirüs dostu dağıtım.

---

## Mevcut Proje Durumu (Tamamlanan İşler)

### 8 Madde Test Düzeltmeleri ✅
1. ✅ Açıklayıcı çıktı dosya adları (13 işlem modülünde)
2. ✅ Yeni dosya liste sonuna ekleniyor (mtime sıralaması + scroll_to_bottom)
3. ✅ Döndür butonu kaldırıldı, yön düzeltme (yatay/dikey) eklendi
4. ✅ Yenile butonu menü çubuğuna taşındı
5. ✅ Yardım menüsü (Rehber, Sistem Gereksinimleri, Hakkında)
6. ✅ Tüm butonlara tooltip eklendi (20 buton)
7. ✅ Input/Output panelleri + çoklu format sürükle-bırak desteği
8. ✅ Filigran Türkçe karakter düzeltmesi (Arial TTF)

### Ekstra Düzeltmeler ✅
- ✅ Word/Excel→PDF: COM otomasyonu (pywin32) ile birebir dönüşüm, fpdf2 fallback
- ✅ Poppler bağımlılığı tamamen kaldırıldı (PyMuPDF ile değiştirildi)
- ✅ Tesseract OCR kuruldu (5.4.0) + Türkçe dil paketi
- ✅ Filigran ortalama: metin sayfanın tam ortasına yerleşiyor, uzun metin satır atlıyor, sığmazsa font küçülüyor
- ✅ Output paneline sürükle-bırak engellendi (sadece Input kabul eder)
- ✅ Seçilileri Sil: her iki listeden tek seferde, geri dönüşüm kutusuna (send2trash)

---

## Dış Bağımlılıklar (Python dışı)

| Bağımlılık | Gerekli mi? | Boyut | Not |
|---|---|---|---|
| **Tesseract OCR 5.4.0** | Sadece OCR için | ~70 MB | `tur.traineddata` + `eng.traineddata` gerekli |
| **Microsoft Office** | Sadece Word/Excel→PDF COM | — | Yoksa fpdf2 fallback devreye girer |
| **Arial font** | Filigran Türkçe karakterler | — | Windows'ta varsayılan olarak var |

## Python Bağımlılıkları (requirements.txt)

```
PyQt6>=6.6, pypdf>=4.0, PyMuPDF>=1.23, pytesseract>=0.3,
python-docx>=1.1, pdf2docx>=0.5, openpyxl>=3.1, fpdf2>=2.7,
Pillow>=10.0, send2trash>=1.8, pywin32>=306 (Windows),
python-dotenv>=1.0, pytest>=7.0
```

---

## Kullanıcı Gereksinimleri (Karar Verildi)

| Gereksinim | Karar |
|---|---|
| Kullanıcı deneyimi | Sadece EXE'ye çift tıklar, başka hiçbir şey yapmaz |
| Bağımlılıklar | Tesseract dahil her şey paketin içinde, internete gerek yok |
| Antivirüs | Ücretsiz yöntemlerle minimize edilir |
| Güncelleme | Uygulama içi — kullanıcı tek tıkla günceller |
| Dağıtım hedefi | Yakın çevre (5-20 kişi) |
| Boyut | Önemli değil |
| Gelecek | Web + Android portları planlanıyor |

---

## Seçilen Mimari: Nuitka + Tesseract Gömülü + GitHub Auto-Update

### Neden PyInstaller değil, Nuitka?

PyInstaller EXE içine sıkıştırılmış Python bytecode koyar → antivirüs bu yapıyı zararlı yazılımla karıştırır.  
**Nuitka**, Python kodunu gerçek C koduna derler, ardından native `.exe` üretir. Antivirüs açısından normal bir uygulama gibi görünür.

| | PyInstaller | **Nuitka** ✅ |
|---|---|---|
| Derleme yöntemi | Python bytecode arşivi | Gerçek C → native EXE |
| Antivirüs false positive | Yüksek | Çok düşük |
| Açılış hızı | Orta | Hızlı |
| Lisans | MIT (ücretsiz) | Apache 2.0 (ücretsiz) |
| Zorluk | Kolay | Orta (ilk kurulum) |

---

## Dağıtım Paketi Yapısı

Kullanıcıya gidecek ZIP içeriği:

```
PDFToolKit_v0.2.0.zip
└── PDFToolKit/
    ├── PDFToolKit.exe          ← çift tıkla çalışır
    ├── tesseract/              ← Tesseract portable (gömülü, kurulum gerekmez)
    │   ├── tesseract.exe
    │   └── tessdata/
    │       ├── tur.traineddata
    │       └── eng.traineddata
    ├── README.txt              ← "ZIP'i çıkart, PDFToolKit.exe'ye çift tıkla"
    └── CHANGELOG.txt
```

İlk çalıştırmada uygulama **otomatik** oluşturur (kullanıcı görmez):
```
PDFToolKit/
└── .pdf_data/    ← gizli klasör (Windows'ta görünmez)
    ├── input/
    ├── output/
    └── app.log
```

---

## Antivirüs Stratejisi (Ücretsiz)

Ücretli dijital imza olmadan antivirüs sorununu minimize etmek için **katmanlı yaklaşım**:

### Katman 1: Nuitka ile derleme
Native EXE üretildiği için antivirüs şüphesi dramatik şekilde azalır. PyInstaller'a kıyasla VirusTotal'da 2/72 yerine 0/72 veya 1/72 çıkma ihtimali çok daha yüksek.

### Katman 2: Microsoft'a ücretsiz whitelist başvurusu
Her sürüm paylaşılmadan önce [Microsoft Security Intelligence](https://www.microsoft.com/en-us/wdsi/filesubmission) portalına EXE yüklenir, "false positive" olarak bildirilir. Windows Defender'da birkaç günde temizlenir. **Ücretsiz.**

### Katman 3: VirusTotal'a önce gönder
Dağıtmadan önce [virustotal.com](https://www.virustotal.com)'a yükle → 72 antivirüs tarar. Büyük antivirüs firmalarına (Kaspersky, Avast, ESET) false positive formu doldur. **Ücretsiz.**

### Katman 4: Kullanıcıyı önceden bilgilendir
README.txt'e yaz: "Windows Smartscreen 'bilinmeyen yayıncı' uyarısı verebilir — 'Yine de çalıştır' seçin." Bu Windows'un imzasız her EXE'ye verdiği normal bir uyarıdır, virüs değildir.

> **Not:** Ücretsiz açık kaynak kod imzalama sertifikası (Certum, SignPath) YALNIZCA projeyi GitHub'da public open-source olarak yayınlarsan mümkün. Eğer ileride projeyi public yaparsan bu seçenek açılır.

---

## Güncelleme Mekanizması

### Akış

```
Uygulama açılır
    │
    ├─► Arka planda (thread) GitHub API'yi sorgula
    │   GET https://api.github.com/repos/KULLANICI/PDFToolKit/releases/latest
    │
    ├─► Mevcut sürüm < Yeni sürüm?
    │       EVET → Durum çubuğunda discrete bildirim göster:
    │               "🔄 Yeni sürüm v0.3.0 mevcut — Güncelle"
    │       HAYIR → Sessizce geç, kullanıcıyı rahatsız etme
    │
    └─► Kullanıcı "Güncelle" butonuna tıklar
            │
            ├─► GitHub Releases'dan yeni ZIP'i indir (progress bar ile)
            ├─► ZIP'i geçici klasöre çıkart
            ├─► Eski PDFToolKit.exe'yi yedekle → PDFToolKit.exe.old
            ├─► Yeni EXE'yi yerine koy
            └─► "Güncelleme tamamlandı, uygulamayı yeniden başlatın" mesajı
```

### Güncelleme Kapsama Alanı

Sadece `PDFToolKit.exe` güncellenir. `tesseract/` ve `.pdf_data/` klasörlerine dokunulmaz — kullanıcının dosyaları kaybolmaz.

### Kullanıcı Kontrolü

- "Bu sürümü atla" → `.env` dosyasına `SKIPPED_UPDATE_VERSION=0.3.0` yazar, bir daha sormaz
- "Sonra hatırlat" → o oturumda göstermez, uygulama kapanınca unutur
- İnternet yoksa → sessizce geç, hiç uyarı çıkma

---

## Tesseract Bağımlılığı — Gömme Planı

Tesseract kurulum gerektirmesin, kullanıcı habersiz çalışsın.

### `settings.py`'e eklenecek kod (uygulama başlangıcında)

```python
if getattr(sys, 'frozen', False):
    # EXE modunda: yanındaki tesseract/ klasörünü kullan
    bundled = self.base_dir / "tesseract" / "tesseract.exe"
    if bundled.exists():
        self.tesseract_path = str(bundled)
        os.environ["TESSDATA_PREFIX"] = str(self.base_dir / "tesseract" / "tessdata")
    # Yoksa .env'deki sistem kurulumu kullanılır (fallback)
```

### Tesseract Portable Nereden

Resmi kaynak: [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) → "portable" veya "no install" paketi.  
`tur.traineddata` ayrıca eklenir (`tessdata_best` veya `tessdata_fast` repodan).

---

## Yapılacaklar Listesi (Uygulama Sırası)

### Aşama 1 — Derleme Altyapısı
- [ ] `pip install nuitka` + gerekli bağımlılıklar (`ordered-set`, `zstandard`)
- [ ] İlk Nuitka test derlemesi (küçük deneme)
- [ ] `.spec` yerine Nuitka için `build.py` scripti yaz
- [ ] `pywin32` uyumluluğunu Nuitka ile doğrula

### Aşama 2 — Tesseract Entegrasyonu
- [ ] Tesseract portable indir ve `dist/tesseract/` altına yerleştir
- [ ] `settings.py`'e gömülü Tesseract algılama kodunu ekle
- [ ] OCR testi EXE modunda yapılır

### Aşama 3 — Güncelleme Modülü
- [ ] `utils/updater.py` oluştur (GitHub API sorgusu, indirme, self-replace)
- [ ] `gui/main_window.py`'e güncelleme bildirim UI'ı ekle (durum çubuğunda)
- [ ] `.env`'e `SKIPPED_UPDATE_VERSION` desteği ekle (`settings.py`)

### Aşama 4 — Antivirüs Hazırlığı
- [ ] EXE'yi VirusTotal'a gönder, raporu kaydet
- [ ] Microsoft Security Intelligence'a whitelist başvurusu yap
- [ ] README.txt'e Smartscreen açıklaması yaz

### Aşama 5 — Paket ve Dağıtım
- [ ] Dağıtım ZIP'i oluştur (`PDFToolKit_v0.2.0.zip`)
- [ ] GitHub'da private repo aç, Releases'a yükle
- [ ] Paylaşım linki oluştur

---

## Teknik Kısıtlar ve Notlar

### OneDrive'da derleme yapmayın
Proje OneDrive içinde (`G:\OneDrive Diski...`). Nuitka/PyInstaller derleme sırasında binlerce dosya hızlıca oluşturur, OneDrive senkronize etmeye çalışır → yavaşlar veya çöker.

```powershell
# Çıktıyı OneDrive dışına yönlendir
nuitka main.py --output-dir=C:\Build\PDFToolKit
```

### pywin32 ve COM thread güvenliği
`gui/worker.py` QThread kullanıyor. Word/Excel→PDF dönüşümü COM üzerinden yapılıyorsa worker thread başında `pythoncom.CoInitialize()` gerekli — aksi hâlde EXE modunda crash.

### Web ve Android portları için şimdiden yapılacak hazırlık
- İş mantığı (`core/`, `converters/`, `utils/`) ile GUI (`gui/`) katmanları zaten ayrı — bu doğru mimari, değişiklik gerekmez
- Web portu için `FastAPI` + `htmx` veya `Streamlit` tercih edilebilir (aynı `core/` kullanılır)
- Android için `Kivy` veya `BeeWare` mevcut ama PDF manipülasyonu mobilde kısıtlı — `core/` modüllerini API servisine taşımak daha mantıklı
- Şimdilik: `core/` ve `utils/` içine GUI bağımlılığı EKLEME (PyQt6 import vs.) — soyutlama korunsun

---

## Devam Etmek İçin

Bu dosyayı açıp "paketlemeye başlayalım" deyin.  
Aşama 1'den itibaren sırayla uygulanır.

