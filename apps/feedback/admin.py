# Базовая регистрация (этап 1). Полная настройка админки и ограничения для Редактора — этап 3.
from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("subject", "type", "full_name", "email", "status", "created_at")
