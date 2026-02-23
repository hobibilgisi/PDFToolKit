"""
PDFToolKit - PDF Birleştirme Testleri
"""

import pytest
import sys
import os
import tempfile
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


class TestPdfMerger:
    """pdf_merger modülü testleri."""

    def test_merge_two_pdfs(self, tmp_path):
        """İki PDF'yi birleştirir."""
        from core.pdf_merger import merge_pdfs

        pdf1 = create_test_pdf(tmp_path / "test1.pdf", 2)
        pdf2 = create_test_pdf(tmp_path / "test2.pdf", 3)
        output = tmp_path / "merged.pdf"

        result = merge_pdfs(
            [{"path": str(pdf1)}, {"path": str(pdf2)}],
            output_path=str(output)
        )

        assert result.exists()
        from pypdf import PdfReader
        reader = PdfReader(str(result))
        assert len(reader.pages) == 5

    def test_merge_with_page_selection(self, tmp_path):
        """Sayfa seçimli birleştirme."""
        from core.pdf_merger import merge_pdfs

        pdf1 = create_test_pdf(tmp_path / "test1.pdf", 5)
        output = tmp_path / "merged.pdf"

        result = merge_pdfs(
            [{"path": str(pdf1), "pages": [1, 3, 5]}],
            output_path=str(output)
        )

        assert result.exists()
        from pypdf import PdfReader
        reader = PdfReader(str(result))
        assert len(reader.pages) == 3

    def test_merge_empty_list(self):
        """Boş liste hata verir."""
        from core.pdf_merger import merge_pdfs

        with pytest.raises(ValueError):
            merge_pdfs([])

    def test_merge_file_not_found(self, tmp_path):
        """Olmayan dosya hata verir."""
        from core.pdf_merger import merge_pdfs

        with pytest.raises(FileNotFoundError):
            merge_pdfs([{"path": str(tmp_path / "nonexistent.pdf")}])


class TestInsertPdf:
    """insert_pdf fonksiyonu testleri."""

    def test_insert_at_beginning(self, tmp_path):
        """PDF'yi başa ekler."""
        from core.pdf_merger import insert_pdf

        target = create_test_pdf(tmp_path / "target.pdf", 3)
        source = create_test_pdf(tmp_path / "source.pdf", 2)
        output = tmp_path / "inserted.pdf"

        result = insert_pdf(str(target), str(source), 0, str(output))

        assert result.exists()
        from pypdf import PdfReader
        reader = PdfReader(str(result))
        assert len(reader.pages) == 5

    def test_insert_at_end(self, tmp_path):
        """PDF'yi sona ekler."""
        from core.pdf_merger import insert_pdf

        target = create_test_pdf(tmp_path / "target.pdf", 3)
        source = create_test_pdf(tmp_path / "source.pdf", 2)
        output = tmp_path / "inserted.pdf"

        result = insert_pdf(str(target), str(source), 3, str(output))

        assert result.exists()
        from pypdf import PdfReader
        reader = PdfReader(str(result))
        assert len(reader.pages) == 5
