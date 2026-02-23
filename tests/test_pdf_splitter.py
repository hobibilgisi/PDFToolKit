"""
PDFToolKit - PDF Ayırma Testleri
"""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pypdf import PdfWriter


def create_test_pdf(filepath: Path, num_pages: int = 3):
    """Test için basit bir PDF oluşturur."""
    writer = PdfWriter()
    for i in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    with open(filepath, "wb") as f:
        writer.write(f)
    return filepath


class TestSplitAllPages:
    """split_all_pages fonksiyonu testleri."""

    def test_split_3_pages(self, tmp_path):
        """3 sayfalık PDF'yi 3 dosyaya ayırır."""
        from core.pdf_splitter import split_all_pages

        pdf = create_test_pdf(tmp_path / "test.pdf", 3)
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = split_all_pages(str(pdf), str(output_dir))

        assert len(result) == 3
        for f in result:
            assert f.exists()
            assert f.suffix == ".pdf"

    def test_split_file_not_found(self, tmp_path):
        """Olmayan dosya hata verir."""
        from core.pdf_splitter import split_all_pages

        with pytest.raises(FileNotFoundError):
            split_all_pages(str(tmp_path / "nonexistent.pdf"))


class TestExtractPages:
    """extract_pages fonksiyonu testleri."""

    def test_extract_specific_pages(self, tmp_path):
        """Belirli sayfaları çıkarır."""
        from core.pdf_splitter import extract_pages

        pdf = create_test_pdf(tmp_path / "test.pdf", 5)
        output = tmp_path / "extracted.pdf"

        result = extract_pages(str(pdf), [1, 3, 5], str(output))

        assert result.exists()
        from pypdf import PdfReader
        reader = PdfReader(str(result))
        assert len(reader.pages) == 3

    def test_extract_empty_pages(self, tmp_path):
        """Boş sayfa listesi hata verir."""
        from core.pdf_splitter import extract_pages

        pdf = create_test_pdf(tmp_path / "test.pdf", 3)

        with pytest.raises(ValueError):
            extract_pages(str(pdf), [])
