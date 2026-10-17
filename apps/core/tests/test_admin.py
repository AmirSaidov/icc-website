"""Админка: все страницы открываются, права ролей, загрузка файлов, CKEditor."""
import io
import zipfile

import pytest
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.cooperation.models import Country, Partner, Project
from apps.core.models import Attachment, ContactInfo, GalleryImage, SiteSettings
from apps.core.tests.factories import add_pdf, add_photo, days, image_file, make
from apps.core.validators import validate_document_file, validate_image_file
from apps.feedback.models import Feedback
from apps.news.models import Event, News, NewsCategory
from apps.pages.models import Direction, HomeBlock, Page, Service

pytestmark = pytest.mark.django_db

HIDDEN_FOR_EDITOR = {User, Group, ContactInfo, SiteSettings}


def make_objects():
    """По одному объекту каждой зарегистрированной модели — для страниц изменения."""
    country = make(Country, "cn", fields=("name",), slug=False, code="CN")
    news = make(News, "news", fields=("title", "excerpt", "content"))
    add_photo(news)
    add_pdf(news)
    return {
        Page: Page.objects.get(key="about"),
        HomeBlock: make(HomeBlock, "block", slug=False, type=HomeBlock.Type.HERO),
        Direction: make(Direction, "dir", icon="export"),
        Service: make(Service, "srv"),
        NewsCategory: make(NewsCategory, "cat", fields=("name",)),
        News: news,
        Event: make(Event, "event", type=Event.Type.FORUM, start_at=days(3)),
        Country: country,
        Partner: make(Partner, "partner", fields=("name",), slug=False, country=country),
        Project: make(Project, "project", country=country),
        GalleryImage: news.gallery.get(),
        Attachment: news.attachments.get(),
        ContactInfo: ContactInfo.load(),
        SiteSettings: SiteSettings.load(),
        Feedback: Feedback.objects.create(
            type="contact", full_name="Иван", company="ООО", country="KG", email="a@example.kg",
            subject="Тема", message="Сообщение длиной больше десяти", consent=True, lang="ru",
        ),
        User: User.objects.create_user("someone"),
        Group: Group.objects.get(name="Редактор"),
    }


def url(model, action, *args):
    opts = model._meta
    return reverse(f"admin:{opts.app_label}_{opts.model_name}_{action}", args=args)


def test_every_model_is_covered():
    assert set(admin.site._registry) == set(make_objects())


@pytest.mark.parametrize("role", ["admin", "editor"])
def test_all_admin_pages_open(request, role):
    client = request.getfixturevalue("admin_role_client" if role == "admin" else "editor_client")
    objects = make_objects()
    assert client.get(reverse("admin:index")).status_code == 200
    for model, obj in objects.items():
        hidden = role == "editor" and model in HIDDEN_FOR_EDITOR
        changelist = client.get(url(model, "changelist"))
        change = client.get(url(model, "change", obj.pk))
        if hidden:
            assert changelist.status_code == 403, model
            assert change.status_code == 403, model
            continue
        if model in (ContactInfo, SiteSettings):
            # singleton: из списка сразу открывается единственная запись
            assert changelist.status_code == 302 and changelist.url == url(model, "change", obj.pk)
        else:
            assert changelist.status_code == 200, model
        assert change.status_code == 200, model
        add = client.get(url(model, "add"))
        if model in (ContactInfo, SiteSettings, Feedback):
            assert add.status_code == 403, model  # добавлять нельзя никому
        else:
            assert add.status_code == 200, model


def test_translation_tabs_and_ckeditor_are_on_forms(admin_role_client):
    html = admin_role_client.get(url(News, "add")).content.decode()
    assert "vendor/jquery-ui/jquery-ui.min.js" in html  # локально, без CDN
    assert "googleapis" not in html
    assert "cpk_admin/translation_tabs.js" in html
    assert "modeltranslation/js/tabbed_translation_fields.js" in html
    for lang in ("ru", "en", "zh"):
        assert f'name="content_{lang}"' in html
    assert html.count('class="django_ckeditor_5') == 3  # только content_*, не excerpt
    assert 'name="core-galleryimage-content_type-object_id-TOTAL_FORMS"' in html
    assert 'name="core-attachment-content_type-object_id-TOTAL_FORMS"' in html
    assert "collapse" in html and 'name="meta_title_ru"' in html  # свёрнутый SEO-fieldset


def test_admin_header(admin_role_client):
    assert "ЦПК при ТПП КР — управление сайтом" in admin_role_client.get(reverse("admin:index")).content.decode()


# --- Критерий 2: Редактор не видит пользователей, группы, контакты, настройки ----------


def test_editor_index_hides_restricted_sections(editor_client, admin_role_client):
    editor_html = editor_client.get(reverse("admin:index")).content.decode()
    admin_html = admin_role_client.get(reverse("admin:index")).content.decode()
    for model in HIDDEN_FOR_EDITOR:
        assert url(model, "changelist") not in editor_html, model
        assert url(model, "changelist") in admin_html, model
    assert url(News, "changelist") in editor_html


