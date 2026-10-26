"""Фабрики тестовых данных (без внешних зависимостей)."""
import io
import zipfile
from datetime import timedelta

from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image
from pypdf import PdfWriter

from apps.core.i18n import LANGS
from apps.core.models import Attachment, GalleryImage, PublishableModel

PUBLISHED = PublishableModel.Status.PUBLISHED


def image_file(name="photo.jpg", size=(1600, 900)):
    buffer = io.BytesIO()
    Image.new("RGB", size, (30, 90, 160)).save(buffer, "JPEG")
    return ContentFile(buffer.getvalue(), name=name)


def pdf_file(name="program.pdf"):
    return ContentFile(b"%PDF-1.4\n%test\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n", name=name)


def slides_pdf_file(pages=3, name="slides.pdf"):
    """Настоящий PDF с pages страницами (pypdf) — для подсчёта страниц."""
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=960, height=540)
    buffer = io.BytesIO()
    writer.write(buffer)
    return ContentFile(buffer.getvalue(), name=name)


def pptx_bytes(with_presentation=True):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("ppt/presentation.xml" if with_presentation else "ppt/other.xml", "<p:presentation/>")
    return buffer.getvalue()


def pptx_file(name="slides.pptx"):
    return ContentFile(pptx_bytes(), name=name)


def translated(name, langs=LANGS, fields=("title",), slug=True):
    """{"title_ru": "<name> ru", ..., "slug_ru": "<name>-ru", ...} для указанных языков."""
    data = {}
    for lang in langs:
        for field in fields:
            data[f"{field}_{lang}"] = f"{name} {field} {lang}"
        if slug:
            data[f"slug_{lang}"] = f"{name}-{lang}"
    return data


def make(model, name, langs=LANGS, fields=("title",), slug=True, status=PUBLISHED, **extra):
    data = translated(name, langs, fields, slug)
    if any(f.name == "status" for f in model._meta.fields):
        data["status"] = status
    data.update(extra)
    return model.objects.create(**data)


def add_photo(obj, langs=LANGS, order=0):
    return GalleryImage.objects.create(
        content_object=obj,
        image=image_file(f"gallery-{order}.jpg"),
        order=order,
        **{f"caption_{lang}": f"caption {lang}" for lang in langs},
    )


def add_pdf(obj=None, langs=LANGS, **extra):
    return Attachment.objects.create(
        content_object=obj,
        file=pdf_file(),
        **{f"title_{lang}": f"Программа {lang}" for lang in langs},
        **extra,
    )


def days(n):
    return timezone.now() + timedelta(days=n)


def make_presentation(name, sector, langs=LANGS, pages=3, **extra):
    """Опубликованная презентация с PDF на pages страниц, переведённая на langs."""
    from apps.cooperation.models import Presentation

    extra.setdefault("file", slides_pdf_file(pages, f"{name}.pdf"))
    return make(Presentation, name, langs, fields=("title", "description"), sector=sector, **extra)
