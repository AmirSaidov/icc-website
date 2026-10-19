import type {Metadata} from 'next';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import {PageHeader} from '@/components/ui/PageHeader';
import {ServiceCard} from '@/components/ui/ServiceCard';
import type {Locale} from '@/i18n/routing';
import {getServices} from '@/lib/api';
import {buildMetadata, staticPaths} from '@/lib/seo';

export const revalidate = 60;

type Props = {params: Promise<{locale: Locale}>};

export async function generateMetadata({params}: Props): Promise<Metadata> {
  const {locale} = await params;
  const t = await getTranslations({locale, namespace: 'Services'});
  return buildMetadata({
    locale,
    paths: staticPaths('/services'),
    title: t('title'),
    description: t('description')
  });
}

export default async function ServicesPage({params}: Props) {
  const {locale} = await params;
  setRequestLocale(locale);
  const [items, t, nav] = await Promise.all([
    getServices(locale),
    getTranslations('Services'),
    getTranslations('Nav')
  ]);

  return (
    <>
      <PageHeader title={t('title')} lead={t('description')} breadcrumbs={[{label: nav('services')}]} />
      <div className="container-page py-12">
        {items.length ? (
          <ul data-reveal-stagger className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((item) => (
              <li key={item.id} className="flex [&>*]:flex-1">
                <ServiceCard item={item} />
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-muted">{t('empty')}</p>
        )}
      </div>
    </>
  );
}
