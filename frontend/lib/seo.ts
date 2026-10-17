import type {Metadata} from 'next';
import {htmlLang, ogLocale, routing, type Locale} from '@/i18n/routing';
import type {LocaleSlugs, Seo} from './api-types';

export const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000').replace(/\/$/, '');

/** og:image, если у страницы своей картинки нет. */
export const DEFAULT_OG_IMAGE = {url: '/og-default.png', width: 1200, height: 630};

/** Путь страницы без префикса языка на каждом языке, где она есть: {ru: '/news/delovaya-missiya', ...}. */
export type LocalePaths = Partial<Record<Locale, string>>;

/** Статическая страница: путь одинаковый на всех языках. '' — главная. */
export const staticPaths = (path: string): LocalePaths =>
  Object.fromEntries(routing.locales.map((l) => [l, path]));

/** Детальная страница: пути из seo.alternates. */
export const detailPaths = (section: string, alternates: LocaleSlugs): LocalePaths =>
  Object.fromEntries(
    Object.entries(alternates)
      .filter(([, slug]) => slug)
      .map(([l, slug]) => [l, `/${section}/${slug}`])
  );

export const absoluteUrl = (locale: Locale, path: string) => `${SITE_URL}/${locale}${path}`;

interface BuildMetadataArgs {
  locale: Locale;
  paths: LocalePaths;
  seo?: Seo | null;
  /** Если seo.title пустой — заголовок записи. */
  title: string;
  /** Если seo.description пустой — краткое описание записи. */
  description?: string;
  image?: string | null;
  /** Для главной: title без шаблона «… | Название сайта». */
  absoluteTitle?: boolean;
  noindex?: boolean;
}

/**
 * Метаданные для generateMetadata: title, description, canonical,
 * hreflang (ru, en, zh-Hans, x-default) и Open Graph.
 */
export function buildMetadata({
  locale,
  paths,
  seo,
  title,
  description,
  image,
  absoluteTitle,
  noindex
}: BuildMetadataArgs): Metadata {
  const metaTitle = seo?.title || title;
  const metaDescription = seo?.description || description || undefined;
  const ogImage = seo?.og_image || image;
  const ownPath = paths[locale] ?? '';
  const canonical = absoluteUrl(locale, ownPath);

  const languages: Record<string, string> = {};
  for (const l of routing.locales) {
    const path = paths[l];
    if (path !== undefined) languages[htmlLang[l]] = absoluteUrl(l, path);
  }
  const defaultPath = paths[routing.defaultLocale];
  if (defaultPath !== undefined) {
    languages['x-default'] = absoluteUrl(routing.defaultLocale, defaultPath);
  }

  return {
    title: absoluteTitle ? {absolute: metaTitle} : metaTitle,
    description: metaDescription,
    alternates: {canonical, languages},
    openGraph: {
      type: 'website',
      url: canonical,
      title: metaTitle,
      description: metaDescription,
      locale: ogLocale[locale],
      alternateLocale: routing.locales
        .filter((l) => l !== locale && paths[l] !== undefined)
        .map((l) => ogLocale[l]),
      images: [ogImage ? {url: ogImage} : DEFAULT_OG_IMAGE]
    },
    twitter: {card: 'summary_large_image'},
    robots: noindex ? {index: false, follow: true} : undefined
  };
}
