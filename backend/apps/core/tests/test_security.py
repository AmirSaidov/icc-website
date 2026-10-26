"""Безопасность (SPEC.md, 5.2): axes, ADMIN_URL, прод-настройки, логирование."""
import importlib
import json
import logging
import logging.handlers
import os
import subprocess
import sys

import pytest
from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.test import Client
from django.urls import clear_url_caches, reverse

pytestmark = pytest.mark.django_db

PASSWORD = "correct-password-1"


@pytest.fixture
def staff():
    return User.objects.create_user("manager", "m@example.kg", PASSWORD, is_staff=True)


def login(client, username, password, **extra):
    return client.post(
        reverse("admin:login"), {"username": username, "password": password, "next": "/admin/"}, **extra
    )


# --- django-axes -------------------------------------------------------------------------


def test_axes_blocks_after_five_failed_logins(staff, caplog):
    client = Client(REMOTE_ADDR="198.51.100.5")
    with caplog.at_level(logging.WARNING):
        statuses = [login(client, "manager", "wrong").status_code for _ in range(5)]
    assert statuses == [200, 200, 200, 200, 429]  # 5-я неудача — блокировка

    blocked = login(client, "manager", PASSWORD)  # даже с верным паролем
    assert blocked.status_code == 429
    html = blocked.content.decode()
    assert "Вход временно заблокирован" in html and "30 минут" in html
    assert blocked["X-Robots-Tag"] == "noindex, nofollow"
    assert "Вход заблокирован после неудачных попыток" in caplog.text
    assert "manager" in caplog.text


def test_axes_lockout_is_per_username_and_ip(staff):
    User.objects.create_user("other", "o@example.kg", PASSWORD, is_staff=True)
    attacker = Client(REMOTE_ADDR="198.51.100.5")
    for _ in range(5):
        login(attacker, "manager", "wrong")
    # тот же пользователь с другого IP и другой пользователь с того же IP — входят
    assert login(Client(REMOTE_ADDR="203.0.113.9"), "manager", PASSWORD).status_code == 302
    assert login(attacker, "other", PASSWORD).status_code == 302


def test_axes_uses_real_ip_behind_proxy(staff, settings):
    settings.REST_FRAMEWORK = {**settings.REST_FRAMEWORK, "NUM_PROXIES": 1}
    nginx = {"REMOTE_ADDR": "127.0.0.1"}
    for _ in range(5):
        login(Client(**nginx), "manager", "wrong", HTTP_X_FORWARDED_FOR="198.51.100.5")
    assert login(Client(**nginx), "manager", PASSWORD, HTTP_X_FORWARDED_FOR="198.51.100.5").status_code == 429
    # другой клиент за тем же nginx не заблокирован
    assert login(Client(**nginx), "manager", PASSWORD, HTTP_X_FORWARDED_FOR="203.0.113.9").status_code == 302


def test_successful_login_resets_failures(staff):
    client = Client(REMOTE_ADDR="198.51.100.5")
    for _ in range(4):
        login(client, "manager", "wrong")
    assert login(client, "manager", PASSWORD).status_code == 302
    client.logout()
    for _ in range(4):
        assert login(client, "manager", "wrong").status_code == 200


# --- ADMIN_URL ---------------------------------------------------------------------------


@pytest.fixture
def reload_urls():
    def reload():
        import config.urls

        importlib.reload(config.urls)
        clear_url_caches()

    yield reload
    reload()  # вернуть адреса по настройкам после теста


def test_admin_url_default(client):
    assert django_settings.ADMIN_URL == "admin/"
    assert client.get("/admin/login/").status_code == 200


def test_admin_url_can_be_changed(client, settings, reload_urls):
    settings.ADMIN_URL = "cpk-panel-7f3k/"
    reload_urls()
    login_page = client.get("/cpk-panel-7f3k/login/")
    assert login_page.status_code == 200
    # админка закрыта от индексации заголовком, а robots.txt её путь не раскрывает
    assert login_page["X-Robots-Tag"] == "noindex, nofollow"
    assert "cpk-panel-7f3k" not in client.get("/robots.txt").content.decode()
    assert client.get("/admin/login/").status_code == 404
    assert reverse("ckeditor-upload") == "/cpk-panel-7f3k/ckeditor/upload/"
    settings.ADMIN_URL = "admin/"


