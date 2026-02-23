# Sayfa Seçimi Kullanıcı Deneyimi İyileştirmesi

Bu çalışma, kullanıcıdan gelen geri bildirim doğrultusunda, dosya listesindeki "Sayfa Seçimi" alanının daha kompakt, modern ve tablo yapısına uygun hale getirilmesini hedefler.

## Önerilen Değişiklikler

### GUI Bileşenleri

#### [MODIFY] [styles.py](file:///g:/onedrive%20diski%2027.8.24/SoftWare/Desktop_Projects/pdfManuplator/gui/styles.py)
* Tablo içindeki input alanları için özel bir stil eklenecek (`QLineEdit#pageInput`).
* `min-height` değeri tablo satırlarını zorlamayacak şekilde düşürülecek.
* Kenarlık ve dolgu (padding) değerleri daha ince bir görünüm için optimize edilecek.

#### [MODIFY] [file_list_widget.py](file:///g:/onedrive%20diski%2027.8.24/SoftWare/Desktop_Projects/pdfManuplator/gui/file_list_widget.py)
* `page_input` nesnesine `setObjectName("pageInput")` eklenerek özel stile bağlanması sağlanacak.
* Input alanının hizalaması ve genişliği tablo sütununa göre rafine edilecek.
* Placeholder metni ("tümü") daha silik veya açıklayıcı yapılabilecek.

## Doğrulama Planı

### Manuel Doğrulama
* Uygulama çalıştırılarak tablo satırlarındaki sayfa seçimi alanının yüksekliği ve genel estetiği kontrol edilecek.
* Farklı sayfa sayılarına sahip PDF'ler eklenerek tablo görünümünün bozulmadığı teyit edilecek.
* Input alanına veri girişi yapıldığında stilin bozulup bozulmadığı gözlemlenecek.
