# Базовая регистрация (этап 1). Полная настройка админки — этап 3.
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Country, Partner, Project


@admin.register(Country)
class CountryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "code", "is_active", "order")


@admin.register(Partner)
class PartnerAdmin(TabbedTranslationAdmin):
    list_display = ("name", "country", "consent_to_publish", "order")


@admin.register(Project)
class ProjectAdmin(TabbedTranslationAdmin):
    list_display = ("title", "country", "status", "published_at")
