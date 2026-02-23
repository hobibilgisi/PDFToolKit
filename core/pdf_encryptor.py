"""
PDFToolKit - PDF Şifreleme/Çözme Modülü

PDF dosyalarını parola ile koruma ve şifre çözme.
"""

from pathlib import Path
from pypdf import PdfReader, PdfWriter

from utils.logger import get_logger
from utils.file_utils import generate_output_filename

logger = get_logger(__name__)


def encrypt_pdf(
    pdf_path: str | Path,
    password: str,
    output_path: str | Path | None = None,
    owner_password: str | None = None
) -> Path:
    """
    PDF dosyasını parola ile şifreler.

    Args:
        pdf_path: Kaynak PDF dosyası.
        password: Kullanıcı parolası (PDF açmak için).
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.
        owner_password: Sahip parolası (izinler için). None ise user_password ile aynı.

    Returns:
        Oluşturulan şifrelenmiş PDF'nin Path nesnesi.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    if not password:
        raise ValueError("Parola boş olamaz")

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Şifrele
    if owner_password is None:
        owner_password = password

    writer.encrypt(
        user_password=password,
        owner_password=owner_password
    )

    # Çıktı yolu
    if output_path is None:
        output_path = generate_output_filename(pdf_path.stem, " (şifreli)")
    else:
        output_path = Path(output_path)

    with open(output_path, "wb") as f:
        writer.write(f)

    logger.info(f"'{pdf_path.name}' şifrelendi → {output_path}")
    return output_path


def decrypt_pdf(
    pdf_path: str | Path,
    password: str,
    output_path: str | Path | None = None
) -> Path:
    """
    Şifreli PDF dosyasının şifresini kaldırır.

    Args:
        pdf_path: Şifreli PDF dosyası.
        password: PDF parolası.
        output_path: Çıktı dosya yolu. None ise otomatik üretilir.

    Returns:
        Oluşturulan şifresiz PDF'nin Path nesnesi.

    Raises:
        ValueError: Yanlış parola girilirse.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {pdf_path}")

    reader = PdfReader(str(pdf_path))

    if not reader.is_encrypted:
        logger.warning(f"'{pdf_path.name}' zaten şifreli değil")
        # Yine de çıktı oluştur
    else:
        result = reader.decrypt(password)
        if result == 0:
            raise ValueError("Yanlış parola")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    # Çıktı yolu
    if output_path is None:
        output_path = generate_output_filename(pdf_path.stem, " (şifre çözüldü)")
    else:
        output_path = Path(output_path)

    with open(output_path, "wb") as f:
        writer.write(f)

    logger.info(f"'{pdf_path.name}' şifresi kaldırıldı → {output_path}")
    return output_path
