"""
Раздача media в dev (DEBUG=True). На проде media отдаёт nginx с теми же заголовками —
docs/DEPLOY.md, раздел 5.

Файлы презентаций (media/presentations/) фронт встраивает в свою страницу (iframe или pdf.js),
поэтому для них — и только для них — вместо X-Frame-Options: DENY отдаётся
Content-Security-Policy: frame-ancestors 'self' <FRONTEND_URL>. PDF — Content-Disposition: inline
(просмотр), PPTX — attachment (скачивание). Админка и всё остальное — по-прежнему DENY.
"""
import re
from pathlib import PurePosixPath

from django.conf import settings
from django.urls import re_path
from django.utils.http import content_disposition_header
from django.views.static import serve

from apps.cooperation.models import PRESENTATION_FILES_DIR


def is_presentation_file(path):
    """path — относительно MEDIA_ROOT, как в URL после /media/."""
    return path.startswith(f"{PRESENTATION_FILES_DIR}/")


def presentation_frame_ancestors():
    return f"frame-ancestors 'self' {settings.FRONTEND_URL}"


def add_presentation_headers(response, path):
    response["Content-Security-Policy"] = presentation_frame_ancestors()
    response.xframe_options_exempt = True  # XFrameOptionsMiddleware не поставит DENY
    filename = PurePosixPath(path).name
    as_attachment = not filename.lower().endswith(".pdf")
    response["Content-Disposition"] = content_disposition_header(as_attachment, filename)
    return response


def serve_media(request, path):
    response = serve(request, path, document_root=settings.MEDIA_ROOT)
    if is_presentation_file(path):
        add_presentation_headers(response, path)
    return response


def media_urlpatterns():
    prefix = re.escape(settings.MEDIA_URL.lstrip("/"))
    return [re_path(rf"^{prefix}(?P<path>.*)$", serve_media, name="media")]