def test_system_page_cannot_be_deleted_and_key_is_readonly(admin_role_client):
    page = Page.objects.get(key="about")
    assert admin_role_client.get(url(Page, "delete", page.pk)).status_code == 403
    html = admin_role_client.get(url(Page, "change", page.pk)).content.decode()
    assert 'name="key"' not in html
    response = admin_role_client.post(
        url(Page, "changelist"), {"action": "delete_selected", "_selected_action": [page.pk], "post": "yes"}
    )
    assert response.status_code == 200  # страница «нельзя удалить», а не удаление
    assert Page.objects.filter(key="about").exists()


# --- Файлы ----------------------------------------------------------------------------


def upload(name, content):
    return SimpleUploadedFile(name, content)


def jpeg_bytes(size=(10, 10)):
    return image_file(size=size).read()


def docx_bytes(with_document=True):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml" if with_document else "other.xml", "<w:document/>")
    return buffer.getvalue()


def test_valid_files_pass():
    validate_image_file(upload("photo.jpg", jpeg_bytes()))
    validate_document_file(upload("doc.pdf", b"%PDF-1.7\n..."))
    validate_document_file(upload("doc.docx", docx_bytes()))


@pytest.mark.parametrize(
    "validator,name,content,message",
    [
        (validate_document_file, "fake.pdf", b"MZ\x90\x00 not a pdf", "не является документом PDF"),
        (validate_document_file, "fake.docx", docx_bytes(with_document=False), "не является документом DOCX"),
        (validate_document_file, "doc.exe", b"%PDF-1.7", "Недопустимый формат"),
        (validate_image_file, "photo.jpg", b"not an image at all", "не является изображением"),
        (validate_image_file, "photo.gif", b"GIF89a", "Недопустимый формат"),
    ],
)
def test_invalid_files_rejected(validator, name, content, message):
    with pytest.raises(ValidationError) as error:
        validator(upload(name, content))
    assert message in " ".join(error.value.messages)


def test_png_with_jpg_extension_rejected():
    png = io.BytesIO()
    from PIL import Image

    Image.new("RGB", (5, 5)).save(png, "PNG")
    with pytest.raises(ValidationError, match="не соответствует расширению"):
        validate_image_file(upload("photo.jpg", png.getvalue()))


def test_image_over_10mb_rejected():
    big = jpeg_bytes() + b"\0" * (10 * 1024 * 1024)
    with pytest.raises(ValidationError, match="слишком большой"):
        validate_image_file(upload("big.jpg", big))


def test_document_over_20mb_rejected():
    big = b"%PDF-1.7\n" + b"\0" * (20 * 1024 * 1024)
    with pytest.raises(ValidationError, match="слишком большой"):
        validate_document_file(upload("big.pdf", big))


def test_admin_form_rejects_fake_pdf_and_big_image(admin_role_client):
    attachment_add = admin_role_client.get(url(Attachment, "add"))
    from apps.core.tests.admin_utils import form_data

    data = form_data(attachment_add)
    data.update({"title_ru": "Документ", "file": upload("fake.pdf", b"not a pdf")})
    response = admin_role_client.post(url(Attachment, "add"), data)
    assert response.status_code == 200
    assert "не является документом PDF" in response.content.decode()
    assert not Attachment.objects.exists()

    data = form_data(admin_role_client.get(url(Country, "add")))
    big = jpeg_bytes() + b"\0" * (10 * 1024 * 1024 + 1)
    data.update({"name_ru": "Китай", "code": "CN", "flag": upload("flag.jpg", big)})
    response = admin_role_client.post(url(Country, "add"), data)
    assert "слишком большой" in response.content.decode()
    assert not Country.objects.exists()


# --- CKEditor: загрузка картинок -----------------------------------------------------------


def test_ckeditor_upload_only_for_staff(client, editor_client):
    upload_url = reverse("ckeditor-upload")
    assert client.post(upload_url, {"upload": upload("a.jpg", jpeg_bytes())}).status_code == 403

    response = editor_client.post(upload_url, {"upload": upload("Фото 1.JPG", jpeg_bytes())})
    assert response.status_code == 200
    assert response.json()["url"].startswith("/media/editor/")
    assert response.json()["url"].endswith(".jpg")

    bad = editor_client.post(upload_url, {"upload": upload("a.png", b"<script>")})
    assert bad.status_code == 400
    assert "error" in bad.json()


def test_ckeditor_upload_requires_csrf(editor_user):
    from django.test import Client

    client = Client(enforce_csrf_checks=True)
    client.force_login(editor_user)
    assert client.post(reverse("ckeditor-upload"), {"upload": upload("a.jpg", jpeg_bytes())}).status_code == 403
