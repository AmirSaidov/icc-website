import createMiddleware from 'next-intl/middleware';
import {NextResponse, type NextRequest} from 'next/server';
import {hasLocale} from 'next-intl';
import {LOCALE_COOKIE, routing} from './i18n/routing';

const intlMiddleware = createMiddleware(routing);

export default function middleware(request: NextRequest) {
  // «/» → язык из cookie NEXT_LOCALE, иначе /ru.
  if (request.nextUrl.pathname === '/') {
    const saved = request.cookies.get(LOCALE_COOKIE)?.value;
    const locale = hasLocale(routing.locales, saved)
      ? saved
      : routing.defaultLocale;
    const url = request.nextUrl.clone();
    url.pathname = `/${locale}`;
    return NextResponse.redirect(url);
  }
  return intlMiddleware(request);
}

export const config = {
  // Всё, кроме api, служебных файлов Next и файлов с расширением.
  matcher: '/((?!api|_next|_vercel|.*\\..*).*)'
};
