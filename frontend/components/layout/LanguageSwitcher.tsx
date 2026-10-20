'use client';

import {useEffect, useId, useRef, useState, type MouseEvent} from 'react';
import {Check, ChevronDown, Globe} from 'lucide-react';
import {useLocale, useTranslations} from 'next-intl';
import {Link, usePathname, useRouter} from '@/i18n/navigation';
import {htmlLang, LOCALE_COOKIE, routing, type Locale} from '@/i18n/routing';
import {cn} from '@/lib/cn';
import {useAlternates} from './Alternates';
import {matchDetail} from './nav';

const SHORT: Record<Locale, string> = {ru: 'RU', en: 'EN', zh: '中文'};
/** Название языка на нём самом — так его найдёт тот, кто не читает текущий язык сайта. */
const NATIVE: Record<Locale, string> = {ru: 'Русский', en: 'English', zh: '中文'};

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

function useSwitch() {
  const router = useRouter();
  const targetPath = useTargetPath();
  const onSwitch = (event: MouseEvent<HTMLAnchorElement>, target: Locale) => {
    document.cookie = `${LOCALE_COOKIE}=${target}; path=/; max-age=31536000; samesite=lax`;
    const {path, keepQuery} = targetPath(target);
    if (!keepQuery || !window.location.search) return; // обычный переход по href
    event.preventDefault();
    router.replace(`${path}${window.location.search}`, {locale: target});
  };
  return {targetPath, onSwitch};
}

/**
 * dropdown — кнопка «🌐 Русский ▾» в шапке (на телефоне «RU»);
 * inline — RU / EN / 中文 в ряд, в бургер-меню.
 */
export function LanguageSwitcher({variant = 'inline', className}: {variant?: 'inline' | 'dropdown'; className?: string}) {
  const t = useTranslations('LanguageSwitcher');
  const locale = useLocale() as Locale;
  const {targetPath, onSwitch} = useSwitch();

  if (variant === 'dropdown') return <Dropdown className={className} />;

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
                  'flex min-h-10 min-w-10 items-center justify-center rounded-sm border px-3 text-sm font-medium transition-colors',
                  isCurrent ? 'border-primary bg-primary text-white' : 'border-border bg-surface text-text hover:border-primary hover:text-primary'
                )}
              >
                {NATIVE[target]}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

function Dropdown({className}: {className?: string}) {
  const t = useTranslations('LanguageSwitcher');
  const locale = useLocale() as Locale;
  const pathname = usePathname();
  const {targetPath, onSwitch} = useSwitch();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listId = useId();

  useEffect(() => setOpen(false), [pathname]);

  useEffect(() => {
    if (!open) return;
    const onPointer = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      setOpen(false);
      buttonRef.current?.focus();
    };
    document.addEventListener('pointerdown', onPointer);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('pointerdown', onPointer);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  return (
    <div ref={rootRef} className={cn('relative', className)}>
      <button
        ref={buttonRef}
        type="button"
        aria-expanded={open}
        aria-controls={listId}
        aria-label={`${t('label')}: ${NATIVE[locale]}`}
        onClick={() => setOpen((value) => !value)}
        className={cn(
          'flex min-h-10 items-center gap-1.5 rounded-sm border bg-surface px-2.5 text-sm font-medium text-text transition-colors sm:px-3',
          open ? 'border-primary' : 'border-border hover:border-primary/60'
        )}
      >
        <Globe aria-hidden className="size-4 text-muted" />
        {/* Коротко на телефоне и на 1280–1535 px, где рядом всё меню; полностью — где есть место. */}
        <span className="sm:hidden xl:inline 2xl:hidden">{SHORT[locale]}</span>
        <span className="hidden sm:inline xl:hidden 2xl:inline">{NATIVE[locale]}</span>
        <ChevronDown aria-hidden className={cn('size-3.5 text-muted transition-transform', open && 'rotate-180')} />
      </button>
      <ul
        id={listId}
        className={cn(
          'absolute right-0 top-full z-50 mt-1.5 min-w-40 origin-top-right rounded-sm border border-border bg-surface p-1 shadow-lg transition duration-150 ease-out',
          open ? 'visible scale-100 opacity-100' : 'invisible scale-95 opacity-0'
        )}
      >
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
                onClick={(event) => {
                  setOpen(false);
                  onSwitch(event, target);
                }}
                className={cn(
                  'flex items-center justify-between gap-3 rounded-sm px-3 py-2 text-sm transition-colors hover:bg-primary-light',
                  isCurrent ? 'font-semibold text-primary' : 'text-text'
                )}
              >
                {NATIVE[target]}
                {isCurrent && <Check aria-hidden className="size-4" />}
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
