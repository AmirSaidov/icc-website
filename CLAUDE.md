# CLAUDE.md — бэкенд сайта ЦПК при ТПП КР

## Главное
- Единственный источник правды — [SPEC.md](SPEC.md). Работать строго по нему.
- Неясно или противоречиво в ТЗ — **спросить**, не придумывать.
- Эта папка = `backend/` из SPEC.md (manage.py, config/, apps/ лежат прямо здесь).
- Работаем по этапам из раздела 7 SPEC.md, **строго по одному**. Не забегать вперёд.
- После каждого этапа: `check` без ошибок, `makemigrations --check` чист, миграции применяются на чистой базе, тесты зелёные → git commit.

## Запуск (Windows, Python 3.12)
```
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        (затем задать SECRET_KEY)
python manage.py migrate
python manage.py seed            (тестовые данные; --flush — пересоздать)
python manage.py runserver
```
Проверки: `python manage.py check`, `python manage.py makemigrations --check --dry-run`, `pytest`.
Swagger: http://localhost:8000/api/docs/ · документация для фронта: [docs/API.md](docs/API.md).

## Правила проекта
- Только переносимые возможности ORM (SQLite → PostgreSQL сменой `DATABASES`). Без `django.contrib.postgres`.
- Переводимые поля [T] — через modeltranslation (`apps/*/translation.py`), языки `ru/en/zh`, fallback-и выключены.
- Slug: `apps.core.fields.NullableSlugField` (пустой → NULL) + `unique_slug_constraints()` в `Meta.constraints`.
- Rich text `content` санитайзится в `save()` через `apps.core.sanitize`.
- Код языка `zh` дописан в `django.conf.locale.LANG_INFO` в settings — не удалять.
- API: вьюхи наследуют `LangMixin` / `TranslatedListAPIView` / `SlugDetailAPIView` (`apps/core/api.py`);
  переводимые поля в сериализаторах — только `TranslatedField` (читает `<field>_<lang>`, "" → null);
  правило «переведено» — `apps/core/i18n.py`; картинки — `ImageVersionsField`; каждую вьюху описывать `@api_doc`.
- Списки без N+1: `select_related` / `prefetch_related`, тесты через `CaptureQueriesContext`.
- Изменил API → пересобрать документацию: `seed`, `export_api_examples`,
  `spectacular --file docs/openapi.yaml --validate` и закоммитить `docs/` + `apps/core/api_examples/`.
- Админка: переводимые модели — `TranslationAdminBase` (`apps/core/admin.py`: вкладки RU/EN/中文, CKEditor 5
  для `content_*`), SEO — `SEO_FIELDSET`, галерея/документы — `GalleryInline` / `AttachmentInline`.
  Права по ролям — `apps/core/roles.py` (`is_admin_role`). Без django-unfold. Без CDN: jQuery UI лежит в `static/vendor/`.
- Файлы: только `ImageUploadField` / `DocumentUploadField` (`apps/core/fields.py`) — проверка расширения, содержимого, размера.
- Slug: в `save()` моделей со slug вызывать `fill_translated_slugs` (пустой slug_X ← title_X, конфликт → -2, -3).
- Отложенная публикация: публичные выборки — только через `published()` (`apps/core/api.py`).
- Тесты — `apps/<app>/tests/`, данные через `apps/core/tests/factories.py`, без новых зависимостей.
- Секреты только в `.env` (не в git). `db.sqlite3`, `media/`, `logs/` не коммитятся.
- Команды в документации — для Windows (`.venv\Scripts\activate`, `copy`).
