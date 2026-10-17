# SPEC — Backend сайта ЦПК при ТПП КР

> Этот документ — единственный источник правды для бэкенда. Работай строго по нему.
> Если что-то здесь не описано или противоречит само себе — **не придумывай, а спроси**.
> Основа — общее ТЗ сайта Центра промышленной кооперации при Торгово-промышленной палате КР.

---

## 1. Общее

**Цель MVP:** API на трёх языках (ru / en / zh), админка с двумя ролями, приём обращений из форм.

| Параметр | Значение |
|---|---|
| Потребители API | Фронтенд на Next.js (Амир, Ариет) |
| Язык и фреймворк | Python 3.12, Django 5.2 LTS, Django REST Framework |
| База данных | SQLite (`db.sqlite3`). Только переносимые возможности ORM — переезд на PostgreSQL должен быть сменой `DATABASES` + `dumpdata/loaddata` |
| Переводы моделей | `django-modeltranslation` (ru / en / zh) |
| Админка | Django Admin по пути из `ADMIN_URL`, интерфейс на русском |
| Документация API | `drf-spectacular` → Swagger на `/api/docs/`, схема на `/api/schema/` |
| Часовой пояс | `Asia/Bishkek`, `USE_TZ=True` |
| Запуск | Без Docker, `python manage.py runserver` |
| Репозиторий | `icc-website`, папка `backend/` |

**Не входит в работу:** личные кабинеты, реестр компаний, CRM, ИИ-ассистент, автоподбор партнёров, интеграции с госсистемами, онлайн-оплата, автоперевод, согласование публикаций руководителем (поле статуса под это закладываем, но сам процесс согласования не делаем).

### Зависимости (актуальные стабильные версии, зафиксировать в `requirements.txt`)

`Django>=5.2,<5.3`, `djangorestframework`, `drf-spectacular`, `django-modeltranslation`, `django-cors-headers`, `django-environ`, `Pillow`, `django-imagekit`, `nh3` (санитайзинг HTML — **не bleach**, он deprecated), `django-ckeditor-5` (**не** старый `django-ckeditor` 4 — у него известные уязвимости), `django-axes`, `python-slugify`, `pypinyin`, `pytest`, `pytest-django`.

Опционально: `django-unfold` (тема админки) — подключать, **только если языковые вкладки modeltranslation в ней работают**. Вкладки важнее красоты.

### Структура проекта

```
backend/
  manage.py
  requirements.txt
  .env.example
  .gitignore            # db.sqlite3, media/, .env, __pycache__, .venv
  README.md
  pytest.ini
  config/               # settings.py, urls.py, wsgi.py, asgi.py
  apps/
    core/               # миксины, ContactInfo, SiteSettings, GalleryImage, Attachment,
                        # утилиты: язык, slug, санитайзинг, валидаторы файлов, sitemap, robots
    pages/              # Page, HomeBlock, Direction, Service
    news/               # NewsCategory, News, Event
    cooperation/        # Country, Partner, Project
    feedback/           # Feedback
  media/                # не в git
```

---

## 2. Модели данных

### 2.1 Общие правила

- **[T]** — переводимое поле, хранится в трёх версиях: `_ru`, `_en`, `_zh` (через modeltranslation).
- **Slug** — свой для каждого языка (`slug_ru`, `slug_en`, `slug_zh`). Уникален в пределах языка. Пустой slug хранится как `NULL`, а не пустая строка, чтобы уникальность не ломалась на незаполненных переводах.
- **Fallback-языки modeltranslation отключены** (`MODELTRANSLATION_ENABLE_FALLBACKS = False`). Если перевода нет — API должен честно отдать `null`, а не подставить русский текст.
- **«Запись переведена на язык X»** = заполнены `title_X` (или `name_X`) и, если у модели есть slug, `slug_X`.
- **Исключение — системные страницы** (Page с непустым `key`): адресуются по `key`, slug им не нужен. Для них «переведено на язык X» = заполнен `title_X`.

### 2.2 Миксины (`apps/core`)

