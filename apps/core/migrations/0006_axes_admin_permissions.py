"""
Группе «Администратор» — журналы входа django-axes: просмотр, а у блокировок (AccessAttempt)
ещё и удаление — так из админки снимается блокировка входа. Редактор их не видит.
"""
from django.db import migrations

PERMISSIONS = {
    "accessattempt": ("view", "delete"),
    "accesslog": ("view",),
    "accessfailurelog": ("view",),
}


def grant(apps, schema_editor):
    from django.contrib.auth.management import create_permissions

    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    group = Group.objects.get(name="Администратор")
    for model, actions in PERMISSIONS.items():
        for action in actions:
            group.permissions.add(
                Permission.objects.get(content_type__app_label="axes", codename=f"{action}_{model}")
            )


def revoke(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    group = Group.objects.filter(name="Администратор").first()
    if group:
        group.permissions.remove(*Permission.objects.filter(content_type__app_label="axes"))


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_phones_trilingual_labels"),
        ("axes", "0010_accessattemptexpiration"),
    ]

    operations = [
        migrations.RunPython(grant, revoke),
    ]
