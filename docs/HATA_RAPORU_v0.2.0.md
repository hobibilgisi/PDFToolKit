# PDFToolKit v0.2.0 — Kapsamlı İnceleme ve Hata Raporu

**Tarih:** 26 Şubat 2026  
**İnceleyen:** İkinci bilgisayar — GitHub release'den indirilen paket test edildi  
**Test Ortamı:** Windows, Python 3.13.3, Tesseract 5.5.0 (sistem kurulu)  
**İncelenen Dosya Sayısı:** ~40 Python dosyası, ~7000+ satır  
**Sonuç:** 17 sorun tespit edildi (3 kritik, 3 yüksek, 5 orta, 6 düşük)

---

## Kullanıcı Senaryosu ve Beklenti

Beklenen akış:
1. Kullanıcı GitHub release sayfasından `PDFToolKit_v0.2.0.zip` indirir
2. ZIP'i çıkartır, `PDFToolKit.exe`'ye çift tıklar
3. İlk çalıştırmada tüm bileşenler hazır olur (Tesseract gömülü, Python gerekmez)
4. OCR dahil tüm özellikler sorunsuz çalışır
5. Yeni sürüm çıktığında uygulama otomatik bildirim gösterir ve tek tıkla günceller

**Gerçekleşen:** EXE açılıyor, GUI çalışıyor ama **OCR hata veriyor:**
```
OCR hatası (sayfa 1): [Errno 2] No such file or directory: 
'C:\Users\ilker\AppData\Local\Temp\tess_wmk4yraa.pdf'. 
Tesseract kurulu ve TESSERACT_PATH ayarlı mı?
```

---

## A. "TEK TUŞLA ÇALIŞSIN" HEDEFİ DURUMU

### Mevcut Mimari:
```
[build.py] → Nuitka ile derle → tesseract/ kopyala → ZIP oluştur → Release'a yükle
[settings.py] → EXE yanındaki tesseract/ klasörünü bul → TESSDATA_PREFIX ayarla
[updater.py] → GitHub API'den yeni sürüm kontrol et → ZIP indir → EXE değiştir
```

### Eksik Olan:
Runtime'da bağımlılık indiren/kuran bir mekanizma yok. Tasarım tamamen **"build zamanında her şeyi göm"** stratejisine dayanıyor. Bu strateji doğru — ama **build süreci eksik kopyalıyor**.

---

## B. KRİTİK SORUNLAR (3 adet)

### KRİTİK 1 — `build.py`: Tesseract eksik dosya kopyalıyor ⚠️ OCR HATANIZIN SEBEBİ

**Dosya:** `build.py` → `copy_tesseract()` fonksiyonu (satır ~140-156)

**Mevcut kod sadece şunları kopyalıyor:**
- `tesseract.exe`
- `*.dll`
- `tessdata/eng.traineddata`, `tur.traineddata`, `osd.traineddata`

**Eksik olan:** `tessdata/pdf.ttf` — Tesseract'ın PDF çıktısı üretmesi için **zorunlu** font dosyası. `pytesseract.image_to_pdf_or_hocr()` fonksiyonu Tesseract'ı PDF modunda çağırıyor ve Tesseract `tessdata/pdf.ttf` bulamadığı için geçici PDF dosyasını oluşturamıyor → `[Errno 2]` hatası veriyor.

Ayrıca `tessdata/configs/` klasörü de eksik.

**ÇÖZÜM — `build.py` içindeki `copy_tesseract()` fonksiyonunu değiştir:**

