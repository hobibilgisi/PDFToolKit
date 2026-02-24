# PDFToolKit — Paketleme Oturum Bağlamı

> Bu dosya, yeni bir AI oturumu açıldığında "nerede kaldık" sorusunu yanıtlamak için tutulur.  
> Güncellenme tarihi: 24 Şubat 2026  
> Son oturum: Konuşma 5 — Git push tamamlandı, derleme bekleniyor.

---

## ‼️ KALDIĞIMIZ YER — HIZLI BAŞLANGIÇ

**Son yapılan:** Git push başarılı — kaynak kod GitHub'da.  
**Sıradaki adım:** Nuitka ile EXE derleme → `python build.py`

Yeni bir oturumda şunu söyle:
> "PAKETLEME_OTURUMU.md dosyasını oku. Kaldığımız yerden devam edelim."

### Yapılacak 2 Adım Kaldı:

```
1. [ ] python build.py çalıştır   → EXE + ZIP üretir (C:\Build\PDFToolKit)
       - İlk seferde MinGW64 indirilecek (~60 MB, "yes" de)
       - Derleme 15-30 dakika sürebilir
       - Çıktı: C:\Build\PDFToolKit\PDFToolKit\PDFToolKit.exe

2. [ ] GitHub Releases'a yükle    → Kullanıcıların indireceği link oluşur
       - github.com/hobibilgisi/PDFToolKit → Releases → Create new release
       - Tag: v0.2.0
       - Başlık: PDFToolKit v0.2.0
       - PDFToolKit_v0.2.0.zip dosyasını sürükle-bırak ile yükle
       - Yayınla
```

---

## 1. Proje Kimliği

| Alan | Değer |
|---|---|
| Proje adı | PDFToolKit |
| Versiyon | 0.2.0 |
| Dil | Python 3.12.1 |
| GUI | PyQt6 |
| Venv | `.venv/` (proje kökünde, CPython official) |
| Python yolu | `G:\onedrive diski 27.8.24\SoftWare\Desktop_Projects\PDFToolKit\.venv\Scripts\python.exe` |
| İşletim sistemi | Windows 10/11 x86_64 |

---

## 2. Tamamlanan Uygulama İşleri (Paketlemeden Önce Bitti)

1. ✅ Açıklayıcı çıktı dosya adları (13 işlem modülünde)
2. ✅ Yeni dosya liste sonuna ekleniyor (mtime sıralaması + scroll_to_bottom)
3. ✅ Döndür butonu kaldırıldı → yön düzeltme (yatay/dikey) eklendi
4. ✅ Yenile butonu menü çubuğuna taşındı
5. ✅ Yardım menüsü (Rehber, Sistem Gereksinimleri, Hakkında)
6. ✅ Tüm butonlara tooltip eklendi (20 buton)
7. ✅ Input/Output panelleri + çoklu format sürükle-bırak desteği
8. ✅ Filigran Türkçe karakter düzeltmesi (Arial TTF)
9. ✅ Word/Excel→PDF: COM otomasyonu (pywin32) + fpdf2 fallback
10. ✅ Poppler kaldırıldı → PyMuPDF ile değiştirildi
11. ✅ Tesseract 5.4.0 kuruldu + Türkçe dil paketi
12. ✅ Filigran ortalama: tam merkez, uzun metin satır atlar, font küçülür
13. ✅ Output paneline sürükle-bırak engellendi
14. ✅ Seçilileri Sil: her iki listeden, geri dönüşüm kutusuna (send2trash)

---

## 3. Paketleme Kararları (Kesinleşti)

### 3.1 Hedef Kullanıcı
- Yakın çevre (5-20 kişi)
- Teknik bilgisi yok, hiçbir kurulum yapmayacak
- Sadece ZIP indir → çıkart → EXE çift tıkla

### 3.2 Derleme Aracı: Nuitka ✅ KURULDU
**Neden PyInstaller değil:** PyInstaller bytecode arşivi oluşturur → antivirüs false positive.  
Nuitka Python'u gerçek C koduna derler → native EXE → antivirüs dostu.

```
Kurulu sürüm: Nuitka 4.0.1
Derleyici: GCC/MinGW64 (ilk derleme sırasında otomatik indirilecek, ~60 MB, bir kerelik)
Paketler: nuitka, ordered-set, zstandard, imageio
```

### 3.3 Dağıtım Modeli: Portable ZIP (onedir benzeri)
```
PDFToolKit_v0.2.0.zip
└── PDFToolKit/
    ├── PDFToolKit.exe
    ├── tesseract/               ← gömülü, kurulum gerekmez
    │   ├── tesseract.exe
    │   └── tessdata/
    │       ├── tur.traineddata
    │       └── eng.traineddata
    ├── README.txt
    └── CHANGELOG.txt
```

