"""Загрузка картинок из CKEditor 5: только сотрудники, та же проверка, что у ImageField."""
from pathlib import PurePath

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from slugify import slugify

from .validators import validate_image_file


def _error(message, status):
    return JsonResponse({"error": {"message": message}}, status=status)


@require_POST
def ckeditor_upload(request):
    if not (request.user.is_active and request.user.is_staff):
        return _error("Загружать файлы могут только сотрудники.", 403)
    upload = request.FILES.get("upload")
    if upload is None:
        return _error("Файл не передан.", 400)
    try:
        validate_image_file(upload)
    except ValidationError as error:
        return _error(" ".join(error.messages), 400)
    name = PurePath(upload.name)
    filename = f"{slugify(name.stem)[:60] or 'image'}{name.suffix.lower()}"
    path = default_storage.save(f"editor/{timezone.now():%Y/%m}/{filename}", upload)
    return JsonResponse({"url": default_storage.url(path)})
