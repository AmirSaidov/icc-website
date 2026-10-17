# Базовая регистрация (этап 1). Полная настройка админки — этап 3.
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Direction, HomeBlock, Page, Service


@admin.register(Page)
class PageAdmin(TabbedTranslationAdmin):
    list_display = ("title", "key", "status", "show_in_menu", "order")

    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        # key системной страницы менять нельзя
        if obj is not None and obj.is_system:
            readonly = (*readonly, "key")
        return readonly

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(HomeBlock)
class HomeBlockAdmin(TabbedTranslationAdmin):
    list_display = ("title", "type", "status", "order")


@admin.register(Direction)
class DirectionAdmin(TabbedTranslationAdmin):
    list_display = ("title", "status", "order")


@admin.register(Service)
class ServiceAdmin(TabbedTranslationAdmin):
    list_display = ("title", "status", "order")
