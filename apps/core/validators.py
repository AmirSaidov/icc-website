"""
Проверка загружаемых файлов (SPEC.md, 4.1): расширение + содержимое + размер.

Картинки: JPG / PNG / WebP до 10 МБ, содержимое проверяется Pillow verify().
Документы: PDF / DOCX до 20 МБ; PDF — заголовок %PDF, DOCX — zip с word/document.xml.
"""
import zipfile
from pathlib import PurePath

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from PIL import Image

MB = 1024 * 1024

IMAGE_MAX_SIZE = 10 * MB
# расширение → формат, который Pillow должен распознать в содержимом
IMAGE_FORMATS = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}

DOCUMENT_MAX_SIZE = 20 * MB
DOCUMENT_EXTENSIONS = ("pdf", "docx")

IMAGE_ACCEPT = ",".join(f".{ext}" for ext in IMAGE_FORMATS)
DOCUMENT_ACCEPT = ",".join(f".{ext}" for ext in DOCUMENT_EXTENSIONS)


def _is_stored(value):
    """Уже сохранённый файл (форма пересохраняется без новой загрузки) повторно не проверяем."""
    return getattr(value, "_committed", False)


def _extension(value):
    return PurePath(value.name or "").suffix.lower().lstrip(".")


def _check_size(value, limit):
    if value.size > limit:
        raise ValidationError(
            f"Файл слишком большой ({filesizeformat(value.size)}). Максимум — {filesizeformat(limit)}.",
            code="file_too_large",
        )


def _open(value):
    file = getattr(value, "file", value)
    file.seek(0)
    return file


def validate_image_file(value):
    if not value or _is_stored(value):
        return
    ext = _extension(value)
    if ext not in IMAGE_FORMATS:
        raise ValidationError(
            f"Недопустимый формат «.{ext}». Разрешены: JPG, PNG, WebP.", code="invalid_extension"
        )
    _check_size(value, IMAGE_MAX_SIZE)
    file = _open(value)
    try:
        with Image.open(file) as image:
            detected = image.format
            image.verify()
    except Exception:
        raise ValidationError("Файл повреждён или не является изображением.", code="invalid_image")
    finally:
        file.seek(0)
    if detected != IMAGE_FORMATS[ext]:
        raise ValidationError(
            f"Содержимое файла ({detected}) не соответствует расширению «.{ext}».",
            code="invalid_image",
        )


def validate_document_file(value):
    if not value or _is_stored(value):
        return
    ext = _extension(value)
    if ext not in DOCUMENT_EXTENSIONS:
        raise ValidationError(
            f"Недопустимый формат «.{ext}». Разрешены: PDF, DOCX.", code="invalid_extension"
        )
    _check_size(value, DOCUMENT_MAX_SIZE)
    file = _open(value)
    try:
        if ext == "pdf":
            valid = file.read(5) == b"%PDF-"
        else:
            valid = zipfile.is_zipfile(file)
            if valid:
                file.seek(0)
                with zipfile.ZipFile(file) as archive:
                    valid = "word/document.xml" in archive.namelist()
    except Exception:
        valid = False
    finally:
        file.seek(0)
    if not valid:
        raise ValidationError(
            f"Содержимое файла не является документом {ext.upper()}.", code="invalid_document"
        )
