import {defineRouting} from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['ru', 'en', 'zh'],
  defaultLocale: 'ru',
  localePrefix: 'always',
  // По ТЗ «/» ведёт на /ru, а не по Accept-Language. Выбор пользователя
  // из cookie учитываем сами в middleware.ts.
  localeDetection: false,
  localeCookie: {name: 'NEXT_LOCALE', maxAge: 60 * 60 * 24 * 365}
});

export type Locale = (typeof routing.locales)[number];

/** Значение для <html lang>, hreflang и og:locale. */
export const htmlLang: Record<Locale, string> = {
  ru: 'ru',
  en: 'en',
  zh: 'zh-Hans'
};

export const ogLocale: Record<Locale, string> = {
  ru: 'ru_RU',
  en: 'en_US',
  zh: 'zh_CN'
};

export const LOCALE_COOKIE = 'NEXT_LOCALE';
