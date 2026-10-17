import mimetypes

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Общее"

    def ready(self):
        # Python 3.12 на Windows не знает .webp → runserver отдаёт превью как
        # application/octet-stream, и браузер с nosniff может их не показать.
        mimetypes.add_type("image/webp", ".webp")
