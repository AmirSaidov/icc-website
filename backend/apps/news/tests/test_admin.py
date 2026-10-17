"""Новости в админке: создание Редактором, автозаполнение slug, санитайзинг."""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.core.sanitize import sanitize_html
from apps.core.tests.admin_utils import form_data
from apps.core.tests.factories import image_file
from apps.news.models import News, NewsCategory
from apps.pages.models import Page

pytestmark = pytest.mark.django_db

ADD_URL = reverse("admin:news_news_add")
GALLERY = "core-galleryimage-content_type-object_id"
ATTACHMENTS = "core-attachment-content_type-object_id"

TITLES = {"ru": "Деловая миссия в Урумчи", "en": "Business mission to Urumqi", "zh": "乌鲁木齐商务考察"}
EXPECTED_SLUGS = {"ru": "delovaia-missiia-v-urumchi", "en": "business-mission-to-urumqi", "zh": "wu-lu-mu-qi-shang-wu-kao-cha"}


# --- Критерий приёмки 2: Редактор создаёт новость на 3 языках с фото и PDF ---------------


def test_editor_creates_news_with_photo_and_pdf_and_it_is_in_zh_api(editor_client, api):
    data = form_data(editor_client.get(ADD_URL))
    for lang, title in TITLES.items():
        data[f"title_{lang}"] = title
        data[f"excerpt_{lang}"] = f"Анонс {lang}"
        data[f"content_{lang}"] = f"<p>Текст {lang}</p><script>alert(1)</script>"
    data["status"] = "published"
    data[f"{GALLERY}-0-image"] = SimpleUploadedFile("photo.jpg", image_file().read())
    for lang in TITLES:
        data[f"{GALLERY}-0-caption_{lang}"] = f"Фото {lang}"
        data[f"{ATTACHMENTS}-0-title_{lang}"] = f"Программа {lang}"
    data[f"{GALLERY}-0-order"] = "0"
    data[f"{ATTACHMENTS}-0-file"] = SimpleUploadedFile("program.pdf", b"%PDF-1.7\n%test\n")
    data[f"{ATTACHMENTS}-0-order"] = "0"

    response = editor_client.post(ADD_URL, data)
    assert response.status_code == 302, response.context["adminform"].form.errors if response.context else ""

    news = News.objects.get()
    assert {lang: getattr(news, f"slug_{lang}") for lang in TITLES} == EXPECTED_SLUGS
    assert "<script>" not in news.content_ru  # критерий 14 через админку

    items = api.get("/api/v1/news/", {"lang": "zh"}).json()["results"]
    assert [item["slug"] for item in items] == [EXPECTED_SLUGS["zh"]]
    detail = api.get(f"/api/v1/news/{EXPECTED_SLUGS['zh']}/", {"lang": "zh"}).json()
    assert detail["title"] == TITLES["zh"]
    assert detail["gallery"][0]["caption"] == "Фото zh"
    assert detail["attachments"][0]["title"] == "Программа zh"
    assert detail["attachments"][0]["ext"] == "pdf"


# --- Автозаполнение slug ---------------------------------------------------------------


def make_news(**extra):
    fields = {f"title_{lang}": title for lang, title in TITLES.items()}
    fields.update(extra)
    return News.objects.create(**fields)


def test_slug_autofill_on_three_languages_including_pinyin():
    news = make_news()
    assert {lang: getattr(news, f"slug_{lang}") for lang in TITLES} == EXPECTED_SLUGS


def test_slug_conflict_gets_numeric_suffix():
    make_news()
    second = make_news()
    third = make_news()
    assert second.slug_zh == f"{EXPECTED_SLUGS['zh']}-2"
    assert third.slug_ru == f"{EXPECTED_SLUGS['ru']}-3"
    third.save()  # пересохранение не меняет собственный slug
    third.refresh_from_db()
    assert third.slug_ru == f"{EXPECTED_SLUGS['ru']}-3"


def test_manual_slug_is_kept_and_not_regenerated_on_title_change():
    news = make_news(slug_en="my-own-slug")
    assert news.slug_en == "my-own-slug"
    news.title_ru = "Совсем другой заголовок"
    news.save()
    assert news.slug_ru == EXPECTED_SLUGS["ru"]


