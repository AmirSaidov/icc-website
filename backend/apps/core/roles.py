"""Роли сотрудников (SPEC.md, 4.2). Группы создаются миграцией core/0003_roles."""

ADMIN_GROUP = "Администратор"
EDITOR_GROUP = "Редактор"


def is_admin_role(user):
    """Суперпользователь или член группы «Администратор». Всё остальное — права Редактора."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name=ADMIN_GROUP).exists()
