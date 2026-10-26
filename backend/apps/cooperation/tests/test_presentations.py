"""Презентации: модели, API, файлы (PDF / PPTX), заголовки для встраивания, админка и права."""
import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.models import ProtectedError
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from apps.cooperation.models import Country, Presentation, Project, Sector
from apps.core.models import PublishableModel
from apps.core.tests.admin_utils import form_data
from apps.core.tests.factories import (
    add_pdf,
    days,
    image_file,
    make,
    make_presentation,
    pdf_file,
    pptx_bytes,
    pptx_file,
    slides_pdf_file,
)
from apps.core.validators import MB

pytestmark = pytest.mark.django_db

FRONT = "https://icc.example.kg"


@pytest.fixture
def industry():
    return Sector.objects.get(slug_ru="promyshlennost")  # создана миграцией


@pytest.fixture
def it_sector():
    return Sector.objects.get(slug_ru="informatsionnye-tekhnologii")


@pytest.fixture
def china():
    return make(Country, "china", fields=("name",), slug=False, code="CN")


@pytest.fixture
def project(china):
    return make(Project, "proj", fields=("title", "excerpt"), country=china)


def admin_url(model, action, *args):
    opts = model._meta
    return reverse(f"admin:{opts.app_label}_{opts.model_name}_{action}", args=args)


# --- Сферы -----------------------------------------------------------------------------------


def test_default_sectors_created_by_migration(api):
    assert api.get("/api/v1/sectors/").json() == [
        {"slug": "promyshlennost", "name": "Промышленность"},
        {"slug": "informatsionnye-tekhnologii", "name": "Информационные технологии"},
    ]
    assert api.get("/api/v1/sectors/", {"lang": "zh"}).json() == [
        {"slug": "gong-ye", "name": "工业"},
        {"slug": "xin-xi-ji-shu", "name": "信息技术"},
    ]


def test_new_sector_gets_slugs_and_untranslated_is_hidden(api):
    sector = Sector.objects.create(name_ru="Сельское хозяйство", name_en="Agriculture", order=5)
    assert (sector.slug_ru, sector.slug_en, sector.slug_zh) == ("selskoe-khoziaistvo", "agriculture", None)
    assert "agriculture" in [s["slug"] for s in api.get("/api/v1/sectors/", {"lang": "en"}).json()]
    assert len(api.get("/api/v1/sectors/", {"lang": "zh"}).json()) == 2


def test_sector_with_presentations_cannot_be_deleted(industry):
    make_presentation("p", industry)
    with pytest.raises(ProtectedError):
        industry.delete()


# --- category: projects / industry ----------------------------------------------------------


def test_category_field_and_filter(api, industry, it_sector, project, china):
    draft_project = make(Project, "draftproj", country=china, status=PublishableModel.Status.DRAFT)
    later_project = make(Project, "laterproj", country=china, published_at=days(1))
    with_project = make_presentation("withproj", industry, project=project)
    draft = make_presentation("draft", industry, project=draft_project)
    later = make_presentation("later", it_sector, project=later_project)
    plain = make_presentation("plain", it_sector)

    def categories(**params):
        results = api.get("/api/v1/presentations/", params).json()["results"]
        return {item["id"]: item["category"] for item in results}

    # projects — только презентации опубликованных проектов (черновик и отложенный — industry)
    assert categories() == {
        with_project.id: "projects", draft.id: "industry", later.id: "industry", plain.id: "industry",
    }
    assert set(categories(category="projects")) == {with_project.id}
    assert set(categories(category="industry")) == {draft.id, later.id, plain.id}
    # sector уточняет раздел industry
    assert set(categories(category="industry", sector="xin-xi-ji-shu")) == {later.id, plain.id}
    assert api.get("/api/v1/presentations/withproj-ru/").json()["category"] == "projects"
    assert api.get("/api/v1/presentations/draft-ru/").json()["category"] == "industry"

    response = api.get("/api/v1/presentations/", {"category": "it"})
    assert response.status_code == 400
    assert "category" in response.json()


