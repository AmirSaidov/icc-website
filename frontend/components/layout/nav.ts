/** 7 разделов сайта: шапка, мобильное меню, подвал. Подписи — messages: Nav.{key}. */
export const NAV_ITEMS = [
  {key: 'home', href: '/', match: []},
  {key: 'about', href: '/about', match: []},
  {key: 'directions', href: '/directions', match: []},
  {key: 'services', href: '/services', match: []},
  {key: 'news', href: '/news', match: ['/events']},
  {key: 'cooperation', href: '/cooperation', match: []},
  {key: 'contacts', href: '/contacts', match: []}
] as const;

export type NavKey = (typeof NAV_ITEMS)[number]['key'];

/** pathname без префикса языка: '/news/delovaya-missiya'. */
export function isActive(item: (typeof NAV_ITEMS)[number], pathname: string) {
  if (item.href === '/') return pathname === '/';
  return [item.href, ...item.match].some((href) => pathname === href || pathname.startsWith(`${href}/`));
}

/** Разделы с детальными страницами /{section}/{slug}. */
export const DETAIL_SECTIONS = ['directions', 'services', 'news', 'events'] as const;
export type DetailSection = (typeof DETAIL_SECTIONS)[number];

export function matchDetail(pathname: string): {section: DetailSection; slug: string} | null {
  const [, section, slug, ...rest] = pathname.split('/');
  if (!slug || rest.length) return null;
  return (DETAIL_SECTIONS as readonly string[]).includes(section)
    ? {section: section as DetailSection, slug}
    : null;
}
