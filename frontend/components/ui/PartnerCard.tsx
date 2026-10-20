import Image from 'next/image';
import {ArrowUpRight} from 'lucide-react';
import {useTranslations} from 'next-intl';
import type {Partner} from '@/lib/api-types';

/** Инициалы вместо логотипа: «Silk Road Trading» → «SR». */
const initials = (name: string) =>
  name
    .replace(/[«»"()]/g, '')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase();

/**
 * Партнёр в разделе «Сотрудничество»: логотип на белой плашке, страна, название,
 * описание и ссылка на сайт. Логотипы обычно широкие (3:1) — вписываем, не обрезая.
 */
export function PartnerCard({partner}: {partner: Partner}) {
  const t = useTranslations('Cooperation');
  const tCommon = useTranslations('Common');
  const name = partner.name ?? '';

  return (
    <article className="flex h-full flex-col border border-border bg-surface transition-colors duration-300 hover:border-primary/40">
      <div className="flex h-28 items-center justify-center border-b border-border bg-white px-6 py-4">
        {partner.logo ? (
          <span className="relative block h-full w-full">
            <Image
              src={partner.logo.small}
              alt={name}
              fill
              sizes="(min-width: 1024px) 320px, (min-width: 640px) 45vw, 90vw"
              className="object-contain"
            />
          </span>
        ) : (
          <span aria-hidden className="flex size-14 items-center justify-center rounded-sm bg-navy font-serif text-xl font-bold text-white">
            {initials(name)}
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-2 p-5">
        {partner.country.name && <p className="eyebrow text-primary">{partner.country.name}</p>}
        <h3 className="text-lg font-bold leading-snug text-navy">{name}</h3>
        {partner.description && <p className="line-clamp-3 text-sm text-muted">{partner.description}</p>}
        {partner.website && (
          <a
            href={partner.website}
            target="_blank"
            rel="noopener noreferrer"
            className="group mt-auto inline-flex items-center gap-1 self-start pt-2 text-[13px] font-semibold text-primary hover:underline"
          >
            {t('website')}
            <span className="sr-only"> {name} ({tCommon('openInNewTab')})</span>
            <ArrowUpRight aria-hidden className="size-4 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
          </a>
        )}
      </div>
    </article>
  );
}
