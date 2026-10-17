# Базовая регистрация (этап 1). Полная настройка админки — этап 3.
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Attachment, ContactInfo, GalleryImage, SiteSettings


class SingletonAdminMixin:
    """Singleton: запись создаётся миграцией — без добавления и удаления."""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactInfo)
class ContactInfoAdmin(SingletonAdminMixin, TabbedTranslationAdmin):
    pass


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    pass


@admin.register(GalleryImage)
class GalleryImageAdmin(TabbedTranslationAdmin):
    list_display = ("__str__", "content_type", "object_id", "order")


@admin.register(Attachment)
class AttachmentAdmin(TabbedTranslationAdmin):
    list_display = ("title", "size", "show_in_documents", "order")
