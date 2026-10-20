import {Globe, Send} from 'lucide-react';
import {getTranslations} from 'next-intl/server';
import {Link} from '@/i18n/navigation';
import type {Locale} from '@/i18n/routing';
import {getContacts} from '@/lib/api';
import type {Contacts} from '@/lib/api-types';
import {NAV_ITEMS} from './nav';

/** type из API — ключ соцсети; незнакомый показываем как есть. */
const SOCIAL_NAMES: Record<string, string> = {
  telegram: 'Telegram',
  whatsapp: 'WhatsApp',
  facebook: 'Facebook',
  instagram: 'Instagram',
  youtube: 'YouTube',
  linkedin: 'LinkedIn',
  wechat: 'WeChat'
};

/** Подвал не должен ронять страницу, если /contacts/ недоступен. */
async function loadContacts(locale: Locale): Promise<Contacts | null> {
  try {
    return await getContacts(locale);
  } catch (error) {
    console.error('[Footer] contacts:', error);
    return null;
  }
}

const telHref = (phone: string) => `tel:${phone.replace(/[^\d+]/g, '')}`;

export async function Footer({locale}: {locale: Locale}) {
  const [t, tNav, tHeader, contacts] = await Promise.all([
    getTranslations('Footer'),
    getTranslations('Nav'),
    getTranslations('Header'),
    loadContacts(locale)
  ]);

  return (
    <footer className="mt-auto bg-navy text-white/80">
      <div aria-hidden className="ornament-band" />
      <div className="container-page grid gap-10 py-12 md:grid-cols-2 lg:grid-cols-[1.3fr_1fr_1fr]">
        <div>
          <p className="font-serif text-lg font-bold text-white">{tHeader('logoTitle')}</p>
          <p className="mt-1 text-sm">{tHeader('logoSubtitle')}</p>
          {/* Название по-китайски — часть фирменного стиля; на китайской версии оно уже в строке выше. */}
          {locale !== 'zh' && (
            <p lang="zh-Hans" className="mt-1 text-sm text-white/60">
              工业合作中心
            </p>
          )}
        </div>

        <nav aria-labelledby="footer-menu">
          <h2 id="footer-menu" className="mb-3 font-sans text-sm font-semibold text-white">
            {t('menu')}
          </h2>
          <ul className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm md:grid-cols-1">
            {NAV_ITEMS.map((item) => (
              <li key={item.key}>
                <Link href={item.href} className="hover:text-white hover:underline">
                  {tNav(item.key)}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <section aria-labelledby="footer-contacts">
          <h2 id="footer-contacts" className="mb-3 font-sans text-sm font-semibold text-white">
            {t('contacts')}
          </h2>
          {contacts && (
            <ul className="space-y-1.5 text-sm">
              {contacts.address && <li>{contacts.address}</li>}
              {contacts.phones.map((phone) => (
                <li key={phone.number}>
                  {phone.label && <span className="text-white/55">{phone.label}: </span>}
                  <a href={telHref(phone.number)} className="hover:text-white hover:underline">
                    {phone.number}
                  </a>
                </li>
              ))}
              {contacts.email && (
                <li>
                  <a href={`mailto:${contacts.email}`} className="break-all hover:text-white hover:underline">
                    {contacts.email}
                  </a>
                </li>
              )}
            </ul>
          )}
          {contacts && contacts.socials.length > 0 && (
            <>
              <h3 className="sr-only">{t('socials')}</h3>
              <ul className="mt-4 flex flex-wrap gap-2 text-sm">
                {contacts.socials.map((social) => (
                  <li key={social.url}>
                    <a
                      href={social.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 rounded-sm border border-white/20 px-3 py-1.5 hover:border-white/50 hover:text-white"
                    >
                      {social.type === 'telegram' ? (
                        <Send aria-hidden className="size-4" />
                      ) : (
                        <Globe aria-hidden className="size-4" />
                      )}
                      {SOCIAL_NAMES[social.type] ?? social.type}
                    </a>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      </div>
      <div className="container-page">
        <p className="border-t border-white/10 py-5 text-xs text-white/60">
          {t('rights', {year: new Date().getFullYear()})}
        </p>
      </div>
    </footer>
  );
}
