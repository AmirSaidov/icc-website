import type {Metadata} from 'next';
import Image from 'next/image';
import {ArrowRight} from 'lucide-react';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import {CtaBlock} from '@/components/sections/CtaBlock';
import {Button} from '@/components/ui/Button';
import {DirectionCard} from '@/components/ui/DirectionCard';
import {EventCard} from '@/components/ui/EventCard';
import {NewsCard} from '@/components/ui/NewsCard';
import {SectionTitle} from '@/components/ui/SectionTitle';
import {Link} from '@/i18n/navigation';
import type {Locale} from '@/i18n/routing';
import {getHome} from '@/lib/api';
import type {Home, HomeBlock, HomeBlockType} from '@/lib/api-types';
import {buildMetadata, staticPaths} from '@/lib/seo';

// ISR. Next требует здесь литерал, поэтому не REVALIDATE из lib/api.
export const revalidate = 60;

type Props = {params: Promise<{locale: Locale}>};

/** Блок главной из CMS по типу. Непереведённый на язык блок не показываем. */
function block(home: Home, type: HomeBlockType): HomeBlock | undefined {
  return home.blocks.find((b) => b.type === type && b.is_translated && b.title);
}

export async function generateMetadata({params}: Props): Promise<Metadata> {
  const {locale} = await params;
  const home = await getHome(locale);
  const hero = block(home, 'hero');
  return buildMetadata({
    locale,
    paths: staticPaths(''),
    seo: home.seo,
    title: hero?.title ?? null,
    description: hero?.text,
    image: hero?.image?.large,
    absoluteTitle: true
  });
}

export default async function HomePage({params}: Props) {
  const {locale} = await params;
  setRequestLocale(locale);
  const [home, t, tCommon] = await Promise.all([
    getHome(locale),
    getTranslations('Home'),
    getTranslations('Common')
  ]);
  const hero = block(home, 'hero');
  const about = block(home, 'about');
  const advantages = block(home, 'advantages');
  const kgChina = block(home, 'kg_china');
  const cta = block(home, 'cta');

  return (
    <>
      {/* 1. Первый экран */}
      {hero && (
        <section className="bg-primary-light">
          <div className="container-page grid items-center gap-8 py-10 md:py-14 lg:grid-cols-2 lg:gap-12 lg:py-20">
            <div>
              <h1 className="text-3xl font-bold leading-tight text-text motion-safe:animate-fade-up sm:text-4xl xl:text-5xl">{hero.title}</h1>
              {hero.text && <p className="mt-5 max-w-xl text-lg text-muted motion-safe:animate-fade-up motion-safe:[animation-delay:120ms]">{hero.text}</p>}
              <div className="mt-8 flex flex-wrap gap-3 motion-safe:animate-fade-up motion-safe:[animation-delay:240ms]">
                <Button href={hero.button_link || '/services'} size="lg">
                  {hero.button_text || t('heroServices')}
                </Button>
                <Button href="/contacts#form" size="lg" variant="secondary">
                  {t('heroContact')}
                </Button>
              </div>
            </div>
            {hero.image && (
              <div className="relative aspect-[16/10] overflow-hidden rounded-lg shadow-xl motion-safe:animate-zoom-in lg:aspect-[4/3]">
                <Image
                  src={hero.image.large}
                  alt=""
                  fill
                  priority
                  sizes="(min-width: 1280px) 600px, (min-width: 1024px) 50vw, 100vw"
                  className="object-cover"
                />
              </div>
            )}
          </div>
        </section>
      )}

      {/* 2. Кратко о Центре */}
      {about && (
        <section aria-labelledby="home-about" className="container-page py-14 md:py-20">
          <div data-reveal className="grid gap-6 lg:grid-cols-[1fr_2fr] lg:gap-12">
            <h2 id="home-about" className="text-2xl font-bold md:text-3xl">
              {about.title}
            </h2>
            <div>
              {about.text && <p className="text-lg leading-relaxed">{about.text}</p>}
              <Link
                href={about.button_link || '/about'}
                className="group mt-5 inline-flex items-center gap-1 font-medium text-primary hover:underline"
              >
                {about.button_text || t('aboutLink')}
                <ArrowRight aria-hidden className="size-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* 3. Направления */}
      {home.directions.length > 0 && (
        <section aria-labelledby="home-directions" className="border-t border-border py-14 md:py-20">
          <div className="container-page">
            <SectionTitle id="home-directions" action={{href: '/directions', label: tCommon('allDirections')}}>
              {t('directionsTitle')}
            </SectionTitle>
            <ul data-reveal-stagger className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {home.directions.map((item) => (
                <li key={item.id} className="flex [&>*]:flex-1">
                  <DirectionCard item={item} />
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {/* 4. Сотрудничество Кыргызстана и Китая */}
      {kgChina && (
        <section aria-labelledby="home-cooperation" className="bg-primary-light py-14 md:py-20">
          <div data-reveal className="container-page grid items-center gap-8 lg:grid-cols-2 lg:gap-12">
            {kgChina.image && (
              <div className="relative aspect-[16/10] overflow-hidden rounded-lg shadow-xl">
                <Image
                  src={kgChina.image.large}
                  alt=""
                  fill
                  sizes="(min-width: 1280px) 600px, (min-width: 1024px) 50vw, 100vw"
                  className="object-cover"
                />
              </div>
            )}
            <div>
              <h2 id="home-cooperation" className="text-2xl font-bold md:text-3xl">
                {kgChina.title}
              </h2>
              {kgChina.text && <p className="mt-4 text-lg leading-relaxed text-muted">{kgChina.text}</p>}
              <Button href={kgChina.button_link || '/cooperation'} variant="secondary" className="mt-6">
                {kgChina.button_text || t('cooperationLink')}
                <ArrowRight aria-hidden className="size-4" />
              </Button>
            </div>
          </div>
        </section>
      )}

      {/* 5. Преимущества */}
      {advantages && (
        <section aria-labelledby="home-advantages" className="container-page py-14 md:py-20">
          <SectionTitle id="home-advantages">{advantages.title}</SectionTitle>
          {advantages.text && <p data-reveal className="max-w-3xl text-lg leading-relaxed text-muted">{advantages.text}</p>}
        </section>
      )}

      {/* 6. Новости и мероприятия */}
      <section aria-labelledby="home-news" className="border-t border-border py-14 md:py-20">
        <div className="container-page">
          <SectionTitle id="home-news" action={{href: '/news', label: tCommon('allNews')}}>
            {t('newsTitle')}
          </SectionTitle>
          <ul data-reveal-stagger className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {home.news.map((item) => (
              <li key={item.id} className="flex [&>*]:flex-1">
                <NewsCard item={item} />
              </li>
            ))}
          </ul>

          <SectionTitle id="home-events" className="mt-14 md:mt-20" action={{href: '/events', label: tCommon('allEvents')}}>
            {t('eventsTitle')}
          </SectionTitle>
          {home.events.length > 0 ? (
            <ul data-reveal-stagger className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {home.events.map((item) => (
                <li key={item.id} className="flex [&>*]:flex-1">
                  <EventCard item={item} />
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted">{t('noEvents')}</p>
          )}
        </div>
      </section>

      {/* 7. Призыв к действию */}
      <CtaBlock title={cta?.title} text={cta?.text} />
    </>
  );
}
