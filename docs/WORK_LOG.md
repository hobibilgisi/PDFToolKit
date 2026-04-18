# PDFToolKit - Islem Gunlugu

Bu dosya, proje uzerinde yapilan gercek islemlerin kurumsal kaydidir.

## Kullanim Kurallari

1. Her anlamli gorev icin yeni bir oturum kaydi ac.
2. Kod degisikliginden once en az `docs/yapılacaklar.md` ve `docs/WORK_LOG.md` dosyalarinin okundugunu yaz.
3. Gerekirse `docs/PROJECT_GUIDE.md` okundugu da belirtilmeli.
4. Komutlar, duzenlenen dosyalar, testler ve kararlar ozetlenmeli.
5. Yalnizca sonuc degil, yarim kalan durumlar ve riskler de kaydedilmeli.
6. Bu dosya guncellenmeden gorev tamamlanmis sayilmaz.

---

## Oturum Sablosu

```md
## Oturum 000 - YYYY-MM-DD HH:MM
- Talep:
- Okunan baglam:
  - docs/yapılacaklar.md
  - docs/WORK_LOG.md
  - docs/PROJECT_GUIDE.md (gerekiyorsa)
- Plan:
- Islemler:
  - 
- Dogrulama:
  - 
- Kararlar:
  - 
- Riskler / eksikler:
  - 
- Commit / dagitim:
  - Commit metni taslagi:
  - GitHub durumu:
  - Release durumu:
- Sonraki oturum notu:
```

---

## Surum Gecmisi (CHANGELOG Gocu)

### 0.4.2 - 2026-03-16
- Splash ekrani paketlenmis uygulamada acilmiyordu; logo dosyasi arama mantigi duzeltildi.
- GIF yukleme hatasinda cokme onlendi; statik logo moduna dusme davranisi eklendi.

### 0.4.1 - 2026-03-09
- Yeni uygulama ikonu eklendi; EXE, gorev cubugu ve masaustu kisayolu guncellendi.

### 0.4.0 - 2026-03-09
- Modern SVG ikon sistemi eklendi.
- Splash ekrani, donusturme modu diyalogu ve birlestirme secenekleri diyalogu eklendi.
- PDF birlestirmede ardısık ve dosya bazli numaralandirma modu eklendi.
- Word ve Excel'den PDF'e coklu dosya secimi desteklendi.
- Buton ikonlari ve numaralandirma gorselligi iyilestirildi.
- README kapsamli kullanma kilavuzuna donusturuldu.

### 0.2.0 - 2026-02-21
- QThread worker sistemi, BatchWorker ve progress bar entegrasyonu eklendi.
- PDF islemleri arka plan thread'ine tasindi; GUI donmasi giderildi.
- PyPDF2 yerine pypdf kullanilmaya baslandi.

### 0.1.0 - 2026-02-20
- Proje altyapisi, cekirdek PDF modulleri, donusturuculer, GUI ve yardimci moduller kuruldu.
- Ilk kapsamli test yapisi olusturuldu.

---

## Oturum 001 - 2026-03-19
- Talep: Projede kalici, kurumsal ve gelecege donuk bir calisma sistemi kurmak; talimat, log ve dokumantasyon duzenini standartlastirmak.
- Okunan baglam:
  - docs/yapılacaklar.md
  - docs/WORK_LOG.md
  - docs/PROJECT_GUIDE.md
- Plan:
  - repo icin kalici bir copilot talimati eklemek
  - yapilacaklar ile islem gecmisini ayiran bir log yapisi kurmak
- Calistirilan komutlar:
  - repo ve docs klasor yapisi incelendi
- Duzenlenen dosyalar:
  - .github/copilot-instructions.md
  - docs/WORK_LOG.md
  - docs/PROJECT_GUIDE.md
  - README.md
  - CHANGELOG.md (silindi)
  - docs/ENGINEERING_SYSTEM.md (silindi)
  - docs/WORKFLOW_TEMPLATES.md (silindi)
- Test / dogrulama:
  - belge yapisi ve dosya konumlari dogrulandi
