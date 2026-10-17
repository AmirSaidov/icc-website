import type {Metadata, Viewport} from 'next';
import {Inter, Noto_Sans_SC} from 'next/font/google';
import {notFound} from 'next/navigation';
import {hasLocale, NextIntlClientProvider} from 'next-intl';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import type {ReactNode} from 'react';
import {AlternatesProvider} from '@/components/layout/Alternates';
import {Footer} from '@/components/layout/Footer';
import {Header} from '@/components/layout/Header';
import {htmlLang, routing, type Locale} from '@/i18n/routing';
import {SITE_URL} from '@/lib/seo';
import '../globals.css';

const inter = Inter({
  subsets: ['latin', 'cyrillic'],
  variable: '--font-inter',
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

export function generateStaticParams() {
  return routing.locales.map((locale) => ({locale}));
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
  themeColor: '#0b3d91'
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
    <html lang={htmlLang[locale]} className={`${inter.variable} ${notoSansSC.variable}`}>
      <body className="flex min-h-dvh flex-col font-sans antialiased">
        <NextIntlClientProvider>
          <AlternatesProvider>
            <Header />
            <main id="main" className="flex-1">
              {children}
            </main>
            <Footer locale={locale} />
          </AlternatesProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