def test_excerpt_limited_to_300_chars(industry):
    obj = Presentation(title_ru="Проверка", sector=industry, file=SimpleUploadedFile("a.pdf", b"%PDF-1.7"))
    obj.excerpt_ru = "x" * 301
    with pytest.raises(ValidationError) as error:
        obj.full_clean()
    assert "excerpt_ru" in error.value.message_dict
    obj.excerpt_ru = "x" * 300
    obj.full_clean()


# --- Список и фильтры ----------------------------------------------------------------------


def test_list_fresh_first_with_file_info(api, industry):
    old = make_presentation("old", industry, published_at=days(-10), pages=4)
    new = make_presentation("new", industry, published_at=days(-1))
    data = api.get("/api/v1/presentations/").json()
    assert data["count"] == 2
    assert [item["id"] for item in data["results"]] == [new.id, old.id]
    item = data["results"][1]
    assert set(item) == {
        "id", "slug", "title", "excerpt", "category", "cover", "sector", "project", "country", "file",
        "published_at", "is_translated",
    }
    assert item["slug"] == "old-ru" and item["title"] == "old title ru"
    assert item["excerpt"] == "old excerpt ru" and item["category"] == "industry"
    assert "content" not in item
    assert item["sector"] == {"slug": "promyshlennost", "name": "Промышленность"}
    assert item["file"]["url"].startswith("http://testserver/media/presentations/")
    assert item["file"]["pages"] == 4 and item["file"]["ext"] == "pdf"
    assert item["file"]["size"] == old.file.size
    assert item["project"] is None and item["country"] is None and item["cover"] is None


def test_list_filters(api, industry, it_sector, project, china):
    kz = make(Country, "kz", fields=("name",), slug=False, code="KZ")
    a = make_presentation("a", industry, project=project, country=china)
    b = make_presentation("b", it_sector, country=kz)
    c = make_presentation("c", it_sector)

    def ids(**params):
        return {item["id"] for item in api.get("/api/v1/presentations/", params).json()["results"]}

    assert ids() == {a.id, b.id, c.id}
    # сфера и проект — slug на любом языке, страна — код без учёта регистра
    assert ids(sector="promyshlennost") == {a.id}
    assert ids(sector="information-technology", lang="ru") == {b.id, c.id}
    assert ids(project="proj-zh") == {a.id}
    assert ids(country="kz") == {b.id}
    assert ids(sector="information-technology", country="KZ") == {b.id}
    # неизвестные значения → пустой список
    assert ids(sector="nope") == set()
    assert ids(project="nope") == set()
    assert ids(country="US") == set()


def test_list_pagination(api, industry):
    for i in range(3):
        make_presentation(f"p{i}", industry)
    data = api.get("/api/v1/presentations/", {"page_size": 2}).json()
    assert data["count"] == 3 and len(data["results"]) == 2 and data["next"]


def test_project_filter_ignores_unpublished_project(api, industry, project):
    make_presentation("a", industry, project=project)
    project.status = PublishableModel.Status.DRAFT
    project.save()
    assert api.get("/api/v1/presentations/", {"project": "proj-ru"}).json()["count"] == 0


def test_list_has_no_n_plus_1(api, industry, project, china):
    for i in range(5):
        make_presentation(f"p{i}", industry, project=project, country=china, cover=image_file(f"c{i}.jpg"))
    api.get("/api/v1/presentations/")  # прогрев превью
    with CaptureQueriesContext(connection) as queries:
        assert api.get("/api/v1/presentations/").status_code == 200
    assert len(queries) <= 3  # count + выборка с select_related (+ запас)


# --- Детальный ответ -----------------------------------------------------------------------


