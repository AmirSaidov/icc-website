import {Handshake} from 'lucide-react';
import {useTranslations} from 'next-intl';
import {Button} from '@/components/ui/Button';

/**
 * «Добро пожаловать к сотрудничеству» → форма на странице контактов.
 * На главной заголовок и текст приходят из CMS (блок cta), на остальных — из messages.
 */
export function CtaBlock({title, text}: {title?: string | null; text?: string | null} = {}) {
  const t = useTranslations('Cta');
  return (
    <section aria-labelledby="cta-title" className="container-page py-14 md:py-20">
      <div
        data-reveal
        className="flex flex-col items-center gap-6 border border-border bg-surface px-6 py-10 text-center md:flex-row md:gap-8 md:px-10 md:py-12 md:text-left"
      >
        <span aria-hidden className="flex size-14 shrink-0 items-center justify-center rounded-sm bg-seal text-white">
          <Handshake className="size-7" strokeWidth={1.75} />
        </span>
        <div className="min-w-0 flex-1">
          <h2 id="cta-title" className="text-2xl font-bold leading-tight text-navy md:text-[28px]">
            {title || t('title')}
          </h2>
          <p className="mt-2 text-muted">{text || t('text')}</p>
        </div>
        <Button href="/contacts#form" size="lg" className="w-full shrink-0 sm:w-auto">
          {t('apply')}
        </Button>
      </div>
    </section>
  );
}
