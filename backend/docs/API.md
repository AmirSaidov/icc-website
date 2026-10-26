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
Презентации бэк отдаёт в форме, которую уже читает фронт (`category`, `excerpt`, `content`, `cover`, `file.url` / `file.size` / `file.ext`, `seo`). Что поменять во фронте:

| Где во фронте | Сейчас | Что поменять |
|---|---|---|
| `components/ui/PresentationViewer.tsx` | PPT/PPTX показываются через Office Online (`view.officeapps.live.com`) | **Office Online не поддерживаем.** `file` — всегда PDF: показывать только его (iframe или pdf.js). Ветку `OFFICE_EXT` / `officeUrl` и `noPreview` можно убрать |
| то же — кнопка «Скачать» | скачивает `file.url` (PDF) | если есть **`source_file`** (`{url, size, ext: "pptx"}`) — добавить кнопку «Скачать PPTX» по `source_file.url`. Учтите: атрибут `download` у ссылки на другой домен браузеры игнорируют — PDF по такой кнопке откроется (он отдаётся `inline`), PPTX скачается (`attachment`) |
| `lib/api-types.ts` — `PresentationListItem`, `Presentation` (описаны вручную) | `file: Attachment` | типы есть в `openapi.yaml`: `npm run gen:types` и `S['PresentationList']` / `S['PresentationDetail']`. `file` — это `PresentationFile` `{url, size, pages, ext}`, без `title` (фронт его и не читает); `published_at` приходит всегда |
| `lib/api.ts` — `getPresentations` | 404 → пустой список (эндпоинта не было) | эндпоинт есть; обработку 404 можно убрать |
| деплой фронта на Vercel | — | PDF встраивается во фрейм только на доменах из `FRAME_ANCESTORS` бэка (по умолчанию — `FRONTEND_URL`). Для превью-деплоев на тестовом бэке нужно `FRAME_ANCESTORS=...,https://*.vercel.app` |

Новое в API, что фронт пока не использует (не обязательно): `sector` (`{slug, name}`) и справочник `/sectors/` — для подвкладок внутри «Промышленность и IT» (`?category=industry&sector=<slug>`); `project`, `country`, `file.pages`, фильтры `?project=`, `?country=`.

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
| Презентация | `/{lang}/presentations/{slug}` | `/presentations/{slug}/` |

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
| `/presentations/` | `category` | `projects` — презентации опубликованных проектов, `industry` — остальные. Другое значение даёт `400` |
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

Презентации совместных проектов и отраслей (промышленность, IT, …). На сайте они **смотрятся как PDF**; PPTX (если есть) — только для скачивания.

**Список** `GET /presentations/?lang=&category=&sector=&project=&country=&page=&page_size=` — опубликованные и переведённые на `lang`, свежие сверху (по `published_at`), с пагинацией как у новостей. Элемент:

| Поле | Что это |
|---|---|
| `id`, `slug`, `title`, `excerpt` | как у новости; `excerpt` — короткий текст без HTML (до 300 символов) |
| `category` | `projects` — презентация опубликованного проекта, `industry` — все остальные. Вычисляется, не зависит от языка |
| `cover` | `{small, large}` или `null` — тогда на карточке иконка файла |
| `sector` | `{slug, name}` — сфера («Промышленность», «Информационные технологии», …); `null`, если не переведена на `lang` |
| `project` | `{slug, title}` или `null` (нет проекта, он не опубликован или не переведён на `lang`) |
| `country` | `{code, name}` или `null` |
| `file` | PDF: `{url, size, pages, ext: "pdf"}` |
| `published_at`, `is_translated` | как у новости |

**Детальный ответ** `GET /presentations/{slug}/` — то же плюс `content` (безопасный HTML), `source_file` и `seo` (`meta_description` по умолчанию — `excerpt`):

```json
"file":        {"url": "https://api.../media/presentations/2026/10/deck.pdf", "size": 124425, "pages": 12, "ext": "pdf"},
"source_file": {"url": "https://api.../media/presentations/2026/10/deck.pptx", "size": 5242880, "ext": "pptx"}
```

- `file` — всегда PDF, есть у каждой презентации. `pages` может быть `null`, если файл не удалось разобрать.
- `source_file` — исходник PPTX или `null`. Отдаётся с `Content-Disposition: attachment`: браузер его скачает. **Показывать PPTX на сайте (Office Online и т.п.) не нужно.**
- Правила языка, `is_translated`, отложенной публикации и поиска по slug на любом языке — как у новостей.

