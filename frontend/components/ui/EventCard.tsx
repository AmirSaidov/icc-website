import Image from 'next/image';
import {MapPin} from 'lucide-react';
import {useLocale, useTranslations} from 'next-intl';
import type {Locale} from '@/i18n/routing';
import type {EventListItem} from '@/lib/api-types';
import {dayMonth, formatDateRange} from '@/lib/format';
import {Badge} from './Badge';
import {CardLink} from './Card';
import {CARD_IMAGE_SIZES} from './NewsCard';

/** Карточка в разделе «Мероприятия»: фото в рамке, как у новостей. */
export function EventCard({item, headingLevel = 'h3'}: {item: EventListItem; headingLevel?: 'h2' | 'h3'}) {
  const locale = useLocale() as Locale;
  const tCard = useTranslations('EventCard');
  const Heading = headingLevel;

  return (
    <article className="group relative flex flex-col gap-3">
      <div className="border border-border bg-surface p-1.5 transition-colors duration-300 group-has-[a.card-link:hover]:border-primary/40">
        <div className="relative aspect-[3/2] overflow-hidden bg-primary-light">
          {item.cover && (
            <Image
              src={item.cover.small}
              alt={item.title ?? ''}
              fill
              sizes={CARD_IMAGE_SIZES}
              className="object-cover transition-transform duration-500 group-has-[a.card-link:hover]:scale-105"
            />
          )}
          <Badge tone="inverse" className="absolute left-2 top-2">
            {item.type.label}
          </Badge>
        </div>
      </div>
      <div className="flex flex-col gap-1.5">
        <p className="text-xs font-semibold text-primary">
          <span className="sr-only">{tCard('date')}: </span>
          <time dateTime={item.start_at}>{formatDateRange(item.start_at, item.end_at ?? null, locale)}</time>
        </p>
        <Heading className="line-clamp-3 text-lg font-bold leading-snug text-navy">
          <CardLink href={`/events/${item.slug}`}>{item.title}</CardLink>
        </Heading>
        {item.location && (
          <p className="flex items-start gap-1.5 text-sm text-muted">
            <MapPin aria-hidden className="mt-0.5 size-3.5 shrink-0" />
            <span>
              <span className="sr-only">{tCard('location')}: </span>
              {item.location}
            </span>
          </p>
        )}
      </div>
    </article>
  );
}

/** Строка ближайшего мероприятия на главной: большой день, месяц, название, «тип · город». */
export function EventRow({item}: {item: EventListItem}) {
  const locale = useLocale() as Locale;
  const {day, month} = dayMonth(item.start_at, locale);

  return (
    <article className="group relative flex items-start gap-4 border-b border-border py-4">
      <time dateTime={item.start_at} className="flex w-12 shrink-0 flex-col items-center text-center leading-none">
        <span className="font-serif text-[28px] font-bold text-primary">{day}</span>
        <span className="mt-1 text-[11px] text-muted">{month}</span>
      </time>
      <div className="min-w-0">
        <h3 className="font-sans text-sm font-semibold leading-snug text-navy">
          <CardLink href={`/events/${item.slug}`}>{item.title}</CardLink>
        </h3>
        <p className="mt-1 text-xs text-muted">
          {item.type.label}
          {item.location && ` · ${item.location}`}
        </p>
      </div>
    </article>
  );
}
