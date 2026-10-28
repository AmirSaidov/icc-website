import {useTranslations} from 'next-intl';
import {BrandMark} from '@/components/ui/BrandMark';
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
        className="grid items-center gap-10 rounded-[28px] bg-navy px-6 py-12 text-white md:grid-cols-[1fr_auto] md:gap-16 md:rounded-[36px] md:px-14 md:py-16"
      >
        <div className="max-w-2xl">
          <h2 id="cta-title" className="text-[28px] font-extrabold leading-[1.1] md:text-[40px]">
            {title || t('title')}
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-white/65">{text || t('text')}</p>
          <Button href="/contacts#form" size="lg" variant="inverse" className="mt-8 w-full sm:w-auto">
            {t('apply')}
          </Button>
        </div>
        {/* Знак на тёмном, как в брендбуке */}
        <BrandMark inverse className="hidden h-36 w-auto md:block lg:h-44" />
      </div>
    </section>
  );
}