- Teknik kararlar:
  - plan ve gerceklesen is kayitlari farkli dosyalarda tutulacak
  - repo talimati ayri, log ayri tutulacak
- Acik riskler / eksikler:
  - surec daha sonra sadeletilebilir
- Commit metni taslagi: docs: add engineering operating system and work log protocol
- GitHub durumu: Henuz yuklenmedi
- Release durumu: Release'e tek basina alinmasi gerekmeyebilir; surec iyilestirmesi olarak degerlendirilmeli
- Sonraki oturum notu: Yeni bir gorev baslarken once docs/yapılacaklar.md, sonra docs/WORK_LOG.md dosyalarini oku.

## Oturum 002 - 2026-03-19
- Talep: Sureci sadeletmek; tek talimat dosyasi, zorunlu log, standart kayit formati ve gorev basinda okunacak minimum dosya yapisina inmek. CHANGELOG gecmisini kaybetmeden WORK_LOG'a tasimak.
- Okunan baglam:
  - docs/yapılacaklar.md
  - docs/WORK_LOG.md
  - docs/PROJECT_GUIDE.md
- Plan:
  - talimat dosyasini ENGINEERING_SYSTEM icerigiyle birlestirmek
  - CHANGELOG icerigini WORK_LOG icinde surum gecmisi olarak tasimak
  - gereksiz md dosyalarini kaldirmak ve referanslari guncellemek
- Calistirilan komutlar:
  - dokuman referanslari tarandi
  - CHANGELOG icerigi okunup ozetlenerek bu dosyaya tasindi
- Duzenlenen dosyalar:
  - .github/copilot-instructions.md
  - docs/WORK_LOG.md
- Test / dogrulama:
  - dokumanlar arasi rol dagilimi kontrol edildi
  - silinen dosyalara kalan referanslar temizlendi
- Teknik kararlar:
  - zorunlu okuma seti iki dosyaya indirildi: docs/yapılacaklar.md ve docs/WORK_LOG.md
  - docs/PROJECT_GUIDE.md yalnizca ihtiyac halinde okunacak yardimci referans olarak kaldi
  - standart gorev ve oturum formati WORK_LOG icine gomuldu
- Acik riskler / eksikler:
  - PROJECT_GUIDE icindeki eski surec anlatimlari yeni yapiya gore guncellenmeli
- Commit metni taslagi: docs: simplify workflow docs and migrate changelog into work log
- GitHub durumu: Henuz yuklenmedi
- Release durumu: Yalnizca surec sadeletmesi; release notu zorunlu degil
- Sonraki oturum notu: Yeni gorevlerde ilk okuma seti docs/yapılacaklar.md ve docs/WORK_LOG.md olsun.

## Oturum 003 - 2026-03-20
- Talep: Baslangic akisinin komut mu yoksa repo protokolu mu oldugunu netlestirmek; ilk gorevin teknik alanlarini doldurmak; log sablonunu kisaltmak; PROJECT_GUIDE icindeki eski surec metinlerini yeni yapiya uydurmak.
- Okunan baglam:
  - docs/yapılacaklar.md
  - docs/WORK_LOG.md
  - docs/PROJECT_GUIDE.md
- Plan:
  - gorev listesindeki ilk maddenin teknik alanlarini doldurmak
  - oturum sablonunu daha kisa ve pratik hale getirmek
  - proje rehberinde AI hizli baslangic ve surec notlarini iki dosyali modele uydurmak
- Islemler:
  - ilgili belgeler okundu
  - gorev, log ve rehber metinleri sade sisteme gore guncellendi
- Dogrulama:
  - degisikliklerin yeni iki dosyali akisa uydugu kontrol edildi
- Kararlar:
  - baslangic akisi bir terminal komutu degil, repo icindeki talimat protokoludur
  - baska projeye gecildiginde ayni model yeni projenin kendi talimat dosyasina tasinar veya acilis promptu olarak verilir
- Riskler / eksikler:
  - baska projeler icin tekrar kullanilabilir bir hazir acilis prompt sablonu henuz ayri bir dosyaya alinmadi
