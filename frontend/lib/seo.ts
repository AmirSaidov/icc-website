import type {Metadata} from 'next';
import {getTranslations} from 'next-intl/server';
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

/** Детальная страница: пути из seo.alternates. section '' — страница редактора /{slug}. */
export const detailPaths = (section: string, alternates: LocaleSlugs): LocalePaths =>
  Object.fromEntries(
    Object.entries(alternates)
      .filter(([, slug]) => slug)
      .map(([l, slug]) => [l, section ? `/${section}/${slug}` : `/${slug}`])
  );

export const absoluteUrl = (locale: Locale, path: string) => `${SITE_URL}/${locale}${path}`;

interface BuildMetadataArgs {
  locale: Locale;
  paths: LocalePaths;
  seo?: Seo | null;
  /** Если seo.meta_title пустой — заголовок записи. */
  title: string | null;
  /** Если seo.meta_description пустой — краткое описание записи. */
  description?: string | null;
  image?: string | null;
  /** Для главной: title без шаблона «… | Название сайта». */
  absoluteTitle?: boolean;
  noindex?: boolean;
}

/**
 * Метаданные для generateMetadata: title, description, canonical,
 * hreflang (ru, en, zh-Hans, x-default) и Open Graph.
 * openGraph страницы целиком заменяет openGraph из layout, поэтому siteName ставим здесь.
 */
export async function buildMetadata({
  locale,
  paths,
  seo,
  title,
  description,
  image,
  absoluteTitle,
  noindex
}: BuildMetadataArgs): Promise<Metadata> {
  const t = await getTranslations({locale, namespace: 'Meta'});
  const metaTitle = seo?.meta_title || title || t('siteName');
  const metaDescription = seo?.meta_description || description || undefined;
  const ogImage = seo?.og_image || image;
  // Нет пути на своём языке — запись не переведена (страница-заглушка с noindex): canonical не ставим.
  const ownPath = paths[locale];
  const canonical = ownPath !== undefined ? absoluteUrl(locale, ownPath) : undefined;

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
      siteName: t('siteName'),
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
