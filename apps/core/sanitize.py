"""Санитайзинг rich text через nh3 (SPEC.md, раздел 2.4)."""
import re

import nh3
from django.conf import settings

ALLOWED_TAGS = {
    "h2", "h3", "h4",
    "p", "br",
    "strong", "em", "u", "s",
    "ul", "ol", "li",
    "a", "img",
    "blockquote",
    "table", "thead", "tbody", "tr", "th", "td",
    "figure", "figcaption",
}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "target", "rel"},
    "img": {"src", "alt", "width", "height"},
}


# CKEditor 5 выводит курсив как <i>, а в разрешённых тегах — <em>: без замены курсив пропал бы.
ITALIC_TAG_RE = re.compile(r"<(/?)i(?=[\s/>])", re.IGNORECASE)


def sanitize_html(value):
    """Очищает HTML, оставляя только разрешённые теги и атрибуты."""
    if not value:
        return value
    value = ITALIC_TAG_RE.sub(r"<\1em", value)
    # link_rel=None: атрибут rel разрешён явно, nh3 не должен его перезаписывать.
    return nh3.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel=None,
    )


def sanitize_translated_fields(instance, *field_names):
    """Очищает все языковые версии переводимых rich text полей модели."""
    for name in field_names:
        for lang, _ in settings.LANGUAGES:
            attr = f"{name}_{lang}"
            value = getattr(instance, attr, None)
            if value:
                setattr(instance, attr, sanitize_html(value))
