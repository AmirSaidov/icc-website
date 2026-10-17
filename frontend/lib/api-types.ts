/**
 * ВРЕМЕННЫЕ типы ответов API, пока нет Swagger Айбека.
 * Когда схема появится: `npm run gen:types` → lib/api-schema.d.ts,
 * и эти интерфейсы заменяются на `components['schemas'][...]`.
 * Всё, что здесь расходится с бэком, правим по Swagger, а не наоборот.
 */
import type {Locale} from '@/i18n/routing';

/** slug записи на каждом языке, где есть перевод: {ru: 'delovaya-missiya', en: 'business-mission'}. */
export type LocaleSlugs = Partial<Record<Locale, string>>;

export interface Seo {
  title: string;
  description: string;
  og_image: string | null;
  alternates: LocaleSlugs;
}

export interface ImageAsset {
  url: string;
  alt: string;
  width: number;
  height: number;
}

export interface Attachment {
  id: number;
  title: string;
  url: string;
  /** Байты. */
  size: number;
  ext: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/** false — записи нет на запрошенном языке, контент отдан пустым. */
export interface Translatable {
  is_translated: boolean;
}

export interface DirectionListItem {
  id: number;
  slug: string;
  title: string;
  summary: string;
  icon: string;
}

export interface Direction extends DirectionListItem, Translatable {
  content: string;
  seo: Seo;
}

export interface ServiceListItem {
  id: number;
  slug: string;
  title: string;
  summary: string;
  icon: string;
}

export interface ServiceStep {
  title: string;
  text: string;
}

export interface ContactPerson {
  name: string;
  position: string;
  phone: string;
  email: string;
}

export interface Service extends ServiceListItem, Translatable {
  content: string;
  steps: ServiceStep[];
  contact_person: ContactPerson | null;
  seo: Seo;
}

export interface NewsCategory {
  slug: string;
  title: string;
}

export interface NewsListItem {
  id: number;
  slug: string;
  title: string;
  summary: string;
  /** ISO 8601. */
  published_at: string;
  cover: ImageAsset | null;
  category: NewsCategory | null;
}

export interface NewsItem extends NewsListItem, Translatable {
  content: string;
  gallery: ImageAsset[];
  attachments: Attachment[];
  related: NewsListItem[];
  seo: Seo;
}

export type EventType = 'mission' | 'forum' | 'exhibition' | 'b2b';
export type EventStatus = 'upcoming' | 'past';

export interface EventListItem {
  id: number;
  slug: string;
  title: string;
  summary: string;
  type: EventType;
  /** YYYY-MM-DD. */
  start_date: string;
  end_date: string | null;
  location: string;
  cover: ImageAsset | null;
}

export interface EventItem extends EventListItem, Translatable {
  content: string;
  gallery: ImageAsset[];
  attachments: Attachment[];
  related: EventListItem[];
  seo: Seo;
}

export interface Person {
  id: number;
  name: string;
  position: string;
  photo: ImageAsset | null;
}

export interface Page extends Translatable {
  slug: string;
  title: string;
  lead: string;
  /** HTML из CMS. */
  content: string;
  /** Пустой массив, пока заказчик не согласовал руководство. */
  leadership: Person[];
  seo: Seo;
}

export interface DocumentFile extends Attachment {
  /** regulation — Положение о Центре. */
  kind: 'regulation' | 'other';
}

export interface Country {
  id: number;
  code: string;
  name: string;
}

export interface Partner {
  id: number;
  name: string;
  logo: ImageAsset;
  url: string | null;
  country: string;
}

export interface Project {
  id: number;
  title: string;
  summary: string;
  cover: ImageAsset | null;
  country: string;
}

export interface SocialLink {
  type: 'telegram' | 'whatsapp' | 'facebook' | 'instagram' | 'youtube' | 'linkedin' | 'wechat';
  url: string;
}

export interface Contacts {
  name: string;
  address: string;
  phones: string[];
  emails: string[];
  /** Пустая строка — блок графика скрывается. */
  schedule: string;
  map_lat: number;
  map_lng: number;
  socials: SocialLink[];
}

export interface Advantage {
  icon: string;
  title: string;
  text: string;
}

export interface Home {
  hero: {title: string; subtitle: string; image: ImageAsset};
  about: {title: string; text: string};
  directions: DirectionListItem[];
  cooperation: {title: string; text: string; image: ImageAsset | null};
  advantages: Advantage[];
  news: NewsListItem[];
  events: EventListItem[];
  seo: Seo;
}

export type FeedbackType = 'contact' | 'cooperation';

export interface FeedbackPayload {
  type: FeedbackType;
  name: string;
  company: string;
  country: string;
  email: string;
  phone?: string;
  subject: string;
  message: string;
  consent: boolean;
  /** honeypot, всегда пустой. */
  website: string;
  locale: Locale;
}

/** 400 от DRF: {field: ['ошибка', ...]}. */
export type FieldErrors = Partial<Record<keyof FeedbackPayload | 'non_field_errors', string[]>>;
