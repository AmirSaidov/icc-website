# API сайта ЦПК — для фронтенда

Публичное API для фронтенда на Next.js. Здесь описаны общие правила, а также дан реальный пример ответа на каждый эндпоинт.

- **Базовый URL (локально):** `http://localhost:8000/api/v1/`
- **Swagger:** http://localhost:8000/api/docs/ — можно вызывать эндпоинты прямо из браузера
- **OpenAPI-схема:** http://localhost:8000/api/schema/ или файл [`openapi.yaml`](openapi.yaml) (для генерации типов, например `openapi-typescript docs/openapi.yaml -o api.d.ts`)
- **Админка:** http://localhost:8000/admin/

Все эндпоинты — `GET` без авторизации, кроме `POST /feedback/` (форма обращения, см. раздел «Форма обращения»).

---

## Важно для интеграции

Сверено с `frontend/` в `main` (коммит `7d8f7dd`). Язык (`?lang=`) и поля формы (`full_name`, `lang`) фронт уже передаёт так, как ждёт бэк. Осталось:

| Где во фронте | Сейчас | Что ждёт бэк |
|---|---|---|
| `app/api/feedback/route.ts` | прокси через Next.js с `X-Forwarded-For` | так и задумано; от схемы прокси зависит `NUM_PROXIES` на сервере — см. [DEPLOY.md](DEPLOY.md), раздел 6 |
| `lib/api-types.ts` — `PresentationListItem`, `Presentation` (описаны вручную) | `category: "projects" \| "industry"`, фильтр `?category=` | сферы — справочник **`/sectors/`** (`{slug, name}`), фильтр **`?sector=<slug>`**; связь с проектом — поле **`project`** (`{slug, title}` или `null`) и фильтр **`?project=<slug>`**. Вкладка «Совместные проекты» — см. раздел «Презентации» |
| то же | `excerpt` и `content` | одно поле **`description`** (безопасный HTML), только в детальном ответе |
| то же | `file: Attachment` (`title`, `url`, `size`, `ext`), PPTX — через Office Online | `file` — всегда PDF: `{url, size, pages, ext}`; PPTX — отдельное поле **`source_file`** `{url, size, ext}` или `null`, только для скачивания. Типы теперь есть в `openapi.yaml` — `npm run gen:types` |

## Как запустить бэкенд локально

Нужны Python 3.12 и Git. Бэкенд — папка `backend/` общего репозитория, **все команды выполняются из неё**. Подробнее, в том числе вариант для PowerShell, — в [README бэкенда](../README.md).

```
git clone https://github.com/AmirSaidov/icc-website.git
cd icc-website/backend
```

**Windows (cmd):**
```
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createcachetable
python manage.py seed
python manage.py runserver
```

**macOS / Linux:**
```
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate && python manage.py createcachetable
python manage.py seed && python manage.py runserver
```

`seed` заполняет базу тестовыми данными на трёх языках и создаёт пользователей `admin` и `editor`, пароли выводит в консоль. Повторный запуск дублей не создаёт. Чтобы пересоздать тестовые данные, используйте `python manage.py seed --flush`.

CORS по умолчанию открыт для `http://localhost:3000`. Другой адрес задаётся в `.env` переменной `CORS_ALLOWED_ORIGINS`.

---

## Общие правила

| Что | Как |
|---|---|
| Формат | JSON, UTF-8 |
| Даты | ISO 8601 с поясом Бишкека: `2026-10-15T10:00:00+06:00` |
| URL файлов и картинок | Всегда абсолютные (`http://localhost:8000/media/...`) |
| Картинки | Объект `{"small": "...400px.webp", "large": "...1200px.webp"}` или `null`, если картинки нет |
| Пустые значения | Пустая строка и отсутствующий перевод отдаются как `null`, а не `""` |
| `content` | Готовый безопасный HTML: при сохранении в нём оставляются только разрешённые теги (h2–h4, p, strong, em, u, s, списки, ссылки, картинки, таблицы, blockquote, figure/figcaption). Классов и стилей нет — оформление задаёт фронт. Картинки из редактора приходят с абсолютными URL. Можно вставлять через `dangerouslySetInnerHTML` |
| Порядок | Списки уже отсортированы, порядок пересортировывать не нужно |
| Отложенная публикация | Новости и проекты с `published_at` в будущем не видны нигде (списки, детальные ответы → 404, `/home/`) до наступления этой даты |

### Параметр `lang`

У каждого эндпоинта есть параметр `?lang=ru|en|zh`, по умолчанию `ru`. Все переводимые поля (`title`, `slug`, `excerpt`, `content`, `name`, подписи и т.д.) приходят на этом языке.

Невалидное значение даёт ответ `400`:
```json
{"lang": ["Недопустимое значение «de». Допустимо: ru, en, zh."]}
```

### `is_translated`: что, если перевода нет

Запись считается **переведённой на язык X**, если у неё заполнены `title` (или `name`) и `slug` на этом языке. Исключение — системные страницы (`home`, `about`, `cooperation`): у них нет slug, и для них достаточно заполненного `title`.

- **Списки** содержат только опубликованные записи, переведённые на `lang`. Если новость не переведена на китайский, в `/news/?lang=zh` её нет.
- **Детальные ответы** на непереведённую запись **не** отдают 404. Ответ приходит со статусом `200`, все переводимые поля в нём `null`, а `is_translated` равно `false`. Русский текст вместо отсутствующего перевода **не подставляется**. Пример приведён ниже, в разделе «Новость без перевода на zh».

Что делать фронту при `is_translated: false`: показать заглушку «Материал недоступен на этом языке» со ссылками на доступные языки из `seo.alternates`, либо сразу редиректнуть. Такую страницу стоит закрыть от индексации (`noindex`).

### Slug на любом языке

Детальный эндпоинт находит запись по slug **на любом из трёх языков**. Например, `/news/delovaia-missiia-v-urumchi/?lang=zh` вернёт новость, хотя в запросе русский slug.

В ответе поле `slug` уже указано на языке запроса. Если оно не совпадает со slug из URL, нужно сделать редирект на правильный адрес:

```ts
const data = await fetchNews(params.slug, params.lang);
if (data.slug && data.slug !== params.slug) {
  redirect(`/${params.lang}/news/${data.slug}`);   // 301/308
}
```

### Переключатель языка и hreflang: `seo.alternates`

В каждом детальном ответе (и в `/home/`) есть объект `seo`:

```json
"seo": {
  "meta_title": "...",          // если пусто — title
  "meta_description": "...",    // если пусто — excerpt / short_text
  "og_image": "http://.../xxx.webp",  // 1200px; если пусто — cover, затем картинка по умолчанию
  "alternates": { "ru": "slug-ru", "en": "slug-en", "zh": null }
}
```

`alternates` содержит slug этой же записи на каждом языке, а `null` означает, что на этот язык запись не переведена. Отдельного эндпоинта для поиска slug нет, всё нужное уже лежит в `alternates`.

