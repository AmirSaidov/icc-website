import Image from 'next/image';
import {useLocale} from 'next-intl';
import type {Locale} from '@/i18n/routing';
import type {NewsListItem} from '@/lib/api-types';
import {formatDate} from '@/lib/format';
import {cn} from '@/lib/cn';
import {CardLink} from './Card';

export const CARD_IMAGE_SIZES = '(min-width: 1280px) 384px, (min-width: 768px) 33vw, (min-width: 640px) 50vw, 100vw';

/**
 * Фото в белой рамке, под ним «дата · категория» и заголовок с засечками.
 * compact — на телефоне строкой «превью + текст» (вторая и третья новость на главной).
 * Работает и в серверных, и в клиентских компонентах («Загрузить ещё»).
 */
export function NewsCard({
  item,
  headingLevel = 'h3',
  excerpt = true,
  compact = false
}: {
  item: NewsListItem;
  headingLevel?: 'h2' | 'h3';
  excerpt?: boolean;
  compact?: boolean;
}) {
  const locale = useLocale() as Locale;
  const Heading = headingLevel;

  return (
    <article className={cn('group relative flex flex-col gap-3', compact && 'max-sm:flex-row max-sm:items-start')}>
      <div
        className={cn(
          'border border-border bg-surface p-1.5 transition-colors duration-300 group-has-[a.card-link:hover]:border-primary/40',
          compact && 'max-sm:w-28 max-sm:shrink-0 max-sm:p-1'
        )}
      >
        <div className="relative aspect-[3/2] overflow-hidden bg-primary-light">
          {item.cover && (
            <Image
              src={item.cover.small}
              alt={item.title ?? ''}
              fill
              sizes={compact ? `(max-width: 639px) 112px, ${CARD_IMAGE_SIZES}` : CARD_IMAGE_SIZES}
              className="object-cover transition-transform duration-500 group-has-[a.card-link:hover]:scale-105"
            />
          )}
        </div>
      </div>
      <div className="flex min-w-0 flex-1 flex-col gap-1.5">
        <p className="text-xs font-semibold text-primary">
          {item.published_at && <time dateTime={item.published_at}>{formatDate(item.published_at, locale)}</time>}
          {item.published_at && item.category?.name && ' · '}
          {item.category?.name}
        </p>
        <Heading className={cn('line-clamp-3 text-lg font-bold leading-snug text-navy', compact && 'max-sm:text-base')}>
          <CardLink href={`/news/${item.slug}`}>{item.title}</CardLink>
        </Heading>
        {excerpt && item.excerpt && <p className="line-clamp-3 text-sm text-muted">{item.excerpt}</p>}
      </div>
    </article>
  );
}