- Commit / dagitim:
  - Commit metni taslagi: docs: refine simple workflow docs and prepare first task details
  - GitHub durumu: Henuz yuklenmedi
  - Release durumu: Release gerektirmez
- Sonraki oturum notu: Uygulamaya gececegin ilk gorev secildiginde yalnizca yapilacaklar ve work log okunarak baslanabilir.

## Oturum 004 - 2026-03-20
- Talep: README.md dosyasini docs altina tasimak.
- Okunan baglam:
  - docs/yapılacaklar.md
  - docs/WORK_LOG.md
  - docs/PROJECT_GUIDE.md
- Plan:
  - README icerigini docs altina tasimak
  - proje rehberindeki README yol referanslarini guncellemek
  - bu tasiyi loga kaydetmek
- Islemler:
  - kokteki README icerigi docs/README.md altina tasindi
  - PROJECT_GUIDE icindeki README konumlari guncellendi
- Dogrulama:
  - docs klasorunde yeni README hedefi olusturuldu
  - rehberdeki yol referanslari yeni konuma cekildi
- Kararlar:
  - README bundan sonra docs altinda tutulacak
- Riskler / eksikler:
  - kok README'nin kaldirilmasi GitHub depo ana sayfasindaki otomatik tanitim gorunumunu etkileyebilir
- Commit / dagitim:
  - Commit metni taslagi: docs: move README into docs folder
  - GitHub durumu: Henuz yuklenmedi
  - Release durumu: Release gerektirmez
- Sonraki oturum notu: README ile ilgili yeni degisikliklerde docs/README.md dosyasini esas al.

## Oturum 005 - 2026-03-20
- Talep: Kök README silinmesinin GitHub ana sayfa görünümünü bozma riskine karşı README taşıma işlemini geri almak.
- Okunan baglam:
  - docs/yapılacaklar.md
  - docs/WORK_LOG.md
  - docs/README.md
- Plan:
  - kok README dosyasini geri olusturmak
  - docs altindaki README kopyasini kaldirmak
  - rehber ve log referanslarini tekrar kok README'ye cevirmek
- Islemler:
  - README icerigi tekrar repo kokune alindi
  - PROJECT_GUIDE icindeki README referanslari kok konuma donduruldu
  - docs/README.md kaldirildi
- Dogrulama:
  - kok README geri getirildi
  - GitHub ana sayfa gorunumunu etkileyen risk ortadan kaldirildi
- Kararlar:
  - README bu repo icin kokte kalacak
- Riskler / eksikler:
  - yok
- Commit / dagitim:
  - Commit metni taslagi: docs: restore root README location
  - GitHub durumu: Henuz yuklenmedi
  - Release durumu: Release gerektirmez
- Sonraki oturum notu: README ile ilgili degisikliklerde repo kokundeki README.md dosyasini esas al.

  ## Oturum 006 - 2026-03-20
  - Talep: PDF Islemleri grubundaki Birlestir butonunun diger butonlardan farkli mavi gorunmesini kaldirmak; diger butonlarla ayni renge getirmek.
  - Okunan baglam:
    - docs/yapılacaklar.md
    - docs/WORK_LOG.md
  - Plan:
    - mavi gorunume neden olan ozel buton stilini bulmak
    - sadece Birlestir butonundaki farkli stili kaldirmak
    - sonucu loga kaydetmek
  - Islemler:
    - gui/action_panel.py icinde Birlestir butonuna verilen primaryButton stili kaldirildi
  - Dogrulama:
    - kod incelemesinde Birlestir butonunun artik varsayilan QPushButton temasini kullanacagi dogrulandi
  - Kararlar:
    - ana islem butonlari ayni gorunmeli; farkli vurgu gerekirse grup basliklari veya diyalog aksiyonlari uzerinden verilmeli
  - Riskler / eksikler:
    - gorunusel kontrol uygulama calistirilarak ayrica yapilmadi
  - Commit / dagitim:
    - Commit metni taslagi: style: align merge button color with other action buttons
    - GitHub durumu: Henuz yuklenmedi
    - Release durumu: Release gerektirmez
  - Sonraki oturum notu: Buton gorunum farklarinda once objectName ve ortak stil dosyasini kontrol et.