**Переключатель языка** на странице `/{lang}/news/{slug}`:
```ts
function switchLanguage(target: "ru" | "en" | "zh") {
  const alt = data.seo.alternates[target];
  return alt
    ? `/${target}/news/${alt}`      // перевод есть — на ту же новость
    : `/${target}/news`;            // перевода нет — на список раздела
}
```

**hreflang** выводятся только для языков, где `alternates[lang] !== null`, плюс `x-default`, который ведёт на `ru`:
```html
<link rel="alternate" hreflang="ru" href="https://site.kg/ru/news/slug-ru" />
<link rel="alternate" hreflang="en" href="https://site.kg/en/news/slug-en" />
<link rel="alternate" hreflang="x-default" href="https://site.kg/ru/news/slug-ru" />
```

**Системные страницы** (`home`, `about`, `cooperation`) адресуются по `key`, slug у них `null`. В их `alternates` вместо slug стоит `key`, например `{"ru": "about", "en": "about", "zh": null}`. URL на фронте строится так: главная — `/{lang}`, остальные системные — `/{lang}/{key}`.

### Схема URL на фронте (из ТЗ)

| Сущность | URL на фронте | Эндпоинт |
|---|---|---|
| Главная | `/{lang}` | `/home/` |
| Системная страница | `/{lang}/{key}` | `/pages/{key}/` |
| Обычная страница | `/{lang}/{slug}` | `/pages/{slug}/` |
| Направление | `/{lang}/directions/{slug}` | `/directions/{slug}/` |
| Услуга | `/{lang}/services/{slug}` | `/services/{slug}/` |
| Новость | `/{lang}/news/{slug}` | `/news/{slug}/` |
| Мероприятие | `/{lang}/events/{slug}` | `/events/{slug}/` |
| Проект | `/{lang}/cooperation/projects/{slug}` | `/projects/{slug}/` |
| Презентация | `/{lang}/presentations/{slug}` (согласовать с фронтом) | `/presentations/{slug}/` |

### Пагинация

