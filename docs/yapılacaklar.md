# Yapılacaklar

## 1. PDF sonuna düzenleme bilgisi ekleme
- Amaç: Oluşturulan dosyanın son sayfasına işlem özeti eklemek
- Yapılacak iş: Son sayfaya "bu dosya ... tarihinde ... tarafından PDFToolKit ile düzenlenmiştir" açıklaması eklensin.
- Yapılacak iş: Açıklama içinde yapılan değişiklikler maddeler halinde yazılsın.
- Yapılacak iş: Bu açıklamanın eklenmesi için kullanıcıdan onay istensin.
- Kullanıcıdan istenecek bilgiler: Düzenlemeyi yapan kullanıcı adı, tarih bilgisi
- Etkilenen alanlar: PDF cikti ureten ilgili core/converters akislarinda son sayfaya ozet metni ekleme, kullanici onay akisi ve ozet icerigi olusturma mantigi
- Test kontrolü: Onay verildiginde olusan PDF'in son sayfasinda ozet metni gorunmeli; onay verilmediginde ek sayfa veya metin eklenmemeli; kullanici adi ve tarih dogru yazilmali; farkli islem turlerinde cikti bozulmamali
- Başka kaynaktan istenecek bilgi: Yapılan değişiklik listesinin hangi işlemlerden otomatik üretileceği netleştirilmeli.
- Yeni eklenti / bağımlılık ihtiyacı: Ilk asamada mevcut PDF kutuphaneleri yeterli gorunuyor; uygulama sirasinda yetersiz kalirsa yeniden degerlendirilecek
- Commit metni taslağı: feat: add optional edit summary page to generated PDFs
- GitHub'a yüklendi mi: Hayır
- Release'e eklenecek mi: Evet
- Notlar: Ozet metninin sabit formatta mi yoksa isleme gore dinamik mi uretilecegi uygulama oncesinde netlestirilmeli

## 2. Yeni görev
- Amaç:
- Yapılacak iş:
- Kullanıcıdan istenecek bilgiler:
- Etkilenen alanlar:
- Test kontrolü:
- Başka kaynaktan istenecek bilgi:
- Yeni eklenti / bağımlılık ihtiyacı:
- Commit metni taslağı:
- GitHub'a yüklendi mi: Hayır
- Release'e eklenecek mi:
- Notlar: