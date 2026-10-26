"""
/sitemap.xml и /robots.txt (SPEC.md, 5.3).

В sitemap — все опубликованные записи (тот же published(), что у API, включая отложенную
публикацию), каждая — только на языках, на которые она переведена. URL ведут на фронт
(FRONTEND_URL) по схеме ниже, у каждого варианта — xhtml:link hreflang на все переводы
и x-default → ru.
"""
from xml.sax.saxutils import escape, quoteattr

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from apps.cooperation.models import Presentation, Project
from apps.news.models import Event, News
from apps.pages.models import Direction, Page, Service

from .api import published
from .i18n import LANGS, is_translated, translated_value

# Схема URL на фронте — в одном месте: её ещё нужно согласовать с фронтом (SPEC.md, раздел 9).
FRONTEND_URL_SCHEME = {
    "home": "/{lang}",
    "system_page": "/{lang}/{key}",
    "page": "/{lang}/{slug}",
    "direction": "/{lang}/directions/{slug}",
    "service": "/{lang}/services/{slug}",
    "news": "/{lang}/news/{slug}",
    "event": "/{lang}/events/{slug}",
    "project": "/{lang}/cooperation/projects/{slug}",
    "presentation": "/{lang}/presentations/{slug}",  # согласовать с фронтом
}

SITEMAP_MODELS = [
    (Page, None),  # вид URL зависит от key
    (Direction, "direction"),
    (Service, "service"),
    (News, "news"),
    (Event, "event"),
    (Project, "project"),
    (Presentation, "presentation"),
]

X_DEFAULT_LANG = "ru"


def frontend_path(obj, kind, lang):
    if isinstance(obj, Page):
        if obj.key == "home":
            kind = "home"
        elif obj.key:
            kind = "system_page"
        else:
            kind = "page"
    return FRONTEND_URL_SCHEME[kind].format(
        lang=lang, key=getattr(obj, "key", None), slug=translated_value(obj, "slug", lang)
    )


def sitemap_entries():
    """[(lastmod, {lang: абсолютный URL})] — по одной записи на объект, только переведённые языки."""
    entries = []
    for model, kind in SITEMAP_MODELS:
        for obj in published(model.objects.all()).order_by("pk"):
            urls = {
                lang: settings.FRONTEND_URL + frontend_path(obj, kind, lang)
                for lang in LANGS
                if is_translated(obj, lang)
            }
            if urls:
                entries.append((obj.updated_at, urls))
    return entries


def render_sitemap(entries):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for updated_at, urls in entries:
        lastmod = timezone.localtime(updated_at).isoformat(timespec="seconds")
        x_default = urls.get(X_DEFAULT_LANG) or next(iter(urls.values()))
        alternates = [(lang, url) for lang, url in urls.items()] + [("x-default", x_default)]
        for url in urls.values():
            lines.append("  <url>")
            lines.append(f"    <loc>{escape(url)}</loc>")
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
            for hreflang, href in alternates:
                lines.append(f'    <xhtml:link rel="alternate" hreflang="{hreflang}" href={quoteattr(href)}/>')
            lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


@require_GET
def sitemap_xml(request):
    return HttpResponse(render_sitemap(sitemap_entries()), content_type="application/xml; charset=utf-8")


@require_GET
def robots_txt(request):
    # Путь ADMIN_URL сюда не пишем — это раскрыло бы нестандартный адрес админки.
    # Админку закрывает от индексации заголовок X-Robots-Tag (apps.core.middleware).
    lines = [
        "User-agent: *",
        "Disallow: /api/",
        "",
        f"Sitemap: {settings.BACKEND_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")
