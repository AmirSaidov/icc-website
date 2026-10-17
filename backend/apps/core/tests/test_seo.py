"""/sitemap.xml и /robots.txt — критерий 13 раздела 6 SPEC.md и смежные проверки."""
import xml.etree.ElementTree as ET

import pytest

from apps.cooperation.models import Country, Project
from apps.core.models import PublishableModel
from apps.core.tests.factories import days, make
from apps.news.models import Event, News
from apps.pages.models import Direction, Page, Service

pytestmark = pytest.mark.django_db

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "xhtml": "http://www.w3.org/1999/xhtml"}
FRONT = "https://icc.example.kg"


@pytest.fixture(autouse=True)
def urls(settings):
    settings.FRONTEND_URL = FRONT
    settings.BACKEND_URL = "https://api.icc.example.kg"


def publish_system_page(key, langs=("ru", "en", "zh")):
    page = Page.objects.get(key=key)
    for lang in langs:
        setattr(page, f"title_{lang}", f"{key} {lang}")
    page.status = PublishableModel.Status.PUBLISHED
    page.save()


def sitemap(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/xml")
    root = ET.fromstring(response.content)
    result = {}
    for url in root.findall("sm:url", NS):
        loc = url.find("sm:loc", NS).text
        result[loc] = {
            "lastmod": url.find("sm:lastmod", NS).text,
            "alternates": {
                link.get("hreflang"): link.get("href") for link in url.findall("xhtml:link", NS)
            },
        }
    return result


# --- Критерий 13 ------------------------------------------------------------------------


def test_sitemap_has_hreflang_alternates_and_robots_closes_api(client):
    make(News, "mission")
    urls = sitemap(client)
    expected = {lang: f"{FRONT}/{lang}/news/mission-{lang}" for lang in ("ru", "en", "zh")}
    assert set(urls) == set(expected.values())
    for loc in expected.values():
        assert urls[loc]["alternates"] == {**expected, "x-default": expected["ru"]}
        assert urls[loc]["lastmod"].endswith("+06:00")

    robots = client.get("/robots.txt")
    assert robots.status_code == 200
    assert robots["Content-Type"].startswith("text/plain")
    lines = robots.content.decode().splitlines()
    assert "Disallow: /api/" in lines
    assert "Disallow: /admin/" in lines
    assert "Sitemap: https://api.icc.example.kg/sitemap.xml" in lines


# --- Схема URL и языки ----------------------------------------------------------------------


def test_untranslated_language_is_not_in_sitemap(client):
    make(News, "ruen", langs=("ru", "en"))
    urls = sitemap(client)
    assert set(urls) == {f"{FRONT}/ru/news/ruen-ru", f"{FRONT}/en/news/ruen-en"}
    assert "zh" not in urls[f"{FRONT}/ru/news/ruen-ru"]["alternates"]


def test_url_scheme_for_every_entity(client):
    publish_system_page("home")
    publish_system_page("about", langs=("ru",))
    make(Page, "custom")
    make(Direction, "dir", icon="export")
    make(Service, "srv")
    make(Event, "ev", type=Event.Type.FORUM, start_at=days(3))
    make(Project, "proj", country=make(Country, "cn", fields=("name",), slug=False, code="CN"))
    urls = sitemap(client)
    for path in (
        "/ru", "/zh",
        "/ru/about",
        "/en/custom-en",
        "/zh/directions/dir-zh",
        "/en/services/srv-en",
        "/ru/events/ev-ru",
        "/zh/cooperation/projects/proj-zh",
    ):
        assert FRONT + path in urls, path
    assert FRONT + "/en/about" not in urls  # about переведена только на ru
    assert urls[FRONT + "/en"]["alternates"]["x-default"] == FRONT + "/ru"


def test_x_default_falls_back_when_no_russian(client):
    News.objects.create(title_en="Only English", status="published")
    urls = sitemap(client)
    assert urls[FRONT + "/en/news/only-english"]["alternates"]["x-default"] == FRONT + "/en/news/only-english"


# --- Черновики и отложенные ------------------------------------------------------------------


@pytest.mark.parametrize("status", [PublishableModel.Status.DRAFT, PublishableModel.Status.REVIEW])
def test_drafts_not_in_sitemap(client, status):
    make(News, "draft", status=status)
    make(Direction, "dir-draft", icon="export", status=status)
    assert sitemap(client) == {}


def test_scheduled_not_in_sitemap(client):
    make(News, "later", published_at=days(1))
    make(Project, "later-proj", published_at=days(1),
         country=make(Country, "cn", fields=("name",), slug=False, code="CN"))
    make(News, "now", langs=("ru",), published_at=days(-1))
    assert set(sitemap(client)) == {FRONT + "/ru/news/now-ru"}


def test_draft_system_pages_not_in_sitemap(client):
    assert sitemap(client) == {}  # миграция создаёт системные страницы черновиками


# --- robots и ADMIN_URL ------------------------------------------------------------------------


def test_robots_follows_admin_url(client, settings):
    settings.ADMIN_URL = "cpk-panel-7f3k/"
    lines = client.get("/robots.txt").content.decode().splitlines()
    assert "Disallow: /cpk-panel-7f3k/" in lines
    assert "Disallow: /admin/" not in lines


def test_sitemap_query_count_does_not_grow(client, django_assert_max_num_queries):
    for i in range(10):
        make(News, f"n{i}")
    with django_assert_max_num_queries(8):
        client.get("/sitemap.xml")
