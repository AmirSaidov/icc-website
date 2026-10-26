"""Группам «Администратор» и «Редактор» — полный доступ к сферам и презентациям (SPEC.md, 4.2)."""
from django.db import migrations

ALL = ("add", "change", "delete", "view")
MODELS = ("sector", "presentation")
GROUPS = ("Администратор", "Редактор")


def grant(apps, schema_editor):
    # Права Django создаются сигналом post_migrate, т. е. после всех миграций — создаём явно.
    from django.contrib.auth.management import create_permissions

    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    permissions = [
        Permission.objects.get(content_type__app_label="cooperation", codename=f"{action}_{model}")
        for model in MODELS
        for action in ALL
    ]
    for group in Group.objects.filter(name__in=GROUPS):
        group.permissions.add(*permissions)


def revoke(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    permissions = Permission.objects.filter(
        content_type__app_label="cooperation",
        codename__in=[f"{action}_{model}" for model in MODELS for action in ALL],
    )
    for group in Group.objects.filter(name__in=GROUPS):
        group.permissions.remove(*permissions)


class Migration(migrations.Migration):
    dependencies = [
        ("cooperation", "0004_default_sectors"),
        ("core", "0003_roles"),
    ]

    operations = [
        migrations.RunPython(grant, revoke),
    ]
