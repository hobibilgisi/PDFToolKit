"""
PDFToolKit - Sayfa Numarası Ayrıştırıcı

Kullanıcı girdisini ("1-5,8", "3", "tümü" vb.) sayfa numarası listesine çevirir.
"""


def parse_page_input(input_str: str, max_pages: int) -> list[int]:
    """
    Sayfa numarası girdisini ayrıştırır ve sıralı bir liste döndürür.

    Desteklenen formatlar:
        - "tümü" veya "" → tüm sayfalar [1, 2, ..., max_pages]
        - "3" → tek sayfa [3]
        - "1-5" → aralık [1, 2, 3, 4, 5]
        - "1,3,5" → virgülle ayrılmış [1, 3, 5]
        - "1-3,5,7-9" → karışık [1, 2, 3, 5, 7, 8, 9]

    Args:
        input_str: Kullanıcı tarafından girilen sayfa numarası metni.
        max_pages: PDF'deki toplam sayfa sayısı (üst sınır doğrulaması için).

    Returns:
        Sıralı ve tekrarsız sayfa numaraları listesi (1-indexed).

    Raises:
        ValueError: Geçersiz girdi veya aralık dışı sayfa numarası durumunda.
    """
    if max_pages < 1:
        raise ValueError(f"Geçersiz sayfa sayısı: {max_pages}")

    # Boşlukları temizle
    input_str = input_str.strip()

    # Boş veya "tümü" → tüm sayfalar
    if not input_str or input_str.lower() in ("tümü", "tumu", "all", "hepsi"):
        return list(range(1, max_pages + 1))

    pages = set()

    # Virgülle ayır
    parts = input_str.split(",")

    for part in parts:
        part = part.strip()

        if not part:
            continue

        # Aralık kontrolü: "1-5"
        if "-" in part:
            range_parts = part.split("-", 1)

            if len(range_parts) != 2:
                raise ValueError(f"Geçersiz aralık formatı: '{part}'")

            try:
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
            except ValueError:
                raise ValueError(f"Geçersiz sayfa numarası: '{part}'")

            if start > end:
                raise ValueError(
                    f"Aralık başlangıcı bitişten büyük olamaz: '{part}'"
                )

            if start < 1:
                raise ValueError(
                    f"Sayfa numarası 1'den küçük olamaz: '{part}'"
                )

            if end > max_pages:
                raise ValueError(
                    f"Sayfa numarası {max_pages}'i aşıyor: '{part}'"
                )

            pages.update(range(start, end + 1))

        else:
            # Tek sayfa: "3"
            try:
                page = int(part)
            except ValueError:
                raise ValueError(f"Geçersiz sayfa numarası: '{part}'")

            if page < 1:
                raise ValueError(
                    f"Sayfa numarası 1'den küçük olamaz: {page}"
                )

            if page > max_pages:
                raise ValueError(
                    f"Sayfa numarası {max_pages}'i aşıyor: {page}"
                )

            pages.add(page)

    if not pages:
        raise ValueError("Hiçbir geçerli sayfa numarası bulunamadı")

    return sorted(pages)
