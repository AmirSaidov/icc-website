import {useTranslations} from 'next-intl';
import {Button} from '@/components/ui/Button';
import {LanguageSwitcher} from './LanguageSwitcher';
import {Logo} from './Logo';
import {MobileMenu} from './MobileMenu';
import {NavLinks} from './NavLinks';

/**
 * ≥1280 px: логотип, 8 пунктов, язык, «Подать заявку».
 * <1280 px: логотип, язык, «Подать заявку» (от 768 px), бургер.
 * Без backdrop-filter: он ломает position: fixed у панели бургер-меню.
 */
export function Header() {
  const t = useTranslations('Header');
  return (
    <header className="sticky top-0 z-50 border-b border-border/70 bg-page">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-2 focus:z-50 focus:rounded focus:bg-primary focus:px-4 focus:py-2 focus:text-white"
      >
        {t('skipToContent')}
      </a>
      <div className="container-page flex h-16 items-center justify-between gap-4 md:h-[72px]">
        <div className="min-w-0 xl:max-w-[320px]">
          <Logo />
        </div>
        <nav aria-label={t('mainNav')} className="hidden xl:block">
          <NavLinks variant="desktop" />
        </nav>
        <div className="flex shrink-0 items-center gap-2">
          <LanguageSwitcher variant="dropdown" />
          {/* display задаёт обёртка: hidden на самой кнопке спорит с её inline-flex */}
          <div className="hidden md:block">
            <Button href="/contacts#form">{t('apply')}</Button>
          </div>
          <MobileMenu />
        </div>
      </div>
    </header>
  );
}
