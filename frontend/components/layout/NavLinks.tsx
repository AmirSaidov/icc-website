'use client';

import {useTranslations} from 'next-intl';
import {Link, usePathname} from '@/i18n/navigation';
import {cn} from '@/lib/cn';
import {isActive, NAV_ITEMS} from './nav';

/** Пункты меню с подсветкой текущего раздела. */
export function NavLinks({variant, onNavigate}: {variant: 'desktop' | 'mobile'; onNavigate?: () => void}) {
  const t = useTranslations('Nav');
  const pathname = usePathname();

  return (
    <ul className={variant === 'desktop' ? 'flex items-center' : 'flex flex-col'}>
      {NAV_ITEMS.map((item) => {
        const active = isActive(item, pathname);
        return (
          <li key={item.key}>
            <Link
              href={item.href}
              aria-current={active ? 'page' : undefined}
              onClick={onNavigate}
              className={cn(
                'block font-medium transition-colors hover:text-primary',
                variant === 'desktop'
                  ? 'whitespace-nowrap px-2 py-2 text-sm'
                  : 'border-b border-border py-4 text-lg',
                active ? 'text-primary' : 'text-text',
                variant === 'desktop' && active && 'underline decoration-2 underline-offset-[10px]'
              )}
            >
              {t(item.key)}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
