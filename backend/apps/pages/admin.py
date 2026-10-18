from django.contrib import admin

from apps.core.admin import SEO_FIELDSET, TranslationAdminBase, image_preview
from apps.core.i18n import LANGS

from .models import Direction, HomeBlock, Page, Service

TITLE_SEARCH = [f"title_{lang}" for lang in LANGS]


@admin.register(Page)
class PageAdmin(TranslationAdminBase):
    list_display = ("title", "key", "status", "show_in_menu", "order", "updated_at")
    list_filter = ("status", "show_in_menu")
    search_fields = TITLE_SEARCH
    ordering = ("order", "id")
    # key есть только у системных страниц (создаются миграцией) — всегда только для чтения
    readonly_fields = ("key",)
    fieldsets = (
        (None, {"fields": ("title", "slug", "key", "status", "show_in_menu", "order")}),
        ("Содержимое", {"fields": ("content",)}),
        SEO_FIELDSET,
    )

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def get_deleted_objects(self, objs, request):
        # массовое удаление: системные страницы удалить нельзя
        deleted, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        protected += [str(obj) for obj in objs if obj.is_system]
        return deleted, model_count, perms_needed, protected


@admin.register(HomeBlock)
class HomeBlockAdmin(TranslationAdminBase):
    list_display = ("title", "type", "status", "order", "preview")
    list_filter = ("status", "type")
    search_fields = TITLE_SEARCH
    ordering = ("order", "id")
    fields = ("type", "title", "text", "image", "button_text", "button_link", "order", "status")

    @admin.display(description="картинка")
    def preview(self, obj):
        return image_preview(obj.image, height=40)


@admin.register(Direction)
class DirectionAdmin(TranslationAdminBase):
    list_display = ("title", "icon", "status", "order", "updated_at")
    list_filter = ("status", "icon")
    search_fields = TITLE_SEARCH
    ordering = ("order", "id")
    fieldsets = (
        (None, {"fields": ("title", "slug", "icon", "status", "order")}),
        ("Содержимое", {"fields": ("short_text", "content")}),
        SEO_FIELDSET,
    )


@admin.register(Service)
class ServiceAdmin(TranslationAdminBase):
    list_display = ("title", "status", "order", "updated_at")
    list_filter = ("status",)
    search_fields = TITLE_SEARCH
    ordering = ("order", "id")
    fieldsets = (
        (None, {"fields": ("title", "slug", "status", "order")}),
        ("Содержимое", {"fields": ("short_text", "content", "how_to_apply")}),
        ("Контакты", {"fields": ("contact_person", "contact_email", "contact_phone")}),
        SEO_FIELDSET,
    )
