"""Системные страницы home / about / cooperation. SPEC.md, 2.3–2.4."""
from django.db import migrations

SYSTEM_PAGES = [
    # key, title_ru, order
    ("home", "Главная", 0),
    ("about", "О Центре", 1),
    ("cooperation", "Сотрудничество", 2),
]


def create_system_pages(apps, schema_editor):
    Page = apps.get_model("pages", "Page")
    for key, title_ru, order in SYSTEM_PAGES:
        Page.objects.get_or_create(
            key=key,
            defaults={"title": title_ru, "title_ru": title_ru, "order": order},
        )


def delete_system_pages(apps, schema_editor):
    Page = apps.get_model("pages", "Page")
    Page.objects.filter(key__in=[key for key, _, _ in SYSTEM_PAGES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_system_pages, delete_system_pages),
    ]
