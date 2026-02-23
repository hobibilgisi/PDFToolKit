"""
PDFToolKit - Dönüştürme Testleri
"""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pypdf import PdfWriter


def create_test_pdf(filepath: Path, num_pages: int = 2):
    """Test için basit bir PDF oluşturur."""
    writer = PdfWriter()
    for i in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    with open(filepath, "wb") as f:
        writer.write(f)
    return filepath


class TestJpgToPdf:
    """jpg_to_pdf fonksiyonu testleri."""

    def test_jpg_to_pdf(self, tmp_path):
        """JPG görselinden PDF oluşturur."""
        from PIL import Image
        from converters.to_pdf import jpg_to_pdf

        # Test görseli oluştur
        img = Image.new("RGB", (200, 300), color="red")
        img_path = tmp_path / "test.jpg"
        img.save(str(img_path))

        output = tmp_path / "output.pdf"
        result = jpg_to_pdf(str(img_path), str(output))

        assert result.exists()
        assert result.stat().st_size > 0

    def test_jpg_file_not_found(self, tmp_path):
        """Olmayan dosya hata verir."""
        from converters.to_pdf import jpg_to_pdf

        with pytest.raises(FileNotFoundError):
            jpg_to_pdf(str(tmp_path / "nonexistent.jpg"))


class TestImagesToPdf:
    """images_to_pdf fonksiyonu testleri."""

    def test_multiple_images(self, tmp_path):
        """Birden fazla görselden PDF oluşturur."""
        from PIL import Image
        from converters.to_pdf import images_to_pdf

        images = []
        for i in range(3):
            img = Image.new("RGB", (100, 100), color=f"#{i*30:02x}{i*50:02x}ff")
            path = tmp_path / f"test{i}.jpg"
            img.save(str(path))
            images.append(str(path))

        output = tmp_path / "combined.pdf"
        result = images_to_pdf(images, str(output))

        assert result.exists()

    def test_empty_list(self):
        """Boş liste hata verir."""
        from converters.to_pdf import images_to_pdf

        with pytest.raises(ValueError):
            images_to_pdf([])
