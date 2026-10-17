# Сайт ЦПК при ТПП КР — frontend

Next.js 15 (App Router) · TypeScript · Tailwind CSS v4 · next-intl · ISR 60 с.

## Запуск

```bash
npm install
cp .env.example .env.local   # по умолчанию NEXT_PUBLIC_USE_MOCKS=true — бэк не нужен
npm run dev                  # http://localhost:3000 → /ru
```

| Переменная | Что делает |
|---|---|
| `NEXT_PUBLIC_USE_MOCKS` | `true` — данные из `mocks/`, `false` — из API |
| `API_URL` | адрес API Айбека, например `http://localhost:8000/api/v1` (только сервер) |
| `NEXT_PUBLIC_SITE_URL` | публичный адрес сайта для canonical / hreflang / OG |

Проверки перед PR: `npm run typecheck && npm run lint && npm run build`.

## Структура

```
app/[locale]/          страницы; layout.tsx — html lang, шрифты, Header/Footer
app/api/feedback/      прокси POST /feedback/ (в режиме моков — фейковый ответ)
components/ui/         Button, Card, Badge, SectionTitle, Breadcrumbs, PageHeader,
                       NewsCard, EventCard, DirectionCard, RichText, Gallery, Attachments, Icon
components/layout/     Header, Footer, LanguageSwitcher, MobileMenu, Alternates
components/sections/   CtaBlock и блоки страниц
i18n/                  routing (ru/en/zh), navigation (Link, useRouter), request
lib/api.ts             все запросы к API; переключение на моки
lib/api-types.ts       типы ответов (временно, до Swagger)
lib/seo.ts             buildMetadata(): title, description, canonical, hreflang, OG
lib/format.ts          даты по языку, размер файла
lib/feedback.ts        sendFeedback() для FeedbackForm
messages/*.json        тексты интерфейса на трёх языках
mocks/                 данные моков + handlers.ts (фейковый бэкенд)
```

## Правила

- **Текст в JSX не пишем.** Всё из `messages/{ru,en,zh}.json` через `useTranslations` / `getTranslations`. Ключ добавляем сразу во все три файла. TypeScript проверяет ключи по `ru.json`.
- **Ссылки только через `Link` из `@/i18n/navigation`**: он сам добавляет `/ru`, `/en`, `/zh`. Пишем `href="/news"`, а не `/ru/news`.
- **Цвета только токенами:** `bg-primary`, `bg-primary-light`, `text-text`, `text-muted`, `border-border`. Токены лежат в `app/globals.css` (`@theme`). В Tailwind v4 нет `tailwind.config`, токены задаются там.
- **Контейнер:** `container-page` (1200 px + 16 px по краям).
- **Картинки только через `next/image`** с `sizes`; первый экран — `priority`.
- **Даты:** `formatDate(value, locale)`, `formatDateRange(start, end, locale)`.
- В каждом `page.tsx` указываем `export const revalidate = 60;` (литерал — Next не принимает импортированную константу) и `setRequestLocale(locale)`.

## Как сделать детальную страницу (для Ариета)

```tsx
// app/[locale]/news/[slug]/page.tsx
import {notFound} from 'next/navigation';
import {setRequestLocale} from 'next-intl/server';
import {SetAlternates} from '@/components/layout/Alternates';
import type {Locale} from '@/i18n/routing';
import {getNewsItem} from '@/lib/api';
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
    description: item.summary,
    image: item.cover?.url,
    noindex: !item.is_translated
  });
}

export default async function NewsPage({params}: Props) {
  const {locale, slug} = await params;
  setRequestLocale(locale);
  const item = await getNewsItem(locale, decodeURIComponent(slug));
  if (!item) notFound();
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

## Моки

Записи в `mocks/*.json` хранятся как модели с переводами: `{"title": {"ru": "...", "en": "...", "zh": "..."}}`, картинка задаётся ключом из `images.json`. `mocks/handlers.ts` собирает из них ответы в формате `lib/api-types.ts`: выбирает язык, собирает `seo.alternates` и `is_translated`, применяет фильтры (`?category=`, `?status=upcoming|past`, `?type=`, `?country=`) и пагинацию (`page`, `page_size`).

Тестовые случаи:
- `/ru/news/delovaya-missiya` ↔ `/en/news/business-mission`: новость с переводом;
- `/ru/news/iniciativa-sozdaniya-centra`: только на русском;
- `/en/news/eaeu-seminar`: нет китайского;
- в новостях на русском 11 штук, чтобы проверить «Загрузить ещё» по 9;
- форма (`/api/feedback` в режиме моков): email на `@example.invalid` → 400 под полем, тема `429` → 429.

## Форма обратной связи

```ts
import {sendFeedback} from '@/lib/feedback';
const result = await sendFeedback({...values, type: 'contact', locale, website: honeypot});
// result.ok | result.status === 400 → result.errors.{field} | result.status === 429
```

## Типы из Swagger

Когда Айбек поднимет схему: `npm run gen:types` (берёт `http://localhost:8000/api/schema/`) → `lib/api-schema.d.ts`. После этого интерфейсы в `lib/api-types.ts` заменяем на `components['schemas'][...]`.