Пагинация есть только у `/news/`, `/events/`, `/projects/` и `/presentations/`. Параметры: `page` (с 1) и `page_size` (по умолчанию 9, максимум 50; если передать больше, вернётся 50).

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/v1/news/?lang=ru&page=2",
  "previous": null,
  "results": [ ... ]
}
```
`next` и `previous` — готовые URL, в которых уже сохранены `lang` и фильтры. Если запросить номер страницы больше последней, придёт `404`.

Остальные списки (направления, услуги, категории, страны, партнёры, страницы меню, документы, типы мероприятий, сферы презентаций) приходят простым массивом, без пагинации.

### Фильтры

| Эндпоинт | Параметр | Значения |
|---|---|---|
| `/news/` | `category` | slug категории на любом языке (из `/news-categories/`). Неизвестный slug даёт пустой список |
| `/events/` | `when` | `upcoming` — предстоящие, ближайшие сверху; `past` — прошедшие, свежие сверху; без параметра — все, по убыванию даты. Другое значение даёт `400` |
| `/events/` | `type` | `mission`, `forum`, `exhibition`, `b2b`, `other` (подписи на языке запроса — из `/event-types/`). Другое значение даёт `400` |
| `/partners/`, `/projects/`, `/presentations/` | `country` | ISO-код страны (`CN`, `KZ`; регистр не важен) |
| `/presentations/` | `sector` | slug сферы на любом языке (из `/sectors/`). Неизвестный slug даёт пустой список |
| `/presentations/` | `project` | slug проекта на любом языке. Неизвестный или неопубликованный проект даёт пустой список |

Мероприятие считается предстоящим, если оно ещё не закончилось. Проверяется `end_at`, а если он пуст — `start_at`. Поле `is_upcoming` уже посчитано на бэке.

### Ошибки

| Код | Тело | Когда |
|---|---|---|
| 400 | `{"lang": ["..."]}`, `{"when": ["..."]}` | Невалидный параметр |
| 404 | `{"detail": "Страница не найдена."}` | Запись не найдена или не опубликована (черновики не видны) |
| 429 | `{"detail": "..."}` | Превышен лимит запросов (только `POST /feedback/`) |
| 500 | — | Ошибка сервера |

---

## Эндпоинты

| Эндпоинт | Что отдаёт |
|---|---|
| `GET /home/` | Всё для главной: `blocks`, 4 `directions`, 3 последние `news`, 3 ближайших `events`, `seo` |
| `GET /pages/` | Страницы для меню: `key`, `slug`, `title`, `order` |
| `GET /pages/{key_or_slug}/` | Страница: сначала поиск по `key`, затем по slug на любом языке |
| `GET /directions/`, `/directions/{slug}/` | Направления (в списке без `content`). `icon` — смысловой ключ: `cooperation`, `partnership`, `joint-production`, `localization`, `subcontracting`, `consulting`, `b2b-meetings`, `export` |
| `GET /services/`, `/services/{slug}/` | Услуги (в списке без `content`, `how_to_apply` и контактов) |
| `GET /news-categories/` | Категории: `slug`, `name` |
| `GET /news/`, `/news/{slug}/` | Новости; в детальном ответе есть `gallery` и `attachments` |
| `GET /events/`, `/events/{slug}/` | Мероприятия; в детальном ответе есть `gallery` и `attachments` |
| `GET /event-types/` | Типы мероприятий с подписями |
| `GET /countries/` | Активные страны |
| `GET /partners/` | Партнёры с согласием на публикацию |
| `GET /projects/`, `/projects/{slug}/` | Международные проекты; в детальном ответе есть `partners`, `gallery`, `attachments` и `presentations` |
| `GET /sectors/` | Сферы презентаций: `slug`, `name` |
| `GET /presentations/`, `/presentations/{slug}/` | Презентации (PDF для просмотра + необязательный PPTX для скачивания) — см. раздел «Презентации» |
| `GET /contacts/` | Контакты. `phones` — `[{"label", "number"}]`, подпись на языке запроса (может быть `null`); `socials` — `[{"type", "url"}]`, `type` — ключ иконки (не переводится) |
| `GET /settings/` | `analytics_id`, `default_og_image` |
| `GET /documents/` | Документы для раздела «Документы» |

## Форма обращения: `POST /feedback/`

Одна форма для «Контактов» и «Сотрудничества». Тело запроса — JSON, авторизация и CSRF-токен не нужны:

```ts
const response = await fetch(`${API}/feedback/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(form),
});
```

| Поле | Тип | Обязательно | Правила |
|---|---|---|---|
| `type` | `contact` / `cooperation` | да | `contact` — общий вопрос (форма «Контакты»), `cooperation` — сотрудничество |
| `full_name` | string | да | 2–150 символов |
| `company` | string | да | до 200 |
| `country` | string | да | до 100 |
| `email` | string | да | корректный email |
| `phone` | string / null | нет | цифры, `+`, пробелы, `-`, `()`, до 30 |
| `subject` | string | да | до 200 |
| `message` | string | да | 10–5000 символов |
| `consent` | bool | да | только `true` (согласие на обработку данных) |
| `lang` | `ru` / `en` / `zh` | да | язык страницы, с которой отправлено |
| `website` | string | — | **honeypot**, всегда пустая строка (см. ниже) |

**Ответы:**

| Код | Тело | Что делать фронту |
|---|---|---|
| `201` | `{"ok": true}` | Показать «Спасибо, мы свяжемся с вами» |
| `400` | `{"email": ["Обязательное поле."], "message": ["Убедитесь, что это значение содержит не менее 10 символов."]}` | Подсветить поля по ключам. Тексты ошибок приходят на русском — для en/zh лучше показывать свои подписи по имени поля |
| `429` | `{"detail": "Слишком много обращений с вашего адреса. Попробуйте снова через 3599 с."}` + заголовок `Retry-After` (секунды) | «Слишком много запросов, попробуйте позже» |

**Лимит:** 5 запросов в час с одного IP. Считаются все POST, включая отклонённые с ошибкой `400`, поэтому стоит проверять поля на фронте до отправки. Шестой запрос получит `429`.

**Honeypot.** Это ловушка для ботов: поле `website`, которое человек не видит, а бот заполняет. Если оно не пустое, бэк отвечает `201`, как при успехе, но ничего не сохраняет и письмо не шлёт. Как сделать на фронте:

```tsx
{/* не display:none и не type="hidden" — некоторые боты их пропускают; прячем за экраном */}
<div aria-hidden="true" style={{ position: "absolute", left: "-10000px", width: 1, height: 1, overflow: "hidden" }}>
  <label htmlFor="website">Website</label>
  <input id="website" name="website" type="text" tabIndex={-1} autoComplete="off"
         value={form.website} onChange={...} />
</div>
```

В JSON поле `website` отправляется всегда, обычно как пустая строка.

## Презентации

Презентации проектов и сфер (промышленность, IT, …). На сайте они **смотрятся как PDF**, а PPTX (если есть) — только для скачивания.

**Список** `GET /presentations/?lang=&sector=&project=&country=&page=&page_size=` — опубликованные и переведённые на `lang`, свежие сверху (по `published_at`), с пагинацией как у новостей. Элемент: `id`, `slug`, `title`, `cover` (`{small, large}` или `null` — тогда на карточке иконка файла), `sector` (`{slug, name}`), `project` (`{slug, title}` или `null`), `country` (`{code, name}` или `null`), `file`, `published_at`, `is_translated`.

**Детальный ответ** `GET /presentations/{slug}/` — то же плюс `description` (безопасный HTML), `source_file` и `seo`:

```json
"file":        {"url": "https://api.../media/presentations/2026/10/deck.pdf", "size": 124425, "pages": 12, "ext": "pdf"},
"source_file": {"url": "https://api.../media/presentations/2026/10/deck.pptx", "size": 5242880, "ext": "pptx"}
```

- `file` — всегда PDF, есть у каждой презентации. `pages` — число страниц (может быть `null`, если файл не удалось разобрать).
- `source_file` — исходник PPTX или `null`. Отдаётся с `Content-Disposition: attachment`: браузер скачает его, а не откроет.
- `project` — `null`, если проекта нет, он не опубликован или не переведён на `lang`. `sector` — `null`, если сфера не переведена на `lang`.
- Правила языка, `is_translated`, отложенной публикации и поиска по slug на любом языке — как у новостей.

**Презентации проекта** — в детальном ответе `/projects/{slug}/` поле `presentations`: опубликованные и переведённые на `lang`, в порядке, заданном в админке (поле «порядок»). Поля — как у элемента списка, без `project`.

**Вкладки на странице `/presentations`.** Сферы берите из `/sectors/`: их добавляют сотрудники, список не фиксирован. «Совместные проекты» — презентации с `project != null`; отдельного фильтра для этого пока нет (вопрос к руководителю — см. SPEC.md, раздел 9).

### Как показать PDF на странице

Самый простой способ — `<iframe>` со ссылкой `file.url`: браузер покажет PDF встроенным просмотрщиком.

```tsx
<iframe src={`${item.file.url}#view=FitH`} title={item.title ?? ''} className="aspect-[16/10] w-full" />
<a href={item.file.url} target="_blank" rel="noopener noreferrer">Открыть на весь экран</a>
{item.source_file && <a href={item.source_file.url} download>Скачать PPTX</a>}
```

- Встраивать PDF во фрейм можно **только со страниц `FRONTEND_URL`** (и самого бэка): у файлов презентаций бэк отдаёт `Content-Security-Policy: frame-ancestors 'self' <FRONTEND_URL>` вместо `X-Frame-Options: DENY`. С другого домена (например, превью-деплоя Vercel) фрейм останется пустым — открывайте по ссылке.
- PDF отдаётся с `Content-Disposition: inline`: по ссылке он открывается, а не скачивается.
- На телефонах встроенный просмотр PDF во фрейме часто не работает — оставляйте рядом ссылку «Открыть».
- Вариант с **pdf.js** (свой просмотрщик, листание по страницам, одинаково на всех устройствах): pdf.js загружает файл через `fetch`, поэтому у файлов презентаций включён CORS для origins из `CORS_ALLOWED_ORIGINS`. `file.pages` можно показать ещё до загрузки файла.
- Office Online (`view.officeapps.live.com`) не нужен: на сайте показывается PDF.

## sitemap.xml и robots.txt

Бэк отдаёт `/sitemap.xml` и `/robots.txt` (вне `/api/v1/`):

- в sitemap — все опубликованные материалы (включая презентации), каждый только на тех языках, где он переведён; URL ведут на фронт (`FRONTEND_URL`) по схеме из раздела «Схема URL на фронте»; у каждого URL есть `xhtml:link hreflang` на все переводы и `x-default` на русскую версию;
- в robots — `Disallow: /api/` и строка `Sitemap:`. Путь админки в robots не пишется (чтобы не раскрывать её адрес): админка закрыта от индексации заголовком `X-Robots-Tag: noindex, nofollow`. Если фронт будет генерировать свой robots.txt — путь админки туда тоже не добавлять.

Отдавать ли их с домена фронта (проксировать с бэка или генерировать в Next.js) — открытый вопрос (SPEC.md, раздел 9).

## Примеры ответов

Примеры ниже — реальные ответы на данных из `python manage.py seed`. Чтобы примеры были короче, все списки в них сокращены до 2 элементов. Хеши в именах картинок у вас будут другими.

<!-- examples:start -->

### Главная

`GET /api/v1/home/?lang=ru` → 200

```json
{
  "blocks": [
    {
      "id": 11,
      "type": "hero",
      "title": "Центр промышленной кооперации",
      "text": "Помогаем предприятиям Кыргызстана находить партнёров за рубежом",
      "image": {
        "small": "http://localhost:8000/media/CACHE/images/home/hero/7c97cbbd6910903db6d8984ec0a61b83.webp",
        "large": "http://localhost:8000/media/CACHE/images/home/hero/d31d418e7647766cabfc160f31597949.webp"
      },
      "button_text": "Наши услуги",
      "button_link": "/services",
      "order": 0,
      "is_translated": true
    },
    {
      "id": 12,
      "type": "about",
      "title": "О Центре",
      "text": "Центр создан при Торгово-промышленной палате для развития промышленной кооперации.",
      "image": {
        "small": "http://localhost:8000/media/CACHE/images/home/about/89df32e7302812723bbe2f5c9187f575.webp",
        "large": "http://localhost:8000/media/CACHE/images/home/about/f61f513eb35923254e5db4428bc300c9.webp"
      },
      "button_text": "Подробнее",
      "button_link": "/about",
      "order": 1,
      "is_translated": true
    }
  ],
  "directions": [
    {
      "id": 17,
      "slug": "promyshlennaia-kooperatsiia",
      "title": "Промышленная кооперация",
      "short_text": "Связываем производителей для совместной работы.",
      "icon": "cooperation",
      "order": 0,
      "is_translated": true
    },
    {
      "id": 18,
      "slug": "poisk-partnerov",
      "title": "Поиск партнёров",
      "short_text": "Подбираем надёжных партнёров за рубежом.",
      "icon": "partnership",
      "order": 1,
      "is_translated": true
    }
  ],
  "news": [
    {
      "id": 25,
      "slug": "delovaia-missiia-v-urumchi",
      "title": "Деловая миссия в Урумчи",
      "excerpt": "Предприниматели Кыргызстана провели переговоры с компаниями Синьцзяна.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/news/2026/10/news-1/180f0002dfa5cacc94a2a51ef9efc6a6.webp",
        "large": "http://localhost:8000/media/CACHE/images/news/2026/10/news-1/8d061b86952d98a3aab9a4c50f4b83c2.webp"
      },
      "category": {
        "slug": "missions",
        "name": "Деловые миссии"
      },
      "published_at": "2026-10-15T10:00:00+06:00",
      "is_translated": true
    },
    {
      "id": 26,
      "slug": "tsentr-podpisal-memorandum-s-torgovoi-palatoi-sintsziana",
      "title": "Центр подписал меморандум с торговой палатой Синьцзяна",
      "excerpt": "Стороны договорились о совместной работе по поиску партнёров.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/news/2026/10/news-2/6a636923db5281d95aa52c724a0461cd.webp",
        "large": "http://localhost:8000/media/CACHE/images/news/2026/10/news-2/7642e9d4216d1ccb43996ec0f78b7d12.webp"
      },
      "category": {
        "slug": "partnership",
        "name": "Партнёрство"
      },
      "published_at": "2026-10-11T10:00:00+06:00",
      "is_translated": true
    }
  ],
  "events": [
    {
      "id": 22,
      "slug": "biznes-missiia-v-guanchzhou",
      "title": "Бизнес-миссия в Гуанчжоу",
      "type": {
        "code": "mission",
        "label": "Деловая миссия"
      },
      "start_at": "2026-11-06T10:00:00+06:00",
      "end_at": "2026-11-11T10:00:00+06:00",
      "location": "Гуанчжоу",
      "excerpt": "Участие в выставке и деловые встречи.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/events/2026/10/event-6/64e85e9c458c6776c919be396e7d3a96.webp",
        "large": "http://localhost:8000/media/CACHE/images/events/2026/10/event-6/878abf26973605a2e9e086cd13e5d03b.webp"
      },
      "is_upcoming": true,
      "is_translated": true
    },
    {
      "id": 23,
      "slug": "investitsionnyi-forum-v-bishkeke",
      "title": "Инвестиционный форум в Бишкеке",
      "type": {
        "code": "forum",
        "label": "Форум"
      },
      "start_at": "2026-12-01T10:00:00+06:00",
      "end_at": "2026-12-02T10:00:00+06:00",
      "location": "Бишкек",
      "excerpt": "Презентация инвестиционных проектов.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/events/2026/10/event-7/72635c5b81bbb81dbccce8d54500b6b1.webp",
        "large": "http://localhost:8000/media/CACHE/images/events/2026/10/event-7/a775d6f995813deb882d107cf0688c68.webp"
      },
      "is_upcoming": true,
      "is_translated": true
    }
  ],
  "seo": {
    "meta_title": "Центр промышленной кооперации при ТПП КР",
    "meta_description": "Поиск партнёров, деловые миссии и промышленная кооперация с Китаем и другими странами.",
    "og_image": "http://localhost:8000/media/CACHE/images/seo/icc-kyrgyzstan/2caac81c6a38255f974b5c2fc041f7f1.webp",
    "alternates": {
      "ru": "home",
      "en": "home",
      "zh": "home"
    }
  }
}
```

### Страницы для меню

`GET /api/v1/pages/?lang=ru` → 200

```json
[
  {
    "key": "about",
    "slug": null,
    "title": "О Центре",
    "order": 1
  },
  {
    "key": "cooperation",
    "slug": null,
    "title": "Сотрудничество",
    "order": 2
  }
]
```

### Страница (системная, по key)

`GET /api/v1/pages/about/?lang=en` → 200

```json
{
  "id": 2,
  "key": "about",
  "slug": null,
  "title": "About the Centre",
  "content": "<h2>Who we are</h2><p>The Industrial Cooperation Centre helps Kyrgyz companies find partners, enter new markets and develop joint production.</p><p>The Centre operates under the Chamber of Commerce and Industry of the Kyrgyz Republic.</p>",
  "is_translated": true,
  "seo": {
    "meta_title": "About the Centre",
    "meta_description": null,
    "og_image": "http://localhost:8000/media/CACHE/images/seo/icc-kyrgyzstan/2caac81c6a38255f974b5c2fc041f7f1.webp",
    "alternates": {
      "ru": "about",
      "en": "about",
      "zh": "about"
    }
  }
}
```

### Направления

`GET /api/v1/directions/?lang=ru` → 200

```json
[
  {
    "id": 17,
    "slug": "promyshlennaia-kooperatsiia",
    "title": "Промышленная кооперация",
    "short_text": "Связываем производителей для совместной работы.",
    "icon": "cooperation",
    "order": 0,
    "is_translated": true
  },
  {
    "id": 18,
    "slug": "poisk-partnerov",
    "title": "Поиск партнёров",
    "short_text": "Подбираем надёжных партнёров за рубежом.",
    "icon": "partnership",
    "order": 1,
    "is_translated": true
  }
]
```

### Направление

`GET /api/v1/directions/promyshlennaia-kooperatsiia/?lang=ru` → 200

```json
{
  "id": 17,
  "slug": "promyshlennaia-kooperatsiia",
  "title": "Промышленная кооперация",
  "short_text": "Связываем производителей для совместной работы.",
  "content": "<p>Связываем производителей для совместной работы.</p><p>Центр промышленной кооперации помогает предприятиям Кыргызстана находить партнёров, выходить на новые рынки и развивать совместные производства.</p>",
  "icon": "cooperation",
  "order": 0,
  "is_translated": true,
  "seo": {
    "meta_title": "Промышленная кооперация",
    "meta_description": "Связываем производителей для совместной работы.",
    "og_image": "http://localhost:8000/media/CACHE/images/seo/icc-kyrgyzstan/2caac81c6a38255f974b5c2fc041f7f1.webp",
    "alternates": {
      "ru": "promyshlennaia-kooperatsiia",
      "en": "industrial-cooperation",
      "zh": "gong-ye-he-zuo"
    }
  }
}
```

### Услуги

`GET /api/v1/services/?lang=ru` → 200

```json
[
  {
    "id": 15,
    "slug": "podbor-partnerov-v-kitae",
    "title": "Подбор партнёров в Китае",
    "short_text": "Поиск и проверка производителей и поставщиков.",
    "order": 0,
    "is_translated": true
  },
  {
    "id": 16,
    "slug": "organizatsiia-delovykh-missii",
    "title": "Организация деловых миссий",
    "short_text": "Программа визитов, встречи, сопровождение.",
    "order": 1,
    "is_translated": true
  }
]
```

### Услуга

`GET /api/v1/services/podbor-partnerov-v-kitae/?lang=ru` → 200

```json
{
  "id": 15,
  "slug": "podbor-partnerov-v-kitae",
  "title": "Подбор партнёров в Китае",
  "short_text": "Поиск и проверка производителей и поставщиков.",
  "content": "<p>Поиск и проверка производителей и поставщиков.</p><p>Центр промышленной кооперации помогает предприятиям Кыргызстана находить партнёров, выходить на новые рынки и развивать совместные производства.</p>",
  "how_to_apply": "Оставьте заявку через форму на сайте или позвоните нам.",
  "contact_person": "Иванова Анна",
  "contact_email": "services@example.kg",
  "contact_phone": "+996 312 000 002",
  "order": 0,
  "is_translated": true,
  "seo": {
    "meta_title": "Подбор партнёров в Китае",
    "meta_description": "Поиск и проверка производителей и поставщиков.",
    "og_image": "http://localhost:8000/media/CACHE/images/seo/icc-kyrgyzstan/2caac81c6a38255f974b5c2fc041f7f1.webp",
    "alternates": {
      "ru": "podbor-partnerov-v-kitae",
      "en": "partner-search-in-china",
      "zh": "zai-zhong-guo-xun-zhao-he-zuo-huo-ban"
    }
  }
}
```

### Категории новостей

`GET /api/v1/news-categories/?lang=ru` → 200

```json
[
  {
    "slug": "center",
    "name": "Новости Центра"
  },
  {
    "slug": "missions",
    "name": "Деловые миссии"
  }
]
```

### Новости

`GET /api/v1/news/?lang=ru&page_size=2` → 200

```json
{
  "count": 12,
  "next": "http://localhost:8000/api/v1/news/?lang=ru&page=2&page_size=2",
  "previous": null,
  "results": [
    {
      "id": 25,
      "slug": "delovaia-missiia-v-urumchi",
      "title": "Деловая миссия в Урумчи",
      "excerpt": "Предприниматели Кыргызстана провели переговоры с компаниями Синьцзяна.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/news/2026/10/news-1/180f0002dfa5cacc94a2a51ef9efc6a6.webp",
        "large": "http://localhost:8000/media/CACHE/images/news/2026/10/news-1/8d061b86952d98a3aab9a4c50f4b83c2.webp"
      },
      "category": {
        "slug": "missions",
        "name": "Деловые миссии"
      },
      "published_at": "2026-10-15T10:00:00+06:00",
      "is_translated": true
    },
    {
      "id": 26,
      "slug": "tsentr-podpisal-memorandum-s-torgovoi-palatoi-sintsziana",
      "title": "Центр подписал меморандум с торговой палатой Синьцзяна",
      "excerpt": "Стороны договорились о совместной работе по поиску партнёров.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/news/2026/10/news-2/6a636923db5281d95aa52c724a0461cd.webp",
        "large": "http://localhost:8000/media/CACHE/images/news/2026/10/news-2/7642e9d4216d1ccb43996ec0f78b7d12.webp"
      },
      "category": {
        "slug": "partnership",
        "name": "Партнёрство"
      },
      "published_at": "2026-10-11T10:00:00+06:00",
      "is_translated": true
    }
  ]
}
```

### Новость

`GET /api/v1/news/delovaia-missiia-v-urumchi/?lang=ru` → 200

```json
{
  "id": 25,
  "slug": "delovaia-missiia-v-urumchi",
  "title": "Деловая миссия в Урумчи",
  "excerpt": "Предприниматели Кыргызстана провели переговоры с компаниями Синьцзяна.",
  "content": "<p>Предприниматели Кыргызстана провели переговоры с компаниями Синьцзяна.</p><p>Центр промышленной кооперации помогает предприятиям Кыргызстана находить партнёров, выходить на новые рынки и развивать совместные производства.</p>",
  "cover": {
    "small": "http://localhost:8000/media/CACHE/images/news/2026/10/news-1/180f0002dfa5cacc94a2a51ef9efc6a6.webp",
    "large": "http://localhost:8000/media/CACHE/images/news/2026/10/news-1/8d061b86952d98a3aab9a4c50f4b83c2.webp"
  },
  "category": {
    "slug": "missions",
    "name": "Деловые миссии"
  },
  "published_at": "2026-10-15T10:00:00+06:00",
  "gallery": [
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-1/3fbeb4c9d36df2f3914fb2e5d015c9ce.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-1/09142fef4aba283b8a0d640e15a313e2.webp",
      "caption": "Открытие встречи"
    },
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-2/27934dff64ad428503edb6fb41d9c026.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-2/747c2e80015e11af58c01a46b7a27a34.webp",
      "caption": "Переговоры"
    }
  ],
  "attachments": [
    {
      "title": "Программа",
      "url": "http://localhost:8000/media/documents/2026/10/programme.pdf",
      "size": 40949,
      "ext": "pdf"
    }
  ],
  "is_translated": true,
  "seo": {
    "meta_title": "Деловая миссия в Урумчи — ЦПК",
    "meta_description": "Предприниматели Кыргызстана провели переговоры с компаниями Синьцзяна.",
    "og_image": "http://localhost:8000/media/CACHE/images/news/2026/10/news-1/8d061b86952d98a3aab9a4c50f4b83c2.webp",
    "alternates": {
      "ru": "delovaia-missiia-v-urumchi",
      "en": "business-mission-to-urumqi",
      "zh": "wu-lu-mu-qi-shang-wu-kao-cha"
    }
  }
}
```

### Новость без перевода на zh (is_translated: false)

`GET /api/v1/news/vstrecha-s-predprinimateliami-osha/?lang=zh` → 200

```json
{
  "id": 35,
  "slug": null,
  "title": null,
  "excerpt": null,
  "content": null,
  "cover": {
    "small": "http://localhost:8000/media/CACHE/images/news/2026/10/news-11/227783ae5c441677d1ff66dc67bef39e.webp",
    "large": "http://localhost:8000/media/CACHE/images/news/2026/10/news-11/9510921bb2c8029ebe63babeddbae2e8.webp"
  },
  "category": {
    "slug": "center",
    "name": "中心新闻"
  },
  "published_at": "2026-08-08T10:00:00+06:00",
  "gallery": [],
  "attachments": [],
  "is_translated": false,
  "seo": {
    "meta_title": null,
    "meta_description": null,
    "og_image": "http://localhost:8000/media/CACHE/images/news/2026/10/news-11/9510921bb2c8029ebe63babeddbae2e8.webp",
    "alternates": {
      "ru": "vstrecha-s-predprinimateliami-osha",
      "en": "meeting-with-osh-entrepreneurs",
      "zh": null
    }
  }
}
```

### Мероприятия (предстоящие)

`GET /api/v1/events/?lang=ru&when=upcoming&page_size=2` → 200

```json
{
  "count": 3,
  "next": "http://localhost:8000/api/v1/events/?lang=ru&page=2&page_size=2&when=upcoming",
  "previous": null,
  "results": [
    {
      "id": 22,
      "slug": "biznes-missiia-v-guanchzhou",
      "title": "Бизнес-миссия в Гуанчжоу",
      "type": {
        "code": "mission",
        "label": "Деловая миссия"
      },
      "start_at": "2026-11-06T10:00:00+06:00",
      "end_at": "2026-11-11T10:00:00+06:00",
      "location": "Гуанчжоу",
      "excerpt": "Участие в выставке и деловые встречи.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/events/2026/10/event-6/64e85e9c458c6776c919be396e7d3a96.webp",
        "large": "http://localhost:8000/media/CACHE/images/events/2026/10/event-6/878abf26973605a2e9e086cd13e5d03b.webp"
      },
      "is_upcoming": true,
      "is_translated": true
    },
    {
      "id": 23,
      "slug": "investitsionnyi-forum-v-bishkeke",
      "title": "Инвестиционный форум в Бишкеке",
      "type": {
        "code": "forum",
        "label": "Форум"
      },
      "start_at": "2026-12-01T10:00:00+06:00",
      "end_at": "2026-12-02T10:00:00+06:00",
      "location": "Бишкек",
      "excerpt": "Презентация инвестиционных проектов.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/events/2026/10/event-7/72635c5b81bbb81dbccce8d54500b6b1.webp",
        "large": "http://localhost:8000/media/CACHE/images/events/2026/10/event-7/a775d6f995813deb882d107cf0688c68.webp"
      },
      "is_upcoming": true,
      "is_translated": true
    }
  ]
}
```

### Типы мероприятий

`GET /api/v1/event-types/?lang=zh` → 200

```json
[
  {
    "code": "mission",
    "label": "商务考察团"
  },
  {
    "code": "forum",
    "label": "论坛"
  }
]
```

### Мероприятие

`GET /api/v1/events/business-mission-to-xinjiang/?lang=en` → 200

```json
{
  "id": 17,
  "slug": "business-mission-to-xinjiang",
  "title": "Business mission to Xinjiang",
  "type": {
    "code": "mission",
    "label": "Business mission"
  },
  "start_at": "2026-08-18T10:00:00+06:00",
  "end_at": "2026-08-21T10:00:00+06:00",
  "location": "Urumqi",
  "excerpt": "Company visits and negotiations.",
  "content": "<p>Company visits and negotiations.</p><p>The Industrial Cooperation Centre helps Kyrgyz companies find partners, enter new markets and develop joint production.</p>",
  "cover": {
    "small": "http://localhost:8000/media/CACHE/images/events/2026/10/event-1/0dd78e7373ae6d2000b6f19a4904b7e7.webp",
    "large": "http://localhost:8000/media/CACHE/images/events/2026/10/event-1/a510160fb27adf0dbad59cdb0183a770.webp"
  },
  "is_upcoming": false,
  "gallery": [
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-1_36J5oXL/1052edca0ef98ab40469df6750c4015f.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-1_36J5oXL/37275bf6f80a26d1fc57a4440653a0a4.webp",
      "caption": "Opening of the meeting"
    },
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-2_qlX79ne/376505789d67531cd0df75fdda210bd2.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-2_qlX79ne/c76ee863dfd4b1ca7f1ead3ade1e72f4.webp",
      "caption": "Negotiations"
    }
  ],
  "attachments": [],
  "is_translated": true,
  "seo": {
    "meta_title": "Business mission to Xinjiang",
    "meta_description": "Company visits and negotiations.",
    "og_image": "http://localhost:8000/media/CACHE/images/events/2026/10/event-1/a510160fb27adf0dbad59cdb0183a770.webp",
    "alternates": {
      "ru": "biznes-missiia-v-sintszian",
      "en": "business-mission-to-xinjiang",
      "zh": "xin-jiang-shang-wu-kao-cha-tuan"
    }
  }
}
```

### Страны

`GET /api/v1/countries/?lang=ru` → 200

```json
[
  {
    "id": 5,
    "code": "CN",
    "name": "Китай",
    "description": "Ключевой партнёр Кыргызстана в промышленной кооперации.",
    "flag": {
      "small": "http://localhost:8000/media/CACHE/images/flags/cn/016c0dbcea457959ba6bb508ac5f537f.webp",
      "large": "http://localhost:8000/media/CACHE/images/flags/cn/662eb7c33a66ec0595b18575d17bb2ac.webp"
    },
    "is_translated": true
  },
  {
    "id": 6,
    "code": "KZ",
    "name": "Казахстан",
    "description": "Партнёр по Евразийскому экономическому союзу.",
    "flag": {
      "small": "http://localhost:8000/media/CACHE/images/flags/kz/68283f27fc4876187533fbdb098e3efc.webp",
      "large": "http://localhost:8000/media/CACHE/images/flags/kz/6ce26751f5da7ff7c92989d8afe12e5b.webp"
    },
    "is_translated": true
  }
]
```

### Партнёры

`GET /api/v1/partners/?lang=ru&country=CN` → 200

```json
[
  {
    "id": 9,
    "name": "Торговая компания «Шёлковый путь» (демо)",
    "logo": {
      "small": "http://localhost:8000/media/CACHE/images/partners/logo-1/4102341f8ee4cfc88052f5d4bba63378.webp",
      "large": "http://localhost:8000/media/CACHE/images/partners/logo-1/de558907b3fdb77063a7219c781a54b4.webp"
    },
    "country": {
      "code": "CN",
      "name": "Китай"
    },
    "website": "https://example.com/silkroad",
    "description": "Оптовая торговля и логистика.",
    "is_translated": true
  },
  {
    "id": 10,
    "name": "«Тяньшань Машинери» (демо)",
    "logo": {
      "small": "http://localhost:8000/media/CACHE/images/partners/logo-2/c63583e8b06cfcfc91d4176deae1956f.webp",
      "large": "http://localhost:8000/media/CACHE/images/partners/logo-2/28bb25a8d42e128eadd01af0d5844f16.webp"
    },
    "country": {
      "code": "CN",
      "name": "Китай"
    },
    "website": "https://example.com/tianshan",
    "description": "Производство сельхозтехники.",
    "is_translated": true
  }
]
```

### Проекты

`GET /api/v1/projects/?lang=ru&page_size=2` → 200

```json
{
  "count": 3,
  "next": "http://localhost:8000/api/v1/projects/?lang=ru&page=2&page_size=2",
  "previous": null,
  "results": [
    {
      "id": 7,
      "slug": "sovmestnoe-proizvodstvo-stroimaterialov-v-chuiskoi-oblasti",
      "title": "Совместное производство стройматериалов в Чуйской области",
      "excerpt": "Запуск завода мощностью 100 тыс. тонн в год.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/projects/2026/10/project-1/a78f6a3c567a5b27884697aa88571959.webp",
        "large": "http://localhost:8000/media/CACHE/images/projects/2026/10/project-1/666e36e067f2ac51c7aed23fb837aa7d.webp"
      },
      "country": {
        "code": "CN",
        "name": "Китай"
      },
      "published_at": "2026-10-07T10:00:00+06:00",
      "is_translated": true
    },
    {
      "id": 8,
      "slug": "lokalizatsiia-sborki-selkhoztekhniki",
      "title": "Локализация сборки сельхозтехники",
      "excerpt": "Сборка тракторов из машинокомплектов.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/projects/2026/10/project-2/b6d3c524062c951d457356f24aca2141.webp",
        "large": "http://localhost:8000/media/CACHE/images/projects/2026/10/project-2/933fa97af6e8edb7ef3830ff18feb5f5.webp"
      },
      "country": {
        "code": "CN",
        "name": "Китай"
      },
      "published_at": "2026-09-07T10:00:00+06:00",
      "is_translated": true
    }
  ]
}
```

### Проект

`GET /api/v1/projects/sovmestnoe-proizvodstvo-stroimaterialov-v-chuiskoi-oblasti/?lang=zh` → 200

```json
{
  "id": 7,
  "slug": "chu-he-zhou-jian-cai-he-zi-sheng-chan",
  "title": "楚河州建材合资生产",
  "excerpt": "建设年产10万吨的工厂。",
  "content": "<p>建设年产10万吨的工厂。</p><p>工业合作中心帮助吉尔吉斯斯坦企业寻找合作伙伴、开拓新市场并发展合资生产。</p>",
  "cover": {
    "small": "http://localhost:8000/media/CACHE/images/projects/2026/10/project-1/a78f6a3c567a5b27884697aa88571959.webp",
    "large": "http://localhost:8000/media/CACHE/images/projects/2026/10/project-1/666e36e067f2ac51c7aed23fb837aa7d.webp"
  },
  "country": {
    "code": "CN",
    "name": "中国"
  },
  "published_at": "2026-10-07T10:00:00+06:00",
  "partners": [
    {
      "id": 9,
      "name": "丝路贸易有限公司（演示）",
      "logo": {
        "small": "http://localhost:8000/media/CACHE/images/partners/logo-1/4102341f8ee4cfc88052f5d4bba63378.webp",
        "large": "http://localhost:8000/media/CACHE/images/partners/logo-1/de558907b3fdb77063a7219c781a54b4.webp"
      },
      "country": {
        "code": "CN",
        "name": "中国"
      },
      "website": "https://example.com/silkroad",
      "description": "批发贸易与物流。",
      "is_translated": true
    },
    {
      "id": 10,
      "name": "天山机械（演示）",
      "logo": {
        "small": "http://localhost:8000/media/CACHE/images/partners/logo-2/c63583e8b06cfcfc91d4176deae1956f.webp",
        "large": "http://localhost:8000/media/CACHE/images/partners/logo-2/28bb25a8d42e128eadd01af0d5844f16.webp"
      },
      "country": {
        "code": "CN",
        "name": "中国"
      },
      "website": "https://example.com/tianshan",
      "description": "农业机械制造。",
      "is_translated": true
    }
  ],
  "gallery": [
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-1_N6u0BWb/2a4e605e95a58aff12eb0e593b05e969.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-1_N6u0BWb/3c9b3ec861991b8c3611abdc6c6f463b.webp",
      "caption": "会议开幕"
    },
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-2_UjcmiyV/fc5ffca5e52128889b64a8b2337d97f1.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/photo-2_UjcmiyV/82c90ed5354eee7d179243f03df98ad8.webp",
      "caption": "洽谈"
    }
  ],
  "attachments": [],
  "presentations": [
    {
      "id": 1,
      "slug": "chu-he-zhou-jian-cai-chang-tou-zi-jian-yi-shu",
      "title": "楚河州建材厂：投资建议书",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/presentation-covers/2026/10/presentation-1/dac4678d340cca6ffc9f92447d5eb492.webp",
        "large": "http://localhost:8000/media/CACHE/images/presentation-covers/2026/10/presentation-1/ca69a5ba9adcd1d6008a33343362da53.webp"
      },
      "sector": {
        "slug": "gong-ye",
        "name": "工业"
      },
      "country": {
        "code": "CN",
        "name": "中国"
      },
      "file": {
        "url": "http://localhost:8000/media/presentations/2026/10/zavod-stroimaterialov-v-chuiskoi-oblasti-investitsionnoe-predlozhenie.pdf",
        "size": 162972,
        "pages": 4,
        "ext": "pdf"
      },
      "published_at": "2026-10-21T10:00:00+06:00",
      "is_translated": true
    }
  ],
  "is_translated": true,
  "seo": {
    "meta_title": "楚河州建材合资生产",
    "meta_description": "建设年产10万吨的工厂。",
    "og_image": "http://localhost:8000/media/CACHE/images/projects/2026/10/project-1/666e36e067f2ac51c7aed23fb837aa7d.webp",
    "alternates": {
      "ru": "sovmestnoe-proizvodstvo-stroimaterialov-v-chuiskoi-oblasti",
      "en": "joint-production-of-building-materials-in-the-chui-region",
      "zh": "chu-he-zhou-jian-cai-he-zi-sheng-chan"
    }
  }
}
```

### Сферы презентаций

`GET /api/v1/sectors/?lang=ru` → 200

```json
[
  {
    "slug": "promyshlennost",
    "name": "Промышленность"
  },
  {
    "slug": "informatsionnye-tekhnologii",
    "name": "Информационные технологии"
  }
]
```

### Презентации

`GET /api/v1/presentations/?lang=ru&page_size=2` → 200

```json
{
  "count": 5,
  "next": "http://localhost:8000/api/v1/presentations/?lang=ru&page=2&page_size=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "slug": "zavod-stroimaterialov-v-chuiskoi-oblasti-investitsionnoe-predlozhenie",
      "title": "Завод стройматериалов в Чуйской области: инвестиционное предложение",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/presentation-covers/2026/10/presentation-1/dac4678d340cca6ffc9f92447d5eb492.webp",
        "large": "http://localhost:8000/media/CACHE/images/presentation-covers/2026/10/presentation-1/ca69a5ba9adcd1d6008a33343362da53.webp"
      },
      "sector": {
        "slug": "promyshlennost",
        "name": "Промышленность"
      },
      "project": {
        "slug": "sovmestnoe-proizvodstvo-stroimaterialov-v-chuiskoi-oblasti",
        "title": "Совместное производство стройматериалов в Чуйской области"
      },
      "country": {
        "code": "CN",
        "name": "Китай"
      },
      "file": {
        "url": "http://localhost:8000/media/presentations/2026/10/zavod-stroimaterialov-v-chuiskoi-oblasti-investitsionnoe-predlozhenie.pdf",
        "size": 162972,
        "pages": 4,
        "ext": "pdf"
      },
      "published_at": "2026-10-21T10:00:00+06:00",
      "is_translated": true
    },
    {
      "id": 2,
      "slug": "lokalizatsiia-sborki-traktorov-etapy-i-trebovaniia",
      "title": "Локализация сборки тракторов: этапы и требования",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/presentation-covers/2026/10/presentation-2/d02bc5e477d093f7f59dc05dcea99c02.webp",
        "large": "http://localhost:8000/media/CACHE/images/presentation-covers/2026/10/presentation-2/923c64d9a4ad8d43857f40f211b96282.webp"
      },
      "sector": {
        "slug": "promyshlennost",
        "name": "Промышленность"
      },
      "project": {
        "slug": "lokalizatsiia-sborki-selkhoztekhniki",
        "title": "Локализация сборки сельхозтехники"
      },
      "country": {
        "code": "CN",
        "name": "Китай"
      },
      "file": {
        "url": "http://localhost:8000/media/presentations/2026/10/lokalizatsiia-sborki-traktorov-etapy-i-trebovaniia.pdf",
        "size": 124425,
        "pages": 3,
        "ext": "pdf"
      },
      "published_at": "2026-10-11T10:00:00+06:00",
      "is_translated": true
    }
  ]
}
```

### Презентация (PDF + исходник PPTX)

`GET /api/v1/presentations/lokalizatsiia-sborki-traktorov-etapy-i-trebovaniia/?lang=ru` → 200

```json
{
  "id": 2,
  "slug": "lokalizatsiia-sborki-traktorov-etapy-i-trebovaniia",
  "title": "Локализация сборки тракторов: этапы и требования",
  "description": "<p>Как устроена сборка из машинокомплектов и что требуется от площадки.</p>",
  "cover": {
    "small": "http://localhost:8000/media/CACHE/images/presentation-covers/2026/10/presentation-2/d02bc5e477d093f7f59dc05dcea99c02.webp",
    "large": "http://localhost:8000/media/CACHE/images/presentation-covers/2026/10/presentation-2/923c64d9a4ad8d43857f40f211b96282.webp"
  },
  "sector": {
    "slug": "promyshlennost",
    "name": "Промышленность"
  },
  "project": {
    "slug": "lokalizatsiia-sborki-selkhoztekhniki",
    "title": "Локализация сборки сельхозтехники"
  },
  "country": {
    "code": "CN",
    "name": "Китай"
  },
  "file": {
    "url": "http://localhost:8000/media/presentations/2026/10/lokalizatsiia-sborki-traktorov-etapy-i-trebovaniia.pdf",
    "size": 124425,
    "pages": 3,
    "ext": "pdf"
  },
  "source_file": {
    "url": "http://localhost:8000/media/presentations/2026/10/lokalizatsiia-sborki-traktorov-etapy-i-trebovaniia.pptx",
    "size": 322,
    "ext": "pptx"
  },
  "published_at": "2026-10-11T10:00:00+06:00",
  "is_translated": true,
  "seo": {
    "meta_title": "Локализация сборки тракторов: этапы и требования",
    "meta_description": "Как устроена сборка из машинокомплектов и что требуется от площадки.",
    "og_image": "http://localhost:8000/media/CACHE/images/presentation-covers/2026/10/presentation-2/923c64d9a4ad8d43857f40f211b96282.webp",
    "alternates": {
      "ru": "lokalizatsiia-sborki-traktorov-etapy-i-trebovaniia",
      "en": "localizing-tractor-assembly-stages-and-requirements",
      "zh": "tuo-la-ji-zu-zhuang-ben-di-hua-jie-duan-yu-yao-qiu"
    }
  }
}
```

### Контакты

`GET /api/v1/contacts/?lang=ru` → 200

```json
{
  "official_name": "Центр промышленной кооперации при Торгово-промышленной палате Кыргызской Республики",
  "address": "720000, г. Бишкек, ул. Примерная, 1 (тестовый адрес)",
  "phones": [
    {
      "label": "Приёмная",
      "number": "+996 312 000 000"
    },
    {
      "label": "Отдел кооперации",
      "number": "+996 312 000 001"
    }
  ],
  "email": "info@example.kg",
  "work_hours": "Пн–Пт, 9:00–18:00",
  "map_lat": 42.8746,
  "map_lng": 74.6122,
  "socials": [
    {
      "type": "telegram",
      "url": "https://t.me/example"
    },
    {
      "type": "facebook",
      "url": "https://facebook.com/example"
    }
  ]
}
```

### Публичные настройки

`GET /api/v1/settings/?lang=ru` → 200

```json
{
  "analytics_id": null,
  "default_og_image": {
    "small": "http://localhost:8000/media/CACHE/images/seo/icc-kyrgyzstan/829137d66a2b7af8d82c19ccd85a8b59.webp",
    "large": "http://localhost:8000/media/CACHE/images/seo/icc-kyrgyzstan/2caac81c6a38255f974b5c2fc041f7f1.webp"
  }
}
```

### Документы

`GET /api/v1/documents/?lang=ru` → 200

```json
[
  {
    "title": "Положение о Центре",
    "url": "http://localhost:8000/media/documents/2026/10/polozhenie-o-centre.pdf",
    "size": 46092,
    "ext": "pdf"
  }
]
```

### Ошибка: невалидный lang (400)

`GET /api/v1/news/?lang=de` → 400

```json
{
  "lang": [
    "Недопустимое значение «de». Допустимо: ru, en, zh."
  ]
}
```

<!-- examples:end -->

---

## Для бэкенда: как обновить эту документацию

```
python manage.py seed
python manage.py export_api_examples
python manage.py spectacular --file docs/openapi.yaml --validate
```
Первая команда пересобирает примеры в этом файле и в Swagger (`apps/core/api_examples/`), вторая — схему `docs/openapi.yaml`.
