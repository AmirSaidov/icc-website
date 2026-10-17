"""
Настройки проекта. Все секреты и параметры окружения — из .env (django-environ).
См. SPEC.md, раздел 5.4.
"""
from pathlib import Path

import environ
from django.conf.locale import LANG_INFO

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:3000"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
    ADMIN_URL=(str, "admin/"),
    FRONTEND_URL=(str, "http://localhost:3000"),
    NUM_PROXIES=(int, 0),
    EMAIL_HOST=(str, ""),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    EMAIL_USE_TLS=(bool, True),
    DEFAULT_FROM_EMAIL=(str, "noreply@example.kg"),
    FEEDBACK_EMAIL=(str, ""),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

ADMIN_URL = env("ADMIN_URL")
FRONTEND_URL = env("FRONTEND_URL").rstrip("/")
NUM_PROXIES = env("NUM_PROXIES")

# --- Приложения ---------------------------------------------------------------

INSTALLED_APPS = [
    # modeltranslation должен стоять раньше django.contrib.admin
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # сторонние
    "corsheaders",
    "imagekit",
    "rest_framework",
    "drf_spectacular",
    "django_ckeditor_5",
    # проект
    "apps.core",
    "apps.pages",
    "apps.news",
    "apps.cooperation",
    "apps.feedback",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- База данных --------------------------------------------------------------
# Только переносимые возможности ORM: переезд на PostgreSQL = смена DATABASES.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "init_command": "PRAGMA journal_mode=WAL;",
            "transaction_mode": "IMMEDIATE",
        },
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Пароли -------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Язык и время -------------------------------------------------------------

LANGUAGE_CODE = "ru"
LANGUAGES = [
    ("ru", "Русский"),
    ("en", "English"),
    ("zh", "中文"),
]
# Django знает только zh-hans / zh-hant, а по ТЗ код языка — "zh" (поля *_zh, ?lang=zh).
# Без этой записи админка modeltranslation падает с "Unknown language code zh".
LANG_INFO.setdefault(
    "zh",
    {"bidi": False, "code": "zh", "name": "Chinese", "name_local": "中文"},
)

TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True

# django-modeltranslation
MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"
MODELTRANSLATION_LANGUAGES = ("ru", "en", "zh")
# Обязательные поля модели обязательны только в русской версии, en/zh — опциональны.
MODELTRANSLATION_REQUIRED_LANGUAGES = ("ru",)
# Fallback-и выключены: нет перевода — API отдаёт null, а не русский текст.
MODELTRANSLATION_ENABLE_FALLBACKS = False
MODELTRANSLATION_FALLBACK_LANGUAGES = ()
# Вкладки языков в админке: jQuery UI из static/, без CDN.
JQUERY_UI_URL = "vendor/jquery-ui/jquery-ui.min.js"

# --- Статика и медиа ----------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- CORS ---------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")

# --- Почта --------------------------------------------------------------------
# Если EMAIL_HOST пустой — console backend (письма печатаются в консоль).

EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
FEEDBACK_EMAIL = env("FEEDBACK_EMAIL")

if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# --- API (DRF + drf-spectacular) ----------------------------------------------
# Публичный API: только GET без авторизации (POST /feedback/ — этап 4).

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "UNAUTHENTICATED_USER": None,
    "COERCE_DECIMAL_TO_STRING": False,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API сайта ЦПК при ТПП КР",
    "DESCRIPTION": (
        "Публичное API сайта Центра промышленной кооперации. Все эндпоинты — GET без "
        "авторизации. Язык — параметр `?lang=ru|en|zh` (по умолчанию ru). "
        "Подробности для фронтенда — docs/API.md."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "COMPONENT_SPLIT_REQUEST": True,
}

# --- CKEditor 5 (rich text в админке) -----------------------------------------
# Тулбар — только то, что пропускает nh3 (SPEC.md, 2.4). Плагины, дающие другую
# разметку (стили, шрифты, выравнивание, размеры картинок, Markdown, HTML-вставки),
# отключены, чтобы редактор не показывал того, что потом вырежет санитайзер.

CKEDITOR_5_CONFIGS = {
    "default": {
        "language": "ru",
        "removePlugins": [
            "Markdown", "FullPage", "SourceEditing", "GeneralHtmlSupport", "Style", "HtmlEmbed",
            "CodeBlock", "Code", "Subscript", "Superscript", "Font", "Highlight", "Alignment",
            "ImageStyle", "ImageResize", "LinkImage", "MediaEmbed", "PageBreak", "HorizontalLine",
            "Indent", "IndentBlock", "TodoList", "ListProperties", "TableProperties",
            "TableCellProperties", "TableCaption", "Mention", "Autosave",
        ],
        "toolbar": [
            "heading", "|",
            "bold", "italic", "underline", "strikethrough", "|",
            "link", "bulletedList", "numberedList", "blockQuote", "|",
            "insertImage", "insertTable", "|",
            "removeFormat", "undo", "redo",
        ],
        "heading": {
            "options": [
                {"model": "paragraph", "title": "Абзац", "class": "ck-heading_paragraph"},
                {"model": "heading2", "view": "h2", "title": "Заголовок 2", "class": "ck-heading_heading2"},
                {"model": "heading3", "view": "h3", "title": "Заголовок 3", "class": "ck-heading_heading3"},
                {"model": "heading4", "view": "h4", "title": "Заголовок 4", "class": "ck-heading_heading4"},
            ],
        },
        "image": {"toolbar": ["imageTextAlternative", "toggleImageCaption"]},
        # без объединения ячеек: colspan/rowspan nh3 не пропускает
        "table": {"contentToolbar": ["tableColumn", "tableRow"]},
        "link": {"addTargetToExternalLinks": True, "defaultProtocol": "https://"},
    },
}
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"
# Своя вьюха загрузки: та же проверка картинок, что и у ImageField (SPEC.md, 4.1).
CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME = "ckeditor-upload"
CKEDITOR_5_UPLOAD_FILE_TYPES = ["jpeg", "jpg", "png", "webp"]