```python
def copy_tesseract():
    """Tesseract portable'ı dist klasörüne kopyalar."""
    src = PROJECT_DIR / "tesseract"

    if not src.exists():
        system_paths = [
            Path("C:/Program Files/Tesseract-OCR"),
            Path("C:/Program Files (x86)/Tesseract-OCR"),
        ]
        for p in system_paths:
            if (p / "tesseract.exe").exists():
                src = p
                print(f"ℹ️  tesseract/ bulunamadı, sistem kurulumu kullanılıyor: {src}")
                break

    if not src.exists():
        print(
            "\n⚠️  Tesseract bulunamadı — OCR çalışmaz!\n"
            "   Çözüm A: Proje kökünde 'tesseract/' klasörü oluşturun.\n"
            "   Çözüm B: Tesseract'ı kurun: https://github.com/UB-Mannheim/tesseract/wiki"
        )
        return

    dst = DIST_DIR / "tesseract"
    if dst.exists():
        shutil.rmtree(dst)

    # TÜM Tesseract kurulumunu kopyala (pdf.ttf, configs dahil)
    shutil.copytree(src, dst)

    # Boyut optimizasyonu: gereksiz dil paketlerini sil
    keep_langs = {"eng", "tur", "osd"}
    tessdata = dst / "tessdata"
    for td in tessdata.glob("*.traineddata"):
        if td.stem not in keep_langs:
            td.unlink()

    tess_size = sum(f.stat().st_size for f in dst.rglob("*") if f.is_file()) / 1_048_576
    print(f"✅ Tesseract kopyalandı: {dst} ({tess_size:.0f} MB)")
```

---

### KRİTİK 2 — `updater.py`: Güncelleme sadece EXE'yi değiştiriyor

**Dosya:** `utils/updater.py` → `apply_update()` fonksiyonu (satır ~127-150)

**Sorun:** `apply_update()` ZIP'ten sadece `PDFToolKit.exe`'yi buluyor ve mevcut EXE ile değiştiriyor. Ama Nuitka `--standalone` çıktısı yüzlerce DLL ve `.pyd` dosyası içeriyor. Yeni sürümde herhangi bir Python paketi güncellenirse, **eski DLL + yeni EXE = crash**.

**ÇÖZÜM — `apply_update()` tüm dosyaları güncellemeli (tesseract/ ve .pdf_data/ hariç):**

```python
def apply_update(zip_path: Path) -> bool:
    if not getattr(sys, 'frozen', False):
        logger.warning("apply_update yalnızca EXE modunda çalışır.")
        return False

    current_dir = Path(sys.executable).resolve().parent
    backup_exe = current_dir / "PDFToolKit.exe.old"
    extract_dir = zip_path.parent / "extracted"

    SKIP_DIRS = {"tesseract", ".pdf_data"}

    try:
        if backup_exe.exists():
            backup_exe.unlink(missing_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        # ZIP içindeki PDFToolKit/ klasörünü bul
        new_root = None
        for candidate in extract_dir.iterdir():
            if candidate.is_dir() and "PDFToolKit" in candidate.name:
                new_root = candidate
                break
        if not new_root:
            new_root = extract_dir

        # Mevcut EXE'yi yedekle
        current_exe = current_dir / "PDFToolKit.exe"
        if current_exe.exists():
            current_exe.rename(backup_exe)

        # tesseract/ ve .pdf_data/ HARİÇ tüm dosyaları kopyala
        for item in new_root.rglob("*"):
            rel = item.relative_to(new_root)
            if rel.parts and rel.parts[0] in SKIP_DIRS:
                continue
            dst = current_dir / rel
            if item.is_dir():
                dst.mkdir(parents=True, exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dst)

        logger.info("Güncelleme tamamlandı, yeniden başlatma gerekli.")
        return True

    except Exception as e:
        logger.error(f"Güncelleme hatası: {e}")
        # Yedekten geri dön
        if backup_exe.exists() and not current_exe.exists():
            backup_exe.rename(current_exe)
        return False
    finally:
        shutil.rmtree(extract_dir, ignore_errors=True)
```

---

### KRİTİK 3 — `worker.py`: BatchWorker hata durumunda sonuçları kaybediyor

**Dosya:** `gui/worker.py` → `BatchWorker.run()`

