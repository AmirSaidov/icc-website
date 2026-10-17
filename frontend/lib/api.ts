import 'server-only';
import type {Locale} from '@/i18n/routing';
import type {
  Contacts,
  Country,
  Direction,
  DirectionListItem,
  DocumentFile,
  EventItem,
  EventListItem,
  EventStatus,
  EventType,
  Home,
  NewsCategory,
  NewsItem,
  NewsListItem,
  Page,
  Paginated,
  Partner,
  Project,
  Service,
  ServiceListItem
} from './api-types';

export const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS === 'true';
export const API_URL = (process.env.API_URL ?? 'http://localhost:8000/api/v1').replace(/\/$/, '');
/** ISR: страницы и запросы обновляются раз в 60 секунд. */
export const REVALIDATE = 60;
export const NEWS_PAGE_SIZE = 9;

/** Как язык называется для Django (LocaleMiddleware + modeltranslation). */
export const API_LANG: Record<Locale, string> = {ru: 'ru', en: 'en', zh: 'zh-hans'};

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

function toSearchParams(query?: Query) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined && value !== null && value !== '') params.set(key, String(value));
  }
  return params;
}

async function get<T>(path: string, locale: Locale, query?: Query): Promise<T> {
  const params = toSearchParams(query);

  if (USE_MOCKS) {
    const {mockGet} = await import('@/mocks/handlers');
    return mockGet(path, locale, params) as T;
  }

  const qs = params.toString();
  const res = await fetch(`${API_URL}${path}${qs ? `?${qs}` : ''}`, {
    headers: {Accept: 'application/json', 'Accept-Language': API_LANG[locale]},
    next: {revalidate: REVALIDATE}
  });
  if (!res.ok) throw new ApiError(res.status, `GET ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

/** Для детальных страниц: 404 → null, страница вызывает notFound(). */
async function getOrNull<T>(path: string, locale: Locale): Promise<T | null> {
  try {
    return await get<T>(path, locale);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

const slugPath = (slug: string) => encodeURIComponent(slug);

// ——— Главная и страницы ———

export const getHome = (locale: Locale) => get<Home>('/home/', locale);

export const getPage = (locale: Locale, slug: 'about' | 'cooperation') =>
  getOrNull<Page>(`/pages/${slug}/`, locale);

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
  get<NewsCategory[]>('/news/categories/', locale);

export const getEvents = (
  locale: Locale,
  {status = 'upcoming', type, page = 1, pageSize = NEWS_PAGE_SIZE}: {status?: EventStatus; type?: EventType; page?: number; pageSize?: number} = {}
) => get<Paginated<EventListItem>>('/events/', locale, {status, type, page, page_size: pageSize});

export const getEvent = (locale: Locale, slug: string) =>
  getOrNull<EventItem>(`/events/${slugPath(slug)}/`, locale);

// ——— Международное сотрудничество ———

export const getCountries = (locale: Locale) => get<Country[]>('/countries/', locale);

export const getPartners = (locale: Locale, country?: string) =>
  get<Partner[]>('/partners/', locale, {country});

export const getProjects = (locale: Locale, country?: string) =>
  get<Project[]>('/projects/', locale, {country});

// ——— Контакты ———

export const getContacts = (locale: Locale) => get<Contacts>('/contacts/', locale);