### 3.4 Tesseract: Gömülü Portable
- Kullanıcı Tesseract kurmayacak
- EXE'nin yanındaki `tesseract/` klasöründen çalışır
- `settings.py` zaten `sys.frozen` kontrolü yapıyor → kod değişikliği minimal
- Portable Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

### 3.5 Güncelleme: Uygulama İçi GitHub Releases
- Arka thread'de GitHub API sorgusu (açılışı yavaşlatmaz)
- Durum çubuğunda bildirim: "Yeni sürüm v0.X.X mevcut — Güncelle"
- Sadece EXE güncellenir, `tesseract/` ve `.pdf_data/` dokunulmaz
- Seçenekler: "Güncelle" / "Sonra hatırlat" / "Bu sürümü atla"
- "Atla" → `.env`'e `SKIPPED_UPDATE_VERSION=` yazar

### 3.6 Antivirüs (Ücretsiz Katmanlı)
1. Nuitka → native EXE (en kritik adım)
2. Microsoft Security Intelligence portalı → whitelist başvurusu (ücretsiz)
3. VirusTotal → dağıtmadan önce tara, büyük firmalara bildir (ücretsiz)
4. README.txt → "Smartscreen uyarısı normal, 'Yine de çalıştır' seçin"
5. **Ücretli imza YOK** — bütçe yok, gerek de yok yakın çevre için

### 3.7 Dijital İmza Notu
Gelecekte proje GitHub'da public/open-source yapılırsa:
- **SignPath.io** (ücretsiz open-source plan) veya **Certum open-source sertifikası** gündeme gelebilir.
- Şimdilik kapsam dışı.

---

## 4. Kod Değişiklik Planı

### 4.1 `config/settings.py` — Gömülü Tesseract Algılama
Mevcut `__init__` metoduna EXE modu tespiti sonrasına eklenecek:

```python
# Tesseract gömülüyse EXE'nin yanındaki klasörü kullan
if getattr(sys, 'frozen', False):
    bundled = self.base_dir / "tesseract" / "tesseract.exe"
    if bundled.exists():
        self.tesseract_path = str(bundled)
        os.environ["TESSDATA_PREFIX"] = str(self.base_dir / "tesseract" / "tessdata")
```

### 4.2 `utils/updater.py` — YENİ DOSYA
GitHub Releases API sorgulama, indirme, self-replace mantığı.  
İçerik: `check_for_update()`, `download_update()`, `apply_update()` fonksiyonları.

### 4.3 `gui/main_window.py` — Güncelleme UI
- Başlangıçta arka thread'de `check_for_update()` çağrısı
- Durum çubuğuna bildirim widgeti eklenir

### 4.4 `gui/worker.py` — COM Thread Güvenliği
Word/Excel→PDF dönüşümleri için worker thread'e:
```python
import pythoncom
# run() metodunun başında:
pythoncom.CoInitialize()
# run() metodunun sonunda (finally bloğunda):
pythoncom.CoUninitialize()
```

### 4.5 `build.py` — YENİ DOSYA (Nuitka derleme scripti)
Proje kökünde, tek komutla EXE üretir. İçerik:

```python
# Çalıştırma: python build.py
# Çıktı: C:\Build\PDFToolKit\dist\PDFToolKit.exe (OneDrive dışında)
import subprocess, sys

cmd = [
    sys.executable, "-m", "nuitka",
    "--standalone",
    "--enable-plugin=pyqt6",
    "--windows-console-mode=disable",  # konsol penceresi çıkmasın
    "--windows-icon-from-ico=assets/icon.ico",  # varsa
    "--output-dir=C:/Build/PDFToolKit",
    "--output-filename=PDFToolKit",
    "--include-package=fitz",
    "--include-package=pytesseract",
    "--include-package=docx",
    "--include-package=pdf2docx",
    "--include-package=openpyxl",
    "--include-package=fpdf2",
    "--include-package=send2trash",
    "--include-package=win32com",
    "--include-package=pythoncom",
    "--include-data-dir=config=config",  # .env.example varsa
    "main.py"
]
subprocess.run(cmd, check=True)
```

---

## 5. Yapılacaklar — Onay Bekleniyor

### Aşama 1 — Altyapı Kurulumu ✅ TAMAMLANDI
- [x] Nuitka 4.0.1 kuruldu
- [x] `ordered-set`, `zstandard`, `imageio` kuruldu
- [x] MinGW64 → ilk `build.py` çalışmasında otomatik inecek

