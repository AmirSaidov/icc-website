# Сайт ЦПК при ТПП КР — frontend

Next.js 15 (App Router) · TypeScript · Tailwind CSS v4 · next-intl · ISR 60 с.

## Запуск

Фронт работает только с бэком, моков нет. Сначала поднять бэк (`backend/README.md`: `migrate`, `createcachetable`, `seed`, `runserver`), потом:

```bash
npm install
cp .env.example .env.local
npm run dev                  # http://localhost:3000 → /ru
```

| Переменная | Что делает |
|---|---|
| `API_URL` | адрес API, локально `http://127.0.0.1:8000/api/v1` (только сервер). Именно `127.0.0.1`: Node резолвит `localhost` в IPv6, а runserver слушает IPv4 |
| `NEXT_PUBLIC_SITE_URL` | публичный адрес сайта для canonical / hreflang / OG |

Сборке бэк не нужен: страницы рендерятся при первом запросе и кэшируются на 60 с (`generateStaticParams` в layout возвращает `[]`). Страницы с фильтрами (`searchParams`) — `dynamic = "force-dynamic"`, ответы API кэшируются в `fetch`. Деплой — [../DEPLOY.md](../DEPLOY.md).

Проверки перед PR: `npm run typecheck && npm run lint && npm run build`.

## Структура

```
app/[locale]/          страницы; layout.tsx — html lang, шрифты, Header/Footer
app/[locale]/[...slug] страницы редактора /{slug} из админки и 404 для остальных адресов
app/api/feedback/      прокси POST /feedback/ → Django
app/robots.ts          robots.txt; app/sitemap.xml/ — sitemap бэка с домена сайта
components/ui/         Button, Card, Badge, SectionTitle, Breadcrumbs, PageHeader,
                       NewsCard, EventCard, DirectionCard, RichText, Gallery, Attachments, Icon
components/layout/     Header, Footer, LanguageSwitcher, MobileMenu, Alternates
components/sections/   CtaBlock и блоки страниц
i18n/                  routing (ru/en/zh), navigation (Link, useRouter), request
lib/api.ts             все запросы к API (язык — параметром ?lang=)
lib/api-types.ts       имена типов ответов → lib/api-schema.d.ts (генерируется из openapi.yaml)
lib/detail.ts          redirectToOwnSlug(): 308 на slug записи на текущем языке
lib/seo.ts             buildMetadata(): title, description, canonical, hreflang, OG
lib/format.ts          даты по языку, размер файла
lib/feedback.ts        sendFeedback() для FeedbackForm
messages/*.json        тексты интерфейса на трёх языках
```

## Правила

- **Текст в JSX не пишем.** Всё из `messages/{ru,en,zh}.json` через `useTranslations` / `getTranslations`. Ключ добавляем сразу во все три файла. TypeScript проверяет ключи по `ru.json`.
- **Ссылки только через `Link` из `@/i18n/navigation`**: он сам добавляет `/ru`, `/en`, `/zh`. Пишем `href="/news"`, а не `/ru/news`.
- **Цвета только токенами:** `bg-primary`, `bg-primary-light`, `text-text`, `text-muted`, `border-border`. Токены лежат в `app/globals.css` (`@theme`). В Tailwind v4 нет `tailwind.config`, токены задаются там.
- **Контейнер:** `container-page` (1200 px + 16 px по краям).
- **Картинки только через `next/image`** с `sizes`; первый экран — `priority`.
- **Даты:** `formatDate(value, locale)`, `formatDateRange(start, end, locale)`.
- В каждом `page.tsx` указываем `export const revalidate = 60;` (литерал — Next не принимает импортированную константу) и `setRequestLocale(locale)`.

## Детальная страница

```tsx
// app/[locale]/news/[slug]/page.tsx
import {notFound} from 'next/navigation';
import {setRequestLocale} from 'next-intl/server';
import {SetAlternates} from '@/components/layout/Alternates';
import type {Locale} from '@/i18n/routing';
import {getNewsItem} from '@/lib/api';
import {redirectToOwnSlug} from '@/lib/detail';
import {buildMetadata, detailPaths} from '@/lib/seo';

export const revalidate = 60;
type Props = {params: Promise<{locale: Locale; slug: string}>};

export async function generateMetadata({params}: Props) {
  const {locale, slug} = await params;
  const item = await getNewsItem(locale, decodeURIComponent(slug));
  if (!item) return {};
  return buildMetadata({
    locale,
    paths: detailPaths('news', item.seo.alternates),
    seo: item.seo,
    title: item.title,
    description: item.excerpt,
    image: item.cover?.large,
    noindex: !item.is_translated
  });
}

export default async function NewsPage({params}: Props) {
  const {locale, slug: rawSlug} = await params;
  const slug = decodeURIComponent(rawSlug);
  setRequestLocale(locale);
  const item = await getNewsItem(locale, slug);
  if (!item) notFound();
  // бэк находит запись по slug на любом языке — поправляем адрес
  redirectToOwnSlug(locale, 'news', slug, item);
  return (
    <>
      {/* обязательно: без этого переключатель языка уведёт на список */}
      <SetAlternates section="news" slugs={item.seo.alternates} />
      ...
    </>
  );
}
```

Переключатель языка работает так:
- на статических страницах меняет только префикс;
- на детальных берёт slug из `SetAlternates`;
- если перевода нет, ведёт на список раздела.

Непереведённая запись приходит со статусом 200, `is_translated: false` и `title: null`: показываем заглушку `untranslated`, в метаданных `noindex`.

**Не добавлять `loading.tsx` над детальными страницами:** со стримингом статус 200 уходит раньше, чем страница вызовет `notFound()` или редирект, и вместо 404/308 получается 200.

Картинки с бэка — `{small, large}` (WebP 400 и 1200 px): в карточках `small`, на первом экране и в детальной `large`.

## Проверка на данных seed

- `/ru/news/delovaia-missiia-v-urumchi` ↔ `/en/news/business-mission-to-urumqi`: новость с переводом;
- `/en/news/delovaia-missiia-v-urumchi` → 308 на английский slug;
- `/zh/news/vstrecha-s-predprinimateliami-osha`: нет китайского — заглушка и `noindex`;
- `/ru/news/no-such-news` → 404.

## Форма обратной связи

```ts
import {sendFeedback} from '@/lib/feedback';
const result = await sendFeedback({...values, type: 'contact', lang: locale, website: honeypot});
// result.ok | result.status === 400 → result.errors.{field} | result.status === 429
```

Поля — как в `FeedbackRequest` из схемы: `full_name`, `lang`, `phone` (или `null`). Лимит бэка — 5 обращений в час с одного IP, считаются и отклонённые.

## Типы из схемы бэка

Айбек поменял API → `npm run gen:types` (берёт `../backend/docs/openapi.yaml`) → `lib/api-schema.d.ts` → `npm run typecheck` покажет, что сломалось.