**Sorun:** Toplu işlemde (birden fazla dosyaya OCR/sıkıştırma/filigran) bazı dosyalar başarılı olup bazıları başarısız olursa: `error` sinyali gönderiliyor ama `finished` sinyali **hiç gönderilmiyor**. Başarılı olan dosyaların sonuçları kayboluyor.

**ÇÖZÜM:**

```python
def run(self):
    self._com_init()
    try:
        results = []
        errors = []
        for i, path in enumerate(self.file_paths):
            try:
                result = self.func(path, **self.kwargs)
                results.append(result)
            except Exception as e:
                errors.append(f"{Path(path).name}: {e}")
            self.progress.emit(
                int((i + 1) / len(self.file_paths) * 100),
                f"{i + 1}/{len(self.file_paths)}"
            )

        if results:
            self.finished.emit(results)
        if errors:
            self.error.emit("\n".join(errors))
    finally:
        self._com_uninit()
```

---

## C. YÜKSEK ÖNCELİKLİ SORUNLAR (3 adet)

### YÜKSEK 1 — `settings.py`: Sistem PATH'teki Tesseract bulunamıyor

**Dosya:** `config/settings.py` → `_detect_bundled_tesseract()` (satır ~81-107)

**Sorun:** Tesseract arama sırası:
1. `.env` → `TESSERACT_PATH` ✓
2. Frozen (EXE) → `base_dir/tesseract/tesseract.exe` ✓
3. Dev → proje kökü `tesseract/` ✓
4. **Sistem PATH** → **KONTROL EDİLMİYOR** ✗

Kaynak koddan çalıştırmada sistem Tesseract'ı kurulu olsa bile bulunamıyor.

**ÇÖZÜM — `_detect_bundled_tesseract()` sonuna ekle:**

```python
    # Fallback: Sistem PATH ve bilinen konumlar
    import shutil as _shutil
    system_tess = _shutil.which("tesseract")
    if system_tess:
        self.tesseract_path = system_tess
        return
    for candidate in [
        Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
        Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
    ]:
        if candidate.exists():
            self.tesseract_path = str(candidate)
            return
```

---

### YÜKSEK 2 — `worker.py`: COM `_com_uninit()` finally bloğu içinde değil

**Dosya:** `gui/worker.py` → `PdfWorker.run()` ve `BatchWorker.run()`

**Sorun:** `_com_uninit()` çağrısı try/finally bloğunun dışında. Beklenmeyen bir exception olursa COM initialization leak oluşur.

**ÇÖZÜM:** Tüm `run()` metotlarında:
```python
def run(self):
    self._com_init()
    try:
        # ... iş mantığı ...
    finally:
        self._com_uninit()
```

---

### YÜKSEK 3 — `file_list_widget.py`: ↑↓ buton lambda'ları stale row referansı

**Dosya:** `gui/file_list_widget.py` (satır ~246-260)

**Sorun:** Up/down buton lambda'ları `r=row` ile oluşturuluyor ama satır takasından sonra referanslar güncellenmediği için hızlı çift tıklamada yanlış satır taşınabiliyor.

**ÇÖZÜM:** Satır taşındıktan sonra butonların lambda'larını yeniden oluşturmak veya satır indeksini widget'tan dinamik olarak almak.

---

## D. ORTA ÖNCELİKLİ SORUNLAR (5 adet)

| # | Sorun | Dosya | Açıklama |
|---|-------|-------|----------|
| 1 | Test eksikliği | `tests/` | OCR, compressor, encryptor, watermark, annotator, metadata modüllerinin testleri yok |
| 2 | `pdf_to_excel` boş tablo | `converters/from_pdf.py` | Tablo bulunamazsa ham metin A sütununa yazılıyor, kullanıcıya uyarı yok |
| 3 | `decrypt_pdf` return tipi | `core/pdf_encryptor.py` | pypdf 4.x'te `reader.decrypt()` enum döndürüyor, `== 0` karşılaştırması hatalı |
| 4 | Watermark trial shape | `core/pdf_watermark.py` | Ölçüm döngüsünde `page.new_shape()` uncommitted oluşturuluyor, riskli |
| 5 | Arial font hardcoded | `core/pdf_watermark.py` + `converters/to_pdf.py` | `C:/Windows/Fonts/arial.ttf` sabit yazılmış |

