"""Сведения о загруженных файлах."""
import logging

from pypdf import PdfReader

logger = logging.getLogger(__name__)


def count_pdf_pages(field_file):
    """
    Число страниц PDF (pypdf — чистый Python, без системных зависимостей).
    Не получилось (повреждённый или зашифрованный файл) — None: сохранение записи не падает.
    """
    try:
        if field_file._committed:
            with field_file.storage.open(field_file.name, "rb") as file:
                return len(PdfReader(file).pages) or None
        # Новый, ещё не сохранённый файл: читаем из загрузки и возвращаем позицию —
        # дальше его запишет хранилище.
        file = field_file.file
        file.seek(0)
        try:
            return len(PdfReader(file).pages) or None
        finally:
            file.seek(0)
    except Exception as error:
        logger.warning("Не удалось посчитать страницы PDF %s: %s", field_file.name, error)
        return None
