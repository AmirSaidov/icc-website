import Image from 'next/image';
import {CalendarDays, MapPin} from 'lucide-react';
import {useLocale, useTranslations} from 'next-intl';
import type {Locale} from '@/i18n/routing';
import type {EventListItem} from '@/lib/api-types';
import {formatDateRange} from '@/lib/format';
import {Badge} from './Badge';
import {Card, CardLink} from './Card';
import {CARD_IMAGE_SIZES} from './NewsCard';

export function EventCard({item, headingLevel = 'h3'}: {item: EventListItem; headingLevel?: 'h2' | 'h3'}) {
  const locale = useLocale() as Locale;
  const tCard = useTranslations('EventCard');
  const Heading = headingLevel;

  return (
    <Card>
      <div className="relative aspect-[3/2] bg-primary-light">
        {item.cover && (
          <Image
            src={item.cover.small}
            alt={item.title ?? ''}
            fill
            sizes={CARD_IMAGE_SIZES}
            className="object-cover transition-transform duration-500 group-has-[a.card-link:hover]:scale-105"
          />
        )}
        <Badge tone="inverse" className="absolute left-3 top-3">
          {item.type.label}
        </Badge>
      </div>
      <div className="flex flex-1 flex-col gap-3 p-5">
        <Heading className="line-clamp-3 text-lg font-semibold leading-snug">
          <CardLink href={`/events/${item.slug}`}>{item.title}</CardLink>
        </Heading>
        <dl className="mt-auto space-y-1.5 text-sm text-muted">
          <div className="flex items-start gap-2">
            <dt className="sr-only">{tCard('date')}</dt>
            <CalendarDays aria-hidden className="mt-0.5 size-4 shrink-0 text-primary" />
            <dd>
              <time dateTime={item.start_at}>{formatDateRange(item.start_at, item.end_at ?? null, locale)}</time>
            </dd>
          </div>
          {item.location && (
            <div className="flex items-start gap-2">
              <dt className="sr-only">{tCard('location')}</dt>
              <MapPin aria-hidden className="mt-0.5 size-4 shrink-0 text-primary" />
              <dd>{item.location}</dd>
            </div>
          )}
        </dl>
      </div>
    </Card>
  );
}