def test_detail_full(api, industry, project, china):
    presentation = make_presentation(
        "full", industry, project=project, country=china, pages=5,
        source_file=pptx_file("full.pptx"), cover=image_file("cover.jpg"),
        excerpt_ru="Коротко о презентации",
        content_ru="<p>Текст <strong>жирным</strong></p><script>alert(1)</script>",
    )
    response = api.get("/api/v1/presentations/full-en/", {"lang": "ru"})
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "full-ru" and data["title"] == "full title ru"
    assert data["excerpt"] == "Коротко о презентации"
    assert data["content"] == "<p>Текст <strong>жирным</strong></p>"  # nh3 при сохранении
    assert data["category"] == "projects"
    assert "description" not in data
    assert data["sector"] == {"slug": "promyshlennost", "name": "Промышленность"}
    assert data["project"] == {"slug": "proj-ru", "title": "proj title ru"}
    assert data["country"] == {"code": "CN", "name": "china name ru"}
    assert data["file"] == {
        "url": f"http://testserver/media/{presentation.file.name}",
        "size": presentation.file.size,
        "pages": 5,
        "ext": "pdf",
    }
    assert data["source_file"] == {
        "url": f"http://testserver/media/{presentation.source_file.name}",
        "size": len(pptx_bytes()),
        "ext": "pptx",
    }
    assert data["cover"]["large"].endswith(".webp")
    assert data["is_translated"] is True
    seo = data["seo"]
    assert seo["meta_title"] == "full title ru"
    assert seo["meta_description"] == "Коротко о презентации"  # из excerpt
    assert seo["og_image"] == data["cover"]["large"]
    assert seo["alternates"] == {"ru": "full-ru", "en": "full-en", "zh": "full-zh"}


def test_detail_nulls_without_pptx_project_and_country(api, industry):
    make_presentation("bare", industry)
    data = api.get("/api/v1/presentations/bare-ru/").json()
    assert data["source_file"] is None
    assert data["project"] is None and data["country"] is None


def test_project_ref_is_null_when_project_unpublished_or_untranslated(api, industry, china):
    draft = make(Project, "draft", country=china, status=PublishableModel.Status.DRAFT)
    ru_only = make(Project, "ruonly", langs=("ru",), country=china)
    make_presentation("a", industry, project=draft)
    make_presentation("b", industry, project=ru_only)
    assert api.get("/api/v1/presentations/a-ru/").json()["project"] is None
    assert api.get("/api/v1/presentations/b-en/", {"lang": "en"}).json()["project"] is None
    ru = api.get("/api/v1/presentations/b-ru/").json()
    assert ru["project"] == {"slug": "ruonly-ru", "title": "ruonly title ru"}


# --- Публикация, переводы ------------------------------------------------------------------


@pytest.mark.parametrize("status", [PublishableModel.Status.DRAFT, PublishableModel.Status.REVIEW])
def test_drafts_hidden(api, industry, status):
    make_presentation("draft", industry, status=status)
    assert api.get("/api/v1/presentations/").json()["count"] == 0
    assert api.get("/api/v1/presentations/draft-ru/").status_code == 404


def test_scheduled_presentation_hidden_until_published_at(api, client, settings, industry, project):
    settings.FRONTEND_URL = FRONT
    make_presentation("later", industry, project=project, published_at=days(1))
    assert api.get("/api/v1/presentations/").json()["count"] == 0
    assert api.get("/api/v1/presentations/later-ru/").status_code == 404
    assert api.get("/api/v1/projects/proj-ru/").json()["presentations"] == []
    assert "/presentations/later-ru" not in client.get("/sitemap.xml").content.decode()

    Presentation.objects.update(published_at=days(-1))
    assert api.get("/api/v1/presentations/").json()["count"] == 1
    assert api.get("/api/v1/presentations/later-ru/").status_code == 200


