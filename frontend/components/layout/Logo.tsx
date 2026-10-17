import {useTranslations} from 'next-intl';
import {Link} from '@/i18n/navigation';

/** Временный текстовый логотип, пока заказчик не дал фирменный (открытый вопрос ТЗ). */
export function Logo({inverse = false}: {inverse?: boolean}) {
  const t = useTranslations('Header');
  return (
    <Link href="/" className="flex min-w-0 items-center gap-3">
      <span
        aria-hidden
        className={`flex size-10 shrink-0 items-center justify-center rounded-md text-sm font-bold ${inverse ? 'bg-white text-primary' : 'bg-primary text-white'}`}
      >
        {t('logoMark')}
      </span>
      <span className="flex min-w-0 flex-col leading-tight">
        <span className={`line-clamp-2 text-sm font-semibold ${inverse ? 'text-white' : 'text-text'}`}>{t('logoTitle')}</span>
        <span className={`truncate text-xs ${inverse ? 'text-white/75' : 'text-muted'}`}>{t('logoSubtitle')}</span>
      </span>
    </Link>
  );
}
