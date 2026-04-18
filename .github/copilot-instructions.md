# PDFToolKit - Calisma Protokolu

Bu repo icinde minimum ama zorunlu isletim modeli kullanilir.

## Zorunlu Dosyalar

1. `docs/yapılacaklar.md`
   - planlanan gorevler burada tutulur
2. `docs/WORK_LOG.md`
   - yapilan isler, komutlar, testler ve kararlar burada tutulur

## Zorunlu Okuma Sirasi

Her yeni gorevde, anlamli bir kod degisikligi veya komut calistirmadan once su dosyalari oku:

1. `docs/yapılacaklar.md`
2. `docs/WORK_LOG.md`

Gorev mimari, paketleme, dagitim veya genis kapsamli davranis degisikligi iceriyorsa ek olarak `docs/PROJECT_GUIDE.md` okunur.

## Zorunlu Calisma Kurallari

1. Her gorev icin ise baslamadan once kisa bir plan yaz.
2. Her anlamli komut, kod degisikligi, test sonucu ve karar `docs/WORK_LOG.md` dosyasina islenmeli.
3. `docs/WORK_LOG.md` icindeki standart oturum formatina uy.
4. Log guncellenmeden gorev tamamlanmis sayilmaz.

## Mimari ve Kalite Kurallari

1. `core/` ve `utils/` icine PyQt6 import'u ekleme.
2. GUI mantigi `gui/` klasorunde kalmali; cekirdek is mantigi `core/`, yardimcilar `utils/`, donusturmeler `converters/` icinde kalmali.
3. Clean Code, SOLID, tek sorumluluk ve dusuk bagimlilik ilkelerine uy.
4. Degisiklikler minimum kapsamli, geri alinabilir ve testlenebilir olmali.
5. Yeni davranis ekleniyorsa mumkunse `tests/` altinda test ekle veya mevcut testleri guncelle.
6. Kullanici arayuzu degisikliklerinde acik, tutarli ve anlasilir davranis onceliklidir.

## Token ve Baglam Yonetimi

1. Ilk baglam icin sadece `docs/yapılacaklar.md` ve `docs/WORK_LOG.md` oku.
2. Daha derin teknik baglam yalnizca gerektiginde ilgili kod dosyalarindan ve `docs/PROJECT_GUIDE.md` dosyasindan al.
3. Ayrintili tarihce icin `docs/WORK_LOG.md` kullan; ayni aciklamayi sohbet icinde tekrar etme.