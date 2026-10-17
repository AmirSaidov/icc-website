"""
Язык запроса и правило «запись переведена на язык X» (SPEC.md, 2.1 и 3.1).

Переводимые поля читаются явно как <field>_<lang>, без дескрипторов
modeltranslation и без fallback-ов.
"""
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from rest_framework.exceptions import ValidationError

LANGS = tuple(settings.MODELTRANSLATION_LANGUAGES)
DEFAULT_LANG = settings.MODELTRANSLATION_DEFAULT_LANGUAGE


def get_request_lang(request):
    """?lang=ru|en|zh, по умолчанию ru. Невалидное значение → 400 {"lang": [...]}."""
    value = request.query_params.get("lang", DEFAULT_LANG)
    if value not in LANGS:
        raise ValidationError(
            {"lang": [f"Недопустимое значение «{value}». Допустимо: {', '.join(LANGS)}."]}
        )
    return value


def translated_value(obj, field, lang):
    """Значение <field>_<lang>; "" и NULL → None."""
    return getattr(obj, f"{field}_{lang}", None) or None


def has_field(model, name):
    try:
        model._meta.get_field(name)
    except FieldDoesNotExist:
        return False
    return True


def title_field_name(model):
    return "title" if has_field(model, "title") else "name"


def _system_key_field(model):
    # Системные страницы (Page с key) адресуются по key, slug им не нужен.
    return getattr(model, "system_key_field", None)


def _filled(field):
    # `> ""` отсекает и NULL, и пустую строку; работает в SQLite и PostgreSQL.
    return Q(**{f"{field}__gt": ""})


def translated_q(model, lang):
    """Q-фильтр «запись переведена на lang»: заполнены title_X/name_X и (если есть) slug_X."""
    q = _filled(f"{title_field_name(model)}_{lang}")
    if has_field(model, "slug"):
        slug_q = _filled(f"slug_{lang}")
        key_field = _system_key_field(model)
        if key_field:
            slug_q |= Q(**{f"{key_field}__isnull": False})
        q &= slug_q
    return q


def is_translated(obj, lang):
    """То же правило, что translated_q, но для объекта в памяти."""
    model = type(obj)
    if not translated_value(obj, title_field_name(model), lang):
        return False
    if has_field(model, "slug") and not translated_value(obj, "slug", lang):
        key_field = _system_key_field(model)
        return bool(key_field and getattr(obj, key_field))
    return True


def alternate_value(obj, lang):
    """
    Значение для seo.alternates[lang]: slug на этом языке, если запись на него
    переведена; для системной страницы — её key; иначе None.
    """
    if obj is None or not is_translated(obj, lang):
        return None
    key_field = _system_key_field(type(obj))
    if key_field and getattr(obj, key_field):
        return getattr(obj, key_field)
    return translated_value(obj, "slug", lang)


def any_slug_q(slug):
    q = Q()
    for lang in LANGS:
        q |= Q(**{f"slug_{lang}": slug})
    return q


def find_by_any_slug(queryset, slug, lang):
    """
    Ищет запись по slug на любом языке. Slug уникален только в пределах языка,
    поэтому при совпадении у разных записей приоритет у slug на языке запроса,
    затем ru → en → zh.
    """
    candidates = list(queryset.filter(any_slug_q(slug))[: len(LANGS)])
    for candidate_lang in (lang, *[code for code in LANGS if code != lang]):
        for obj in candidates:
            if getattr(obj, f"slug_{candidate_lang}") == slug:
                return obj
    return None
