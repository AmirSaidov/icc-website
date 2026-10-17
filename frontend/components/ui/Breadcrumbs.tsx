import {ChevronRight} from 'lucide-react';
import {getLocale, getTranslations} from 'next-intl/server';
import {Link} from '@/i18n/navigation';
import type {Locale} from '@/i18n/routing';
import {absoluteUrl} from '@/lib/seo';

export interface Crumb {
  label: string;
  /** Путь без префикса языка. У последнего пункта не нужен. */
  href?: string;
}

/** Главная добавляется сама. Плюс JSON-LD BreadcrumbList для поисковиков. */
export async function Breadcrumbs({items}: {items: Crumb[]}) {
  const [t, tNav, locale] = await Promise.all([
    getTranslations('Common'),
    getTranslations('Nav'),
    getLocale() as Promise<Locale>
  ]);
  const crumbs: Crumb[] = [{label: tNav('home'), href: ''}, ...items];

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: crumbs.map((crumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: crumb.label,
      ...(crumb.href !== undefined && {item: absoluteUrl(locale, crumb.href)})
    }))
  };

  return (
    <nav aria-label={t('breadcrumbs')} className="text-sm text-muted">
      <ol className="flex flex-wrap items-center gap-x-1 gap-y-1">
        {crumbs.map((crumb, index) => {
          const isLast = index === crumbs.length - 1;
          return (
            <li key={index} className="flex min-w-0 items-center gap-1">
              {crumb.href !== undefined && !isLast ? (
                <Link href={crumb.href || '/'} className="hover:text-primary hover:underline">
                  {crumb.label}
                </Link>
              ) : (
                <span aria-current={isLast ? 'page' : undefined} className="line-clamp-1 text-text">
                  {crumb.label}
                </span>
              )}
              {!isLast && <ChevronRight aria-hidden className="size-3.5 shrink-0" />}
            </li>
          );
        })}
      </ol>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{__html: JSON.stringify(jsonLd).replace(/</g, '\\u003c')}}
      />
    </nav>
  );
}