| Миксин | Поля |
|---|---|
| `TimeStampedModel` | `created_at` (auto_now_add), `updated_at` (auto_now) |
| `PublishableModel` | `status`: `draft` / `review` / `published`, по умолчанию `draft`. **Единственный флаг публикации, поля `is_published` нет.** В публичном API видны только `published` |
| `SeoModel` | `meta_title` [T], `meta_description` [T], `og_image` (картинка, общая для всех языков) |

### 2.3 Модели

| Модель | Миксины | Поля |
|---|---|---|
| **Page** — страницы сайта | TimeStamped, Publishable, Seo | `key` (уникальный, nullable; системные страницы: `home`, `about`, `cooperation`), `title` [T], `slug` [T], `content` [T] (rich text), `show_in_menu` (bool), `order` |
| **HomeBlock** — блоки главной | TimeStamped, Publishable | `type`: `hero` / `about` / `advantages` / `kg_china` / `cta`, `title` [T], `text` [T], `image`, `button_text` [T], `button_link` (путь **без** языкового префикса, например `/services`; префикс добавляет фронт), `order` |
| **Direction** — направления деятельности | TimeStamped, Publishable, Seo | `title` [T], `slug` [T], `short_text` [T], `content` [T], `icon` (CharField с choices — смысловой ключ: `cooperation`, `partnership`, `joint-production`, `localization`, `subcontracting`, `consulting`, `b2b-meetings`, `export`; фронт сам сопоставляет ключ с иконкой, SVG не загружаем), `order` |
| **Service** — услуги | TimeStamped, Publishable, Seo | `title` [T], `slug` [T], `short_text` [T], `content` [T], `how_to_apply` [T], `contact_person` [T], `contact_email`, `contact_phone`, `order` |
| **NewsCategory** | TimeStamped | `name` [T], `slug` [T], `order` |
| **News** | TimeStamped, Publishable, Seo | `title` [T], `slug` [T], `excerpt` [T], `content` [T], `cover`, `category` (FK → NewsCategory, `SET_NULL`, nullable), `published_at` (по умолчанию now) |
| **Event** — мероприятия | TimeStamped, Publishable, Seo | `title` [T], `slug` [T], `type`: `mission` / `forum` / `exhibition` / `b2b` / `other`, `start_at`, `end_at` (nullable), `location` [T], `excerpt` [T], `content` [T], `cover` |
| **GalleryImage** | TimeStamped | `image`, `caption` [T], `order`, generic FK (`content_type`, `object_id`) — к News, Event, Project |
| **Attachment** — документы | TimeStamped | `file` (PDF/DOCX), `title` [T], `size` (байты, заполняется автоматически), generic FK (nullable — документ может быть ни к чему не привязан), `show_in_documents` (bool — показывать в `/documents/`, например «Положение о Центре»), `order` |
| **Country** — страны-партнёры | TimeStamped | `name` [T], `code` (ISO 3166-1 alpha-2, уникальный), `flag` (картинка, опционально), `description` [T], `is_active`, `order` |
| **Partner** | TimeStamped | `name` [T], `logo`, `country` (FK → Country), `website`, `description` [T], `consent_to_publish` (bool), `order` |
| **Project** — международные проекты | TimeStamped, Publishable, Seo | `title` [T], `slug` [T], `excerpt` [T], `content` [T], `country` (FK → Country), `partners` (M2M → Partner), `cover`, `published_at` |
| **ContactInfo** — singleton | TimeStamped | `official_name` [T], `address` [T], `phones` (JSON: `[{"label_ru": "...", "label_en": "...", "label_zh": "...", "number": "..."}]` — подписи трёхъязычные; API отдаёт `[{"label", "number"}]` на языке запроса, пустая подпись → `null`), `email`, `work_hours` [T], `map_lat`, `map_lng`, `socials` (JSON: `[{"type": "telegram", "url": "..."}]` — не переводится, `type` — ключ иконки на фронте) |
| **SiteSettings** — singleton | TimeStamped | `feedback_emails` (адреса для заявок через запятую), `analytics_id` (ID счётчика аналитики), `default_og_image` |
| **Feedback** — обращения | — | `type`: `contact` / `cooperation`, `full_name`, `company`, `country` (строка), `email`, `phone` (nullable), `subject`, `message`, `consent`, `lang`, `status`: `new` / `in_progress` / `closed`, `admin_note` (внутренний комментарий), `ip`, `created_at` |

