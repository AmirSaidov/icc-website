import pytest
from django.apps import apps
from django.contrib.auth.models import User
from django.core.management import call_command

from apps.core.models import Attachment, ContactInfo, SiteSettings
from apps.core.tests.factories import add_pdf, image_file

pytestmark = pytest.mark.django_db

ENDPOINTS = [
    "/api/v1/home/",
    "/api/v1/pages/",
    "/api/v1/directions/",
    "/api/v1/services/",
    "/api/v1/news-categories/",
    "/api/v1/news/",
    "/api/v1/events/",
    "/api/v1/event-types/",
    "/api/v1/countries/",
    "/api/v1/partners/",
    "/api/v1/projects/",
    "/api/v1/contacts/",
    "/api/v1/settings/",
    "/api/v1/documents/",
]


@pytest.mark.parametrize("url", ENDPOINTS)
def test_every_endpoint_validates_lang(api, url):
    assert api.get(url).status_code == 200
    assert api.get(url, {"lang": "zh"}).status_code == 200
    response = api.get(url, {"lang": "fr"})
    assert response.status_code == 400
    assert "lang" in response.json()


def test_contacts(api):
    contacts = ContactInfo.load()
    contacts.official_name_ru = "ЦПК"
    contacts.official_name_en = "ICC"
    contacts.phones = [{"label": "Приёмная", "number": "+996"}]
    contacts.map_lat = "42.874600"
    contacts.save()
    data = api.get("/api/v1/contacts/", {"lang": "en"}).json()
    assert data["official_name"] == "ICC"
    assert data["address"] is None
    assert data["phones"] == [{"label": "Приёмная", "number": "+996"}]
    assert data["map_lat"] == 42.8746 and data["map_lng"] is None


def test_public_settings(api):
    site = SiteSettings.load()
    site.analytics_id = "G-TEST"
    site.feedback_emails = "secret@example.kg"
    site.default_og_image = image_file("og.jpg")
    site.save()
    data = api.get("/api/v1/settings/").json()
    assert set(data) == {"analytics_id", "default_og_image"}
    assert data["analytics_id"] == "G-TEST"
    assert data["default_og_image"]["large"].startswith("http://testserver/")


def test_documents_only_flagged_and_translated(api):
    add_pdf(show_in_documents=True, order=1)
    add_pdf(show_in_documents=False)
    add_pdf(langs=("ru",), show_in_documents=True, order=2)
    assert len(api.get("/api/v1/documents/").json()) == 2
    zh = api.get("/api/v1/documents/", {"lang": "zh"}).json()
    assert zh == [
        {"title": "Программа zh", "url": zh[0]["url"], "size": Attachment.objects.first().size, "ext": "pdf"}
    ]


def test_schema_and_swagger_available(api):
    schema = api.get("/api/schema/")
    assert schema.status_code == 200
    assert b"/api/v1/news/{slug}/" in schema.content
    assert api.get("/api/docs/").status_code == 200


# --- seed --------------------------------------------------------------------------


def _counts():
    return {
        model.__name__: model.objects.count()
        for model in apps.get_models()
        if model._meta.app_label in {"core", "pages", "news", "cooperation"}
    } | {"User": User.objects.count()}


def test_seed_is_idempotent_and_flush_recreates(api):
    call_command("seed", verbosity=0)
    first = _counts()
    assert first["News"] == 12 and first["Event"] == 8 and first["Direction"] == 8
    assert first["Service"] == 7 and first["HomeBlock"] == 5 and first["Partner"] == 4
    assert User.objects.get(username="admin").groups.filter(name="Администратор").exists()
    assert User.objects.get(username="editor").groups.filter(name="Редактор").exists()

    call_command("seed", verbosity=0)
    assert _counts() == first

    call_command("seed", flush=True, verbosity=0)
    assert _counts() == first

    # минимум 2 записи без китайского перевода и опубликованные системные страницы
    untranslated = sum(
        api.get(url, {"lang": "zh"}).json()["count"] < api.get(url).json()["count"]
        for url in ("/api/v1/news/", "/api/v1/projects/", "/api/v1/events/")
    ) + (len(api.get("/api/v1/services/", {"lang": "zh"}).json()) < 7)
    assert untranslated >= 2
    assert api.get("/api/v1/pages/about/", {"lang": "zh"}).json()["is_translated"] is True
    assert len(api.get("/api/v1/documents/", {"lang": "zh"}).json()) == 1
