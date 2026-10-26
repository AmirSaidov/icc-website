from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.admin_views import ckeditor_upload
from apps.core.media import media_urlpatterns
from apps.core.sitemap import robots_txt, sitemap_xml

admin.site.site_header = "ЦПК при ТПП КР — управление сайтом"
admin.site.site_title = "ЦПК при ТПП КР"
admin.site.index_title = "Управление сайтом"

api_v1 = [
    path("", include("apps.pages.urls")),
    path("", include("apps.news.urls")),
    path("", include("apps.cooperation.urls")),
    path("", include("apps.core.urls")),
    path("", include("apps.feedback.urls")),
]

urlpatterns = [
    # до admin.site.urls, иначе адрес перехватит админка
    path(f"{settings.ADMIN_URL}ckeditor/upload/", ckeditor_upload, name="ckeditor-upload"),
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/", include(api_v1)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("sitemap.xml", sitemap_xml, name="sitemap"),
    path("robots.txt", robots_txt, name="robots"),
]

if settings.DEBUG:
    # media в dev; файлам презентаций — frame-ancestors вместо DENY (apps/core/media.py)
    urlpatterns += media_urlpatterns()
