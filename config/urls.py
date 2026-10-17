from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

admin.site.site_header = "ЦПК при ТПП КР — администрирование"
admin.site.site_title = "ЦПК — админка"
admin.site.index_title = "Управление сайтом"

api_v1 = [
    path("", include("apps.pages.urls")),
    path("", include("apps.news.urls")),
    path("", include("apps.cooperation.urls")),
    path("", include("apps.core.urls")),
]

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/", include(api_v1)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
