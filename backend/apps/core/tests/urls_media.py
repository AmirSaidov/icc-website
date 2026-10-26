"""Маршруты проекта + раздача media, как при DEBUG=True (тесты идут с DEBUG=False)."""
from apps.core.media import media_urlpatterns
from config.urls import urlpatterns as project_urlpatterns

urlpatterns = [*project_urlpatterns, *media_urlpatterns()]
