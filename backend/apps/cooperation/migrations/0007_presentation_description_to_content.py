"""
Перенос данных: description → content (rich text как есть), excerpt — тот же текст
без тегов, обрезанный до 300 символов. Обратно: content → description.
"""
import re
from html import unescape

from django.db import migrations
from django.utils.html import strip_tags
from django.utils.text import Truncator

LANGS = ("ru", "en", "zh")
EXCERPT_MAX_LENGTH = 300
# конец абзаца, заголовка, пункта списка и т.п. — пробел, иначе strip_tags склеит слова
BLOCK_END_RE = re.compile(r"</(?:p|h[1-6]|li|blockquote|td|th|figcaption)>|<br\s*/?>", re.IGNORECASE)


def excerpt_from_html(html):
    text = " ".join(unescape(strip_tags(BLOCK_END_RE.sub(" ", html))).split())
    return Truncator(text).chars(EXCERPT_MAX_LENGTH) or None


def forward(apps, schema_editor):
    Presentation = apps.get_model("cooperation", "Presentation")
    for obj in Presentation.objects.all():
        fields = []
        for lang in LANGS:
            html = getattr(obj, f"description_{lang}")
            if not html:
                continue
            setattr(obj, f"content_{lang}", html)
            setattr(obj, f"excerpt_{lang}", excerpt_from_html(html))
            fields += [f"content_{lang}", f"excerpt_{lang}"]
        if obj.description:
            obj.content = obj.description
            obj.excerpt = excerpt_from_html(obj.description) or ""
            fields += ["content", "excerpt"]
        if fields:
            obj.save(update_fields=fields)


def backward(apps, schema_editor):
    Presentation = apps.get_model("cooperation", "Presentation")
    for obj in Presentation.objects.all():
        for lang in LANGS:
            setattr(obj, f"description_{lang}", getattr(obj, f"content_{lang}"))
        obj.description = obj.content
        obj.save(update_fields=["description", *[f"description_{lang}" for lang in LANGS]])


class Migration(migrations.Migration):

    dependencies = [
        ("cooperation", "0006_presentation_excerpt_content"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
