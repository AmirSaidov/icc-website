import Image from 'next/image';
import {useLocale} from 'next-intl';
import type {Locale} from '@/i18n/routing';
import type {NewsListItem} from '@/lib/api-types';
import {formatDate} from '@/lib/format';
import {Badge} from './Badge';
import {Card, CardLink} from './Card';

export const CARD_IMAGE_SIZES = '(min-width: 1280px) 384px, (min-width: 768px) 33vw, (min-width: 640px) 50vw, 100vw';

/** Работает и в серверных, и в клиентских компонентах («Загрузить ещё»). */
export function NewsCard({item, headingLevel = 'h3'}: {item: NewsListItem; headingLevel?: 'h2' | 'h3'}) {
  const locale = useLocale() as Locale;
  const Heading = headingLevel;

  return (
    <Card>
      <div className="relative aspect-[3/2] bg-primary-light">
        {item.cover && (
          <Image
            src={item.cover.url}
            alt={item.cover.alt}
            fill
            sizes={CARD_IMAGE_SIZES}
            className="object-cover"
          />
        )}
      </div>
      <div className="flex flex-1 flex-col gap-3 p-5">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
          <time dateTime={item.published_at}>{formatDate(item.published_at, locale)}</time>
          {item.category && <Badge>{item.category.title}</Badge>}
        </div>
        <Heading className="line-clamp-3 text-lg font-semibold leading-snug">
          <CardLink href={`/news/${item.slug}`}>{item.title}</CardLink>
        </Heading>
        {item.summary && <p className="line-clamp-3 text-sm text-muted">{item.summary}</p>}
      </div>
    </Card>
  );
}
