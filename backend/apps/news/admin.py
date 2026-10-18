from django.contrib import admin

from apps.core.admin import (
    SEO_FIELDSET,
    AttachmentInline,
    GalleryInline,
    TranslationAdminBase,
    image_preview,
)
from apps.core.i18n import LANGS

from .models import Event, News, NewsCategory

TITLE_SEARCH = [f"title_{lang}" for lang in LANGS]


@admin.register(NewsCategory)
class NewsCategoryAdmin(TranslationAdminBase):
    list_display = ("name", "order", "updated_at")
    search_fields = [f"name_{lang}" for lang in LANGS]
    ordering = ("order", "id")
    fields = ("name", "slug", "order")


@admin.register(News)
class NewsAdmin(TranslationAdminBase):
    list_display = ("title", "category", "status", "published_at", "preview")
    list_filter = ("status", "category", "published_at")
    list_select_related = ("category",)
    search_fields = TITLE_SEARCH
    date_hierarchy = "published_at"
    ordering = ("-published_at", "-id")
    inlines = (GalleryInline, AttachmentInline)
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "category", "status", "published_at", "cover"),
            "description": "Дата публикации в будущем — новость появится на сайте только в этот момент.",
        }),
        ("Содержимое", {"fields": ("excerpt", "content")}),
        SEO_FIELDSET,
    )

    @admin.display(description="обложка")
    def preview(self, obj):
        return image_preview(obj.cover, height=40)


@admin.register(Event)
class EventAdmin(TranslationAdminBase):
    list_display = ("title", "type", "status", "start_at", "end_at", "location")
    list_filter = ("status", "type", "start_at")
    search_fields = TITLE_SEARCH
    date_hierarchy = "start_at"
    ordering = ("-start_at", "-id")
    inlines = (GalleryInline, AttachmentInline)
    fieldsets = (
        (None, {"fields": ("title", "slug", "type", "status", "start_at", "end_at", "location", "cover")}),
        ("Содержимое", {"fields": ("excerpt", "content")}),
        SEO_FIELDSET,
    )
