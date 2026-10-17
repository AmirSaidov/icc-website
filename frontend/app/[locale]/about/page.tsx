import type {Metadata} from 'next';
import Image from 'next/image';
import {notFound} from 'next/navigation';
import {Download, ExternalLink} from 'lucide-react';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import {CtaBlock} from '@/components/sections/CtaBlock';
import {Attachments} from '@/components/ui/Attachments';
import {Button} from '@/components/ui/Button';
import {PageHeader} from '@/components/ui/PageHeader';
import {RichText} from '@/components/ui/RichText';
import {SectionTitle} from '@/components/ui/SectionTitle';
import type {Locale} from '@/i18n/routing';
import {getDocuments, getPage} from '@/lib/api';
import {buildMetadata, staticPaths} from '@/lib/seo';

// ISR. Next требует здесь литерал, поэтому не REVALIDATE из lib/api.
export const revalidate = 60;

type Props = {params: Promise<{locale: Locale}>};

export async function generateMetadata({params}: Props): Promise<Metadata> {
  const {locale} = await params;
  const page = await getPage(locale, 'about');
  if (!page) return {};
  return buildMetadata({
    locale,
    paths: staticPaths('/about'),
    seo: page.seo,
    title: page.title,
    description: page.lead
  });
}

export default async function AboutPage({params}: Props) {
  const {locale} = await params;
  setRequestLocale(locale);
  const [page, documents, t, tNav] = await Promise.all([
    getPage(locale, 'about'),
    getDocuments(locale),
    getTranslations('About'),
    getTranslations('Nav')
  ]);
  if (!page) notFound();

  const regulation = documents.find((doc) => doc.kind === 'regulation');
  const otherDocuments = documents.filter((doc) => doc !== regulation);

  return (
    <>
      <PageHeader title={page.title} lead={page.lead} breadcrumbs={[{label: tNav('about')}]}>
        {regulation && (
          <div className="mt-6 flex flex-wrap gap-3">
            <Button href={regulation.url} download size="lg">
              <Download aria-hidden className="size-5" />
              {t('downloadRegulation')}
            </Button>
            <Button href={regulation.url} target="_blank" rel="noopener" size="lg" variant="secondary">
              <ExternalLink aria-hidden className="size-5" />
              {t('viewRegulation')}
            </Button>
          </div>
        )}
      </PageHeader>

      <div className="container-page space-y-14 py-12 md:py-16">
        {/* Общая информация, история, цели и задачи, функции — h2 внутри content */}
        <RichText html={page.content} className="max-w-3xl" />

        {/* Руководство: скрыто, пока заказчик не согласует данные */}
        {page.leadership.length > 0 && (
          <section aria-labelledby="about-leadership">
            <SectionTitle id="about-leadership">{t('leadershipTitle')}</SectionTitle>
            <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {page.leadership.map((person) => (
                <li key={person.id} className="flex items-center gap-4">
                  <div className="relative size-20 shrink-0 overflow-hidden rounded-full bg-primary-light">
                    {person.photo && (
                      <Image src={person.photo.url} alt={person.photo.alt} fill sizes="80px" className="object-cover" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold">{person.name}</h3>
                    <p className="text-sm text-muted">{person.position}</p>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}

        {otherDocuments.length > 0 && <Attachments items={otherDocuments} title={t('documentsTitle')} />}
      </div>

      <CtaBlock />
    </>
  );
}
