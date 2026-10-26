import {useTranslations} from 'next-intl';
import {Link} from '@/i18n/navigation';
import {cn} from '@/lib/cn';

/**
 * Красная печать с аббревиатурой (ЦПК / ICC). Временный знак,
 * пока заказчик не прислал брендбук с фирменным логотипом.
 */
function Seal({text}: {text: string}) {
  return (
    <span
      aria-hidden
      className={cn(
        'relative flex size-10 shrink-0 items-center justify-center rounded-sm bg-seal font-serif text-[11px] font-bold tracking-wide text-white',
        'after:absolute after:inset-[3px] after:rounded-[1px] after:border after:border-white/55 after:content-[""]'
      )}
    >
      {text}
    </span>
  );
}

export function Logo({inverse = false}: {inverse?: boolean}) {
  const t = useTranslations('Header');
  return (
    <Link href="/" className="flex min-w-0 items-center gap-3">
      <Seal text={t('logoMark')} />
      <span className="flex min-w-0 flex-col leading-tight">
        <span className={cn('line-clamp-3 font-serif text-[13px] font-bold leading-[1.2] sm:line-clamp-2 sm:text-[15px]', inverse ? 'text-white' : 'text-navy')}>
          {t('logoTitle')}
        </span>
        {/* На телефоне рядом кнопка языка и бургер — подзаголовок не влезает. */}
        <span className={cn('mt-0.5 hidden truncate text-xs sm:block', inverse ? 'text-white/70' : 'text-muted')}>{t('logoSubtitle')}</span>
      </span>
    </Link>
  );
}
