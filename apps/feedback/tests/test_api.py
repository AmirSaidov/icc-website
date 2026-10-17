"""POST /api/v1/feedback/ — критерии 5–9 раздела 6 SPEC.md и смежные проверки."""
import logging
from smtplib import SMTPException

import pytest
from django.core.mail import EmailMessage
from rest_framework.test import APIClient

from apps.core.models import SiteSettings
from apps.feedback.models import Feedback

pytestmark = pytest.mark.django_db

URL = "/api/v1/feedback/"


def payload(**overrides):
    data = {
        "type": "cooperation",
        "full_name": "Асель Токтогулова",
        "company": "ОсОО «Ала-Тоо Текстиль»",
        "country": "Кыргызстан",
        "email": "asel@example.kg",
        "phone": "+996 (555) 123-456",
        "subject": "Поиск партнёра в Китае",
        "message": "Ищем производителя оборудования для швейного цеха.",
        "consent": True,
        "lang": "zh",
        "website": "",
    }
    data.update(overrides)
    return data


@pytest.fixture
def recipients():
    site = SiteSettings.load()
    site.feedback_emails = "centre@example.kg, manager@example.kg"
    site.save()
    return ["centre@example.kg", "manager@example.kg"]


def post(client, data, **extra):
    return client.post(URL, data, format="json", **extra)


# --- Критерий 8: успешное обращение сохраняется и отправляет письмо ---------------


def test_valid_feedback_is_saved_and_emailed(api, recipients, mailoutbox, django_capture_on_commit_callbacks, settings):
    settings.BACKEND_URL = "https://api.example.kg"
    with django_capture_on_commit_callbacks(execute=True):
        response = post(api, payload())
    assert response.status_code == 201
    assert response.json() == {"ok": True}

    feedback = Feedback.objects.get()
    assert feedback.status == Feedback.Status.NEW
    assert feedback.ip == "127.0.0.1"
    assert feedback.lang == "zh"
    assert feedback.phone == "+996 (555) 123-456"

    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.subject == "[ЦПК] Новое обращение: Сотрудничество — Поиск партнёра в Китае"
    assert mail.to == recipients
    assert mail.reply_to == ["asel@example.kg"]
    assert "Асель Токтогулова" in mail.body and "Ищем производителя" in mail.body
    assert "Язык сайта: 中文" in mail.body
    assert f"https://api.example.kg/admin/feedback/feedback/{feedback.pk}/change/" in mail.body


def test_phone_is_optional(api, recipients):
    data = payload()
    del data["phone"]
    assert post(api, data).status_code == 201
    assert post(api, payload(phone="")).status_code == 201
    assert list(Feedback.objects.values_list("phone", flat=True)) == [None, None]


# --- Критерий 5: валидация ----------------------------------------------------------


def test_empty_email_returns_400_with_field_error(api):
    response = post(api, payload(email=""))
    assert response.status_code == 400
    assert list(response.json()) == ["email"]
    assert not Feedback.objects.exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("type", "spam"),
        ("full_name", "А"),
        ("full_name", "x" * 151),
        ("company", ""),
        ("company", "x" * 201),
        ("country", "x" * 101),
        ("email", "not-an-email"),
        ("phone", "+996 555 abc"),
        ("phone", "1" * 31),
        ("subject", ""),
        ("subject", "x" * 201),
        ("message", "коротко"),
        ("message", "x" * 5001),
        ("consent", False),
        ("lang", "de"),
    ],
)
def test_invalid_field_returns_400_for_that_field(api, field, value):
    response = post(api, payload(**{field: value}))
    assert response.status_code == 400
    assert list(response.json()) == [field]


@pytest.mark.parametrize("field", ["type", "full_name", "company", "country", "email", "subject", "message", "consent", "lang"])
def test_required_fields(api, field):
    data = payload()
    del data[field]
    response = post(api, data)
    assert response.status_code == 400
    assert field in response.json()