### 2.4 Правила по моделям

- Страны вынесены в отдельную таблицу, чтобы добавлять новые без изменения архитектуры.
- Статус мероприятия «предстоящее / прошедшее» **не хранится** — вычисляется по `end_at` (если пусто — по `start_at`) относительно текущего времени.
- Партнёры попадают в API, только если `consent_to_publish = True`.
- **Отложенная публикация:** News и Project с `published_at` в будущем (`published_at > now`) скрыты везде — в списках, детальных ответах (404), `/home/` и sitemap — до наступления этой даты.
- Картинки (`cover`, `image`, `logo`, `og_image`): превью через django-imagekit — WebP, ширина 400 и 1200 px.
- Singleton-модели (ContactInfo, SiteSettings): ровно одна запись, создаётся миграцией, удалить нельзя.
- Системные страницы (с непустым `key`) создаются миграцией (статус `draft`), удалить нельзя, `key` в админке только для чтения. Адресуются по `key`, slug не нужен (см. 2.1). Команда `seed` заполняет их на трёх языках и публикует.
- Rich text (`content`) санитайзится через `nh3` **при сохранении**. Разрешены: заголовки h2–h4, p, br, strong, em, u, s, ul, ol, li, a (href, target, rel), img (src, alt, width, height), blockquote, table/thead/tbody/tr/th/td, figure, figcaption.

---

## 3. API

### 3.1 Общие правила

- Базовый путь — `/api/v1/`. Все публичные эндпоинты — только GET без авторизации, кроме `POST /feedback/`.
- Язык передаётся параметром `?lang=ru|en|zh`, по умолчанию `ru`. Невалидное значение → `400 {"lang": ["..."]}`.
- **Списки** показывают только опубликованные записи (`status=published`), переведённые на запрошенный язык.
- **Детальные ответы:**
  - Запись ищется по slug **на любом из трёх языков** (`slug_ru` ИЛИ `slug_en` ИЛИ `slug_zh`). Так ссылка `/zh/news/<русский-slug>` не даёт 404, а фронт может сделать редирект на правильный slug.
  - Если перевода на запрошенный язык нет — **не ошибка**: ответ 200, переводимые поля = `null`, `is_translated: false`.
  - В ответе есть `slug` (на запрошенном языке, может быть `null`) и объект `seo`.
- **Объект `seo`** в каждом детальном ответе:
  ```json
  "seo": {
    "meta_title": "...",          // если пусто — title
    "meta_description": "...",    // если пусто — excerpt / short_text
    "og_image": "https://.../1200.webp",  // если пусто — cover, затем default_og_image
    "alternates": { "ru": "slug-ru", "en": "slug-en", "zh": null }
  }
  ```
  `alternates` — это и есть данные для переключателя языка и для hreflang. **Отдельного эндпоинта для slug нет.**
- `content` — безопасный HTML (уже очищен при сохранении).
- Все URL файлов и картинок — **абсолютные** (`https://...`).
- Даты — ISO 8601 с часовым поясом `Asia/Bishkek` (`+06:00`).
- Пагинация (новости, мероприятия, проекты): `page`, `page_size` (по умолчанию 9, максимум 50). Направления, услуги, категории, страны, партнёры — без пагинации.
- Ошибки: `{"detail": "..."}` или `{"field": ["ошибка"]}` для валидации; коды 400 / 404 / 429 / 500.
- CORS разрешён для origins из `CORS_ALLOWED_ORIGINS` (по умолчанию `http://localhost:3000`).

### 3.2 Эндпоинты

