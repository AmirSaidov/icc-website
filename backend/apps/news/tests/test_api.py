import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.core.models import PublishableModel, SiteSettings
from apps.core.tests.factories import add_pdf, add_photo, days, image_file, make
from apps.news.models import Event, News, NewsCategory
from apps.pages.models import Page

pytestmark = pytest.mark.django_db

NEWS_FIELDS = ("title", "excerpt", "content")
EVENT_FIELDS = ("title", "excerpt", "content", "location")


def make_news(name="n", langs=("ru", "en", "zh"), **extra):
    return make(News, name, langs=langs, fields=NEWS_FIELDS, **extra)


def make_event(name, start, end=None, **extra):
    extra.setdefault("type", Event.Type.FORUM)
    return make(Event, name, fields=EVENT_FIELDS, start_at=start, end_at=end, **extra)


# --- Критерий 1 (API-часть) ---------------------------------------------------


def test_news_with_three_translations_photo_and_pdf_is_visible_in_zh(api):
    news = make_news("mission", cover=image_file("cover.jpg"))
    add_photo(news)
    add_pdf(news)

    response = api.get("/api/v1/news/", {"lang": "zh"})
    assert response.status_code == 200
    item = response.json()["results"][0]
    assert item["slug"] == "mission-zh"
    assert item["title"] == "mission title zh"
    assert item["is_translated"] is True
    assert item["cover"]["small"].startswith("http://testserver/media/")
    assert item["cover"]["large"].endswith(".webp")

    detail = api.get("/api/v1/news/mission-zh/", {"lang": "zh"}).json()
    assert len(detail["gallery"]) == 1
    photo = detail["gallery"][0]
    assert photo["caption"] == "caption zh"
    assert photo["small"].startswith("http://testserver/") and photo["small"].endswith(".webp")
    assert photo["large"].endswith(".webp")
    assert detail["attachments"] == [
        {
            "title": "Программа zh",
            "url": detail["attachments"][0]["url"],
            "size": news.attachments.get().size,
            "ext": "pdf",
        }
    ]
    assert detail["attachments"][0]["url"].startswith("http://testserver/media/documents/")
    assert detail["attachments"][0]["size"] > 0


# --- Критерий 3: нет китайского перевода -------------------------------------


def test_untranslated_record_absent_in_zh_list_but_detail_returns_nulls(api):
    make_news("ruen", langs=("ru", "en"))
    make_news("full")

    zh_list = api.get("/api/v1/news/", {"lang": "zh"}).json()
    assert [item["slug"] for item in zh_list["results"]] == ["full-zh"]
    assert zh_list["count"] == 1

    response = api.get("/api/v1/news/ruen-ru/", {"lang": "zh"})
    assert response.status_code == 200
    detail = response.json()
    assert detail["is_translated"] is False
    for field in ("slug", "title", "excerpt", "content"):
        assert detail[field] is None, field
    assert detail["seo"]["meta_title"] is None
    assert detail["seo"]["meta_description"] is None
    assert detail["seo"]["alternates"] == {"ru": "ruen-ru", "en": "ruen-en", "zh": None}


def test_empty_string_translation_is_null_and_not_translated(api):
    make_news("blank", langs=("ru",), title_en="", excerpt_en="")
    detail = api.get("/api/v1/news/blank-ru/", {"lang": "en"}).json()
    assert detail["title"] is None and detail["excerpt"] is None
    assert detail["is_translated"] is False
    assert api.get("/api/v1/news/", {"lang": "en"}).json()["count"] == 0


# --- Критерий 4: slug на другом языке ----------------------------------------


@pytest.mark.parametrize("slug", ["multi-ru", "multi-en", "multi-zh"])
def test_detail_found_by_slug_in_any_language(api, slug):
    news = make_news("multi")
    detail = api.get(f"/api/v1/news/{slug}/", {"lang": "en"}).json()
    assert detail["id"] == news.id
    assert detail["slug"] == "multi-en"
    assert detail["seo"]["alternates"] == {"ru": "multi-ru", "en": "multi-en", "zh": "multi-zh"}


def test_slug_collision_between_languages_prefers_requested_language(api):
    first = make_news("a", slug_en="shared")
    second = make_news("b", slug_ru="shared")
    assert api.get("/api/v1/news/shared/", {"lang": "en"}).json()["id"] == first.id
    assert api.get("/api/v1/news/shared/", {"lang": "ru"}).json()["id"] == second.id


