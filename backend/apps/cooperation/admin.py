from django.contrib import admin

from apps.core.admin import (
    SEO_FIELDSET,
    AttachmentInline,
    GalleryInline,
    TranslationAdminBase,
    image_preview,
)
from apps.core.i18n import LANGS

from .models import Country, Partner, Project

NAME_SEARCH = [f"name_{lang}" for lang in LANGS]


@admin.register(Country)
class CountryAdmin(TranslationAdminBase):
    list_display = ("name", "code", "is_active", "order", "preview")
    list_filter = ("is_active",)
    search_fields = [*NAME_SEARCH, "code"]
    ordering = ("order", "id")
    fields = ("name", "code", "flag", "description", "is_active", "order")

    @admin.display(description="флаг")
    def preview(self, obj):
        return image_preview(obj.flag, height=24)


@admin.register(Partner)
class PartnerAdmin(TranslationAdminBase):
    list_display = ("name", "country", "consent_to_publish", "order", "preview")
    list_filter = ("consent_to_publish", "country")
    list_select_related = ("country",)
    search_fields = NAME_SEARCH
    ordering = ("order", "id")
    fields = ("name", "country", "logo", "website", "description", "consent_to_publish", "order")

    @admin.display(description="логотип")
    def preview(self, obj):
        return image_preview(obj.logo, height=30)


@admin.register(Project)
class ProjectAdmin(TranslationAdminBase):
    list_display = ("title", "country", "status", "published_at")
    list_filter = ("status", "country", "published_at")
    list_select_related = ("country",)
    search_fields = [f"title_{lang}" for lang in LANGS]
    date_hierarchy = "published_at"
    ordering = ("-published_at", "-id")
    filter_horizontal = ("partners",)
    inlines = (GalleryInline, AttachmentInline)
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "country", "partners", "status", "published_at", "cover"),
            "description": "Дата публикации в будущем — проект появится на сайте только в этот момент.",
        }),
        ("Содержимое", {"fields": ("excerpt", "content")}),
        SEO_FIELDSET,
    )
