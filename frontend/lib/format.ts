import type {Locale} from '@/i18n/routing';

const INTL_LOCALE: Record<Locale, string> = {ru: 'ru-RU', en: 'en-US', zh: 'zh-Hans-CN'};

// Даты считаем по Бишкеку, иначе на сервере в UTC новость «уедет» на день.
const DATE_OPTIONS: Intl.DateTimeFormatOptions = {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: 'Asia/Bishkek'
};

/** Intl добавляет «г.» в русской дате, по ТЗ его нет: «15 октября 2026». */
const stripRuYear = (value: string) => value.replace(/\s?г\.$/, '');

function formatter(locale: Locale) {
  return new Intl.DateTimeFormat(INTL_LOCALE[locale], DATE_OPTIONS);
}

/** «15 октября 2026», «October 15, 2026», «2026年10月15日». */
export function formatDate(value: string | Date, locale: Locale) {
  return stripRuYear(formatter(locale).format(new Date(value)));
}

/** «12–13 ноября 2026», «November 12 – 13, 2026», «2026年11月12日至13日». */
export function formatDateRange(start: string, end: string | null, locale: Locale) {
  if (!end || end === start) return formatDate(start, locale);
  return stripRuYear(formatter(locale).formatRange(new Date(start), new Date(end)));
}

/** 57726 → {value: '56,4', unit: 'kb'}; подпись единицы берётся из messages. */
export function fileSize(bytes: number, locale: Locale) {
  const number = new Intl.NumberFormat(INTL_LOCALE[locale], {maximumFractionDigits: 1});
  if (bytes < 1024) return {value: number.format(bytes), unit: 'b' as const};
  if (bytes < 1024 * 1024) return {value: number.format(bytes / 1024), unit: 'kb' as const};
  return {value: number.format(bytes / 1024 / 1024), unit: 'mb' as const};
}

/** Для календарного листка: {day: '05', month: 'нояб.'} / {day: '05', month: 'Nov'} / {day: '05', month: '11月'}. */
export function dayMonth(value: string | Date, locale: Locale) {
  const date = new Date(value);
  const part = (options: Intl.DateTimeFormatOptions) =>
    new Intl.DateTimeFormat(INTL_LOCALE[locale], {...options, timeZone: 'Asia/Bishkek'}).format(date);
  return {day: part({day: '2-digit'}).replace(/\D/g, ''), month: part({month: 'short'})};
}
