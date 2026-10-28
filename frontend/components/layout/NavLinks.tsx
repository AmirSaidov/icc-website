'use client';

import {useTranslations} from 'next-intl';
import {Link, usePathname} from '@/i18n/navigation';
import {cn} from '@/lib/cn';
import {isActive, NAV_ITEMS} from './nav';

/** Пункты меню с подсветкой текущего раздела. В шапке без «Главной» — туда ведёт логотип. */
export function NavLinks({variant, onNavigate}: {variant: 'desktop' | 'mobile'; onNavigate?: () => void}) {
  const t = useTranslations('Nav');
  const pathname = usePathname();

  return (
    <ul className={variant === 'desktop' ? 'flex items-center' : 'flex flex-col'}>
      {NAV_ITEMS.filter((item) => variant === 'mobile' || item.key !== 'home').map((item) => {
        const active = isActive(item, pathname);
        return (
          <li key={item.key}>
            <Link
              href={item.href}
              aria-current={active ? 'page' : undefined}
              onClick={onNavigate}
              className={cn(
                'block transition-colors',
                variant === 'desktop'
                  ? cn(
                      'whitespace-nowrap rounded-full px-2 py-2 text-[13px] font-semibold',
                      active ? 'bg-navy text-white' : 'text-navy/75 hover:bg-navy/[0.06] hover:text-navy'
                    )
                  : cn('border-b border-border py-4 text-lg font-semibold hover:text-primary', active ? 'text-primary' : 'text-navy')
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