def test_line_breaks_removed_from_subject_and_full_name(api, recipients, mailoutbox, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        response = post(api, payload(subject="Тема\r\nBcc: victim@example.com", full_name="Иван\nПетров"))
    assert response.status_code == 201
    feedback = Feedback.objects.get()
    assert feedback.subject == "Тема Bcc: victim@example.com"
    assert feedback.full_name == "Иван Петров"
    assert "\n" not in mailoutbox[0].subject and "\r" not in mailoutbox[0].subject
    assert mailoutbox[0].bcc == []


# --- Критерий 7: honeypot ------------------------------------------------------------


def test_honeypot_returns_201_but_saves_nothing(api, recipients, mailoutbox, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        response = post(api, payload(website="http://spam.example"))
    assert response.status_code == 201
    assert response.json() == {"ok": True}
    assert not Feedback.objects.exists()
    assert mailoutbox == []


def test_honeypot_wins_even_for_invalid_data(api):
    response = post(api, {"website": "bot"})
    assert response.status_code == 201
    assert not Feedback.objects.exists()


# --- Критерий 6: rate limit -------------------------------------------------------------


def test_sixth_request_per_hour_returns_429(api):
    # считаются все POST: валидные, невалидные и honeypot
    statuses = [
        post(api, payload()).status_code,
        post(api, payload(email="")).status_code,
        post(api, payload(website="bot")).status_code,
        post(api, payload()).status_code,
        post(api, payload(consent=False)).status_code,
    ]
    assert statuses == [201, 400, 201, 201, 400]
    response = post(api, payload())
    assert response.status_code == 429
    assert response.json()["detail"].startswith("Слишком много обращений с вашего адреса. Попробуйте снова через")
    assert int(response["Retry-After"]) > 0
    assert Feedback.objects.count() == 2


def test_rate_limit_is_per_ip(api):
    for _ in range(5):
        post(api, payload(), REMOTE_ADDR="10.0.0.1")
    assert post(api, payload(), REMOTE_ADDR="10.0.0.1").status_code == 429
    assert post(api, payload(), REMOTE_ADDR="10.0.0.2").status_code == 201


def test_rate_limit_uses_database_cache(settings):
    assert settings.CACHES["default"]["BACKEND"] == "django.core.cache.backends.db.DatabaseCache"


# --- IP с учётом NUM_PROXIES ----------------------------------------------------------


def test_ip_behind_one_proxy(api, settings):
    settings.REST_FRAMEWORK = {**settings.REST_FRAMEWORK, "NUM_PROXIES": 1}
    # клиент подделал X-Forwarded-For, nginx дописал реальный адрес клиента в конец
    response = post(api, payload(), REMOTE_ADDR="127.0.0.1", HTTP_X_FORWARDED_FOR="1.2.3.4, 203.0.113.7")
    assert response.status_code == 201
    assert Feedback.objects.get().ip == "203.0.113.7"

    # лимит считается по реальному IP, а не по адресу nginx
    for _ in range(4):
        post(api, payload(), HTTP_X_FORWARDED_FOR="203.0.113.7")
    assert post(api, payload(), HTTP_X_FORWARDED_FOR="203.0.113.7").status_code == 429
    assert post(api, payload(), HTTP_X_FORWARDED_FOR="198.51.100.1").status_code == 201


def test_x_forwarded_for_ignored_without_proxies(api):
    post(api, payload(), REMOTE_ADDR="192.0.2.10", HTTP_X_FORWARDED_FOR="1.2.3.4")
    assert Feedback.objects.get().ip == "192.0.2.10"


# --- Письмо: получатели и ошибки ----------------------------------------------------------


def test_feedback_email_from_env_when_site_settings_empty(api, settings, mailoutbox, django_capture_on_commit_callbacks):
    settings.FEEDBACK_EMAIL = "fallback@example.kg"
    with django_capture_on_commit_callbacks(execute=True):
        post(api, payload())
    assert mailoutbox[0].to == ["fallback@example.kg"]


def test_no_recipients_no_email_and_warning(api, settings, mailoutbox, caplog, django_capture_on_commit_callbacks):
    settings.FEEDBACK_EMAIL = ""
    with caplog.at_level(logging.WARNING, logger="apps.feedback"), django_capture_on_commit_callbacks(execute=True):
        response = post(api, payload())
    assert response.status_code == 201
    assert Feedback.objects.exists()
    assert mailoutbox == []
    assert "не заданы получатели" in caplog.text


# --- Критерий 9: ошибка SMTP не ломает сохранение ----------------------------------------


def test_smtp_error_does_not_break_saving(api, recipients, monkeypatch, caplog, django_capture_on_commit_callbacks):
    def broken_send(self, fail_silently=False):
        raise SMTPException("SMTP сервер недоступен")

    monkeypatch.setattr(EmailMessage, "send", broken_send)
    with caplog.at_level(logging.ERROR, logger="apps.feedback"), django_capture_on_commit_callbacks(execute=True):
        response = post(api, payload())
    assert response.status_code == 201
    assert response.json() == {"ok": True}
    assert Feedback.objects.count() == 1
    assert "Не удалось отправить письмо" in caplog.text
    assert "SMTP сервер недоступен" in caplog.text


# --- CSRF и CORS ----------------------------------------------------------------------------


def test_post_works_without_csrf_token():
    client = APIClient(enforce_csrf_checks=True)
    assert post(client, payload()).status_code == 201


def test_cors_preflight_for_allowed_origin(api):
    response = api.options(
        URL,
        HTTP_ORIGIN="http://localhost:3000",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type",
    )
    assert response.status_code == 200
    assert response["access-control-allow-origin"] == "http://localhost:3000"
    assert "content-type" in response["access-control-allow-headers"]

    response = post(api, payload(), HTTP_ORIGIN="http://localhost:3000")
    assert response["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_denied_for_unknown_origin(api):
    response = post(api, payload(), HTTP_ORIGIN="https://evil.example")
    assert "access-control-allow-origin" not in response


def test_get_not_allowed(api):
    assert api.get(URL).status_code == 405