| Метод | Эндпоинт | Что отдаёт |
|---|---|---|
| GET | `/home/` | Всё для главной одним запросом: опубликованные `blocks` (по `order`), 4 направления (первые по `order`), 3 последние новости, 3 ближайших предстоящих мероприятия, `seo` из Page с `key=home` |
| GET | `/pages/` | Страницы для меню (`show_in_menu=True`): `key`, `slug`, `title`, `order` |
| GET | `/pages/{key_or_slug}/` | Страница: сначала ищется по `key`, затем по slug на любом языке. Так работают и системные страницы (`about`, `cooperation`), и новые, созданные редактором |
| GET | `/directions/` | Список направлений (без `content`) |
| GET | `/directions/{slug}/` | Направление полностью |
| GET | `/services/` | Список услуг (без `content`) |
| GET | `/services/{slug}/` | Услуга полностью, включая `how_to_apply` и контакты |
| GET | `/news-categories/` | Категории: `slug`, `name` |
| GET | `/news/?category=<slug>&page=&page_size=` | Новости, свежие сверху (по `published_at`). `category` — slug на любом языке |
| GET | `/news/{slug}/` | Новость с `gallery` и `attachments` |
| GET | `/events/?when=upcoming\|past&type=&page=&page_size=` | Мероприятия. `when=upcoming` — по `start_at` по возрастанию; `when=past` — по `start_at` по убыванию; без `when` — все, по убыванию. Параметр называется `when`, а не `status`, чтобы не путать со статусом публикации |
| GET | `/event-types/` | Типы мероприятий с подписями на языке запроса: `[{"code": "forum", "label": "Форум"}]` |
| GET | `/events/{slug}/` | Мероприятие с `gallery` и `attachments` |
| GET | `/countries/` | Активные страны |
| GET | `/partners/?country=<code>` | Партнёры с согласием на публикацию |
| GET | `/projects/?country=<code>&page=` | Международные проекты |
| GET | `/projects/{slug}/` | Проект с партнёрами и `gallery` |
| GET | `/contacts/` | ContactInfo |
| GET | `/settings/` | Публичные настройки: `analytics_id`, `default_og_image` |
| GET | `/documents/` | Attachment с `show_in_documents=True` |
| POST | `/feedback/` | Обращение из формы (см. раздел 5) |

Вне `/api/v1/`: `/sitemap.xml`, `/robots.txt`, `/api/docs/`, `/api/schema/`, админка по `ADMIN_URL`.

### 3.3 Форматы ответов

**Список:**
```json
{
  "count": 42,
  "next": "https://api.example.kg/api/v1/news/?lang=ru&page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "slug": "delovaya-missiya-v-urumchi",
      "title": "Деловая миссия в Урумчи",
      "excerpt": "...",
      "cover": { "small": "https://.../400.webp", "large": "https://.../1200.webp" },
      "category": { "slug": "missions", "name": "Деловые миссии" },
      "published_at": "2026-10-15T10:00:00+06:00",
      "is_translated": true
    }
  ]
}
```

**Детальный ответ (новость):**
```json
{
  "id": 1,
  "slug": "delovaya-missiya-v-urumchi",
  "title": "Деловая миссия в Урумчи",
  "excerpt": "...",
  "content": "<p>...</p>",
  "cover": { "small": "...", "large": "..." },
  "category": { "slug": "missions", "name": "Деловые миссии" },
  "published_at": "2026-10-15T10:00:00+06:00",
  "gallery": [ { "small": "...", "large": "...", "caption": "..." } ],
  "attachments": [ { "title": "Программа", "url": "https://.../program.pdf", "size": 245760, "ext": "pdf" } ],
  "is_translated": true,
  "seo": { "meta_title": "...", "meta_description": "...", "og_image": "...", "alternates": { "ru": "...", "en": "...", "zh": null } }
}
```

**Мероприятие** дополнительно содержит: `type: {"code", "label"}`, `start_at`, `end_at`, `location`, `is_upcoming` (bool, вычисляется).

---

## 4. Админка и роли

### 4.1 Админка