### Aşama 2 — Kod Değişiklikleri ✅ TAMAMLANDI
- [x] `config/settings.py` → gömülü Tesseract algılama + `set_skipped_version()` + `skipped_update_version`
- [x] `gui/worker.py` → COM thread güvenliği (`_com_init`/`_com_uninit`, her iki worker'da)
- [x] `utils/updater.py` → yeni dosya: `UpdateChecker`, `UpdateDownloader`, `check_for_update`, `download_update`, `apply_update`, `cleanup_old_exe`
- [x] `gui/main_window.py` → güncelleme kontrol akışı, durum çubuğu bildirim butonu, indirme/uygulama handler'ları
- [x] `build.py` → Nuitka derleme scripti (Tesseract kopyalama + ZIP oluşturma dahil)
- [x] `.env.example` → kullanıcı yapılandırma şablonu

### Aşama 2.5 — Tesseract + Git ✅ TAMAMLANDI (24 Şubat)
- [x] Tesseract 5.4.0 portable → `tesseract/` klasörüne kopyalandı (eng, tur, osd)
- [x] `.gitignore` oluşturuldu (tesseract/, .venv/, .env, __pycache__ vb. hariç)
- [x] `updater.py` → `GITHUB_OWNER = "hobibilgisi"`, `GITHUB_REPO = "PDFToolKit"`
- [x] `build.py` → sistem Tesseract fallback'i eklendi
- [x] `git init` + `git remote add origin https://github.com/hobibilgisi/PDFToolKit.git`
- [x] İlk commit: `v0.2.0: İlk sürüm` (49 dosya, 7169 satır)
- [x] `git push -u origin main` ✅ BAŞARILI

### Aşama 3 — Derleme ⏳ SIRADA
- [ ] `python build.py` çalıştır (MinGW64 sorusuna "yes" de)
- [ ] Test: `C:\Build\PDFToolKit\PDFToolKit\PDFToolKit.exe`

### Aşama 4 — Test (DERLEME SONRASI)
- [ ] Temiz bir Windows ortamında (ya da Python kurulu olmayan makinede) EXE'yi test et
- [ ] OCR işlemini EXE modunda test et
- [ ] Word/Excel→PDF dönüşümünü EXE modunda test et
- [ ] Güncelleme bildirimini test et (test için `APP_VERSION`'ı geçici düşür)

### Aşama 5 — Antivirüs ve Dağıtım
- [ ] VirusTotal tarama: https://www.virustotal.com
- [ ] Microsoft Security Intelligence whitelist: https://www.microsoft.com/en-us/wdsi/filesubmission
- [ ] GitHub Releases'a ZIP yükle
- [ ] README.txt oluştur (SmartScreen uyarısı açıklaması dahil)

### Aşama 6 — Inno Setup (İsteğe Bağlı, Sonra)
- [ ] Inno Setup indir: https://jrsoftware.org/isinfo.php
- [ ] `.iss` kurulum scripti yaz (dist/ klasörünü paketler)
- [ ] `PDFToolKit_v0.2.0_Setup.exe` üret

---

## 6. Önemli Teknik Notlar

### OneDrive Sorunu
Proje `G:\OneDrive Diski...` içinde. Nuitka derleme çıktısı mutlaka **OneDrive dışına** yönlendirilmeli:
```
Önerilen çıktı dizini: C:\Build\PDFToolKit
```

### PyQt6 Plugin
Nuitka'nın `--enable-plugin=pyqt6` flag'i zorunlu, aksi hâlde Qt bileşenleri derlemeye dahil edilmez.

### Mevcut `settings.py` Avantajı
`_get_base_dir()` fonksiyonu zaten `sys.frozen` kontrolü yapıyor. Nuitka da `sys.frozen = True` setliyor, bu yüzden EXE modunda `base_dir` otomatik EXE'nin klasörünü gösterecek. Mevcut mantık çalışır.

### Web ve Android — Gelecek Not
`core/` ve `converters/` modülleri GUI'ye bağımlı değil → doğru mimari.  
Kural: bu katmanlara PyQt6 import'u girmesin. Girerse web/Android portunu zorlaştırır.  
Web için öneri: FastAPI + aynı `core/` modülleri.  
Android için öneri: `core/` → REST API → mobil istemci (BeeWare yerine bu daha pratik).

---

## 7. Yeni Oturumda Hızlı Başlangıç

Bu dosyayı oku, sonra şunu söyle:
> "Aşama 2'ye geçelim" veya belirli bir aşamayı belirt.

Tüm kararlar kesinleşmiş, tartışmaya kapalı. Sadece uygulamaya devam edilecek.
