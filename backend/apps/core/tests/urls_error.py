"""URLconf для теста логирования ошибок 500."""
from django.urls import path


def boom(request):
    raise RuntimeError("тестовая ошибка 500")


urlpatterns = [path("boom/", boom)]