# --- Прод-настройки при DEBUG=False -------------------------------------------------------


def _settings_in_subprocess(env_overrides, code):
    env = {**os.environ, **env_overrides, "DJANGO_SETTINGS_MODULE": "config.settings"}
    result = subprocess.run(
        [sys.executable, "-c", f"import django; django.setup(); from django.conf import settings as s; {code}"],
        cwd=django_settings.BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_production_security_settings():
    values = _settings_in_subprocess(
        {"DEBUG": "False", "SECRET_KEY": "x" * 60, "ALLOWED_HOSTS": "api.example.kg"},
        "import json; print(json.dumps({k: getattr(s, k, None) for k in ["
        "'DEBUG', 'SECURE_HSTS_SECONDS', 'SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE', "
        "'SECURE_PROXY_SSL_HEADER', 'SECURE_CONTENT_TYPE_NOSNIFF', 'X_FRAME_OPTIONS', "
        "'SESSION_COOKIE_HTTPONLY']}))",
    )
    assert values == {
        "DEBUG": False,
        "SECURE_HSTS_SECONDS": 31536000,
        "SESSION_COOKIE_SECURE": True,
        "CSRF_COOKIE_SECURE": True,
        "SECURE_PROXY_SSL_HEADER": ["HTTP_X_FORWARDED_PROTO", "https"],
        "SECURE_CONTENT_TYPE_NOSNIFF": True,
        "X_FRAME_OPTIONS": "DENY",
        "SESSION_COOKIE_HTTPONLY": True,
    }


FRAME_ANCESTORS_CODE = "import json; print(json.dumps(s.FRAME_ANCESTORS))"


def test_frame_ancestors_default_is_frontend_url():
    values = _settings_in_subprocess({"FRONTEND_URL": "https://icc.kg/", "FRAME_ANCESTORS": ""}, FRAME_ANCESTORS_CODE)
    assert values == ["https://icc.kg"]


def test_frame_ancestors_several_values_and_wildcard():
    values = _settings_in_subprocess(
        {"FRAME_ANCESTORS": " https://icc.kg/, https://*.vercel.app ,http://localhost:3000"}, FRAME_ANCESTORS_CODE
    )
    assert values == ["https://icc.kg", "https://*.vercel.app", "http://localhost:3000"]


@pytest.mark.parametrize("value", ["icc.kg", "https://icc.kg; script-src *", "'unsafe-inline'"])
def test_frame_ancestors_rejects_non_origins(value):
    env = {
        **os.environ, "FRAME_ANCESTORS": value, "DJANGO_SETTINGS_MODULE": "config.settings",
        "PYTHONIOENCODING": "utf-8",  # сообщение об ошибке — по-русски
    }
    result = subprocess.run(
        [sys.executable, "-c", "import django; django.setup()"],
        cwd=django_settings.BASE_DIR, env=env, capture_output=True, text=True, encoding="utf-8", timeout=120,
    )
    assert result.returncode != 0
    assert "FRAME_ANCESTORS" in result.stderr


def test_debug_mode_keeps_cookies_usable_over_http():
    values = _settings_in_subprocess(
        {"DEBUG": "True"},
        "import json; print(json.dumps([s.SESSION_COOKIE_SECURE, getattr(s, 'SECURE_HSTS_SECONDS', 0)]))",
    )
    assert values == [False, 0]


# --- Логирование ----------------------------------------------------------------------------


def test_log_file_rotation_config():
    handler = django_settings.LOGGING["handlers"]["file"]
    assert handler["class"] == "logging.handlers.RotatingFileHandler"
    assert handler["maxBytes"] == 5 * 1024 * 1024 and handler["backupCount"] == 5
    assert str(handler["filename"]).endswith(os.path.join("logs", "app.log"))
    assert (django_settings.BASE_DIR / "logs").is_dir()


@pytest.mark.urls("apps.core.tests.urls_error")
def test_server_errors_are_logged(caplog):
    client = Client(raise_request_exception=False)
    with caplog.at_level(logging.ERROR, logger="django.request"):
        assert client.get("/boom/").status_code == 500
    assert "тестовая ошибка 500" in caplog.text
