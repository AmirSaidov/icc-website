"""Singleton-записи ContactInfo и SiteSettings (pk=1). SPEC.md, 2.4."""
from django.db import migrations


def create_singletons(apps, schema_editor):
    for model_name in ("ContactInfo", "SiteSettings"):
        model = apps.get_model("core", model_name)
        model.objects.get_or_create(pk=1)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_singletons, migrations.RunPython.noop),
    ]
