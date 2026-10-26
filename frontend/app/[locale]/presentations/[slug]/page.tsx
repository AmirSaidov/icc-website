import type {Metadata} from 'next';
import {notFound} from 'next/navigation';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import {SetAlternates} from '@/components/layout/Alternates';
import {CtaBlock} from '@/components/sections/CtaBlock';
import {PageHeader} from '@/components/ui/PageHeader';
import {PresentationViewer} from '@/components/ui/PresentationViewer';
import {RichText} from '@/components/ui/RichText';
import type {Locale} from '@/i18n/routing';
import {getPresentation} from '@/lib/api';
import {redirectToOwnSlug} from '@/lib/detail';
import {formatDate} from '@/lib/format';
import {buildMetadata, detailPaths} from '@/lib/seo';

export const revalidate = 60;

type Props = {params: Promise<{locale: Locale; slug: string}>};

export async function generateMetadata({params}: Props): Promise<Metadata> {
  const {locale, slug} = await params;
  const [item, t] = await Promise.all([
    getPresentation(locale, decodeURIComponent(slug)),
    getTranslations({locale, namespace: 'Presentations'})
  ]);
  if (!item) return {};
  return buildMetadata({
    locale,
    paths: detailPaths('presentations', item.seo.alternates),
    seo: item.seo,
    title: item.title ?? t('untranslated'),
    description: item.excerpt,
    image: item.cover?.large,
    noindex: !item.is_translated
  });
}

export default async function PresentationPage({params}: Props) {
  const {locale, slug: rawSlug} = await params;
  const slug = decodeURIComponent(rawSlug);
  setRequestLocale(locale);
  const [item, t, nav] = await Promise.all([
    getPresentation(locale, slug),
    getTranslations('Presentations'),
    getTranslations('Nav')
  ]);
  if (!item) notFound();
  redirectToOwnSlug(locale, 'presentations', slug, item);
  const title = item.title ?? t('untranslated');

  return (
    <>
      <SetAlternates section="presentations" slugs={item.seo.alternates} />
      <PageHeader
        title={title}
        lead={item.excerpt ?? undefined}
        breadcrumbs={[{label: nav('presentations'), href: '/presentations'}, {label: title}]}
      />
      <div className="container-page space-y-10 py-10">
        {item.is_translated ? (
          <>
            <p className="text-sm font-semibold text-primary">
              {(item.category === 'industry' && item.sector?.name) || t(`categories.${item.category}`)}
              {item.published_at && ` · ${formatDate(item.published_at, locale)}`}
            </p>
            <PresentationViewer file={item.file} sourceFile={item.source_file} title={title} />
            {item.content && <RichText html={item.content} />}
          </>
        ) : (
          <p className="text-muted">{t('untranslated')}</p>
        )}
      </div>
      <CtaBlock />
    </>
  );
}
