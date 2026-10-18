import {Globe, Mail, MapPin, Phone, Send} from 'lucide-react';
import {getTranslations} from 'next-intl/server';
import {Link} from '@/i18n/navigation';
import type {Locale} from '@/i18n/routing';
import {getContacts} from '@/lib/api';
import type {Contacts} from '@/lib/api-types';
import {Logo} from './Logo';
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
  const [t, tNav, contacts] = await Promise.all([
    getTranslations('Footer'),
    getTranslations('Nav'),
    loadContacts(locale)
  ]);

  return (
    <footer className="mt-auto bg-text text-white/85">
      <div className="container-page grid gap-10 py-12 md:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr]">
        <section aria-labelledby="footer-contacts" className="space-y-4">
          <Logo inverse />
          <h2 id="footer-contacts" className="sr-only">
            {t('contacts')}
          </h2>
          {contacts && (
            <ul className="space-y-3 text-sm">
              {contacts.address && (
                <li className="flex gap-3">
                  <MapPin aria-hidden className="mt-0.5 size-4 shrink-0" />
                  <span>{contacts.address}</span>
                </li>
              )}
              {contacts.phones.map((phone) => (
                <li key={phone.number} className="flex gap-3">
                  <Phone aria-hidden className="mt-0.5 size-4 shrink-0" />
                  <span>
                    {phone.label && <span className="text-white/60">{phone.label}: </span>}
                    <a href={telHref(phone.number)} className="hover:text-white hover:underline">
                      {phone.number}
                    </a>
                  </span>
                </li>
              ))}
              {contacts.email && (
                <li className="flex gap-3">
                  <Mail aria-hidden className="mt-0.5 size-4 shrink-0" />
                  <a href={`mailto:${contacts.email}`} className="break-all hover:text-white hover:underline">
                    {contacts.email}
                  </a>
                </li>
              )}
            </ul>
          )}
        </section>

        <nav aria-labelledby="footer-menu">
          <h2 id="footer-menu" className="mb-4 font-semibold text-white">
            {t('menu')}
          </h2>
          <ul className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm md:grid-cols-1">
            {NAV_ITEMS.map((item) => (
              <li key={item.key}>
                <Link href={item.href} className="hover:text-white hover:underline">
                  {tNav(item.key)}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {contacts && contacts.socials.length > 0 && (
          <section aria-labelledby="footer-socials">
            <h2 id="footer-socials" className="mb-4 font-semibold text-white">
              {t('socials')}
            </h2>
            <ul className="flex flex-wrap gap-2 text-sm">
              {contacts.socials.map((social) => (
                <li key={social.url}>
                  <a
                    href={social.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 rounded-md border border-white/20 px-3 py-2 hover:border-white/50 hover:text-white"
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
          </section>
        )}
      </div>
      <div className="border-t border-white/10">
        <p className="container-page py-5 text-sm text-white/60">
          {t('rights', {year: new Date().getFullYear()})}
        </p>
      </div>
    </footer>
  );
}
