import type {Metadata, Viewport} from 'next';
import {Manrope, Noto_Sans_SC} from 'next/font/google';
import {notFound} from 'next/navigation';
import {hasLocale, NextIntlClientProvider} from 'next-intl';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import type {ReactNode} from 'react';
import {AlternatesProvider} from '@/components/layout/Alternates';
import {Footer} from '@/components/layout/Footer';
import {Header} from '@/components/layout/Header';
import {RevealObserver} from '@/components/layout/RevealObserver';
import {htmlLang, routing, type Locale} from '@/i18n/routing';
import {SITE_URL} from '@/lib/seo';
import '../globals.css';

// Гротеск брендбука. cyrillic-ext — для кыргызских ң, ө, ү («Теңир-Тоо»).
const manrope = Manrope({
  subsets: ['latin', 'cyrillic', 'cyrillic-ext'],
  variable: '--font-manrope',
  display: 'swap'
});

// Иероглифы. Google режет шрифт на unicode-range куски, браузер качает
// только нужные, поэтому на /ru и /en китайский шрифт не грузится.
const notoSansSC = Noto_Sans_SC({
  weight: ['400', '500', '700'],
  variable: '--font-noto-sc',
  display: 'swap',
  preload: false
});

// Пустой список: страницы не пререндерятся при сборке, а рендерятся при первом запросе
// и кэшируются (ISR, revalidate = 60). Так деплой на Vercel не зависит от того, доступен ли бэк.
// Неизвестный язык отсекает hasLocale ниже.
export function generateStaticParams() {
  return [];
}

export async function generateMetadata({params}: {params: Promise<{locale: string}>}): Promise<Metadata> {
  const {locale} = await params;
  const t = await getTranslations({locale: locale as Locale, namespace: 'Meta'});
  return {
    metadataBase: new URL(SITE_URL),
    title: {default: t('siteName'), template: `%s | ${t('siteName')}`},
    description: t('siteDescription'),
    openGraph: {siteName: t('siteName')}
  };
}

export const viewport: Viewport = {
  themeColor: '#12151e'
};

export default async function LocaleLayout({
  children,
  params
}: {
  children: ReactNode;
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;
  if (!hasLocale(routing.locales, locale)) notFound();
  setRequestLocale(locale);

  return (
    // suppressHydrationWarning: скрипт ниже добавляет класс js до гидрации
    <html lang={htmlLang[locale]} className={`${manrope.variable} ${notoSansSC.variable}`} suppressHydrationWarning>
      <head>
        {/* До первой отрисовки: включает анимации появления (globals.css). Без JS всё видно сразу. */}
        <script dangerouslySetInnerHTML={{__html: "document.documentElement.classList.add('js')"}} />
      </head>
      <body className="flex min-h-dvh flex-col font-sans antialiased">
        <NextIntlClientProvider>
          <AlternatesProvider>
            <Header />
            <main id="main" className="flex-1">
              {children}
            </main>
            <Footer locale={locale} />
            <RevealObserver />
          </AlternatesProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
