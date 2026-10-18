"""
Превью картинок через django-imagekit: WebP, ширина 400 и 1200 px (SPEC.md, 2.4).

Один набор спецификаций на все картинки (cover, image, logo, flag, og_image,
default_og_image). Файлы генерируются при первом обращении и кешируются
в MEDIA_ROOT/CACHE/.
"""
import logging

from imagekit import ImageSpec, register
from imagekit.cachefiles import ImageCacheFile
from pilkit.processors import ResizeToFit

logger = logging.getLogger(__name__)


class _WebpPreview(ImageSpec):
    format = "WEBP"
    options = {"quality": 85}


class SmallPreview(_WebpPreview):
    processors = [ResizeToFit(width=400, upscale=False)]


class LargePreview(_WebpPreview):
    processors = [ResizeToFit(width=1200, upscale=False)]


# imagekit генерирует файлы (стратегия JustInTime) только для зарегистрированных спецификаций.
register.generator("core:preview_small", SmallPreview)
register.generator("core:preview_large", LargePreview)


def absolute_url(url, request=None):
    if not url:
        return None
    return request.build_absolute_uri(url) if request is not None else url


def preview_url(field_file, spec_class, request=None):
    if not field_file:
        return None
    try:
        url = ImageCacheFile(spec_class(source=field_file)).url
    except Exception:  # битый или отсутствующий исходник не должен ронять API
        logger.exception("Не удалось построить превью для %s", field_file.name)
        return None
    return absolute_url(url, request)


def image_versions(field_file, request=None):
    """{"small": <400px webp>, "large": <1200px webp>} или None, если картинки нет."""
    if not field_file:
        return None
    small = preview_url(field_file, SmallPreview, request)
    large = preview_url(field_file, LargePreview, request)
    if small is None and large is None:
        return None
    return {"small": small, "large": large}
