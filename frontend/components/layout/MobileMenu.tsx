'use client';

import {useEffect, useState} from 'react';
import {Menu, X} from 'lucide-react';
import {useTranslations} from 'next-intl';
import {Button} from '@/components/ui/Button';
import {usePathname} from '@/i18n/navigation';
import {cn} from '@/lib/cn';
import {LanguageSwitcher} from './LanguageSwitcher';
import {NavLinks} from './NavLinks';

/** Бургер-меню до 1280 px. */
export function MobileMenu() {
  const t = useTranslations('Header');
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  // Закрываем при переходе на другую страницу.
  useEffect(() => setOpen(false), [pathname]);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => event.key === 'Escape' && setOpen(false);
    const close = () => window.innerWidth >= 1280 && setOpen(false);
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', onKey);
    window.addEventListener('resize', close);
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('resize', close);
    };
  }, [open]);

  return (
    <div className="xl:hidden">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        aria-controls="mobile-menu"
        aria-label={open ? t('closeMenu') : t('openMenu')}
        className="flex size-10 items-center justify-center rounded-md text-text hover:bg-primary-light"
      >
        {open ? <X aria-hidden className="size-6" /> : <Menu aria-hidden className="size-6" />}
      </button>

      <div
        id="mobile-menu"
        className={cn(
          'fixed inset-x-0 bottom-0 top-16 z-40 overflow-y-auto bg-surface transition duration-200 ease-out',
          open ? 'visible translate-y-0 opacity-100' : 'invisible -translate-y-2 opacity-0'
        )}
      >
        <div className="container-page flex flex-col gap-6 py-4">
          <nav aria-label={t('mainNav')}>
            <NavLinks variant="mobile" onNavigate={() => setOpen(false)} />
          </nav>
          <LanguageSwitcher />
          <Button href="/contacts#form" size="lg" onClick={() => setOpen(false)}>
            {t('contactUs')}
          </Button>
        </div>
      </div>
    </div>
  );
}