- Все модели из раздела 2 доступны для создания, редактирования и удаления (с учётом ограничений singleton и системных страниц).
- **Вкладки RU / EN / 中文** в формах (`TabbedTranslationAdmin` из modeltranslation).
- **Автозаполнение slug** из заголовка на каждом языке: ru — транслит (`python-slugify`), en — slugify, zh — pinyin (`pypinyin` + slugify). Slug можно поправить вручную.
- **Rich text** для `content` — CKEditor 5 (`django-ckeditor-5`) с загрузкой картинок (только для авторизованных сотрудников).
- **Файлы:** картинки JPG/PNG/WebP до 10 МБ; документы PDF/DOCX до 20 МБ. Проверка расширения **и содержимого** (картинка — через Pillow `verify()`, PDF — заголовок `%PDF`, DOCX — zip-архив с `word/document.xml`).
- **Галерея и вложения** — inline внутри News, Event, Project.
- **SEO-поля** — отдельный свёрнутый fieldset в каждой форме.
- **Списки:** `list_display` с ключевыми полями и статусом, фильтры по статусу, поиск по заголовку.
- **Обращения:** список с фильтрами по статусу, типу и дате; смена статуса прямо в списке; action «Экспорт в CSV» (UTF-8 с BOM, чтобы открывалось в Excel).
- **ContactInfo и SiteSettings** — без кнопки «Добавить» и без удаления; из списка сразу открывается единственная запись.

### 4.2 Роли

Роли — группы Django «Администратор» и «Редактор», создаются **дата-миграцией** вместе с правами. Все сотрудники — `is_staff=True`.

| Доступ | Администратор | Редактор |
|---|---|---|
| Страницы, блоки главной, направления, услуги | Полный | Полный |
| Новости, категории, мероприятия | Полный | Полный |
| Страны, партнёры, проекты, фото, документы | Полный | Полный |
| SEO-поля | Да | Да |
| Обращения из форм | Полный | Просмотр + смена `status` и `admin_note`. Остальные поля только для чтения, удалять нельзя |
| Контактная информация | Да | Не видит |
| Системные настройки (SiteSettings) | Да | Не видит |
| Пользователи и группы | Да | Не видит |

Ограничение по обращениям делается через `get_readonly_fields` и `has_delete_permission` в зависимости от группы — одних стандартных прав Django для этого недостаточно.

Согласование публикаций руководителем в MVP не делаем: редактор может сам ставить `published`. Статус `review` уже есть — процесс добавим позже.

---

## 5. Формы, безопасность, SEO, инфраструктура

### 5.1 `POST /api/v1/feedback/`

| Поле | Тип | Обязательно | Валидация |
|---|---|---|---|
| `type` | `contact` / `cooperation` | Да | из списка |
| `full_name` | string | Да | 2–150 символов |
| `company` | string | Да | до 200 |
| `country` | string | Да | до 100 |
| `email` | string | Да | корректный email |
| `phone` | string | Нет | цифры, `+`, пробелы, `-`, `()`, до 30 |
| `subject` | string | Да | до 200 |
| `message` | string | Да | 10–5000 |
| `consent` | bool | Да | только `true` |
| `lang` | `ru` / `en` / `zh` | Да | из списка |
| `website` | string | — | **honeypot**: если заполнено — отвечаем `201 {"ok": true}`, но ничего не сохраняем и письмо не шлём |

- Успех → `201 {"ok": true}`. Ошибка валидации → `400` с ошибками по полям.
- IP сохраняется с учётом прокси (см. `NUM_PROXIES`).
- После сохранения (`transaction.on_commit`) — письмо на адреса из `SiteSettings.feedback_emails` (если пусто — из `FEEDBACK_EMAIL` в `.env`). Тема письма: `[ЦПК] Новое обращение: <тип> — <subject>`. В dev используется console email backend.
- Если письмо не ушло — обращение всё равно сохранено, ошибка пишется в лог.

### 5.2 Безопасность

- **Rate limit** на `/feedback/`: 5 запросов в час с одного IP (DRF `ScopedRateThrottle`) → `429`.
  - Кэш для throttling — **общий для всех воркеров**: `DatabaseCache` (`python manage.py createcachetable`), не `LocMemCache`.
  - `NUM_PROXIES` из `.env` (dev — 0, прод за nginx — 1). Иначе за nginx все запросы придут с 127.0.0.1 и лимит станет общим на весь сайт.
