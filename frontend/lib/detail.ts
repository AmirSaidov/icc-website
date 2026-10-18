import 'server-only';
import {permanentRedirect} from 'next/navigation';
import type {Locale} from '@/i18n/routing';

/**
 * Бэк находит запись по slug на любом из трёх языков и отдаёт slug на языке запроса.
 * Если он не совпадает со slug из URL (/en/news/<русский-slug>) — 308 на правильный адрес.
 * Непереведённая запись приходит со slug: null — тогда остаёмся и показываем заглушку.
 *
 *   redirectToOwnSlug(locale, 'news', slug, item);
 */
export function redirectToOwnSlug(locale: Locale, section: string, urlSlug: string, item: {slug: string | null}) {
  if (item.slug && item.slug !== urlSlug) {
    permanentRedirect(`/${locale}/${section}/${encodeURIComponent(item.slug)}`);
  }
}
