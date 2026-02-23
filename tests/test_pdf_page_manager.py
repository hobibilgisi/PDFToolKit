"""
PDFToolKit - Sayfa Yönetimi Testleri
"""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pypdf import PdfWriter


def create_test_pdf(filepath: Path, num_pages: int = 5):
    """Test için basit bir PDF oluşturur."""
    writer = PdfWriter()
    for i in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    with open(filepath, "wb") as f:
        writer.write(f)
    return filepath


class TestDeletePages:
    """delete_pages fonksiyonu testleri."""

    def test_delete_single_page(self, tmp_path):
        """Tek sayfa siler."""
        from core.pdf_page_manager import delete_pages

        pdf = create_test_pdf(tmp_path / "test.pdf", 5)
        output = tmp_path / "deleted.pdf"

        result = delete_pages(str(pdf), [3], str(output))

        assert result.exists()
        from pypdf import PdfReader
        reader = PdfReader(str(result))
        assert len(reader.pages) == 4

    def test_delete_multiple_pages(self, tmp_path):
        """Birden fazla sayfa siler."""
        from core.pdf_page_manager import delete_pages

        pdf = create_test_pdf(tmp_path / "test.pdf", 5)
        output = tmp_path / "deleted.pdf"

        result = delete_pages(str(pdf), [1, 3, 5], str(output))

        from pypdf import PdfReader
        reader = PdfReader(str(result))
        assert len(reader.pages) == 2

    def test_delete_all_pages_raises(self, tmp_path):
        """Tüm sayfaları silme denemesi hata verir."""
        from core.pdf_page_manager import delete_pages

        pdf = create_test_pdf(tmp_path / "test.pdf", 2)

        with pytest.raises(ValueError):
            delete_pages(str(pdf), [1, 2], str(tmp_path / "out.pdf"))


class TestRotatePages:
    """rotate_pages fonksiyonu testleri."""

    def test_rotate_90(self, tmp_path):
        """Sayfayı 90° döndürür."""
        from core.pdf_page_manager import rotate_pages

        pdf = create_test_pdf(tmp_path / "test.pdf", 3)
        output = tmp_path / "rotated.pdf"

        result = rotate_pages(str(pdf), [1], 90, str(output))
        assert result.exists()

    def test_invalid_angle(self, tmp_path):
        """Geçersiz açı hata verir."""
        from core.pdf_page_manager import rotate_pages

        pdf = create_test_pdf(tmp_path / "test.pdf", 3)

        with pytest.raises(ValueError):
            rotate_pages(str(pdf), [1], 45, str(tmp_path / "out.pdf"))


class TestGetPageCount:
    """get_page_count fonksiyonu testleri."""

    def test_page_count(self, tmp_path):
        """Sayfa sayısını doğru döndürür."""
        from core.pdf_page_manager import get_page_count

        pdf = create_test_pdf(tmp_path / "test.pdf", 7)
        assert get_page_count(str(pdf)) == 7
