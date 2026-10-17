/**
 * Фейковый бэкенд для NEXT_PUBLIC_USE_MOCKS=true.
 *
 * JSON в этой папке хранит записи как модели с переводами (как modeltranslation):
 * переводимое поле — объект {ru, en, zh}, картинка — ключ из images.json.
 * Здесь они превращаются в ответы по контракту из lib/api-types.ts:
 * выбирается язык, собираются seo.alternates, is_translated, related, пагинация.
 */
import {routing, type Locale} from '@/i18n/routing';
import {ApiError} from '@/lib/api';
import type * as T from '@/lib/api-types';

import contactsData from './contacts.json';
import cooperationData from './cooperation.json';
import directionsData from './directions.json';
import documentsData from './documents.json';
import eventsData from './events.json';
import homeData from './home.json';
import imagesData from './images.json';
import newsData from './news.json';
import pagesData from './pages.json';
import servicesData from './services.json';

type L10n = Partial<Record<Locale, string>>;
type ImageKey = keyof typeof imagesData;

const tr = (value: L10n | undefined, locale: Locale) => value?.[locale] ?? '';

function image(key: string | null | undefined, locale: Locale): T.ImageAsset | null {
  const img = key ? imagesData[key as ImageKey] : undefined;
  if (!img) return null;
  return {url: img.url, width: img.width, height: img.height, alt: tr(img.alt, locale)};
}

function seo(
  item: {slug: L10n; title: L10n; summary?: L10n; cover?: string},
  locale: Locale
): T.Seo {
  return {
    title: tr(item.title, locale),
    description: tr(item.summary, locale),
    og_image: image(item.cover, locale)?.url ?? null,
    alternates: Object.fromEntries(
      routing.locales.filter((l) => item.slug[l]).map((l) => [l, item.slug[l]])
    )
  };
}

/** Запись на языке locale; если по slug другого языка — is_translated: false. */
function findBySlug<I extends {slug: L10n}>(items: I[], slug: string, locale: Locale) {
  const exact = items.find((item) => item.slug[locale] === slug);
  if (exact) return {item: exact, translated: true};
  const other = items.find((item) => Object.values(item.slug).includes(slug));
  if (other) return {item: other, translated: false};
  throw new ApiError(404, `mock: ${slug} not found`);
}

function paginate<I>(items: I[], params: URLSearchParams, path: string): T.Paginated<I> {
  const page = Math.max(1, Number(params.get('page') ?? 1));
  const size = Math.max(1, Number(params.get('page_size') ?? 9));
  const results = items.slice((page - 1) * size, page * size);
  const link = (p: number) => {
    const next = new URLSearchParams(params);
    next.set('page', String(p));
    return `${path}?${next}`;
  };
  return {
    count: items.length,
    next: page * size < items.length ? link(page + 1) : null,
    previous: page > 1 ? link(page - 1) : null,
    results
  };
}

// ——— Направления и услуги ———

type DirectionRow = (typeof directionsData)[number];
type ServiceRow = (typeof servicesData)[number];

const directionListItem = (d: DirectionRow, locale: Locale): T.DirectionListItem => ({
  id: d.id,
  slug: tr(d.slug, locale),
  title: tr(d.title, locale),
  summary: tr(d.summary, locale),
  icon: d.icon
});

const serviceListItem = (s: ServiceRow, locale: Locale): T.ServiceListItem => ({
  id: s.id,
  slug: tr(s.slug, locale),
  title: tr(s.title, locale),
  summary: tr(s.summary, locale),
  icon: s.icon
});

// ——— Новости ———

type NewsRow = (typeof newsData.items)[number] & {gallery?: string[]; attachments?: AttachmentRow[]};
type AttachmentRow = {id: number; title: L10n; url: string; size: number; ext: string};
const newsRows = newsData.items as NewsRow[];

function newsCategory(slug: string, locale: Locale): T.NewsCategory | null {
  const category = newsData.categories.find((c) => c.slug === slug);
  return category ? {slug: category.slug, title: tr(category.title, locale)} : null;
}

const newsListItem = (n: NewsRow, locale: Locale): T.NewsListItem => ({
  id: n.id,
  slug: tr(n.slug, locale),
  title: tr(n.title, locale),
  summary: tr(n.summary, locale),
  published_at: n.published_at,
  cover: image(n.cover, locale),
  category: newsCategory(n.category, locale)
});

const attachments = (rows: AttachmentRow[] | undefined, locale: Locale): T.Attachment[] =>
  (rows ?? []).map((a) => ({...a, title: tr(a.title, locale)}));

