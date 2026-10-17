# Базовая регистрация (этап 1). Полная настройка админки — этап 3.
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Event, News, NewsCategory


@admin.register(NewsCategory)
class NewsCategoryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "order")


@admin.register(News)
class NewsAdmin(TabbedTranslationAdmin):
    list_display = ("title", "category", "status", "published_at")


@admin.register(Event)
class EventAdmin(TabbedTranslationAdmin):
    list_display = ("title", "type", "status", "start_at", "end_at")
