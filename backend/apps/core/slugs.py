"""Slug из заголовка: ru — транслит, en — slugify, zh — pinyin + slugify (SPEC.md, 4.1)."""
from django.conf import settings
from pypinyin import lazy_pinyin
from slugify import slugify

SLUG_MAX_LENGTH = 100


def make_slug(text, lang):
    if not text:
        return None
    if lang == "zh":
        text = " ".join(lazy_pinyin(text))
    return slugify(text, max_length=SLUG_MAX_LENGTH, word_boundary=True) or None


def unique_slug(model, field, base, exclude_pk=None):
    """base, а если занят — base-2, base-3, … (уникальность в пределах языка)."""
    queryset = model._default_manager.filter(**{f"{field}__startswith": base})
    if exclude_pk is not None:
        queryset = queryset.exclude(pk=exclude_pk)
    taken = set(queryset.values_list(field, flat=True))
    if base not in taken:
        return base
    number = 2
    while f"{base}-{number}" in taken:
        number += 1
    return f"{base}-{number}"


def fill_translated_slugs(instance, title_field="title"):
    """
    При сохранении: если slug_X пуст, а title_X (name_X) заполнен — генерирует slug.
    Вручную введённый slug не трогает. Системным страницам (с key) slug не нужен.
    """
    key_field = getattr(type(instance), "system_key_field", None)
    if key_field and getattr(instance, key_field):
        return
    for lang in settings.MODELTRANSLATION_LANGUAGES:
        field = f"slug_{lang}"
        if getattr(instance, field):
            continue
        base = make_slug(getattr(instance, f"{title_field}_{lang}", None), lang)
        if base:
            setattr(instance, field, unique_slug(type(instance), field, base, exclude_pk=instance.pk))