- **Админка:** путь из `ADMIN_URL` (на проде нестандартный), `django-axes` (блокировка после 5 неудачных входов на 30 минут), валидаторы паролей с минимальной длиной 10.
- **Секреты** (`SECRET_KEY`, SMTP и т.д.) — только в `.env`, в репозитории лежит `.env.example`.
- **Прод:** `DEBUG=False`, `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_PROXY_SSL_HEADER`, `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS=DENY`. Включаются флагом `DEBUG=False`.
- **Загрузки:** проверка типа и размера (раздел 4.1).
- **Логирование** в файл `logs/app.log` + консоль: ошибки 500, неудачные входы в админку, ошибки отправки почты.

### 5.3 SEO

- **`/sitemap.xml`** — все опубликованные и переведённые страницы, направления, услуги, новости, мероприятия, проекты на трёх языках, с `xhtml:link rel="alternate" hreflang` (ru, en, zh, плюс `x-default` → ru). URL ведут на **фронт** (`FRONTEND_URL`) по схеме:

  | Сущность | URL на фронте |
  |---|---|
  | Главная (Page `key=home`) | `/{lang}` |
  | Системная страница (Page с `key`, кроме `home`) | `/{lang}/{key}` |
  | Page (без `key`) | `/{lang}/{slug}` |
  | Direction | `/{lang}/directions/{slug}` |
  | Service | `/{lang}/services/{slug}` |
  | News | `/{lang}/news/{slug}` |
  | Event | `/{lang}/events/{slug}` |
  | Project | `/{lang}/cooperation/projects/{slug}` |

  Схема задаётся **в одном месте** (словарь в `apps/core/sitemap.py`), потому что её ещё надо согласовать с фронтом.
- **`/robots.txt`** — `Disallow: /admin/` (и путь из `ADMIN_URL`), `Disallow: /api/`, строка `Sitemap:`.
- В каждом детальном ответе API есть объект `seo` (раздел 3.1).

### 5.4 Инфраструктура и `.env`

`.env.example`:
```
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:8000
ADMIN_URL=admin/
FRONTEND_URL=http://localhost:3000
NUM_PROXIES=0
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@example.kg
FEEDBACK_EMAIL=
```
Если `EMAIL_HOST` пустой — используется console email backend.

**SQLite:**
- `OPTIONS: {"init_command": "PRAGMA journal_mode=WAL;", "transaction_mode": "IMMEDIATE"}` — чтение не блокируется записью из админки, меньше ошибок `database is locked`.
- `db.sqlite3` не коммитится.
- Не использовать `django.contrib.postgres`, `ArrayField` и прочее, что работает только в PostgreSQL.
- Известное ограничение: `icontains` в SQLite без учёта регистра работает только для латиницы. Поиск по кириллице в админке чувствителен к регистру — для MVP допустимо.

**Команда `python manage.py seed`:**
- Тестовые данные на трёх языках: 5 блоков главной, 8 направлений, 7 услуг, 3 категории, 12 новостей, 8 мероприятий (половина прошедшие, половина предстоящие, все типы), Китай + ещё 1 страна, 4 партнёра (1 без согласия на публикацию), 3 проекта, контакты, «Положение о Центре» (PDF-заглушка) в документах.
- Системные страницы (`home`, `about`, `cooperation`) заполняются на трёх языках и публикуются.
- Минимум 2 записи **без китайского перевода** — чтобы проверить поведение `is_translated: false`.
- Картинки-заглушки генерируются через Pillow (без скачивания из интернета).
- Флаг `--flush` удаляет старые seed-данные перед созданием. Повторный запуск без флага не плодит дубли.
- Создаёт пользователей `admin` (группа «Администратор» + superuser) и `editor` (группа «Редактор»), пароли выводит в консоль.

