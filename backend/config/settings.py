"""
Настройки проекта. Все секреты и параметры окружения — из .env (django-environ).
См. SPEC.md, раздел 5.4.
"""
from datetime import timedelta
from pathlib import Path

import re

import environ
from django.conf.locale import LANG_INFO
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:3000"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
    ADMIN_URL=(str, "admin/"),
    FRONTEND_URL=(str, "http://localhost:3000"),
    FRAME_ANCESTORS=(str, ""),
    BACKEND_URL=(str, "http://localhost:8000"),
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
# Кому можно встраивать PDF презентаций во фрейм (CSP frame-ancestors, apps/core/media.py):
# origins через запятую, допускается маска поддомена (https://*.vercel.app). Пусто — FRONTEND_URL.
FRAME_ANCESTORS = [
    origin.strip().rstrip("/") for origin in env("FRAME_ANCESTORS").split(",") if origin.strip()
] or [FRONTEND_URL]
for _origin in FRAME_ANCESTORS:
    if not re.fullmatch(r"https?://(\*\.)?[A-Za-z0-9.-]+(:\d+)?", _origin):
        raise ImproperlyConfigured(
            f"FRAME_ANCESTORS: «{_origin}» — нужен origin вида https://site.kg или https://*.vercel.app"
        )
# Публичный адрес бэкенда — для ссылок на админку в письмах.
BACKEND_URL = env("BACKEND_URL").rstrip("/")
# Сколько обратных прокси перед Django (dev — 0, прод за nginx — 1). От этого зависит,
# какой адрес из X-Forwarded-For считается IP клиента (throttling, axes, Feedback.ip).
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
    "axes",
    # проект
    "apps.core",
    "apps.pages",
    "apps.news",
    "apps.cooperation",
    "apps.feedback",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # снаружи остальных: заголовок получают и ответы, созданные middleware (блокировка axes)
    "apps.core.middleware.AdminNoIndexMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # axes — последним (документация django-axes)
    "axes.middleware.AxesMiddleware",
]

AUTHENTICATION_BACKENDS = [
    # axes первым: блокирует вход до проверки пароля
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# Кэш по умолчанию — общий для всех воркеров (throttling): в БД, а не LocMemCache.
# Таблица создаётся командой: python manage.py createcachetable
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
    },
    # imagekit кэширует лишь «превью уже сгенерировано» — это оптимизация, общей ей быть
    # не нужно. В DatabaseCache она стоила бы несколько SQL-запросов на каждую картинку.
    "imagekit": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "imagekit",
    },
}
IMAGEKIT_CACHE_BACKEND = "imagekit"

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
# API и файлы презентаций (их PDF фронт может читать через pdf.js). На проде media
# отдаёт nginx — те же заголовки для /media/presentations/ описаны в docs/DEPLOY.md.
CORS_URLS_REGEX = r"^/(api|media/presentations)/.*$"

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
    # Rate limit на POST /feedback/ (SPEC.md, 5.2). IP клиента — с учётом NUM_PROXIES.
    "DEFAULT_THROTTLE_RATES": {"feedback": "5/hour"},
    "NUM_PROXIES": NUM_PROXIES,
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

# --- django-axes: защита входа в админку (SPEC.md, 5.2) ------------------------
# 5 неудачных входов по связке username + IP → блокировка на 30 минут.

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_RESET_ON_SUCCESS = True
AXES_CLIENT_IP_CALLABLE = "apps.core.net.get_client_ip"  # та же логика, что у DRF throttling
AXES_LOCKOUT_TEMPLATE = "axes_lockout.html"

# --- Логирование: logs/app.log (ротация 5 МБ × 5) + консоль ----------------------
# Ошибки 500 (django.request), неудачные входы и блокировки (axes, apps.core.security),
# ошибки отправки почты (apps.feedback).

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "app.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            # файл открывается при первой записи: на Windows автоперезагрузчик runserver
            # иначе держит его открытым во втором процессе и мешает ротации
            "delay": True,
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": [], "level": "WARNING", "propagate": True},
        # только 5xx; 404 и прочие 4xx — не ошибки сервера
        "django.request": {"level": "ERROR", "propagate": True},
        # журнал запросов runserver — только в консоль, как у Django по умолчанию
        "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "axes": {"level": "WARNING", "propagate": True},
        "apps": {"level": "INFO", "propagate": True},
    },
}

# --- Безопасность в проде (DEBUG=False) ---------------------------------------

SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

if not DEBUG:
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # nginx завершает HTTPS и передаёт схему в X-Forwarded-Proto
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