**Вкладки на странице `/presentations`:** «Совместные проекты» — `?category=projects`, «Промышленность и IT» — `?category=industry`, без параметра — все. Другое значение `category` → `400`. Внутри `industry` можно уточнять сферой: `?category=industry&sector=<slug>` (сферы — из `/sectors/`, их добавляют сотрудники).

**Презентации проекта** — в детальном ответе `/projects/{slug}/` поле `presentations`: опубликованные и переведённые на `lang`, в порядке, заданном в админке (поле «порядок»). Поля — как у элемента списка, без `project` (`category` у них всегда `projects`).

### Как показать PDF на странице

Самый простой способ — `<iframe>` со ссылкой `file.url`: браузер покажет PDF встроенным просмотрщиком.

```tsx
<iframe src={`${item.file.url}#view=FitH`} title={item.title ?? ''} className="aspect-[16/10] w-full" />
<a href={item.file.url} target="_blank" rel="noopener noreferrer">Открыть на весь экран</a>
{item.source_file && <a href={item.source_file.url}>Скачать PPTX</a>}
```

- Встраивать PDF во фрейм можно **только со страниц из `FRAME_ANCESTORS`** бэка (по умолчанию — `FRONTEND_URL`) и с самого бэка: у файлов презентаций бэк отдаёт `Content-Security-Policy: frame-ancestors 'self' <FRAME_ANCESTORS>` вместо `X-Frame-Options: DENY`. С другого домена фрейм останется пустым — открывайте по ссылке. Для превью-деплоев Vercel на тестовом бэке добавляют `https://*.vercel.app`.
- PDF отдаётся с `Content-Disposition: inline`: по ссылке он открывается, а не скачивается.
- На телефонах встроенный просмотр PDF во фрейме часто не работает — оставляйте рядом ссылку «Открыть».
- Вариант с **pdf.js** (свой просмотрщик, листание по страницам, одинаково на всех устройствах): pdf.js загружает файл через `fetch`, поэтому у файлов презентаций включён CORS для origins из `CORS_ALLOWED_ORIGINS` (маски `*.vercel.app` там нет — для превью нужен iframe или ссылка). `file.pages` можно показать ещё до загрузки файла.

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
      "id": 16,
      "type": "hero",
      "title": "Центр промышленной кооперации",
      "text": "Помогаем предприятиям Кыргызстана находить партнёров за рубежом",
      "image": {
        "small": "http://localhost:8000/media/CACHE/images/home/factory/5a79c9e2eb68c19c44989e2c774c8135.webp",
        "large": "http://localhost:8000/media/CACHE/images/home/factory/2a513006aef7645bcebbb8117cfe5735.webp"
      },
      "button_text": "Наши услуги",
      "button_link": "/services",
      "order": 0,
      "is_translated": true
    },
    {
      "id": 17,
      "type": "about",
      "title": "О Центре",
      "text": "Центр создан при Торгово-промышленной палате для развития промышленной кооперации.",
      "image": {
        "small": "http://localhost:8000/media/CACHE/images/home/meeting/8b7410ef3d7ceca7786da84d776e0db5.webp",
        "large": "http://localhost:8000/media/CACHE/images/home/meeting/ca4afb0087125efb7187b59616da7199.webp"
      },
      "button_text": "Подробнее",
      "button_link": "/about",
      "order": 1,
      "is_translated": true
    }
  ],
  "directions": [
    {
      "id": 25,
      "slug": "promyshlennaia-kooperatsiia",
      "title": "Промышленная кооперация",
      "short_text": "Связываем производителей для совместной работы.",
      "icon": "cooperation",
      "order": 0,
      "is_translated": true
    },
    {
      "id": 26,
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
      "id": 38,
      "slug": "delovaia-missiia-v-urumchi",
      "title": "Деловая миссия в Урумчи",
      "excerpt": "Предприниматели Кыргызстана провели переговоры с компаниями Синьцзяна.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/news/2026/10/airplane/bbcf58e3629bee6038ab5f581c86907a.webp",
        "large": "http://localhost:8000/media/CACHE/images/news/2026/10/airplane/843bb73b124bfa5afce45f7633854892.webp"
      },
      "category": {
        "slug": "missions",
        "name": "Деловые миссии"
      },
      "published_at": "2026-10-24T10:00:00+06:00",
      "is_translated": true
    },
    {
      "id": 39,
      "slug": "tsentr-podpisal-memorandum-s-torgovoi-palatoi-sintsziana",
      "title": "Центр подписал меморандум с торговой палатой Синьцзяна",
      "excerpt": "Стороны договорились о совместной работе по поиску партнёров.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/news/2026/10/signing/1ffff9a15a587674337d2c603d238ff4.webp",
        "large": "http://localhost:8000/media/CACHE/images/news/2026/10/signing/9dd5c9ce2a611c956f6f849742f9898a.webp"
      },
      "category": {
        "slug": "partnership",
        "name": "Партнёрство"
      },
      "published_at": "2026-10-20T10:00:00+06:00",
      "is_translated": true
    }
  ],
  "events": [
    {
      "id": 29,
      "slug": "vebinar-po-eksportnym-protseduram",
      "title": "Вебинар по экспортным процедурам",
      "type": {
        "code": "other",
        "label": "Другое"
      },
      "start_at": "2026-11-02T10:00:00+06:00",
      "end_at": null,
      "location": "Онлайн",
      "excerpt": "Таможня, сертификация, логистика.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/events/2026/10/webinar/36ea2b53abc7b98188d0aa92a05bb5bd.webp",
        "large": "http://localhost:8000/media/CACHE/images/events/2026/10/webinar/f8a1fade672f28ef2a8688fe7382379f.webp"
      },
      "is_upcoming": true,
      "is_translated": true
    },
    {
      "id": 30,
      "slug": "biznes-missiia-v-guanchzhou",
      "title": "Бизнес-миссия в Гуанчжоу",
      "type": {
        "code": "mission",
        "label": "Деловая миссия"
      },
      "start_at": "2026-11-15T10:00:00+06:00",
      "end_at": "2026-11-20T10:00:00+06:00",
      "location": "Гуанчжоу",
      "excerpt": "Участие в выставке и деловые встречи.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/events/2026/10/port/02bd6d6e11227eb99127b0a09640fe4e.webp",
        "large": "http://localhost:8000/media/CACHE/images/events/2026/10/port/b99273f1ead714f91d25e8f307fabca8.webp"
      },
      "is_upcoming": true,
      "is_translated": true
    }
  ],
  "seo": {
    "meta_title": "Центр промышленной кооперации при ТПП КР",
    "meta_description": "Поиск партнёров, деловые миссии и промышленная кооперация с Китаем и другими странами.",
    "og_image": "http://localhost:8000/media/CACHE/images/seo/factory/23d9754c91701b35c6e0d8f93c3443fd.webp",
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
    "og_image": "http://localhost:8000/media/CACHE/images/seo/factory/23d9754c91701b35c6e0d8f93c3443fd.webp",
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
    "id": 25,
    "slug": "promyshlennaia-kooperatsiia",
    "title": "Промышленная кооперация",
    "short_text": "Связываем производителей для совместной работы.",
    "icon": "cooperation",
    "order": 0,
    "is_translated": true
  },
  {
    "id": 26,
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
  "id": 25,
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
    "og_image": "http://localhost:8000/media/CACHE/images/seo/factory/23d9754c91701b35c6e0d8f93c3443fd.webp",
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
    "id": 22,
    "slug": "podbor-partnerov-v-kitae",
    "title": "Подбор партнёров в Китае",
    "short_text": "Поиск и проверка производителей и поставщиков.",
    "order": 0,
    "is_translated": true
  },
  {
    "id": 23,
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
  "id": 22,
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
    "og_image": "http://localhost:8000/media/CACHE/images/seo/factory/23d9754c91701b35c6e0d8f93c3443fd.webp",
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
      "id": 38,
      "slug": "delovaia-missiia-v-urumchi",
      "title": "Деловая миссия в Урумчи",
      "excerpt": "Предприниматели Кыргызстана провели переговоры с компаниями Синьцзяна.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/news/2026/10/airplane/bbcf58e3629bee6038ab5f581c86907a.webp",
        "large": "http://localhost:8000/media/CACHE/images/news/2026/10/airplane/843bb73b124bfa5afce45f7633854892.webp"
      },
      "category": {
        "slug": "missions",
        "name": "Деловые миссии"
      },
      "published_at": "2026-10-24T10:00:00+06:00",
      "is_translated": true
    },
    {
      "id": 39,
      "slug": "tsentr-podpisal-memorandum-s-torgovoi-palatoi-sintsziana",
      "title": "Центр подписал меморандум с торговой палатой Синьцзяна",
      "excerpt": "Стороны договорились о совместной работе по поиску партнёров.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/news/2026/10/signing/1ffff9a15a587674337d2c603d238ff4.webp",
        "large": "http://localhost:8000/media/CACHE/images/news/2026/10/signing/9dd5c9ce2a611c956f6f849742f9898a.webp"
      },
      "category": {
        "slug": "partnership",
        "name": "Партнёрство"
      },
      "published_at": "2026-10-20T10:00:00+06:00",
      "is_translated": true
    }
  ]
}
```

### Новость

`GET /api/v1/news/delovaia-missiia-v-urumchi/?lang=ru` → 200

```json
{
  "id": 38,
  "slug": "delovaia-missiia-v-urumchi",
  "title": "Деловая миссия в Урумчи",
  "excerpt": "Предприниматели Кыргызстана провели переговоры с компаниями Синьцзяна.",
  "content": "<p>Предприниматели Кыргызстана провели переговоры с компаниями Синьцзяна.</p><p>Центр промышленной кооперации помогает предприятиям Кыргызстана находить партнёров, выходить на новые рынки и развивать совместные производства.</p>",
  "cover": {
    "small": "http://localhost:8000/media/CACHE/images/news/2026/10/airplane/bbcf58e3629bee6038ab5f581c86907a.webp",
    "large": "http://localhost:8000/media/CACHE/images/news/2026/10/airplane/843bb73b124bfa5afce45f7633854892.webp"
  },
  "category": {
    "slug": "missions",
    "name": "Деловые миссии"
  },
  "published_at": "2026-10-24T10:00:00+06:00",
  "gallery": [
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/conference/b4dabe05cb8b3185c54ecefda771082f.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/conference/3bd53d7e976e5fd761d5800efe37bd98.webp",
      "caption": "Открытие встречи"
    },
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/meeting/546397b0616d8de6cc567852e3759c47.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/meeting/deb1e5109af02394ef2cba1518aa59ad.webp",
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
    "og_image": "http://localhost:8000/media/CACHE/images/news/2026/10/airplane/843bb73b124bfa5afce45f7633854892.webp",
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
  "id": 48,
  "slug": null,
  "title": null,
  "excerpt": null,
  "content": null,
  "cover": {
    "small": "http://localhost:8000/media/CACHE/images/news/2026/10/conference/b49b364dac47936ba2f00cb867c6f37e.webp",
    "large": "http://localhost:8000/media/CACHE/images/news/2026/10/conference/7dba2af1bd6433414bce6ce093e54240.webp"
  },
  "category": {
    "slug": "center",
    "name": "中心新闻"
  },
  "published_at": "2026-08-17T10:00:00+06:00",
  "gallery": [],
  "attachments": [],
  "is_translated": false,
  "seo": {
    "meta_title": null,
    "meta_description": null,
    "og_image": "http://localhost:8000/media/CACHE/images/news/2026/10/conference/7dba2af1bd6433414bce6ce093e54240.webp",
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
  "count": 4,
  "next": "http://localhost:8000/api/v1/events/?lang=ru&page=2&page_size=2&when=upcoming",
  "previous": null,
  "results": [
    {
      "id": 29,
      "slug": "vebinar-po-eksportnym-protseduram",
      "title": "Вебинар по экспортным процедурам",
      "type": {
        "code": "other",
        "label": "Другое"
      },
      "start_at": "2026-11-02T10:00:00+06:00",
      "end_at": null,
      "location": "Онлайн",
      "excerpt": "Таможня, сертификация, логистика.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/events/2026/10/webinar/36ea2b53abc7b98188d0aa92a05bb5bd.webp",
        "large": "http://localhost:8000/media/CACHE/images/events/2026/10/webinar/f8a1fade672f28ef2a8688fe7382379f.webp"
      },
      "is_upcoming": true,
      "is_translated": true
    },
    {
      "id": 30,
      "slug": "biznes-missiia-v-guanchzhou",
      "title": "Бизнес-миссия в Гуанчжоу",
      "type": {
        "code": "mission",
        "label": "Деловая миссия"
      },
      "start_at": "2026-11-15T10:00:00+06:00",
      "end_at": "2026-11-20T10:00:00+06:00",
      "location": "Гуанчжоу",
      "excerpt": "Участие в выставке и деловые встречи.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/events/2026/10/port/02bd6d6e11227eb99127b0a09640fe4e.webp",
        "large": "http://localhost:8000/media/CACHE/images/events/2026/10/port/b99273f1ead714f91d25e8f307fabca8.webp"
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
  "id": 25,
  "slug": "business-mission-to-xinjiang",
  "title": "Business mission to Xinjiang",
  "type": {
    "code": "mission",
    "label": "Business mission"
  },
  "start_at": "2026-08-27T10:00:00+06:00",
  "end_at": "2026-08-30T10:00:00+06:00",
  "location": "Urumqi",
  "excerpt": "Company visits and negotiations.",
  "content": "<p>Company visits and negotiations.</p><p>The Industrial Cooperation Centre helps Kyrgyz companies find partners, enter new markets and develop joint production.</p>",
  "cover": {
    "small": "http://localhost:8000/media/CACHE/images/events/2026/10/mountain-road/83c1c5f7026def9f44fd50df348ccb49.webp",
    "large": "http://localhost:8000/media/CACHE/images/events/2026/10/mountain-road/aefbd2bbc7955f8a663f1f55b5defeff.webp"
  },
  "is_upcoming": false,
  "gallery": [
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/conference_yc6iKh0/7f912da71b7fd19289009c6de5f4e648.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/conference_yc6iKh0/1e55ec6568f50b95fd84873193179498.webp",
      "caption": "Opening of the meeting"
    },
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/meeting_nDmfUma/cea31d7b9df2ed6bcbcfa681faed4494.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/meeting_nDmfUma/536de65eeeedf0630a3ebaac42b4a0e9.webp",
      "caption": "Negotiations"
    }
  ],
  "attachments": [],
  "is_translated": true,
  "seo": {
    "meta_title": "Business mission to Xinjiang",
    "meta_description": "Company visits and negotiations.",
    "og_image": "http://localhost:8000/media/CACHE/images/events/2026/10/mountain-road/aefbd2bbc7955f8a663f1f55b5defeff.webp",
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
    "id": 7,
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
    "id": 8,
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
    "id": 13,
    "name": "Торговая компания «Шёлковый путь» (демо)",
    "logo": {
      "small": "http://localhost:8000/media/CACHE/images/partners/logo-32/f83228973b81584c8d298049ef47f002.webp",
      "large": "http://localhost:8000/media/CACHE/images/partners/logo-32/bde39ccc74ddce843ee85607d6097b39.webp"
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
    "id": 14,
    "name": "«Тяньшань Машинери» (демо)",
    "logo": {
      "small": "http://localhost:8000/media/CACHE/images/partners/logo-33/ddf280687dce28f1a07952388926c146.webp",
      "large": "http://localhost:8000/media/CACHE/images/partners/logo-33/3e68ea1ddbe67135b5a613652a569b92.webp"
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
      "id": 10,
      "slug": "sovmestnoe-proizvodstvo-stroimaterialov-v-chuiskoi-oblasti",
      "title": "Совместное производство стройматериалов в Чуйской области",
      "excerpt": "Запуск завода мощностью 100 тыс. тонн в год.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/projects/2026/10/construction/7e2c6523ae7e934b8794fc3b31865e35.webp",
        "large": "http://localhost:8000/media/CACHE/images/projects/2026/10/construction/9a2d86b3d31b56c231d8f49e80e1f971.webp"
      },
      "country": {
        "code": "CN",
        "name": "Китай"
      },
      "published_at": "2026-10-16T10:00:00+06:00",
      "is_translated": true
    },
    {
      "id": 11,
      "slug": "lokalizatsiia-sborki-selkhoztekhniki",
      "title": "Локализация сборки сельхозтехники",
      "excerpt": "Сборка тракторов из машинокомплектов.",
      "cover": {
        "small": "http://localhost:8000/media/CACHE/images/projects/2026/10/tractor/cd658784c1318cd4773746f430541ec6.webp",
        "large": "http://localhost:8000/media/CACHE/images/projects/2026/10/tractor/745962c7539d952b1ae852a9182fe8ec.webp"
      },
      "country": {
        "code": "CN",
        "name": "Китай"
      },
      "published_at": "2026-09-16T10:00:00+06:00",
      "is_translated": true
    }
  ]
}
```

### Проект

`GET /api/v1/projects/sovmestnoe-proizvodstvo-stroimaterialov-v-chuiskoi-oblasti/?lang=zh` → 200

```json
{
  "id": 10,
  "slug": "chu-he-zhou-jian-cai-he-zi-sheng-chan",
  "title": "楚河州建材合资生产",
  "excerpt": "建设年产10万吨的工厂。",
  "content": "<p>建设年产10万吨的工厂。</p><p>工业合作中心帮助吉尔吉斯斯坦企业寻找合作伙伴、开拓新市场并发展合资生产。</p>",
  "cover": {
    "small": "http://localhost:8000/media/CACHE/images/projects/2026/10/construction/7e2c6523ae7e934b8794fc3b31865e35.webp",
    "large": "http://localhost:8000/media/CACHE/images/projects/2026/10/construction/9a2d86b3d31b56c231d8f49e80e1f971.webp"
  },
  "country": {
    "code": "CN",
    "name": "中国"
  },
  "published_at": "2026-10-16T10:00:00+06:00",
  "partners": [
    {
      "id": 13,
      "name": "丝路贸易有限公司（演示）",
      "logo": {
        "small": "http://localhost:8000/media/CACHE/images/partners/logo-32/f83228973b81584c8d298049ef47f002.webp",
        "large": "http://localhost:8000/media/CACHE/images/partners/logo-32/bde39ccc74ddce843ee85607d6097b39.webp"
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
      "id": 14,
      "name": "天山机械（演示）",
      "logo": {
        "small": "http://localhost:8000/media/CACHE/images/partners/logo-33/ddf280687dce28f1a07952388926c146.webp",
        "large": "http://localhost:8000/media/CACHE/images/partners/logo-33/3e68ea1ddbe67135b5a613652a569b92.webp"
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
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/conference_bWmtfBX/9d12a19169e08915b5bbd92c9d791606.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/conference_bWmtfBX/5b9698ac59966be4e4cfda77a0591a34.webp",
      "caption": "会议开幕"
    },
    {
      "small": "http://localhost:8000/media/CACHE/images/gallery/2026/10/meeting_WOD8vu9/6930bad2611fe4fbf2589b2f33ce4fa8.webp",
      "large": "http://localhost:8000/media/CACHE/images/gallery/2026/10/meeting_WOD8vu9/d72d12d066526f6c04c4fc3d83da9d88.webp",
      "caption": "洽谈"
    }
  ],
  "attachments": [],
  "presentations": [
    {
      "id": 6,
      "slug": "chu-he-zhou-jian-cai-chang-tou-zi-jian-yi-shu",
      "title": "楚河州建材厂：投资建议书",
      "excerpt": "产能、建设周期及合作伙伴参与条件。",
      "category": "projects",
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
    "og_image": "http://localhost:8000/media/CACHE/images/projects/2026/10/construction/9a2d86b3d31b56c231d8f49e80e1f971.webp",
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
      "id": 6,
      "slug": "zavod-stroimaterialov-v-chuiskoi-oblasti-investitsionnoe-predlozhenie",
      "title": "Завод стройматериалов в Чуйской области: инвестиционное предложение",
      "excerpt": "Мощности, сроки строительства и условия участия партнёров.",
      "category": "projects",
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
      "id": 7,
      "slug": "lokalizatsiia-sborki-traktorov-etapy-i-trebovaniia",
      "title": "Локализация сборки тракторов: этапы и требования",
      "excerpt": "Как устроена сборка из машинокомплектов и что требуется от площадки.",
      "category": "projects",
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
  "id": 7,
  "slug": "lokalizatsiia-sborki-traktorov-etapy-i-trebovaniia",
  "title": "Локализация сборки тракторов: этапы и требования",
  "excerpt": "Как устроена сборка из машинокомплектов и что требуется от площадки.",
  "content": "<p>Как устроена сборка из машинокомплектов и что требуется от площадки.</p><p>Центр промышленной кооперации помогает предприятиям Кыргызстана находить партнёров, выходить на новые рынки и развивать совместные производства.</p>",
  "category": "projects",
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
    "small": "http://localhost:8000/media/CACHE/images/seo/factory/7aa6beb1249164fbc9e0ce964f548656.webp",
    "large": "http://localhost:8000/media/CACHE/images/seo/factory/23d9754c91701b35c6e0d8f93c3443fd.webp"
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
