"""
Обращения из форм (SPEC.md, 4.1–4.2).

- добавлять через админку нельзя никому — обращения приходят только из формы на сайте;
- Администратор: полный доступ; Редактор: меняет только status и admin_note, удалять не может
  (стандартных прав Django для этого недостаточно — get_readonly_fields / has_delete_permission);
- смена статуса прямо в списке, экспорт в CSV (UTF-8 с BOM для Excel).
"""
import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone

from apps.core.roles import is_admin_role

from .models import Feedback

EDITOR_EDITABLE_FIELDS = ("status", "admin_note")
ALWAYS_READONLY = ("created_at", "ip")

CSV_COLUMNS = [
    ("id", "ID"),
    ("created_at", "Дата"),
    ("type", "Тип"),
    ("status", "Статус"),
    ("full_name", "ФИО"),
    ("company", "Компания"),
    ("country", "Страна"),
    ("email", "Email"),
    ("phone", "Телефон"),
    ("subject", "Тема"),
    ("message", "Сообщение"),
    ("consent", "Согласие"),
    ("lang", "Язык"),
    ("ip", "IP"),
    ("admin_note", "Комментарий"),
]


def csv_cell(feedback, field):
    if field == "created_at":
        value = timezone.localtime(feedback.created_at).strftime("%d.%m.%Y %H:%M")
    elif field in ("type", "status", "lang"):
        value = getattr(feedback, f"get_{field}_display")()
    elif field == "consent":
        value = "да" if feedback.consent else "нет"
    else:
        value = getattr(feedback, field)
    value = "" if value is None else str(value)
    # Защита от CSV-инъекций: данные приходят из публичной формы, а Excel
    # исполняет ячейки, начинающиеся с = + - @, как формулы.
    if value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        value = "'" + value
    return value


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("subject", "type", "full_name", "company", "email", "created_at", "status")
    list_display_links = ("subject",)
    list_editable = ("status",)
    list_filter = ("status", "type", "created_at")
    date_hierarchy = "created_at"
    search_fields = ("subject", "full_name", "company", "email", "message")
    ordering = ("-created_at", "-id")
    actions = ("export_csv",)
    fieldsets = (
        ("Обращение", {
            "fields": ("type", "full_name", "company", "country", "email", "phone", "subject", "message"),
        }),
        ("Обработка", {"fields": ("status", "admin_note")}),
        ("Служебное", {"fields": ("consent", "lang", "ip", "created_at")}),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return is_admin_role(request.user) and super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if is_admin_role(request.user):
            return ALWAYS_READONLY
        return [f.name for f in self.model._meta.fields if f.name not in EDITOR_EDITABLE_FIELDS]

    @admin.action(description="Экспорт в CSV", permissions=["view"])
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        filename = f"obrashcheniya-{timezone.localdate():%Y-%m-%d}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        # BOM — чтобы Excel распознал UTF-8; «;» — разделитель, который ждёт русский Excel.
        response.write("﻿")
        writer = csv.writer(response, delimiter=";")
        writer.writerow([title for _, title in CSV_COLUMNS])
        for feedback in queryset.order_by("-created_at", "-id"):
            writer.writerow([csv_cell(feedback, field) for field, _ in CSV_COLUMNS])
        return response
