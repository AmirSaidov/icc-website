"""
Общая база админки (SPEC.md, раздел 4) и админки моделей apps.core.

- вкладки RU / EN / 中文 (TabbedTranslationAdmin + static/cpk_admin/translation_tabs.js);
- CKEditor 5 для всех content_*;
- свёрнутый fieldset SEO;
- singleton-админки: без добавления и удаления, из списка сразу открывается запись.
"""
from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import redirect
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.html import format_html
from django_ckeditor_5.widgets import CKEditor5Widget
from modeltranslation.admin import TabbedTranslationAdmin, TranslationGenericTabularInline

from .admin_forms import phones_field, socials_field
from .i18n import LANGS
from .models import Attachment, ContactInfo, GalleryImage, SiteSettings

SEO_FIELDSET = (
    "SEO",
    {
        "classes": ("collapse",),
        "fields": ("meta_title", "meta_description", "og_image"),
        "description": "Если пусто: meta title — заголовок, meta description — анонс, "
        "OG-картинка — обложка или картинка по умолчанию из настроек сайта.",
    },
)


class TranslationAdminBase(TabbedTranslationAdmin):
    """Языковые вкладки + CKEditor 5 для rich text полей."""

    rich_text_fields = ("content",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        rich = {f"{field}_{lang}" for field in self.rich_text_fields for lang in LANGS}
        if db_field.name in rich:
            kwargs["widget"] = CKEditor5Widget(config_name="default")
        if isinstance(db_field, models.URLField):
            kwargs.setdefault("assume_scheme", "https")
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    class Media:
        js = ("cpk_admin/translation_tabs.js",)
        css = {"all": ("cpk_admin/admin.css",)}


class GalleryInline(TranslationGenericTabularInline):
    model = GalleryImage
    fields = ("preview", "image", "caption", "order")
    readonly_fields = ("preview",)
    ordering = ("order", "id")
    extra = 1
    verbose_name = "фото"
    verbose_name_plural = "галерея"

    @admin.display(description="превью")
    def preview(self, obj):
        return image_preview(obj.image)


class AttachmentInline(TranslationGenericTabularInline):
    model = Attachment
    fields = ("file", "title", "size_display", "show_in_documents", "order")
    readonly_fields = ("size_display",)
    ordering = ("order", "id")
    extra = 1
    verbose_name = "документ"
    verbose_name_plural = "документы (PDF, DOCX)"

    @admin.display(description="размер")
    def size_display(self, obj):
        return filesizeformat(obj.size) if obj.pk else "—"


def image_preview(field_file, height=60):
    if not field_file:
        return "—"
    return format_html('<img src="{}" style="height:{}px;border-radius:4px">', field_file.url, height)


class SingletonAdminMixin:
    """Ровно одна запись: без «Добавить» и удаления, из списка сразу открывается запись."""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied
        obj = self.model.load()
        opts = self.model._meta
        return redirect(reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[obj.pk]))


class ContactInfoForm(forms.ModelForm):
    phones = phones_field()
    socials = socials_field()

    class Meta:
        model = ContactInfo
        fields = "__all__"


@admin.register(ContactInfo)
class ContactInfoAdmin(SingletonAdminMixin, TranslationAdminBase):
    form = ContactInfoForm
    fieldsets = (
        (None, {"fields": ("official_name", "address", "work_hours", "email")}),
        ("Телефоны", {"fields": ("phones",)}),
        ("Карта", {"fields": ("map_lat", "map_lng")}),
        ("Соцсети", {"fields": ("socials",)}),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fields = ("feedback_emails", "analytics_id", "default_og_image")


@admin.register(GalleryImage)
class GalleryImageAdmin(TranslationAdminBase):
    list_display = ("preview", "caption", "content_type", "object_id", "order", "created_at")
    list_display_links = ("preview", "caption")
    list_filter = ("content_type",)
    search_fields = [f"caption_{lang}" for lang in LANGS]
    ordering = ("-created_at",)
    fields = ("image", "caption", "content_type", "object_id", "order")

    @admin.display(description="превью")
    def preview(self, obj):
        return image_preview(obj.image, height=40)


@admin.register(Attachment)
class AttachmentAdmin(TranslationAdminBase):
    list_display = ("title", "ext", "size_display", "show_in_documents", "content_type", "order")
    list_filter = ("show_in_documents", "content_type")
    search_fields = [f"title_{lang}" for lang in LANGS]
    ordering = ("order", "id")
    fields = ("file", "title", "show_in_documents", "order", "content_type", "object_id", "size_display")
    readonly_fields = ("size_display",)

    @admin.display(description="тип")
    def ext(self, obj):
        return obj.file.name.rsplit(".", 1)[-1].upper() if obj.file else "—"

    @admin.display(description="размер")
    def size_display(self, obj):
        return filesizeformat(obj.size) if obj.pk else "—"
