import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.core.models import PublishableModel
from apps.core.tests.factories import days, make
from apps.news.models import Event, News
from apps.pages.models import Direction, HomeBlock, Page, Service

pytestmark = pytest.mark.django_db

PUBLISHED = PublishableModel.Status.PUBLISHED


def publish_system_page(key, langs=("ru", "en", "zh"), **extra):
    page = Page.objects.get(key=key)
    for lang in langs:
        setattr(page, f"title_{lang}", f"{key} {lang}")
    page.status = PUBLISHED
    for attr, value in extra.items():
        setattr(page, attr, value)
    page.save()
    return page


# --- Страницы -------------------------------------------------------------------


def test_system_page_found_by_key_and_translated_without_slug(api):
    publish_system_page("about", langs=("ru", "en"), show_in_menu=True)
    detail = api.get("/api/v1/pages/about/", {"lang": "en"}).json()
    assert detail["key"] == "about" and detail["slug"] is None
    assert detail["title"] == "about en"
    assert detail["is_translated"] is True
    assert detail["seo"]["alternates"] == {"ru": "about", "en": "about", "zh": None}

    zh = api.get("/api/v1/pages/about/", {"lang": "zh"}).json()
    assert zh["is_translated"] is False and zh["title"] is None


def test_draft_system_page_is_404(api):
    assert api.get("/api/v1/pages/about/").status_code == 404


def test_regular_page_by_slug_in_any_language_and_menu(api):
    publish_system_page("about", show_in_menu=True, order=1)
    page = make(Page, "custom", fields=("title", "content"), show_in_menu=True, order=2)
    make(Page, "hidden", fields=("title",), show_in_menu=False)
    make(Page, "draft", fields=("title",), show_in_menu=True, status=PublishableModel.Status.DRAFT)

    assert api.get("/api/v1/pages/custom-zh/").json()["id"] == page.id
    menu = api.get("/api/v1/pages/", {"lang": "zh"}).json()
    assert menu == [
        {"key": "about", "slug": None, "title": "about zh", "order": 1},
        {"key": None, "slug": "custom-zh", "title": "custom title zh", "order": 2},
    ]


def test_regular_page_without_slug_is_not_translated(api):
    make(Page, "noslug", fields=("title",), slug=False, show_in_menu=True)
    assert api.get("/api/v1/pages/").json() == []


# --- Направления и услуги ---------------------------------------------------------


def test_directions_list_without_content_and_detail_seo(api):
    make(Direction, "dir", fields=("title", "short_text", "content"), icon="export")
    item = api.get("/api/v1/directions/").json()[0]
    assert "content" not in item and item["icon"] == "export"
    detail = api.get("/api/v1/directions/dir-en/", {"lang": "en"}).json()
    assert detail["content"] == "dir content en"
    assert detail["seo"]["meta_description"] == "dir short_text en"


def test_service_detail_includes_how_to_apply_and_contacts(api):
    make(
        Service, "srv", fields=("title", "short_text", "content", "how_to_apply", "contact_person"),
        contact_email="a@example.kg", contact_phone="",
    )
    item = api.get("/api/v1/services/").json()[0]
    assert "how_to_apply" not in item and "contact_email" not in item
    detail = api.get("/api/v1/services/srv-ru/").json()
    assert detail["how_to_apply"] == "srv how_to_apply ru"
    assert detail["contact_email"] == "a@example.kg"
    assert detail["contact_phone"] is None


@pytest.mark.parametrize("model,url", [(Direction, "/api/v1/directions/"), (Service, "/api/v1/services/")])
def test_drafts_hidden_in_directions_and_services(api, model, url):
    extra = {"icon": "export"} if model is Direction else {}
    make(model, "draft", status=PublishableModel.Status.REVIEW, **extra)
    assert api.get(url).json() == []
    assert api.get(f"{url}draft-ru/").status_code == 404


# --- Главная --------------------------------------------------------------------


def make_home_content():
    make(HomeBlock, "hero", slug=False, type=HomeBlock.Type.HERO, order=1)
    make(HomeBlock, "cta-ru", langs=("ru",), slug=False, type=HomeBlock.Type.CTA, order=2)
    make(HomeBlock, "draft", slug=False, type=HomeBlock.Type.ABOUT, status=PublishableModel.Status.DRAFT)
    for i in range(6):
        make(Direction, f"dir{i}", icon="export", order=i)
    for i in range(5):
        make(News, f"news{i}", published_at=days(-i))
    for name, start in (("past", -3), ("e3", 9), ("e1", 1), ("e2", 5), ("e4", 20)):
        make(Event, name, type=Event.Type.FORUM, start_at=days(start))


def test_home_aggregates_everything(api):
    publish_system_page("home", meta_title_ru="Главная — ЦПК")
    make_home_content()

    data = api.get("/api/v1/home/").json()
    assert [b["type"] for b in data["blocks"]] == ["hero", "cta"]
    assert [d["slug"] for d in data["directions"]] == ["dir0-ru", "dir1-ru", "dir2-ru", "dir3-ru"]
    assert [n["slug"] for n in data["news"]] == ["news0-ru", "news1-ru", "news2-ru"]
    assert [e["slug"] for e in data["events"]] == ["e1-ru", "e2-ru", "e3-ru"]
    assert data["seo"]["meta_title"] == "Главная — ЦПК"
    assert data["seo"]["alternates"] == {"ru": "home", "en": "home", "zh": "home"}

    zh = api.get("/api/v1/home/", {"lang": "zh"}).json()
    assert [b["type"] for b in zh["blocks"]] == ["hero"]  # cta без перевода


def test_home_without_published_home_page_has_empty_seo(api):
    seo = api.get("/api/v1/home/").json()["seo"]
    assert seo["meta_title"] is None
    assert seo["alternates"] == {"ru": None, "en": None, "zh": None}


def test_home_has_no_n_plus_one(api):
    publish_system_page("home")
    make_home_content()

    def count():
        with CaptureQueriesContext(connection) as ctx:
            assert api.get("/api/v1/home/").status_code == 200
        return len(ctx)

    count()
    few = count()
    for i in range(6, 10):
        make(HomeBlock, f"block{i}", slug=False, type=HomeBlock.Type.ADVANTAGES, order=i)
    assert count() == few
