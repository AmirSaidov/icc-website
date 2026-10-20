import {useTranslations} from 'next-intl';
import {Link} from '@/i18n/navigation';
import {cn} from '@/lib/cn';

/**
 * Красная печать 合作 («сотрудничество») — знак из макета «Тянь-Шань»,
 * одинаковый на всех языках. Пока заказчик не дал фирменный логотип.
 */
export function Seal({
  chars = ['合', '作'],
  size = 'md',
  className
}: {
  chars?: [string, string];
  size?: 'md' | 'lg';
  className?: string;
}) {
  return (
    <span
      aria-hidden
      lang="zh-Hans"
      className={cn(
        'relative flex shrink-0 flex-col items-center justify-center rounded-sm bg-seal font-serif font-bold leading-[1.05] text-white',
        size === 'md' ? 'size-10 text-[15px]' : 'size-14 text-xl',
        'after:absolute after:inset-[3px] after:rounded-[1px] after:border after:border-white/55 after:content-[""]',
        className
      )}
    >
      <span>{chars[0]}</span>
      <span>{chars[1]}</span>
    </span>
  );
}

export function Logo({inverse = false}: {inverse?: boolean}) {
  const t = useTranslations('Header');
  return (
    <Link href="/" className="flex min-w-0 items-center gap-3">
      <Seal />
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