# --- Критерий 10: мероприятия upcoming / past --------------------------------


def test_events_when_upcoming_and_past_split_and_sort(api):
    past_old = make_event("past-old", days(-30), days(-29))
    past_no_end = make_event("past-no-end", days(-5))
    ongoing = make_event("ongoing", days(-1), days(2))  # началось, но не закончилось → предстоящее
    soon = make_event("soon", days(3))
    later = make_event("later", days(10), days(12))

    upcoming = api.get("/api/v1/events/", {"when": "upcoming"}).json()["results"]
    assert [e["id"] for e in upcoming] == [ongoing.id, soon.id, later.id]
    assert all(e["is_upcoming"] for e in upcoming)

    past = api.get("/api/v1/events/", {"when": "past"}).json()["results"]
    assert [e["id"] for e in past] == [past_no_end.id, past_old.id]
    assert not any(e["is_upcoming"] for e in past)

    everything = api.get("/api/v1/events/").json()["results"]
    assert [e["id"] for e in everything] == [later.id, soon.id, ongoing.id, past_no_end.id, past_old.id]


def test_events_type_filter_and_labels(api):
    make_event("forum", days(3), type=Event.Type.FORUM)
    make_event("b2b", days(4), type=Event.Type.B2B)
    results = api.get("/api/v1/events/", {"type": "b2b", "lang": "zh"}).json()["results"]
    assert [e["type"] for e in results] == [{"code": "b2b", "label": "B2B洽谈会"}]
    assert api.get("/api/v1/events/", {"type": "party"}).status_code == 400
    assert api.get("/api/v1/events/", {"when": "soon"}).json() == {
        "when": ["Недопустимое значение «soon». Допустимо: upcoming, past."]
    }


def test_event_types_endpoint(api):
    data = api.get("/api/v1/event-types/", {"lang": "en"}).json()
    assert {"code": "forum", "label": "Forum"} in data
    assert [item["code"] for item in data] == list(Event.Type.values)


# --- Критерий 11: черновики не видны -----------------------------------------


@pytest.mark.parametrize("status", [PublishableModel.Status.DRAFT, PublishableModel.Status.REVIEW])
def test_drafts_and_review_are_hidden(api, status):
    make_news("hidden", status=status)
    make_event("hidden-event", days(3), status=status)
    assert api.get("/api/v1/news/").json()["count"] == 0
    assert api.get("/api/v1/news/hidden-ru/").status_code == 404
    assert api.get("/api/v1/events/").json()["count"] == 0
    assert api.get("/api/v1/events/hidden-event-ru/").status_code == 404


# --- Категории, пагинация, язык -----------------------------------------------


def test_category_filter_by_slug_in_any_language(api):
    category = make(NewsCategory, "cat", fields=("name",))
    make_news("in-cat", category=category)
    make_news("other")
    for slug in ("cat-ru", "cat-en", "cat-zh"):
        results = api.get("/api/v1/news/", {"category": slug}).json()["results"]
        assert [n["slug"] for n in results] == ["in-cat-ru"]
        assert results[0]["category"] == {"slug": "cat-ru", "name": "cat name ru"}
    assert api.get("/api/v1/news/", {"category": "unknown"}).json()["count"] == 0


def test_untranslated_category_is_null_in_news(api):
    category = make(NewsCategory, "ru-only", langs=("ru",), fields=("name",))
    make_news("n", category=category)
    item = api.get("/api/v1/news/", {"lang": "zh"}).json()["results"][0]
    assert item["category"] is None
    assert api.get("/api/v1/news-categories/", {"lang": "zh"}).json() == []


def test_pagination_defaults_and_max(api):
    for i in range(12):
        make_news(f"n{i}", published_at=days(-i))
    page = api.get("/api/v1/news/", {"lang": "en"}).json()
    assert page["count"] == 12 and len(page["results"]) == 9
    assert page["previous"] is None
    assert "page=2" in page["next"] and "lang=en" in page["next"]
    assert [n["slug"] for n in page["results"]][:2] == ["n0-en", "n1-en"]  # свежие сверху
    assert len(api.get("/api/v1/news/", {"page_size": 100}).json()["results"]) == 12
    assert len(api.get("/api/v1/news/", {"page_size": 5}).json()["results"]) == 5


