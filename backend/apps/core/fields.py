from django.conf import settings
from django.db import models

from .validators import (
    DOCUMENT_ACCEPT,
    IMAGE_ACCEPT,
    accept,
    validate_document_file,
    validate_image_file,
    validate_presentation_pdf,
    validate_presentation_pptx,
)


def unique_slug_constraints(prefix):
    """
    Уникальность slug в пределах каждого языка: slug_ru, slug_en, slug_zh.

    Сам исходный столбец `slug` (его ведёт modeltranslation как копию активного
    языка) уникальным не делаем — иначе slug одного языка мог бы конфликтовать
    со slug другого. NULL не участвует в уникальности (SQLite и PostgreSQL).
    """
    return [
        models.UniqueConstraint(fields=[f"slug_{lang}"], name=f"{prefix}_slug_{lang}_uniq")
        for lang in settings.MODELTRANSLATION_LANGUAGES
    ]


class NullableSlugField(models.SlugField):
    """
    SlugField, который хранит пустое значение как NULL, а не "".

    Нужен для переводимых slug (slug_ru / slug_en / slug_zh): уникальность
    в пределах языка не должна ломаться на незаполненных переводах.
    modeltranslation создаёт поля переводов на основе этого класса,
    поэтому поведение наследуется всеми языковыми версиями.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 255)
        kwargs.setdefault("null", True)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("allow_unicode", False)
        kwargs.setdefault("help_text", "Оставьте пустым — заполнится из заголовка при сохранении.")
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if value == "":
            value = None
            setattr(model_instance, self.attname, None)
        return value


class ImageUploadField(models.ImageField):
    """Картинка: JPG / PNG / WebP до 10 МБ, расширение + содержимое (SPEC.md, 4.1)."""

    default_validators = [validate_image_file]

    def formfield(self, **kwargs):
        field = super().formfield(**kwargs)
        field.widget.attrs.setdefault("accept", IMAGE_ACCEPT)
        return field


class DocumentUploadField(models.FileField):
    """Документ: PDF / DOCX до 20 МБ, расширение + содержимое (SPEC.md, 4.1)."""

    default_validators = [validate_document_file]
    accept_attr = DOCUMENT_ACCEPT

    def formfield(self, **kwargs):
        field = super().formfield(**kwargs)
        field.widget.attrs.setdefault("accept", self.accept_attr)
        return field


class PresentationPdfField(DocumentUploadField):
    """Презентация для просмотра на сайте: только PDF, до 50 МБ."""

    default_validators = [validate_presentation_pdf]
    accept_attr = accept(["pdf"])


class PresentationPptxField(DocumentUploadField):
    """Исходник презентации для скачивания: только PPTX, до 50 МБ."""

    default_validators = [validate_presentation_pptx]
    accept_attr = accept(["pptx"])
