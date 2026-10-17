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
python manage.py runserver
```
Проверки: `python manage.py check`, `python manage.py makemigrations --check --dry-run`, `pytest`.

## Правила проекта
- Только переносимые возможности ORM (SQLite → PostgreSQL сменой `DATABASES`). Без `django.contrib.postgres`.
- Переводимые поля [T] — через modeltranslation (`apps/*/translation.py`), языки `ru/en/zh`, fallback-и выключены.
- Slug: `apps.core.fields.NullableSlugField` (пустой → NULL) + `unique_slug_constraints()` в `Meta.constraints`.
- Rich text `content` санитайзится в `save()` через `apps.core.sanitize`.
- Код языка `zh` дописан в `django.conf.locale.LANG_INFO` в settings — не удалять.
- Секреты только в `.env` (не в git). `db.sqlite3`, `media/`, `logs/` не коммитятся.
- Команды в документации — для Windows (`.venv\Scripts\activate`, `copy`).