/** Новости на языке locale, новые сверху. */
const newsIn = (locale: Locale) =>
  newsRows
    .filter((n) => n.slug[locale])
    .sort((a, b) => b.published_at.localeCompare(a.published_at));

// ——— Мероприятия ———

type EventRow = (typeof eventsData)[number] & {gallery?: string[]; attachments?: AttachmentRow[]};
const eventRows = eventsData as EventRow[];

const today = () => new Date().toISOString().slice(0, 10);
const isUpcoming = (e: EventRow) => (e.end_date ?? e.start_date) >= today();

const eventListItem = (e: EventRow, locale: Locale): T.EventListItem => ({
  id: e.id,
  slug: tr(e.slug, locale),
  title: tr(e.title, locale),
  summary: tr(e.summary, locale),
  type: e.type as T.EventType,
  start_date: e.start_date,
  end_date: e.end_date,
  location: tr(e.location, locale),
  cover: image(e.cover, locale)
});

/** Предстоящие — ближайшие первыми, архив — последние первыми. */
function eventsIn(locale: Locale, status: T.EventStatus) {
  const list = eventRows.filter((e) => e.slug[locale] && isUpcoming(e) === (status === 'upcoming'));
  return list.sort((a, b) =>
    status === 'upcoming'
      ? a.start_date.localeCompare(b.start_date)
      : b.start_date.localeCompare(a.start_date)
  );
}

// ——— Роутер ———

type Handler = (match: RegExpMatchArray, locale: Locale, params: URLSearchParams) => unknown;

