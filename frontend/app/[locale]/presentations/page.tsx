import type {Metadata} from 'next';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import {PageHeader} from '@/components/ui/PageHeader';
import {PresentationCard} from '@/components/ui/PresentationCard';
import {Link} from '@/i18n/navigation';
import type {Locale} from '@/i18n/routing';
import {getPresentations} from '@/lib/api';
import type {PresentationCategory} from '@/lib/api-types';
import {cn} from '@/lib/cn';
import {buildMetadata, staticPaths} from '@/lib/seo';

export const revalidate = 60;
// Читает searchParams (раздел) — рендерится на каждый запрос; ответы API всё равно кэшируются на 60 с.
export const dynamic = 'force-dynamic';

const CATEGORIES: PresentationCategory[] = ['projects', 'industry'];

type Props = {
  params: Promise<{locale: Locale}>;
  searchParams: Promise<{category?: string}>;
};

export async function generateMetadata({params}: Props): Promise<Metadata> {
  const {locale} = await params;
  const t = await getTranslations({locale, namespace: 'Presentations'});
  return buildMetadata({
    locale,
    paths: staticPaths('/presentations'),
    title: t('title'),
    description: t('description')
  });
}

export default async function PresentationsPage({params, searchParams}: Props) {
  const {locale} = await params;
  const query = await searchParams;
  setRequestLocale(locale);
  // Неизвестный раздел в адресе — показываем все.
  const category = CATEGORIES.find((c) => c === query.category);
  const [data, t, nav] = await Promise.all([
    getPresentations(locale, {category, pageSize: 50}),
    getTranslations('Presentations'),
    getTranslations('Nav')
  ]);
  const tabs = [
    {key: 'all', href: '/presentations', label: t('all'), active: !category},
    ...CATEGORIES.map((c) => ({
      key: c,
      href: `/presentations?category=${c}`,
      label: t(`categories.${c}`),
      active: c === category
    }))
  ];

  return (
    <>
      <PageHeader title={t('title')} lead={t('description')} breadcrumbs={[{label: nav('presentations')}]}>
        <ul className="mt-6 flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <li key={tab.key}>
              <Link
                href={tab.href}
                aria-current={tab.active ? 'page' : undefined}
                className={cn(
                  'inline-flex min-h-10 items-center rounded-md px-4 text-sm font-medium transition-colors',
                  tab.active ? 'bg-primary text-white' : 'border border-primary/30 bg-surface text-primary hover:bg-primary-light'
                )}
              >
                {tab.label}
              </Link>
            </li>
          ))}
        </ul>
      </PageHeader>
      <div className="container-page py-12">
        {data.results.length > 0 ? (
          <ul data-reveal-stagger className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {data.results.map((item) => (
              <li key={item.id} className="flex [&>*]:flex-1">
                <PresentationCard item={item} headingLevel="h2" />
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
