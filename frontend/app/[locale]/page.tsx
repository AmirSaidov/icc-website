import type {Metadata} from 'next';
import Image from 'next/image';
import {ArrowDown, Handshake, Landmark, Languages, Target} from 'lucide-react';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import {CtaBlock} from '@/components/sections/CtaBlock';
import {Button} from '@/components/ui/Button';
import {DirectionRow} from '@/components/ui/DirectionCard';
import {EventRow} from '@/components/ui/EventCard';
import {NewsCard} from '@/components/ui/NewsCard';
import {ArrowLink, SectionTitle} from '@/components/ui/SectionTitle';
import type {Locale} from '@/i18n/routing';
import {getDirections, getDocuments, getHome} from '@/lib/api';
import type {Home, HomeBlock, HomeBlockType} from '@/lib/api-types';
import {cn} from '@/lib/cn';
import {buildMetadata, staticPaths} from '@/lib/seo';

// ISR. Next требует здесь литерал, поэтому не REVALIDATE из lib/api.
export const revalidate = 60;

type Props = {params: Promise<{locale: Locale}>};

/** Блок главной из CMS по типу. Непереведённый на язык блок не показываем. */
function block(home: Home, type: HomeBlockType): HomeBlock | undefined {
  return home.blocks.find((b) => b.type === type && b.is_translated && b.title);
}

/** Дополнительные данные: если запрос упал, главная всё равно открывается. */
async function optional<T>(request: Promise<T>, label: string): Promise<T | null> {
  try {
    return await request;
  } catch (error) {
    console.error(`[Home] ${label}:`, error);
    return null;
  }
}