def test_slug_only_for_filled_titles():
    news = News.objects.create(title_ru="Только по-русски")
    assert news.slug_ru == "tolko-po-russki"
    assert news.slug_en is None and news.slug_zh is None


def test_category_slug_from_name():
    category = NewsCategory.objects.create(name_ru="Деловые миссии", name_zh="商务考察")
    assert category.slug_ru == "delovye-missii"
    assert category.slug_zh == "shang-wu-kao-cha"


def test_system_page_gets_no_slug_but_regular_page_does():
    about = Page.objects.get(key="about")
    about.title_en = "About"
    about.save()
    assert about.slug_en is None and about.slug_ru is None
    page = Page.objects.create(title_ru="Вакансии", title_en="Careers")
    assert (page.slug_ru, page.slug_en) == ("vakansii", "careers")


def test_slug_autofill_via_admin_form(admin_role_client):
    data = form_data(admin_role_client.get(ADD_URL))
    data.update({"title_ru": "Новость", "title_zh": "新闻", "slug_ru": "", "status": "draft"})
    assert admin_role_client.post(ADD_URL, data).status_code == 302
    news = News.objects.get()
    assert (news.slug_ru, news.slug_en, news.slug_zh) == ("novost", None, "xin-wen")


# --- Критерий 14 и разметка CKEditor через nh3 ----------------------------------------------


def test_script_is_removed_on_save():
    news = News.objects.create(
        title_ru="X",
        content_ru='<p onclick="steal()">Текст</p><script>alert("xss")</script>'
        '<a href="javascript:alert(1)">ссылка</a><iframe src="https://evil"></iframe>',
    )
    news.refresh_from_db()
    assert "<script" not in news.content_ru and "alert" not in news.content_ru
    assert "onclick" not in news.content_ru and "javascript:" not in news.content_ru
    assert "<iframe" not in news.content_ru
    assert "<p>Текст</p>" in news.content_ru


def test_ckeditor_markup_survives_sanitizer():
    """Типичный вывод CKEditor 5 с нашим тулбаром не ломается после nh3."""
    ckeditor_html = (
        "<h2>Заголовок</h2><h3>Подзаголовок</h3><h4>Мелкий</h4>"
        "<p>Текст <strong>жирный</strong>, <i>курсив</i>, <u>подчёркнутый</u>, <s>зачёркнутый</s>"
        '<br><a href="https://example.kg" target="_blank" rel="noopener noreferrer">ссылка</a></p>'
        "<ul><li>пункт</li></ul><ol><li>первый</li></ol>"
        "<blockquote><p>Цитата</p></blockquote>"
        '<figure class="image"><img src="/media/editor/2026/10/photo.jpg" alt="Фото" width="800" height="600">'
        "<figcaption>Подпись</figcaption></figure>"
        '<figure class="table"><table><thead><tr><th>Колонка</th></tr></thead>'
        "<tbody><tr><td>Значение</td></tr></tbody></table></figure>"
    )
    expected = (
        "<h2>Заголовок</h2><h3>Подзаголовок</h3><h4>Мелкий</h4>"
        "<p>Текст <strong>жирный</strong>, <em>курсив</em>, <u>подчёркнутый</u>, <s>зачёркнутый</s>"
        '<br><a href="https://example.kg" target="_blank" rel="noopener noreferrer">ссылка</a></p>'
        "<ul><li>пункт</li></ul><ol><li>первый</li></ol>"
        "<blockquote><p>Цитата</p></blockquote>"
        '<figure><img src="/media/editor/2026/10/photo.jpg" alt="Фото" width="800" height="600">'
        "<figcaption>Подпись</figcaption></figure>"
        "<figure><table><thead><tr><th>Колонка</th></tr></thead>"
        "<tbody><tr><td>Значение</td></tr></tbody></table></figure>"
    )
    assert sanitize_html(ckeditor_html) == expected


def test_editor_images_in_content_get_absolute_urls_in_api(api):
    News.objects.create(
        title_ru="С картинкой",
        status="published",
        content_ru='<p><img src="/media/editor/a.jpg" alt=""></p><a href="https://x.kg">x</a>',
    )
    content = api.get("/api/v1/news/s-kartinkoi/").json()["content"]
    assert 'src="http://testserver/media/editor/a.jpg"' in content
    assert 'href="https://x.kg"' in content
