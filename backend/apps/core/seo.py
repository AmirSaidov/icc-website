"""Объект seo в детальных ответах API (SPEC.md, 3.1)."""
from html import unescape

from django.utils.html import strip_tags

from .i18n import LANGS, alternate_value, translated_value
from .images import image_versions


def plain_text(html):
    """HTML → одна строка текста (для meta_description из rich text)."""
    return " ".join(unescape(strip_tags(html)).split()) or None


def build_seo(obj, lang, request, site_settings, description_field=None, image_field=None,
              description_is_html=False):
    """
    meta_title       — meta_title, если пусто — title;
    meta_description — meta_description, если пусто — excerpt / short_text
                       (у презентаций — description без HTML-тегов);
    og_image         — og_image, если пусто — cover, затем default_og_image (версия 1200 px);
    alternates       — slug записи на каждом языке (null, если на язык не переведена).

    obj может быть None (например, страница home не опубликована) —
    тогда всё null, кроме og_image по умолчанию.
    """
    meta_title = meta_description = None
    image_candidates = []
    if obj is not None:
        meta_title = translated_value(obj, "meta_title", lang) or translated_value(obj, "title", lang)
        meta_description = translated_value(obj, "meta_description", lang)
        if not meta_description and description_field:
            meta_description = translated_value(obj, description_field, lang)
            if meta_description and description_is_html:
                meta_description = plain_text(meta_description)
        image_candidates.append(obj.og_image)
        if image_field:
            image_candidates.append(getattr(obj, image_field))
    image_candidates.append(site_settings.default_og_image)

    og_image = None
    for candidate in image_candidates:
        versions = image_versions(candidate, request)
        if versions:
            og_image = versions["large"]
            break

    return {
        "meta_title": meta_title,
        "meta_description": meta_description,
        "og_image": og_image,
        "alternates": {code: alternate_value(obj, code) for code in LANGS},
    }
