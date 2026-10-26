from django.contrib import admin
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.html import format_html

from apps.core.admin import (
    SEO_FIELDSET,
    AttachmentInline,
    GalleryInline,
    TranslationAdminBase,
    image_preview,
)
from apps.core.i18n import LANGS

from .models import Country, Partner, Presentation, Project, Sector

NAME_SEARCH = [f"name_{lang}" for lang in LANGS]
TITLE_SEARCH = [f"title_{lang}" for lang in LANGS]


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


class ProjectPresentationInline(admin.TabularInline):
    """Презентации проекта — только список со ссылками; правятся в разделе «Презентации»."""

    model = Presentation
    fk_name = "project"
    fields = ("edit_link", "sector", "status", "published_at", "order")
    readonly_fields = fields
    ordering = ("order", "-published_at", "-id")
    extra = 0
    can_delete = False
    verbose_name = "презентация"
    verbose_name_plural = "презентации проекта (только просмотр — правка по ссылке)"

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="презентация")
    def edit_link(self, obj):
        url = reverse("admin:cooperation_presentation_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj)


@admin.register(Project)
class ProjectAdmin(TranslationAdminBase):
    list_display = ("title", "country", "status", "published_at")
    list_filter = ("status", "country", "published_at")
    list_select_related = ("country",)
    search_fields = TITLE_SEARCH
    date_hierarchy = "published_at"
    ordering = ("-published_at", "-id")
    filter_horizontal = ("partners",)
    inlines = (GalleryInline, AttachmentInline, ProjectPresentationInline)
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "country", "partners", "status", "published_at", "cover"),
            "description": "Дата публикации в будущем — проект появится на сайте только в этот момент.",
        }),
        ("Содержимое", {"fields": ("excerpt", "content")}),
        SEO_FIELDSET,
    )


@admin.register(Sector)
class SectorAdmin(TranslationAdminBase):
    list_display = ("name", "order", "updated_at")
    search_fields = NAME_SEARCH
    ordering = ("order", "id")
    fields = ("name", "slug", "order")


@admin.register(Presentation)
class PresentationAdmin(TranslationAdminBase):
    rich_text_fields = ("description",)
    list_display = ("title", "sector", "project", "country", "status", "published_at", "file_info")
    list_filter = ("status", "sector", "project", "country", "published_at")
    list_select_related = ("sector", "project", "country")
    search_fields = TITLE_SEARCH
    date_hierarchy = "published_at"
    ordering = ("-published_at", "-id")
    readonly_fields = ("file_info",)
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "sector", "project", "country", "status", "published_at", "order"),
            "description": "Дата публикации в будущем — презентация появится на сайте только в этот момент.",
        }),
        ("Файлы", {
            "fields": ("file", "file_info", "source_file", "cover"),
            "description": "PDF обязателен: именно он показывается на сайте (браузер открывает PDF сам, "
            "PowerPoint — нет). PPTX — по желанию, только для скачивания. Каждый файл — до 50 МБ.",
        }),
        ("Описание", {"fields": ("description",)}),
        SEO_FIELDSET,
    )

    @admin.display(description="файлы")
    def file_info(self, obj):
        if not obj.pk or not obj.file:
            return "—"
        pages = f", {obj.pages} стр." if obj.pages else ""
        info = f"PDF: {filesizeformat(obj.size)}{pages}"
        if obj.source_file:
            info += f"; PPTX: {filesizeformat(obj.source_size or 0)}"
        return info
