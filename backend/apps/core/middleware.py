"""Заголовки ответов, которые зависят от пути запроса."""
from django.conf import settings


def is_admin_path(path):
    prefix = "/" + settings.ADMIN_URL.strip("/")
    return path == prefix or path.startswith(prefix + "/")


class AdminNoIndexMiddleware:
    """
    Все ответы админки (весь путь ADMIN_URL, включая страницу входа и блокировку axes) —
    с X-Robots-Tag: noindex, nofollow. В robots.txt путь админки не пишем, чтобы не
    раскрывать нестандартный адрес (SPEC.md, 5.3).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if is_admin_path(request.path):
            response["X-Robots-Tag"] = "noindex, nofollow"
        return response