def test_presentation_without_zh(api, industry):
    make_presentation("ruen", industry, langs=("ru", "en"))
    assert api.get("/api/v1/presentations/", {"lang": "zh"}).json()["count"] == 0
    response = api.get("/api/v1/presentations/ruen-ru/", {"lang": "zh"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_translated"] is False
    assert data["title"] is None and data["slug"] is None
    assert data["excerpt"] is None and data["content"] is None
    assert data["sector"] == {"slug": "gong-ye", "name": "工业"}
    assert data["file"]["pages"] == 3  # файл общий для всех языков
    assert data["seo"]["alternates"] == {"ru": "ruen-ru", "en": "ruen-en", "zh": None}


# --- Презентации в проекте -----------------------------------------------------------------


def test_project_detail_contains_published_translated_presentations(api, industry, project):
    second = make_presentation("second", industry, project=project, order=2)
    first = make_presentation("first", industry, project=project, order=1)
    make_presentation("draft", industry, project=project, status=PublishableModel.Status.DRAFT)
    ru_only = make_presentation("ruonly", industry, project=project, langs=("ru",), order=3)
    make_presentation("other", industry)  # без проекта

    # по order, а не по дате
    ru = api.get("/api/v1/projects/proj-ru/").json()["presentations"]
    assert [p["id"] for p in ru] == [first.id, second.id, ru_only.id]
    zh = api.get("/api/v1/projects/proj-ru/", {"lang": "zh"}).json()["presentations"]
    assert [p["id"] for p in zh] == [first.id, second.id]
    assert set(zh[0]) == {
        "id", "slug", "title", "excerpt", "category", "cover", "sector", "country", "file", "published_at",
        "is_translated",
    }
    assert zh[0]["slug"] == "first-zh" and zh[0]["file"]["ext"] == "pdf"
    assert zh[0]["category"] == "projects" and zh[0]["excerpt"] == "first excerpt zh"


def test_project_detail_queries_do_not_grow_with_presentations(api, industry, project):
    def count():
        with CaptureQueriesContext(connection) as queries:
            api.get("/api/v1/projects/proj-ru/")
        return len(queries)

    make_presentation("p0", industry, project=project)
    baseline = count()
    for i in range(1, 5):
        make_presentation(f"p{i}", industry, project=project)
    assert count() == baseline


# --- Файлы: валидация, размер, страницы ----------------------------------------------------


def presentation(sector, **files):
    obj = Presentation(title_ru="Проверка", sector=sector, **files)
    obj.full_clean()
    return obj


def test_pptx_in_pdf_field_rejected(industry):
    with pytest.raises(ValidationError) as error:
        presentation(industry, file=SimpleUploadedFile("slides.pptx", pptx_bytes()))
    assert "Разрешены: PDF" in str(error.value.message_dict["file"])


def test_fake_pdf_and_fake_pptx_rejected(industry):
    with pytest.raises(ValidationError) as error:
        presentation(
            industry,
            file=SimpleUploadedFile("slides.pdf", b"PK\x03\x04 not a pdf"),
            source_file=SimpleUploadedFile("slides.pptx", pptx_bytes(with_presentation=False)),
        )
    assert "не является документом PDF" in str(error.value.message_dict["file"])
    assert "не является документом PPTX" in str(error.value.message_dict["source_file"])


def test_docx_and_pdf_in_source_field_rejected(industry):
    for name, content in (("doc.docx", b"PK\x03\x04"), ("slides.pdf", b"%PDF-1.7")):
        with pytest.raises(ValidationError) as error:
            presentation(industry, file=SimpleUploadedFile("ok.pdf", b"%PDF-1.7"),
                         source_file=SimpleUploadedFile(name, content))
        assert "Разрешены: PPTX" in str(error.value.message_dict["source_file"])


def test_pdf_is_required(industry):
    with pytest.raises(ValidationError) as error:
        presentation(industry)
    assert "file" in error.value.message_dict


def test_files_over_50mb_rejected(industry):
    big_pdf = b"%PDF-1.7\n" + b"\0" * (50 * MB)
    big_pptx = pptx_bytes() + b"\0" * (50 * MB)
    with pytest.raises(ValidationError) as error:
        presentation(
            industry,
            file=SimpleUploadedFile("big.pdf", big_pdf),
            source_file=SimpleUploadedFile("big.pptx", big_pptx),
        )
    assert "слишком большой" in str(error.value.message_dict["file"])
    assert "50,0" in str(error.value.message_dict["file"])
    assert "слишком большой" in str(error.value.message_dict["source_file"])


def test_presentation_limit_is_50mb_not_20mb(industry):
    # 30 МБ — больше лимита документов (20 МБ), но в пределах лимита презентаций
    presentation(industry, file=SimpleUploadedFile("big.pdf", b"%PDF-1.7\n" + b"\0" * (30 * MB)))


def test_pages_and_size_counted_on_save(industry):
    obj = make_presentation("p", industry, pages=4, source_file=pptx_file())
    obj.refresh_from_db()
    assert obj.pages == 4
    assert obj.size == obj.file.size > 0
    assert obj.source_size == len(pptx_bytes())

    obj.file = slides_pdf_file(2, "new.pdf")  # новый файл — пересчёт
    obj.source_file = None
    obj.save()
    obj.refresh_from_db()
    assert obj.pages == 2 and obj.source_size is None


def test_unreadable_pdf_saves_with_null_pages(industry, caplog):
    obj = make_presentation("broken", industry, file=ContentFile(b"%PDF-1.7\nbroken", name="broken.pdf"))
    obj.refresh_from_db()
    assert obj.pk and obj.pages is None
    assert obj.size == len(b"%PDF-1.7\nbroken")
    assert "Не удалось посчитать страницы PDF" in caplog.text


# --- Заголовки для встраивания PDF (frame-ancestors) ---------------------------------------


@pytest.fixture
def media_urls(settings):
    settings.ROOT_URLCONF = "apps.core.tests.urls_media"
    settings.FRONTEND_URL = FRONT
    settings.FRAME_ANCESTORS = [FRONT]
    settings.CORS_ALLOWED_ORIGINS = [FRONT]


def test_pdf_can_be_framed_by_frontend_only(client, media_urls, industry):
    obj = make_presentation("p", industry)
    response = client.get(f"/media/{obj.file.name}")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response["Content-Security-Policy"] == f"frame-ancestors 'self' {FRONT}"
    assert "X-Frame-Options" not in response
    assert response["Content-Disposition"].startswith("inline")


def test_frame_ancestors_with_several_origins_and_wildcard(client, media_urls, settings, industry):
    settings.FRAME_ANCESTORS = [FRONT, "https://*.vercel.app", "http://localhost:3000"]
    obj = make_presentation("p", industry)
    response = client.get(f"/media/{obj.file.name}")
    assert response["Content-Security-Policy"] == (
        f"frame-ancestors 'self' {FRONT} https://*.vercel.app http://localhost:3000"
    )
    assert "X-Frame-Options" not in response


def test_pptx_is_downloaded(client, media_urls, industry):
    obj = make_presentation("p", industry, source_file=pptx_file("deck.pptx"))
    response = client.get(f"/media/{obj.source_file.name}")
    assert response.status_code == 200
    assert response["Content-Disposition"].startswith("attachment")
    assert "deck" in response["Content-Disposition"]


def test_other_media_and_admin_stay_deny(client, admin_client, media_urls, industry):
    attachment = add_pdf()
    other = client.get(f"/media/{attachment.file.name}")
    assert other.status_code == 200
    assert other["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" not in other

    assert admin_client.get("/admin/").get("X-Frame-Options") == "DENY"
    assert admin_client.get(admin_url(Presentation, "add"))["X-Frame-Options"] == "DENY"
    assert client.get("/api/v1/presentations/")["X-Frame-Options"] == "DENY"


def test_presentation_files_allow_cors_from_frontend(client, media_urls, industry):
    """Для pdf.js (fetch PDF с другого origin) нужен CORS — только у файлов презентаций."""
    obj = make_presentation("p", industry)
    response = client.get(f"/media/{obj.file.name}", HTTP_ORIGIN=FRONT)
    assert response["Access-Control-Allow-Origin"] == FRONT
    other = client.get(f"/media/{add_pdf().file.name}", HTTP_ORIGIN=FRONT)
    assert "Access-Control-Allow-Origin" not in other


# --- sitemap -------------------------------------------------------------------------------


def test_sitemap_contains_presentations(client, settings, industry):
    settings.FRONTEND_URL = FRONT
    make_presentation("deck", industry, langs=("ru", "en"))
    content = client.get("/sitemap.xml").content.decode()
    assert f"<loc>{FRONT}/ru/presentations/deck-ru</loc>" in content
    assert f"<loc>{FRONT}/en/presentations/deck-en</loc>" in content
    assert "/zh/presentations/" not in content


# --- Админка и права -----------------------------------------------------------------------


@pytest.mark.parametrize("role", ["admin_role_client", "editor_client"])
def test_roles_have_full_access_to_presentations_and_sectors(request, role, industry):
    client = request.getfixturevalue(role)
    perms = User.objects.get(pk=client.session["_auth_user_id"]).get_all_permissions()
    for model in ("sector", "presentation"):
        for action in ("add", "change", "delete", "view"):
            assert f"cooperation.{action}_{model}" in perms


def test_editor_creates_presentation_via_admin(editor_client, industry, project):
    add_page = editor_client.get(admin_url(Presentation, "add"))
    assert add_page.status_code == 200
    html = add_page.content.decode()
    for lang in ("ru", "en", "zh"):
        assert f'name="excerpt_{lang}"' in html and f'name="content_{lang}"' in html
        assert f'name="description_{lang}"' not in html
    assert html.count('class="django_ckeditor_5') == 3  # только content_*, excerpt — простой текст
    assert 'maxlength="300"' in html
    assert 'accept=".pdf"' in html and 'accept=".pptx"' in html

    data = form_data(add_page)
    data.update({
        "title_ru": "Презентация", "title_en": "Deck", "title_zh": "演示",
        "excerpt_ru": "Коротко", "content_ru": "<p>Текст</p>",
        "sector": industry.pk, "project": project.pk, "status": "published",
        "file": SimpleUploadedFile("deck.pdf", slides_pdf_file(4).read()),
        "source_file": SimpleUploadedFile("deck.pptx", pptx_bytes()),
    })
    response = editor_client.post(admin_url(Presentation, "add"), data)
    assert response.status_code == 302, response.context["adminform"].form.errors
    obj = Presentation.objects.get()
    assert (obj.slug_ru, obj.slug_en, obj.slug_zh) == ("prezentatsiia", "deck", "yan-shi")
    assert obj.pages == 4 and obj.source_size == len(pptx_bytes())

    assert editor_client.get(admin_url(Presentation, "change", obj.pk)).status_code == 200
    delete = editor_client.post(admin_url(Presentation, "delete", obj.pk), {"post": "yes"})
    assert delete.status_code == 302 and not Presentation.objects.exists()


def test_admin_form_rejects_pptx_as_main_file(editor_client, industry):
    add_page = editor_client.get(admin_url(Presentation, "add"))
    data = form_data(add_page)
    data.update({
        "title_ru": "Презентация", "sector": industry.pk, "status": "draft",
        "file": SimpleUploadedFile("deck.pptx", pptx_bytes()),
    })
    response = editor_client.post(admin_url(Presentation, "add"), data)
    assert response.status_code == 200
    assert "Недопустимый формат «.pptx». Разрешены: PDF." in response.content.decode()
    assert not Presentation.objects.exists()


def test_editor_adds_sector(editor_client):
    add_page = editor_client.get(admin_url(Sector, "add"))
    data = form_data(add_page)
    data.update({"name_ru": "Энергетика", "name_en": "Energy", "order": 3})
    assert editor_client.post(admin_url(Sector, "add"), data).status_code == 302
    assert Sector.objects.get(slug_en="energy").slug_ru == "energetika"


def test_admin_list_filters_and_search_in_three_languages(admin_role_client, industry, it_sector, project):
    make_presentation("alpha", industry, project=project)
    make(Presentation, "beta", fields=("title",), sector=it_sector, file=pdf_file("b.pdf"),
         title_zh="云计算", status=PublishableModel.Status.DRAFT)
    changelist = admin_url(Presentation, "changelist")
    html = admin_role_client.get(changelist).content.decode()
    for param in ("sector__id__exact", "project__id__exact", "country__id__exact", "status__exact"):
        assert param in html

    def found(**params):
        return [obj.title_ru for obj in admin_role_client.get(changelist, params).context["cl"].result_list]

    assert found(q="alpha title en") == ["alpha title ru"]
    assert found(q="云计算") == ["beta title ru"]
    assert found(sector__id__exact=it_sector.pk) == ["beta title ru"]
    assert found(project__id__exact=project.pk) == ["alpha title ru"]
    assert found(status__exact="draft") == ["beta title ru"]


def test_project_form_shows_presentations_read_only_with_edit_links(editor_client, industry, project):
    obj = make_presentation("linked", industry, project=project)
    make_presentation("unlinked", industry)
    response = editor_client.get(admin_url(Project, "change", project.pk))
    html = response.content.decode()
    assert admin_url(Presentation, "change", obj.pk) in html
    assert "linked title ru" in html and "unlinked title ru" not in html
    # только чтение: ни полей ввода, ни «Добавить ещё» в этом блоке
    inline = next(i for i in response.context["inline_admin_formsets"] if i.opts.model is Presentation)
    assert not inline.has_add_permission and not inline.has_change_permission
    assert not inline.has_delete_permission

    # сохранение проекта с этим блоком не ломается и презентацию не трогает
    data = form_data(response)
    data.pop("partners")  # пустой M2M браузер не отправляет вовсе
    assert data["presentations-MAX_NUM_FORMS"] == "0"
    assert editor_client.post(admin_url(Project, "change", project.pk), data).status_code == 302
    obj.refresh_from_db()
    assert obj.project_id == project.pk



# --- Миграция description → excerpt + content ------------------------------------------------


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_description_migrates_to_excerpt_and_content():
    from django.db.migrations.executor import MigrationExecutor

    before = [("cooperation", "0006_presentation_excerpt_content")]
    executor = MigrationExecutor(connection)
    executor.migrate(before)
    try:
        old_apps = executor.loader.project_state(before).apps
        OldSector = old_apps.get_model("cooperation", "Sector")
        OldPresentation = old_apps.get_model("cooperation", "Presentation")
        long_text = "Очень длинное описание. " * 20
        html = f"<p><strong>Заводы</strong> &amp; цеха.</p><p>{long_text}</p>"
        pk = OldPresentation.objects.create(
            title="Старая", title_ru="Старая", sector=OldSector.objects.get(slug_ru="promyshlennost"),
            file="presentations/old.pdf", description=html, description_ru=html, description_en="<p>Short</p>",
        ).pk
    finally:
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())

    obj = Presentation.objects.get(pk=pk)
    assert obj.content_ru == html and obj.content_en == "<p>Short</p>" and obj.content_zh is None
    assert obj.excerpt_en == "Short"
    assert obj.excerpt_zh is None
    assert obj.excerpt_ru.startswith("Заводы & цеха. Очень длинное описание.")
    assert len(obj.excerpt_ru) == 300 and obj.excerpt_ru.endswith("…")
    assert "<" not in obj.excerpt_ru
