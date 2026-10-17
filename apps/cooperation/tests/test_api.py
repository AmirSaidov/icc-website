import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.cooperation.models import Country, Partner, Project
from apps.core.models import PublishableModel
from apps.core.tests.factories import add_photo, image_file, make

pytestmark = pytest.mark.django_db


@pytest.fixture
def china():
    return make(Country, "china", fields=("name", "description"), slug=False, code="CN")


def make_partner(name, country, consent=True, **extra):
    return make(
        Partner, name, fields=("name", "description"), slug=False,
        country=country, consent_to_publish=consent, **extra,
    )


def make_project(name, country, **extra):
    return make(Project, name, fields=("title", "excerpt", "content"), country=country, **extra)


# --- Критерий 12 ---------------------------------------------------------------


def test_partner_without_consent_is_hidden(api, china):
    public = make_partner("public", china)
    secret = make_partner("secret", china, consent=False)
    project = make_project("proj", china)
    project.partners.set([public, secret])

    partners = api.get("/api/v1/partners/").json()
    assert [p["id"] for p in partners] == [public.id]

    detail = api.get("/api/v1/projects/proj-ru/").json()
    assert [p["id"] for p in detail["partners"]] == [public.id]


def test_partners_filter_by_country_code(api, china):
    kz = make(Country, "kz", fields=("name",), slug=False, code="KZ")
    make_partner("cn-partner", china)
    kz_partner = make_partner("kz-partner", kz, logo=image_file("logo.png"))
    data = api.get("/api/v1/partners/", {"country": "kz", "lang": "en"}).json()
    assert [p["id"] for p in data] == [kz_partner.id]
    assert data[0]["country"] == {"code": "KZ", "name": "kz name en"}
    assert data[0]["logo"]["small"].endswith(".webp")


def test_countries_only_active_and_translated(api, china):
    make(Country, "inactive", fields=("name",), slug=False, code="KZ", is_active=False)
    make(Country, "ru-only", langs=("ru",), fields=("name",), slug=False, code="UZ")
    assert [c["code"] for c in api.get("/api/v1/countries/").json()] == ["CN", "UZ"]
    assert [c["code"] for c in api.get("/api/v1/countries/", {"lang": "zh"}).json()] == ["CN"]


def test_projects_list_country_filter_drafts_and_gallery(api, china):
    kz = make(Country, "kz", fields=("name",), slug=False, code="KZ")
    cn_project = make_project("cn", china)
    make_project("kz", kz)
    make_project("draft", china, status=PublishableModel.Status.DRAFT)
    add_photo(cn_project)

    data = api.get("/api/v1/projects/", {"country": "CN"}).json()
    assert [p["id"] for p in data["results"]] == [cn_project.id]
    assert api.get("/api/v1/projects/draft-ru/").status_code == 404

    detail = api.get("/api/v1/projects/cn-zh/", {"lang": "zh"}).json()
    assert detail["country"] == {"code": "CN", "name": "china name zh"}
    assert len(detail["gallery"]) == 1


def test_project_detail_has_no_n_plus_one(api, china):
    project = make_project("proj", china)
    project.partners.add(make_partner("p0", china))
    add_photo(project)

    def count():
        with CaptureQueriesContext(connection) as ctx:
            assert api.get("/api/v1/projects/proj-ru/").status_code == 200
        return len(ctx)

    count()
    few = count()
    for i in range(1, 6):
        project.partners.add(make_partner(f"p{i}", china))
        add_photo(project, order=i)
    assert count() == few