---

## E. DÜŞÜK ÖNCELİKLİ SORUNLAR (6 adet)

| # | Sorun | Dosya |
|---|-------|-------|
| 1 | `osd.traineddata` varlık kontrolü yok | `core/pdf_ocr.py` |
| 2 | `images_to_pdf` dosya uzantısı kontrolü yok | `converters/to_pdf.py` |
| 3 | GitHub API rate limit (60/saat, unauthenticated) | `utils/updater.py` |
| 4 | `create_zip` sadece `.old` dosyalarını atlıyor | `build.py` |
| 5 | `.env` otomatik oluşturulmuyor (EXE'de `set_skipped_version` ham dosya yaratıyor) | `config/settings.py` |
| 6 | `format_pages_description` nokta belirsizliği | `utils/file_utils.py` |

---

## F. ANA BİLGİSAYARDA YAPILACAKLAR (Öncelik Sırasıyla)

| # | İş | Dosya | Kritiklik |
|---|-----|-------|-----------|
| 1 | `copy_tesseract()` → `shutil.copytree` + gereksiz dil silme | `build.py` | **KRİTİK** — OCR hatasının sebebi |
| 2 | `apply_update()` → tüm dosyaları güncelle (tesseract+data hariç) | `utils/updater.py` | **KRİTİK** — gelecek güncellemeler çökecek |
| 3 | `BatchWorker` → her zaman `finished` sinyali gönder | `gui/worker.py` | **KRİTİK** — toplu işlem sonuçları kaybolur |
| 4 | `_detect_bundled_tesseract()` → sistem PATH fallback | `config/settings.py` | YÜKSEK |
| 5 | COM `_com_uninit()` → finally bloğuna al | `gui/worker.py` | YÜKSEK |
| 6 | `decrypt_pdf` → pypdf 4.x enum kontrolü | `core/pdf_encryptor.py` | ORTA |
| 7 | Tekrar `python build.py` ile derle | Terminal | **KRİTİK** |
| 8 | Release'e yeni `PDFToolKit_v0.2.1.zip` yükle | GitHub | **KRİTİK** |

---

## G. İKİNCİ BİLGİSAYAR ORTAM BİLGİSİ (Referans)

```
Python:           3.13.3
Tesseract:        5.5.0 (C:\Program Files\Tesseract-OCR\)
Dil paketleri:    eng, tur, osd
.env:             YOK (sadece .env.example)
Proje tesseract/: YOK
Venv:             Mevcut ama aktif değil
```

### Kurulu Python Paketleri:
```
✅ pytesseract 0.3.13
✅ openpyxl 3.1.5
✅ Pillow 11.2.1
✅ pywin32 310
✅ python-dotenv 1.1.1
❌ PyQt6          (EKSİK)
❌ pypdf          (EKSİK)
❌ PyMuPDF        (EKSİK)
❌ python-docx    (EKSİK)
❌ pdf2docx       (EKSİK)
❌ fpdf2          (EKSİK)
❌ send2trash     (EKSİK)
❌ pytest         (EKSİK)
❌ nuitka         (EKSİK)
```

> **Not:** Bu eksiklikler kaynak kod için normaldir. EXE modunda tüm paketler Nuitka tarafından gömülüdür. Sorun build sürecindeki Tesseract kopyalama eksikliğindedir.

---

*Bu rapor, ana bilgisayardaki Copilot'a iletilmek üzere hazırlanmıştır. Düzeltmeler uygulandıktan sonra `python build.py` ile yeniden derleme yapılıp release güncellenmelidir.*
