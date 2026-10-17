"""ContactInfo.phones: {"label", "number"} → {"label_ru", "label_en", "label_zh", "number"}."""
from django.db import migrations

LANGS = ("ru", "en", "zh")


def to_trilingual(apps, schema_editor):
    ContactInfo = apps.get_model("core", "ContactInfo")
    for contacts in ContactInfo.objects.all():
        phones = []
        for item in contacts.phones or []:
            if "label" in item:
                item = {"label_ru": item.get("label") or "", "label_en": "", "label_zh": "", "number": item.get("number", "")}
            phones.append(item)
        contacts.phones = phones
        contacts.save(update_fields=["phones"])


def to_single_label(apps, schema_editor):
    ContactInfo = apps.get_model("core", "ContactInfo")
    for contacts in ContactInfo.objects.all():
        contacts.phones = [
            {"label": item.get("label_ru", item.get("label", "")), "number": item.get("number", "")}
            for item in contacts.phones or []
        ]
        contacts.save(update_fields=["phones"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_upload_validation_and_slug_help"),
    ]

    operations = [
        migrations.RunPython(to_trilingual, to_single_label),
    ]