const routes: [RegExp, Handler][] = [
  [
    /^\/home\/$/,
    (_, locale): T.Home => ({
      hero: {
        title: tr(homeData.hero.title, locale),
        subtitle: tr(homeData.hero.subtitle, locale),
        image: image(homeData.hero.image, locale)!
      },
      about: {title: tr(homeData.about.title, locale), text: tr(homeData.about.text, locale)},
      directions: directionsData.slice(0, 4).map((d) => directionListItem(d, locale)),
      cooperation: {
        title: tr(homeData.cooperation.title, locale),
        text: tr(homeData.cooperation.text, locale),
        image: image(homeData.cooperation.image, locale)
      },
      advantages: homeData.advantages.map((a) => ({
        icon: a.icon,
        title: tr(a.title, locale),
        text: tr(a.text, locale)
      })),
      news: newsIn(locale).slice(0, 3).map((n) => newsListItem(n, locale)),
      events: eventsIn(locale, 'upcoming').slice(0, 3).map((e) => eventListItem(e, locale)),
      seo: {
        title: tr(homeData.hero.title, locale),
        description: tr(homeData.hero.subtitle, locale),
        og_image: image(homeData.hero.image, locale)?.url ?? null,
        alternates: {ru: '', en: '', zh: ''}
      }
    })
  ],
  [
    /^\/pages\/([\w-]+)\/$/,
    ([, slug], locale): T.Page => {
      const page = pagesData[slug as keyof typeof pagesData];
      if (!page) throw new ApiError(404, `mock: page ${slug} not found`);
      return {
        slug,
        title: tr(page.title, locale),
        lead: tr(page.lead, locale),
        content: tr(page.content, locale),
        leadership: page.leadership,
        is_translated: Boolean(page.title[locale as keyof typeof page.title]),
        seo: {
          title: tr(page.title, locale),
          description: tr(page.lead, locale),
          og_image: null,
          alternates: {ru: slug, en: slug, zh: slug}
        }
      };
    }
  ],
  [
    /^\/documents\/$/,
    (_, locale): T.DocumentFile[] =>
      documentsData.map((d) => ({...d, kind: d.kind as T.DocumentFile['kind'], title: tr(d.title, locale)}))
  ],
  [
    /^\/directions\/$/,
    (_, locale) => directionsData.filter((d) => d.slug[locale]).map((d) => directionListItem(d, locale))
  ],
  [
    /^\/directions\/([^/]+)\/$/,
    ([, slug], locale): T.Direction => {
      const {item, translated} = findBySlug(directionsData, decodeURIComponent(slug), locale);
      return {
        ...directionListItem(item, locale),
        slug: translated ? tr(item.slug, locale) : decodeURIComponent(slug),
        content: tr(item.content, locale),
        is_translated: translated,
        seo: seo(item, locale)
      };
    }
  ],
  [
    /^\/services\/$/,
    (_, locale) => servicesData.filter((s) => s.slug[locale]).map((s) => serviceListItem(s, locale))
  ],
  [
    /^\/services\/([^/]+)\/$/,
    ([, slug], locale): T.Service => {
      const {item, translated} = findBySlug(servicesData, decodeURIComponent(slug), locale);
      const person = item.contact_person;
      return {
        ...serviceListItem(item, locale),
        slug: translated ? tr(item.slug, locale) : decodeURIComponent(slug),
        content: tr(item.content, locale),
        steps: item.steps.map((s) => ({title: tr(s.title, locale), text: tr(s.text, locale)})),
        contact_person: person
          ? {...person, name: tr(person.name, locale), position: tr(person.position, locale)}
          : null,
        is_translated: translated,
        seo: seo(item, locale)
      };
    }
  ],
  [
    /^\/news\/categories\/$/,
    (_, locale) => newsData.categories.map((c) => newsCategory(c.slug, locale))
  ],
  [
    /^\/news\/$/,
    (_, locale, params) => {
      const category = params.get('category');
      const list = newsIn(locale).filter((n) => !category || n.category === category);
      return paginate(list.map((n) => newsListItem(n, locale)), params, '/news/');
    }
  ],
  [
    /^\/news\/([^/]+)\/$/,
    ([, slug], locale): T.NewsItem => {
      const {item, translated} = findBySlug(newsRows, decodeURIComponent(slug), locale);
      const others = newsIn(locale).filter((n) => n.id !== item.id);
      const related = [
        ...others.filter((n) => n.category === item.category),
        ...others.filter((n) => n.category !== item.category)
      ].slice(0, 3);
      return {
        ...newsListItem(item, locale),
        slug: translated ? tr(item.slug, locale) : decodeURIComponent(slug),
        content: tr(item.content, locale),
        gallery: (item.gallery ?? []).map((key) => image(key, locale)!).filter(Boolean),
        attachments: attachments(item.attachments, locale),
        related: related.map((n) => newsListItem(n, locale)),
        is_translated: translated,
        seo: seo(item, locale)
      };
    }
  ],
  [
    /^\/events\/$/,
    (_, locale, params) => {
      const status = params.get('status') === 'past' ? 'past' : 'upcoming';
      const type = params.get('type');
      const list = eventsIn(locale, status).filter((e) => !type || e.type === type);
      return paginate(list.map((e) => eventListItem(e, locale)), params, '/events/');
    }
  ],
  [
    /^\/events\/([^/]+)\/$/,
    ([, slug], locale): T.EventItem => {
      const {item, translated} = findBySlug(eventRows, decodeURIComponent(slug), locale);
      const related = eventsIn(locale, 'upcoming').filter((e) => e.id !== item.id).slice(0, 3);
      return {
        ...eventListItem(item, locale),
        slug: translated ? tr(item.slug, locale) : decodeURIComponent(slug),
        content: tr(item.content, locale),
        gallery: (item.gallery ?? []).map((key) => image(key, locale)!).filter(Boolean),
        attachments: attachments(item.attachments, locale),
        related: related.map((e) => eventListItem(e, locale)),
        is_translated: translated,
        seo: seo(item, locale)
      };
    }
  ],
  [
    /^\/countries\/$/,
    (_, locale): T.Country[] =>
      cooperationData.countries.map((c) => ({id: c.id, code: c.code, name: tr(c.name, locale)}))
  ],
  [
    /^\/partners\/$/,
    (_, locale, params): T.Partner[] => {
      const country = params.get('country');
      return cooperationData.partners
        .filter((p) => !country || p.country === country)
        .map((p) => ({
          id: p.id,
          name: tr(p.name, locale),
          url: p.url,
          country: p.country,
          logo: {url: p.logo, alt: tr(p.name, locale), width: 240, height: 120}
        }));
    }
  ],
  [
    /^\/projects\/$/,
    (_, locale, params): T.Project[] => {
      const country = params.get('country');
      return cooperationData.projects
        .filter((p) => !country || p.country === country)
        .map((p) => ({
          id: p.id,
          title: tr(p.title, locale),
          summary: tr(p.summary, locale),
          cover: image(p.cover, locale),
          country: p.country
        }));
    }
  ],
  [
    /^\/contacts\/$/,
    (_, locale): T.Contacts => ({
      ...contactsData,
      name: tr(contactsData.name, locale),
      address: tr(contactsData.address, locale),
      schedule: tr(contactsData.schedule, locale),
      socials: contactsData.socials as T.SocialLink[]
    })
  ]
];

export function mockGet(path: string, locale: Locale, params: URLSearchParams): unknown {
  for (const [pattern, handler] of routes) {
    const match = path.match(pattern);
    if (match) return structuredClone(handler(match, locale, params));
  }
  throw new ApiError(404, `mock: no handler for ${path}`);
}
