'use client';

import type {MouseEvent} from 'react';
import {useLocale, useTranslations} from 'next-intl';
import {Link, usePathname, useRouter} from '@/i18n/navigation';
import {htmlLang, LOCALE_COOKIE, routing, type Locale} from '@/i18n/routing';
import {cn} from '@/lib/cn';
import {useAlternates} from './Alternates';
import {matchDetail} from './nav';

const LABELS: Record<Locale, string> = {ru: 'RU', en: 'EN', zh: '中文'};

/**
 * Куда вести при смене языка:
 * - статическая страница — тот же путь: /ru/about → /zh/about;
 * - детальная — slug из seo.alternates: /ru/news/delovaya-missiya → /en/news/business-mission;
 * - перевода нет — список раздела на нужном языке: /en/news.
 */
function useTargetPath() {
  const pathname = usePathname();
  const alternates = useAlternates();
  const detail = matchDetail(pathname);

  return (target: Locale) => {
    if (!detail) return {path: pathname, keepQuery: true};
    const slug = alternates?.section === detail.section ? alternates.slugs[target] : undefined;
    return {path: slug ? `/${detail.section}/${slug}` : `/${detail.section}`, keepQuery: false};
  };
}

export function LanguageSwitcher({className}: {className?: string}) {
  const t = useTranslations('LanguageSwitcher');
  const locale = useLocale() as Locale;
  const router = useRouter();
  const targetPath = useTargetPath();

  const onSwitch = (event: MouseEvent<HTMLAnchorElement>, target: Locale) => {
    document.cookie = `${LOCALE_COOKIE}=${target}; path=/; max-age=31536000; samesite=lax`;
    const {path, keepQuery} = targetPath(target);
    if (!keepQuery || !window.location.search) return; // обычный переход по href
    event.preventDefault();
    router.replace(`${path}${window.location.search}`, {locale: target});
  };

  return (
    <nav aria-label={t('label')} className={className}>
      <ul className="flex items-center gap-1">
        {routing.locales.map((target) => {
          const isCurrent = target === locale;
          return (
            <li key={target}>
              <Link
                href={targetPath(target).path}
                locale={target}
                hrefLang={htmlLang[target]}
                lang={htmlLang[target]}
                aria-current={isCurrent ? 'true' : undefined}
                onClick={(event) => onSwitch(event, target)}
                className={cn(
                  'flex min-h-9 min-w-9 items-center justify-center rounded px-2 text-sm font-medium transition-colors',
                  isCurrent ? 'bg-primary-light text-primary' : 'text-muted hover:text-primary'
                )}
              >
                {LABELS[target]}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
