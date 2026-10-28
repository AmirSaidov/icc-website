import {useTranslations} from 'next-intl';
import {BrandMark} from '@/components/ui/BrandMark';
import {Link} from '@/i18n/navigation';
import {cn} from '@/lib/cn';

/** Знак «CC» и название Центра, как в брендбуке. compact — для шапки. */
export function Logo({inverse = false, compact = false}: {inverse?: boolean; compact?: boolean}) {
  const t = useTranslations('Header');
  return (
    <Link href="/" className="flex min-w-0 items-center gap-3">
      <BrandMark inverse={inverse} className="h-8 w-auto sm:h-9" />
      <span className="flex min-w-0 flex-col leading-tight">
        <span
          className={cn(
            'line-clamp-2 text-[13px] font-bold leading-[1.15] tracking-[-0.01em] sm:text-[15px]',
            compact && 'xl:text-[13px]',
            inverse ? 'text-white' : 'text-navy'
          )}
        >
          {t('logoTitle')}
        </span>
        {/* На телефоне рядом кнопка языка и бургер, на ≥1280 px — всё меню: подзаголовок не влезает. */}
        <span className={cn('mt-0.5 hidden truncate text-xs sm:block', compact && 'xl:hidden', inverse ? 'text-white/60' : 'text-muted')}>
          {t('logoSubtitle')}
        </span>
      </span>
    </Link>
  );
}
