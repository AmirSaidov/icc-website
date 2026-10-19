import 'server-only';
import {notFound} from 'next/navigation';
import {hasLocale} from 'next-intl';
import {routing, type Locale} from '@/i18n/routing';
import type {
  Contacts,
  Country,
  Direction,
  DirectionListItem,
  DocumentFile,
  EventItem,
  EventListItem,
  EventTypeCode,
  EventTypeOption,
  EventWhen,
  Home,
  NewsCategory,
  NewsItem,
  NewsListItem,
  Page,
  Paginated,
  Partner,
  Project,
  ProjectListItem,
  Service,
  ServiceListItem
} from './api-types';

/** Адрес API Айбека, например https://icc.pythonanywhere.com/api/v1 (только сервер Next.js). */
export const API_URL = (process.env.API_URL ?? 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '');
/** ISR: страницы и запросы обновляются раз в 60 секунд. */
export const REVALIDATE = 60;
export const NEWS_PAGE_SIZE = 9;

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export type Query = Record<string, string | number | null | undefined>;

function toSearchParams(locale: Locale, query?: Query) {
  // Бэк читает язык только из ?lang= (ru | en | zh), Accept-Language игнорирует.
  const params = new URLSearchParams({lang: locale});
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined && value !== null && value !== '') params.set(key, String(value));
  }
  return params;
}

async function get<T>(path: string, locale: Locale, query?: Query): Promise<T> {
  // /robots.txt, /wp-login.php и т.п. попадают в [locale]: generateMetadata страницы
  // выполняется раньше проверки в layout, и без этой строки бэк отвечал 400, а сайт — 500.
  if (!hasLocale(routing.locales, locale)) notFound();
  const res = await fetch(`${API_URL}${path}?${toSearchParams(locale, query)}`, {
    headers: {Accept: 'application/json'},
    next: {revalidate: REVALIDATE}
  });
  if (!res.ok) throw new ApiError(res.status, `GET ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

/** Для детальных страниц: 404 → null, страница вызывает notFound(). */
async function getOrNull<T>(path: string, locale: Locale, query?: Query): Promise<T | null> {
  try {
    return await get<T>(path, locale, query);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

const slugPath = (slug: string) => encodeURIComponent(slug);

// ——— Главная и страницы ———

export const getHome = (locale: Locale) => get<Home>('/home/', locale);

/** Системная страница по key (about, cooperation) или страница редактора по slug на любом языке. */
export const getPage = (locale: Locale, keyOrSlug: string) =>
  getOrNull<Page>(`/pages/${slugPath(keyOrSlug)}/`, locale);

export const getDocuments = (locale: Locale) => get<DocumentFile[]>('/documents/', locale);

// ——— Направления, услуги ———

export const getDirections = (locale: Locale) =>
  get<DirectionListItem[]>('/directions/', locale);

export const getDirection = (locale: Locale, slug: string) =>
  getOrNull<Direction>(`/directions/${slugPath(slug)}/`, locale);

export const getServices = (locale: Locale) => get<ServiceListItem[]>('/services/', locale);

export const getService = (locale: Locale, slug: string) =>
  getOrNull<Service>(`/services/${slugPath(slug)}/`, locale);

// ——— Новости, мероприятия ———

export const getNews = (
  locale: Locale,
  {category, page = 1, pageSize = NEWS_PAGE_SIZE}: {category?: string; page?: number; pageSize?: number} = {}
) => get<Paginated<NewsListItem>>('/news/', locale, {category, page, page_size: pageSize});

export const getNewsItem = (locale: Locale, slug: string) =>
  getOrNull<NewsItem>(`/news/${slugPath(slug)}/`, locale);

export const getNewsCategories = (locale: Locale) =>
  get<NewsCategory[]>('/news-categories/', locale);

export const getEvents = (
  locale: Locale,
  {when, type, page = 1, pageSize = NEWS_PAGE_SIZE}: {when?: EventWhen; type?: EventTypeCode; page?: number; pageSize?: number} = {}
) => get<Paginated<EventListItem>>('/events/', locale, {when, type, page, page_size: pageSize});

export const getEvent = (locale: Locale, slug: string) =>
  getOrNull<EventItem>(`/events/${slugPath(slug)}/`, locale);

export const getEventTypes = (locale: Locale) => get<EventTypeOption[]>('/event-types/', locale);

// ——— Международное сотрудничество ———

export const getCountries = (locale: Locale) => get<Country[]>('/countries/', locale);

export const getPartners = (locale: Locale, country?: string) =>
  get<Partner[]>('/partners/', locale, {country});

export const getProjects = (
  locale: Locale,
  {country, page = 1, pageSize = NEWS_PAGE_SIZE}: {country?: string; page?: number; pageSize?: number} = {}
) => get<Paginated<ProjectListItem>>('/projects/', locale, {country, page, page_size: pageSize});

export const getProject = (locale: Locale, slug: string) =>
  getOrNull<Project>(`/projects/${slugPath(slug)}/`, locale);

// ——— Контакты ———

export const getContacts = (locale: Locale) => get<Contacts>('/contacts/', locale);
