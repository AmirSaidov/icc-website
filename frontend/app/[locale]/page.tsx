import type {Metadata} from 'next';
import Image from 'next/image';
import {ArrowRight} from 'lucide-react';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import {CtaBlock} from '@/components/sections/CtaBlock';
import {Button} from '@/components/ui/Button';
import {DirectionCard} from '@/components/ui/DirectionCard';
import {EventCard} from '@/components/ui/EventCard';
import {Icon} from '@/components/ui/Icon';
import {NewsCard} from '@/components/ui/NewsCard';
import {SectionTitle} from '@/components/ui/SectionTitle';
import {Link} from '@/i18n/navigation';
import type {Locale} from '@/i18n/routing';
import {getHome} from '@/lib/api';
import {buildMetadata, staticPaths} from '@/lib/seo';

// ISR. Next требует здесь литерал, поэтому не REVALIDATE из lib/api.
export const revalidate = 60;

type Props = {params: Promise<{locale: Locale}>};

export async function generateMetadata({params}: Props): Promise<Metadata> {
  const {locale} = await params;
  const home = await getHome(locale);
  return buildMetadata({
    locale,
    paths: staticPaths(''),
    seo: home.seo,
    title: home.hero.title,
    description: home.hero.subtitle,
    image: home.hero.image.url,
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

  return (
    <>
      {/* 1. Первый экран */}
      <section className="bg-primary-light">
        <div className="container-page grid items-center gap-8 py-10 md:py-14 lg:grid-cols-2 lg:gap-12 lg:py-20">
          <div>
            <h1 className="text-3xl font-bold leading-tight text-text sm:text-4xl xl:text-5xl">{home.hero.title}</h1>
            <p className="mt-5 max-w-xl text-lg text-muted">{home.hero.subtitle}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button href="/services" size="lg">
                {t('heroServices')}
              </Button>
              <Button href="/contacts#form" size="lg" variant="secondary">
                {t('heroContact')}
              </Button>
            </div>
          </div>
          <div className="relative aspect-[16/10] overflow-hidden rounded-lg lg:aspect-[4/3]">
            <Image
              src={home.hero.image.url}
              alt={home.hero.image.alt}
              fill
              priority
              sizes="(min-width: 1280px) 600px, (min-width: 1024px) 50vw, 100vw"
              className="object-cover"
            />
          </div>
        </div>
      </section>

      {/* 2. Кратко о Центре */}
      <section aria-labelledby="home-about" className="container-page py-14 md:py-20">
        <div className="grid gap-6 lg:grid-cols-[1fr_2fr] lg:gap-12">
          <h2 id="home-about" className="text-2xl font-bold md:text-3xl">
            {home.about.title}
          </h2>
          <div>
            <p className="text-lg leading-relaxed">{home.about.text}</p>
            <Link href="/about" className="mt-5 inline-flex items-center gap-1 font-medium text-primary hover:underline">
              {t('aboutLink')}
              <ArrowRight aria-hidden className="size-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* 3. Направления */}
      {home.directions.length > 0 && (
        <section aria-labelledby="home-directions" className="border-t border-border py-14 md:py-20">
          <div className="container-page">
            <SectionTitle id="home-directions" action={{href: '/directions', label: tCommon('allDirections')}}>
              {t('directionsTitle')}
            </SectionTitle>
            <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
      <section aria-labelledby="home-cooperation" className="bg-primary-light py-14 md:py-20">
        <div className="container-page grid items-center gap-8 lg:grid-cols-2 lg:gap-12">
          {home.cooperation.image && (
            <div className="relative aspect-[16/10] overflow-hidden rounded-lg">
              <Image
                src={home.cooperation.image.url}
                alt={home.cooperation.image.alt}
                fill
                sizes="(min-width: 1280px) 600px, (min-width: 1024px) 50vw, 100vw"
                className="object-cover"
              />
            </div>
          )}
          <div>
            <h2 id="home-cooperation" className="text-2xl font-bold md:text-3xl">
              {home.cooperation.title}
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-muted">{home.cooperation.text}</p>
            <Button href="/cooperation" variant="secondary" className="mt-6">
              {t('cooperationLink')}
              <ArrowRight aria-hidden className="size-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* 5. Преимущества */}
      {home.advantages.length > 0 && (
        <section aria-labelledby="home-advantages" className="container-page py-14 md:py-20">
          <SectionTitle id="home-advantages">{t('advantagesTitle')}</SectionTitle>
          <ul className="grid gap-x-8 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
            {home.advantages.map((advantage) => (
              <li key={advantage.title} className="flex gap-4">
                <span className="flex size-12 shrink-0 items-center justify-center rounded-md bg-primary text-white">
                  <Icon name={advantage.icon} className="size-6" />
                </span>
                <div className="min-w-0">
                  <h3 className="font-semibold">{advantage.title}</h3>
                  <p className="mt-1 text-sm text-muted">{advantage.text}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* 6. Новости и мероприятия */}
      <section aria-labelledby="home-news" className="border-t border-border py-14 md:py-20">
        <div className="container-page">
          <SectionTitle id="home-news" action={{href: '/news', label: tCommon('allNews')}}>
            {t('newsTitle')}
          </SectionTitle>
          <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
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
            <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
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
      <CtaBlock />
    </>
  );
}
