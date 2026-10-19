import type {Metadata} from 'next';
import {notFound} from 'next/navigation';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import {CtaBlock} from '@/components/sections/CtaBlock';
import {PageHeader} from '@/components/ui/PageHeader';
import {RichText} from '@/components/ui/RichText';
import type {Locale} from '@/i18n/routing';
import {getPage} from '@/lib/api';
import {redirectToOwnSlug} from '@/lib/detail';
import {buildMetadata, detailPaths} from '@/lib/seo';

// ISR. Next требует здесь литерал, поэтому не REVALIDATE из lib/api.
export const revalidate = 60;

/**
 * Всё, что не совпало с другими маршрутами:
 * - /{locale}/{slug} — страница, созданная редактором в админке (так её адресует sitemap бэка);
 * - остальное — 404 с шапкой и подвалом сайта, а не голая страница Next.
 */
type Props = {params: Promise<{locale: Locale; slug: string[]}>};

/** Системные страницы (home, about, cooperation) живут по своим адресам. */
async function loadPage(locale: Locale, segments: string[]) {
  if (segments.length !== 1) return null;
  const page = await getPage(locale, decodeURIComponent(segments[0]));
  return page && !page.key ? page : null;
}

export async function generateMetadata({params}: Props): Promise<Metadata> {
  const {locale, slug} = await params;
  const [page, t] = await Promise.all([loadPage(locale, slug), getTranslations({locale, namespace: 'Pages'})]);
  if (!page) return {};
  return buildMetadata({
    locale,
    paths: detailPaths('', page.seo.alternates),
    seo: page.seo,
    title: page.title ?? t('untranslated'),
    noindex: !page.is_translated
  });
}

export default async function CmsPage({params}: Props) {
  const {locale, slug} = await params;
  setRequestLocale(locale);
  const [page, t] = await Promise.all([loadPage(locale, slug), getTranslations('Pages')]);
  if (!page) notFound();
  redirectToOwnSlug(locale, '', decodeURIComponent(slug[0]), page);
  const title = page.title ?? t('untranslated');

  return (
    <>
      <PageHeader title={title} breadcrumbs={[{label: title}]} />
      <div className="container-page py-12 md:py-16">
        {page.is_translated ? (
          page.content && <RichText html={page.content} className="max-w-3xl" />
        ) : (
          <p className="text-muted">{t('untranslated')}</p>
        )}
      </div>
      <CtaBlock />
    </>
  );
}
