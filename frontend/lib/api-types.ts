/**
 * Типы ответов API — из схемы бэка (backend/docs/openapi.yaml).
 * Схема поменялась → `npm run gen:types`, руками lib/api-schema.d.ts не правим.
 */
import type {Locale} from '@/i18n/routing';
import type {components} from './api-schema';

type S = components['schemas'];

/** slug записи на каждом языке; null — на этот язык не переведена. У системных страниц — key. */
export type LocaleSlugs = Record<Locale, string | null>;

export type Seo = S['Seo'];
/** Картинка в двух размерах: small — 400 px, large — 1200 px (WebP). */
export type ImageVersions = S['ImageVersions'];
export type GalleryImage = S['GalleryImage'];
export type Attachment = S['Attachment'];

export interface Paginated<T> {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}

export type IconKey = S['IconEnum'];

export type DirectionListItem = S['DirectionList'];
export type Direction = S['DirectionDetail'];
export type ServiceListItem = S['ServiceList'];
export type Service = S['ServiceDetail'];

export type NewsCategory = S['NewsCategory'];
export type NewsListItem = S['NewsList'];
export type NewsItem = S['NewsDetail'];

export type EventTypeCode = S['CodeEnum'];
export type EventTypeOption = S['EventType'];
export type EventWhen = 'upcoming' | 'past';
export type EventListItem = S['EventList'];
export type EventItem = S['EventDetail'];

export type Page = S['PageDetail'];
export type DocumentFile = S['Attachment'];

export type Country = S['Country'];
export type Partner = S['Partner'];
export type ProjectListItem = S['ProjectList'];
export type Project = S['ProjectDetail'];

export type Contacts = S['ContactInfo'];
export type SocialLink = S['Social'];

export type HomeBlock = S['HomeBlock'];
export type HomeBlockType = S['HomeBlockTypeEnum'];
export type Home = S['Home'];

export type FeedbackType = S['FeedbackTypeEnum'];
export type FeedbackPayload = S['FeedbackRequest'];

/** 400 от DRF: {field: ['ошибка', ...]}. */
export type FieldErrors = Partial<Record<keyof FeedbackPayload | 'non_field_errors' | 'detail', string[]>>;
