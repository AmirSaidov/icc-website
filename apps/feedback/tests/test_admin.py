"""Обращения в админке: ограничения Редактора (критерий 2), смена статуса в списке, CSV."""
import csv
import io

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.core.tests.admin_utils import changelist_data, form_data
from apps.feedback.models import Feedback

pytestmark = pytest.mark.django_db

CHANGELIST = reverse("admin:feedback_feedback_changelist")


@pytest.fixture
def feedback():
    return Feedback.objects.create(
        type=Feedback.Type.COOPERATION,
        full_name="Иван Петров",
        company="ООО «Ромашка»",
        country="Кыргызстан",
        email="ivan@example.kg",
        phone="+996 555 000 000",
        subject="Ищем партнёра",
        message="=HYPERLINK(\"http://evil\")",
        consent=True,
        lang="ru",
        ip="10.0.0.1",
    )


def change_url(obj):
    return reverse("admin:feedback_feedback_change", args=[obj.pk])


def test_editor_can_change_only_status_and_admin_note(editor_client, feedback):
    response = editor_client.get(change_url(feedback))
    form_fields = set(response.context["adminform"].form.fields)
    assert form_fields == {"status", "admin_note"}

    data = form_data(response)
    data.update({
        "status": Feedback.Status.IN_PROGRESS,
        "admin_note": "Перезвонить",
        # попытка подменить остальные поля — должна быть проигнорирована
        "subject": "Взломано",
        "email": "hacker@example.com",
    })
    assert editor_client.post(change_url(feedback), data).status_code == 302
    feedback.refresh_from_db()
    assert feedback.status == Feedback.Status.IN_PROGRESS
    assert feedback.admin_note == "Перезвонить"
    assert feedback.subject == "Ищем партнёра"
    assert feedback.email == "ivan@example.kg"


def test_editor_cannot_delete(editor_client, feedback):
    assert editor_client.get(reverse("admin:feedback_feedback_delete", args=[feedback.pk])).status_code == 403
    response = editor_client.post(
        CHANGELIST, {"action": "delete_selected", "_selected_action": [feedback.pk], "post": "yes"}
    )
    assert Feedback.objects.filter(pk=feedback.pk).exists()
    assert "delete_selected" not in editor_client.get(CHANGELIST).content.decode()
    assert response.status_code in (200, 302)


def test_admin_has_full_access(admin_role_client, feedback):
    response = admin_role_client.get(change_url(feedback))
    assert "subject" in response.context["adminform"].form.fields
    data = form_data(response)
    data["subject"] = "Исправленная тема"
    assert admin_role_client.post(change_url(feedback), data).status_code == 302
    feedback.refresh_from_db()
    assert feedback.subject == "Исправленная тема"
    assert admin_role_client.post(
        reverse("admin:feedback_feedback_delete", args=[feedback.pk]), {"post": "yes"}
    ).status_code == 302
    assert not Feedback.objects.exists()


@pytest.mark.parametrize("client_fixture", ["admin_role_client", "editor_client"])
def test_nobody_can_add_feedback_in_admin(request, client_fixture):
    client = request.getfixturevalue(client_fixture)
    assert client.get(reverse("admin:feedback_feedback_add")).status_code == 403


def test_status_change_in_list(editor_client, feedback):
    response = editor_client.get(CHANGELIST)
    data = changelist_data(response)
    data["form-0-status"] = Feedback.Status.CLOSED
    data["_save"] = "Сохранить"
    assert editor_client.post(CHANGELIST, data).status_code == 302
    feedback.refresh_from_db()
    assert feedback.status == Feedback.Status.CLOSED


def test_filters_by_status_type_and_date(editor_client, feedback):
    year = timezone.localtime(feedback.created_at).year
    response = editor_client.get(CHANGELIST, {"status": "new", "type": "cooperation", "created_at__year": year})
    assert response.status_code == 200
    assert list(response.context["cl"].result_list) == [feedback]
    assert not editor_client.get(CHANGELIST, {"type": "contact"}).context["cl"].result_list
    assert not editor_client.get(CHANGELIST, {"created_at__year": year - 1}).context["cl"].result_list


@pytest.mark.parametrize("client_fixture", ["admin_role_client", "editor_client"])
def test_csv_export(request, client_fixture, feedback):
    client = request.getfixturevalue(client_fixture)
    response = client.post(CHANGELIST, {"action": "export_csv", "_selected_action": [feedback.pk]})
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert "attachment" in response["Content-Disposition"]
    content = response.content.decode("utf-8")
    assert content.startswith("﻿")  # BOM для Excel

    rows = list(csv.reader(io.StringIO(content.lstrip("﻿")), delimiter=";"))
    header, row = rows
    record = dict(zip(header, row))
    assert record["ФИО"] == "Иван Петров"
    assert record["Компания"] == "ООО «Ромашка»"
    assert record["Тип"] == "Сотрудничество"
    assert record["Статус"] == "Новое"
    # защита от CSV-инъекций: формулы из формы не исполняются в Excel
    assert record["Сообщение"].startswith("'=")
    assert record["Телефон"] == "'+996 555 000 000"
