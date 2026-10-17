import {useTranslations} from 'next-intl';
import {Button} from '@/components/ui/Button';

/** «Подать заявку / Связаться с нами» → форма на странице контактов. */
export function CtaBlock() {
  const t = useTranslations('Cta');
  return (
    <section aria-labelledby="cta-title" className="bg-primary text-white">
      <div className="container-page flex flex-col gap-6 py-12 md:flex-row md:items-center md:justify-between md:py-16">
        <div className="max-w-2xl">
          <h2 id="cta-title" className="text-2xl font-bold md:text-3xl">
            {t('title')}
          </h2>
          <p className="mt-3 text-white/85">{t('text')}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button href="/contacts#form" size="lg" variant="inverse">
            {t('apply')}
          </Button>
          <Button href="/contacts" size="lg" variant="inverse-outline">
            {t('contact')}
          </Button>
        </div>
      </div>
    </section>
  );
}