def test_dates_are_iso_with_bishkek_offset(api):
    make_news("dated")
    published_at = api.get("/api/v1/news/").json()["results"][0]["published_at"]
    assert published_at.endswith("+06:00")


@pytest.mark.parametrize("value", ["de", "RU", ""])
def test_invalid_lang_returns_400(api, value):
    response = api.get("/api/v1/news/", {"lang": value})
    assert response.status_code == 400
    assert list(response.json()) == ["lang"]


# --- seo -----------------------------------------------------------------------


def test_seo_fallbacks(api):
    settings_obj = SiteSettings.load()
    settings_obj.default_og_image = image_file("default.jpg")
    settings_obj.save()

    plain = make_news("plain")
    seo = api.get("/api/v1/news/plain-ru/").json()["seo"]
    assert seo["meta_title"] == "plain title ru"
    assert seo["meta_description"] == "plain excerpt ru"
    assert "/CACHE/images/seo/" in seo["og_image"]  # нет og_image и cover → default_og_image

    plain.cover = image_file("cover.jpg")
    plain.meta_title_ru = "Custom"
    plain.meta_description_ru = "Desc"
    plain.save()
    seo = api.get("/api/v1/news/plain-ru/").json()["seo"]
    assert seo["meta_title"] == "Custom" and seo["meta_description"] == "Desc"
    assert "/CACHE/images/news/" in seo["og_image"]  # cover

    plain.og_image = image_file("og.jpg")
    plain.save()
    seo = api.get("/api/v1/news/plain-ru/").json()["seo"]
    assert "/CACHE/images/seo/" in seo["og_image"] and "og" in seo["og_image"]
    assert seo["og_image"].endswith(".webp")


# --- N+1 ----------------------------------------------------------------------


def _count_queries(api, url, params=None):
    with CaptureQueriesContext(connection) as ctx:
        assert api.get(url, params or {}).status_code == 200
    return len(ctx)


def test_news_list_has_no_n_plus_one(api):
    category = make(NewsCategory, "cat", fields=("name",))
    make_news("first", category=category)
    _count_queries(api, "/api/v1/news/")  # прогрев кешей ContentType
    few = _count_queries(api, "/api/v1/news/", {"lang": "zh"})
    for i in range(8):
        make_news(f"more{i}", category=category, cover=image_file())
    assert _count_queries(api, "/api/v1/news/", {"lang": "zh"}) == few


def test_news_and_event_detail_have_no_n_plus_one(api):
    news = make_news("detail", category=make(NewsCategory, "cat", fields=("name",)))
    event = make_event("detail-event", days(3))
    for obj in (news, event):
        add_photo(obj)
        add_pdf(obj)
    _count_queries(api, "/api/v1/news/detail-ru/")
    few_news = _count_queries(api, "/api/v1/news/detail-ru/")
    few_event = _count_queries(api, "/api/v1/events/detail-event-ru/")
    for obj in (news, event):
        for order in range(1, 6):
            add_photo(obj, order=order)
            add_pdf(obj)
    assert _count_queries(api, "/api/v1/news/detail-ru/") == few_news
    assert _count_queries(api, "/api/v1/events/detail-event-ru/") == few_event


# --- Отложенная публикация (SPEC.md, 2.4) ------------------------------------------


def test_scheduled_news_hidden_everywhere_until_published_at(api):
    home = Page.objects.get(key="home")
    home.title_ru, home.status = "Главная", PublishableModel.Status.PUBLISHED
    home.save()
    visible = make_news("now", published_at=days(-1))
    scheduled = make_news("later", published_at=days(1))

    assert [n["id"] for n in api.get("/api/v1/news/").json()["results"]] == [visible.id]
    assert api.get("/api/v1/news/later-ru/").status_code == 404
    assert [n["id"] for n in api.get("/api/v1/home/").json()["news"]] == [visible.id]

    News.objects.filter(pk=scheduled.pk).update(published_at=days(-0.01))  # дата наступила
    assert api.get("/api/v1/news/later-ru/").status_code == 200
    assert api.get("/api/v1/news/").json()["count"] == 2