/** «Почему стоит обратиться»: иконка для каждого пункта. */
const WHY = [
  {key: 'official', Icon: Landmark},
  {key: 'bridge', Icon: Handshake},
  {key: 'languages', Icon: Languages},
  {key: 'result', Icon: Target}
] as const;

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
  const [home, allDirections, documents, t, tCommon] = await Promise.all([
    getHome(locale),
    optional(getDirections(locale), 'directions'),
    optional(getDocuments(locale), 'documents'),
    getTranslations('Home'),
    getTranslations('Common')
  ]);
  const hero = block(home, 'hero');
  const about = block(home, 'about');
  const cta = block(home, 'cta');
  // В /home/ только первые 4 направления, в макете — все.
  const directions = allDirections?.length ? allDirections : home.directions;
  // Документы идут по order из админки: первым — Положение о Центре.
  const regulation = documents?.[0];

  return (
    <>
      {/* 1. Первый экран: заголовок, кнопки; справа — картинка блока hero из CMS, если есть */}
      <section className="container-page grid items-center gap-10 py-12 md:py-16 lg:min-h-[500px] lg:grid-cols-2 lg:gap-16 lg:py-20">
        <div className="max-w-[560px] motion-safe:animate-fade-up">
          <p className="eyebrow text-muted">{t('heroEyebrow')}</p>
          <h1 className="mt-3 text-[40px] font-bold leading-[1.08] text-navy sm:text-5xl xl:text-[56px]">
            {hero?.title || t('heroTitle')}
          </h1>
          <p className="mt-5 max-w-[500px] leading-relaxed text-muted">{hero?.text || t('heroText')}</p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button href="/contacts#form" size="lg">
              {t('heroApply')}
            </Button>
            <Button href={hero?.button_link || '/services'} size="lg" variant="secondary">
              {hero?.button_text || t('heroServices')}
            </Button>
          </div>
        </div>
        {hero?.image && (
          <div className="border border-border bg-surface p-2 motion-safe:animate-fade-up motion-safe:[animation-delay:150ms]">
            <div className="relative aspect-[4/3] overflow-hidden bg-primary-light">
              <Image
                src={hero.image.large}
                alt=""
                fill
                priority
                sizes="(min-width: 1280px) 560px, (min-width: 1024px) 45vw, 100vw"
                className="object-cover"
              />
            </div>
          </div>
        )}
      </section>
      <div aria-hidden className="ornament-band" />

      {/* 2. О Центре */}
      <section aria-labelledby="home-about" className="container-page py-16 md:py-24">
        <div data-reveal className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <div className="border border-border bg-surface p-2">
            <div className="relative aspect-[4/3] overflow-hidden bg-primary-light">
              {about?.image && (
                <Image
                  src={about.image.large}
                  alt=""
                  fill
                  sizes="(min-width: 1280px) 560px, (min-width: 1024px) 45vw, 100vw"
                  className="object-cover"
                />
              )}
            </div>
          </div>
          <div>
            <p className="eyebrow text-primary">{about?.title || t('aboutEyebrow')}</p>
            <h2 id="home-about" className="mt-3 text-[28px] font-bold leading-tight text-navy md:text-[34px]">
              {t('aboutTitle')}
            </h2>
            <p className="mt-5 leading-relaxed text-muted">{about?.text || t('aboutText')}</p>
            <div className="mt-8 flex flex-col items-start gap-5 sm:flex-row sm:items-center sm:gap-6">
              <Button href={about?.button_link || '/about'} size="lg" variant="secondary" className="w-full sm:w-auto">
                {about?.button_text || t('aboutLink')}
              </Button>
              {regulation && (
                <a
                  href={regulation.url}
                  download
                  className="inline-flex items-center gap-1 text-[13px] font-semibold text-primary hover:underline"
                >
                  {t('regulation')}
                  <ArrowDown aria-hidden className="size-4" />
                </a>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* 3. Направления деятельности */}
      {directions.length > 0 && (
        <section aria-labelledby="home-directions" className="border-y border-border bg-surface py-16 md:py-24">
          <div className="container-page">
            <SectionTitle id="home-directions" action={{href: '/directions', label: tCommon('allDirections')}}>
              {t('directionsTitle')}
            </SectionTitle>
            <ul data-reveal-stagger className="grid md:grid-cols-2 md:gap-x-10">
              {directions.map((item, index) => (
                <li key={item.id}>
                  <DirectionRow item={item} index={index} />
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {/* 4. Почему стоит обратиться в Центр */}
      <section aria-labelledby="home-why" className="bg-navy py-16 text-white md:py-24">
        <div className="container-page">
          <SectionTitle id="home-why" inverse className="max-w-md">
            {t('whyTitle')}
          </SectionTitle>
          <ul data-reveal-stagger className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {WHY.map(({key, Icon}) => (
              <li key={key} className="flex gap-4 lg:block">
                <Icon aria-hidden className="size-8 shrink-0 text-sky" strokeWidth={1.5} />
                <div className="lg:mt-4">
                  <h3 className="font-sans text-base font-semibold text-white">{t(`why.${key}.title`)}</h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-white/65">{t(`why.${key}.text`)}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* 5. Новости и мероприятия */}
      <div className="container-page grid gap-14 py-16 md:py-24 lg:grid-cols-[2fr_1fr] lg:gap-12">
        <section aria-labelledby="home-news" className="min-w-0">
          <SectionTitle id="home-news" action={{href: '/news', label: tCommon('allNews')}}>
            {t('newsTitle')}
          </SectionTitle>
          {home.news.length > 0 ? (
            <ul data-reveal-stagger className="grid gap-6 sm:grid-cols-2">
              {home.news.slice(0, 3).map((item, index) => (
                // В макете на компьютере две новости; третья — только на телефоне, строкой.
                <li key={item.id} className={cn('flex [&>*]:flex-1', index === 2 && 'sm:hidden')}>
                  <NewsCard item={item} excerpt={false} compact={index > 0} />
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted">{t('noNews')}</p>
          )}
        </section>

        <section aria-labelledby="home-events" className="min-w-0">
          <SectionTitle id="home-events">
            {t('eventsTitle')}
          </SectionTitle>
          {home.events.length > 0 ? (
            <ul data-reveal-stagger className="border-t border-border">
              {home.events.map((item) => (
                <li key={item.id}>
                  <EventRow item={item} />
                </li>
              ))}
            </ul>
          ) : (
            <p className="border-t border-border pt-4 text-muted">{t('noEvents')}</p>
          )}
          <ArrowLink href="/events" className="mt-5">
            {t('calendar')}
          </ArrowLink>
        </section>
      </div>

      {/* 6. Добро пожаловать к сотрудничеству */}
      <CtaBlock title={cta?.title} text={cta?.text} />
    </>
  );
}
