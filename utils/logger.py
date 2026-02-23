"""
PDFToolKit - Loglama Modülü

Uygulama genelinde standart loglama yapılandırması sağlar.
"""

import logging
import sys
from config.settings import settings


def get_logger(name: str) -> logging.Logger:
    """
    Belirtilen isimle yapılandırılmış bir logger nesnesi döndürür.

    Args:
        name: Logger adı (genellikle modül adı: __name__).

    Returns:
        Yapılandırılmış logging.Logger nesnesi.
    """
    logger = logging.getLogger(name)

    # Zaten handler varsa tekrar ekleme
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.log_level, logging.INFO))

    # Konsol handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
