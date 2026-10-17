"""
Группы «Администратор» и «Редактор» с правами по таблице 4.2 SPEC.md.

Ограничения Редактора по обращениям (менять только status и admin_note,
не удалять) делаются в админке через get_readonly_fields / has_delete_permission
(этап 3) — стандартных прав Django для этого недостаточно.
"""
from django.db import migrations

ALL = ("add", "change", "delete", "view")

CONTENT_PERMISSIONS = {
    ("pages", "page"): ALL,
    ("pages", "homeblock"): ALL,
    ("pages", "direction"): ALL,
    ("pages", "service"): ALL,
    ("news", "newscategory"): ALL,
    ("news", "news"): ALL,
    ("news", "event"): ALL,
    ("cooperation", "country"): ALL,
    ("cooperation", "partner"): ALL,
    ("cooperation", "project"): ALL,
    ("core", "galleryimage"): ALL,
    ("core", "attachment"): ALL,
}

ROLES = {
    "Администратор": {
        **CONTENT_PERMISSIONS,
        ("feedback", "feedback"): ALL,
        # singleton: добавлять и удалять нельзя
        ("core", "contactinfo"): ("change", "view"),
        ("core", "sitesettings"): ("change", "view"),
        ("auth", "user"): ALL,
        ("auth", "group"): ALL,
    },
    "Редактор": {
        **CONTENT_PERMISSIONS,
        ("feedback", "feedback"): ("change", "view"),
    },
}


def create_roles(apps, schema_editor):
    # Права Django создаются сигналом post_migrate, т. е. ПОСЛЕ всех миграций.
    # На чистой базе их ещё нет — создаём явно.
    from django.contrib.auth.management import create_permissions

    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    for group_name, model_perms in ROLES.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        permissions = []
        for (app_label, model), actions in model_perms.items():
            for action in actions:
                permissions.append(
                    Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=f"{action}_{model}",
                    )
                )
        group.permissions.set(permissions)


def delete_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=ROLES.keys()).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("core", "0002_singletons"),
        ("pages", "0002_system_pages"),
        ("news", "0001_initial"),
        ("cooperation", "0001_initial"),
        ("feedback", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_roles, delete_roles),
    ]
