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


def _staff_user(username, group_name):
    from django.contrib.auth.models import Group, User

    user = User.objects.create_user(username, f"{username}@example.kg", "x-test-password-1", is_staff=True)
    user.groups.add(Group.objects.get(name=group_name))
    return user


@pytest.fixture
def admin_role_user(db):
    """Сотрудник из группы «Администратор» (не суперпользователь — проверяем именно права группы)."""
    return _staff_user("admin-role", "Администратор")


@pytest.fixture
def editor_user(db):
    return _staff_user("editor-role", "Редактор")


@pytest.fixture
def admin_role_client(admin_role_user):
    from django.test import Client

    client = Client()
    client.force_login(admin_role_user)
    return client


@pytest.fixture
def editor_client(editor_user):
    from django.test import Client

    client = Client()
    client.force_login(editor_user)
    return client
