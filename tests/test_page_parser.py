"""
PDFToolKit - Sayfa Numarası Ayrıştırıcı Testleri
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.page_parser import parse_page_input


class TestParsePageInput:
    """parse_page_input fonksiyonu testleri."""

    def test_empty_returns_all(self):
        """Boş girdi tüm sayfaları döndürür."""
        assert parse_page_input("", 5) == [1, 2, 3, 4, 5]

    def test_tumu_returns_all(self):
        """'tümü' girdisi tüm sayfaları döndürür."""
        assert parse_page_input("tümü", 3) == [1, 2, 3]

    def test_all_returns_all(self):
        """'all' girdisi tüm sayfaları döndürür."""
        assert parse_page_input("all", 4) == [1, 2, 3, 4]

    def test_single_page(self):
        """Tek sayfa numarası."""
        assert parse_page_input("3", 10) == [3]

    def test_range(self):
        """Sayfa aralığı."""
        assert parse_page_input("1-5", 10) == [1, 2, 3, 4, 5]

    def test_comma_separated(self):
        """Virgülle ayrılmış sayfalar."""
        assert parse_page_input("1,3,5", 10) == [1, 3, 5]

    def test_mixed(self):
        """Karışık format: aralık + tekli."""
        assert parse_page_input("1-3,5,7-9", 10) == [1, 2, 3, 5, 7, 8, 9]

    def test_duplicates_removed(self):
        """Tekrarlayan sayfa numaraları kaldırılır."""
        assert parse_page_input("1,1,2,2,3", 5) == [1, 2, 3]

    def test_sorted(self):
        """Sonuç sıralı döner."""
        assert parse_page_input("5,1,3", 10) == [1, 3, 5]

    def test_whitespace_handling(self):
        """Boşluklar temizlenir."""
        assert parse_page_input(" 1 - 3 , 5 ", 10) == [1, 2, 3, 5]

    def test_invalid_page_number(self):
        """Geçersiz sayfa numarası hata verir."""
        with pytest.raises(ValueError):
            parse_page_input("abc", 10)

    def test_page_exceeds_max(self):
        """Aralık dışı sayfa numarası hata verir."""
        with pytest.raises(ValueError):
            parse_page_input("11", 10)

    def test_negative_page(self):
        """Negatif sayfa numarası hata verir."""
        with pytest.raises(ValueError):
            parse_page_input("0", 10)

    def test_reverse_range(self):
        """Ters aralık hata verir."""
        with pytest.raises(ValueError):
            parse_page_input("5-1", 10)

    def test_invalid_max_pages(self):
        """Geçersiz max_pages hata verir."""
        with pytest.raises(ValueError):
            parse_page_input("1", 0)
