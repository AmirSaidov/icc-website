import type {Metadata} from 'next';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import {PageHeader} from '@/components/ui/PageHeader';
import {PresentationCard} from '@/components/ui/PresentationCard';
import {Link} from '@/i18n/navigation';
import type {Locale} from '@/i18n/routing';
import {getPresentations, getSectors} from '@/lib/api';
import type {PresentationCategory, Sector} from '@/lib/api-types';
import {cn} from '@/lib/cn';
import {buildMetadata, staticPaths} from '@/lib/seo';

export const revalidate = 60;
// Читает searchParams (раздел, сфера) — рендерится на каждый запрос; ответы API всё равно кэшируются на 60 с.
export const dynamic = 'force-dynamic';

const CATEGORIES: PresentationCategory[] = ['projects', 'industry'];

type Props = {
  params: Promise<{locale: Locale}>;
  searchParams: Promise<{category?: string; sector?: string}>;
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
  // Сферы — подвкладки «Промышленность и IT»; непереведённые на этот язык (slug null) не показываем.
  // Slug сферы бэк ищет на любом языке, поэтому ?sector= переживает переключение языка.
  const sectors =
    category === 'industry'
      ? (await getSectors(locale)).filter((s): s is Sector & {slug: string; name: string} => Boolean(s.slug && s.name))
      : [];
  const sector = category === 'industry' && query.sector ? query.sector : undefined;
  const [data, t, nav] = await Promise.all([
    getPresentations(locale, {category, sector, pageSize: 50}),
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
  const sectorTabs = sectors.length
    ? [
        {key: 'all', href: '/presentations?category=industry', label: t('allSectors'), active: !sector},
        ...sectors.map((s) => ({
          key: s.slug,
          href: `/presentations?category=industry&sector=${encodeURIComponent(s.slug)}`,
          label: s.name,
          active: s.slug === sector
        }))
      ]
    : [];

  return (
    <>
      <PageHeader title={t('title')} lead={t('description')} breadcrumbs={[{label: nav('presentations')}]}>
        <Tabs tabs={tabs} label={t('sections')} className="mt-6" />
        {sectorTabs.length > 0 && <Tabs tabs={sectorTabs} label={t('sectors')} size="sm" className="mt-3" />}
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

type Tab = {key: string; href: string; label: string; active: boolean};

function Tabs({tabs, label, size = 'md', className}: {tabs: Tab[]; label: string; size?: 'md' | 'sm'; className?: string}) {
  return (
    <nav aria-label={label} className={className}>
      <ul className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <li key={tab.key}>
            <Link
              href={tab.href}
              aria-current={tab.active ? 'page' : undefined}
              className={cn(
                'inline-flex items-center rounded-md font-medium transition-colors',
                size === 'md' ? 'min-h-10 px-4 text-sm' : 'min-h-9 px-3 text-xs',
                tab.active ? 'bg-primary text-white' : 'border border-primary/30 bg-surface text-primary hover:bg-primary-light'
              )}
            >
              {tab.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
