import pytest
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def _test_settings(settings, tmp_path):
    # загрузки и превью — во временную папку, а не в media/ проекта
    settings.MEDIA_ROOT = tmp_path / "media"
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def api():
    return APIClient()