**README** — запуск на чистой машине за 5 команд:
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate && python manage.py createcachetable
python manage.py seed && python manage.py runserver
```
Плюс: ссылки на Swagger и админку, описание ролей, как запустить тесты.

**После MVP (сейчас не делать):** VPS, nginx + gunicorn, HTTPS (Let's Encrypt), ежедневная копия `db.sqlite3` через `sqlite3 .backup` + копия `media/` с хранением 14 дней.

---

## 6. Тесты (pytest-django)

Каждый критерий приёмки покрыт автотестом:

1. Новость, созданная с тремя переводами, фото и PDF, появляется в `/news/?lang=zh` с галереей и вложением.
2. Пользователь из группы «Редактор» получает 403/скрытие для пользователей, групп, ContactInfo, SiteSettings; не может удалить обращение и изменить в нём что-то кроме `status` / `admin_note`.
3. Запись без китайского перевода: её нет в списке `?lang=zh`, а детальный ответ — `200` с `is_translated: false` и `null` в переводимых полях.
4. Детальный ответ находит запись по slug на другом языке.
5. `POST /feedback/` с пустым email → `400` с ошибкой по полю `email`.
6. Шестой `POST /feedback/` за час с одного IP → `429`.
7. Honeypot: заполненное `website` → `201`, но в БД записи нет.
8. Успешное обращение сохраняется и отправляет письмо (`mail.outbox`).
9. Ошибка SMTP не ломает сохранение обращения.
10. `/events/?when=upcoming` и `?when=past` правильно делят и сортируют мероприятия.
11. Черновики (`draft`, `review`) не видны в API.
12. Партнёр без `consent_to_publish` не виден в API.
13. `/sitemap.xml` содержит hreflang-ссылки; `/robots.txt` закрывает `/api/`.
14. HTML с `<script>` в `content` вырезается при сохранении.

---

## 7. Этапы

Каждый этап заканчивается рабочим состоянием: `python manage.py check` без ошибок, миграции применяются, тесты зелёные. После каждого этапа — коммит.

| Этап | Что делаем | Результат |
|---|---|---|
| **1. Каркас и модели** | Проект, settings через `.env`, `requirements.txt`, `.gitignore`, все приложения, миксины, все модели, регистрация переводов, миграции (включая singleton, системные страницы, группы ролей), базовая регистрация моделей в админке | `migrate` проходит, модели видны в админке с вкладками языков |
| **2. API + Swagger + seed** | Сериализаторы, все GET-эндпоинты, логика языка / `is_translated` / `seo` / slug на любом языке, пагинация, фильтры, Swagger, команда `seed` | Фронт может работать с API — **отдаём контракт Амиру и Ариету** |
| **3. Админка полностью + роли** | Вкладки, автозаполнение slug, CKEditor 5, inline галерея и вложения, валидация файлов, SEO-fieldset, singleton-админки, обращения + CSV, ограничения для Редактора | Критерии приёмки 2 и 3 |
| **4. Формы и безопасность** | `POST /feedback/`, валидация, honeypot, throttle, письма, axes, логирование, прод-настройки безопасности | Критерии приёмки 5 и 6 |
| **5. SEO, README, приёмка** | sitemap, robots, README, все тесты из раздела 6, прогон проекта с нуля по README | MVP готов |

---

## 8. Критерии приёмки MVP

1. Проект поднимается по README на чистой машине.
2. Редактор создаёт новость на трёх языках с фото и PDF, и она сразу есть в `/api/v1/news/?lang=zh`.
3. Редактор не видит пользователей, контактную информацию и системные настройки.
4. Запись без китайского перевода не ломает API: детальный ответ отдаёт `is_translated: false`.
5. Форма с пустым email получает `400` с ошибкой по полю; шестой запрос за час получает `429`.
6. Новое обращение видно в админке и приходит на почту.

## 9. Открытые вопросы (не блокируют MVP)

- На какой email приходят заявки и есть ли SMTP у заказчика? (Пока — console backend.)
- Кто даёт VPS и домен?
- Подписи типов мероприятий на en/zh (`/event-types/`) — проверить переводы носителем языка.
- Схема URL на фронте (раздел 5.3) — согласовать с Амиром и Ариетом. (Ключи иконок направлений и URL системных страниц — решено, см. 2.3 и 5.3.)
- Где отдавать sitemap/robots: с бэка (как сейчас) или фронт проксирует — согласовать.
