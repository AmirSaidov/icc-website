'use client';

import {useLocale, useTranslations} from 'next-intl';
import type {EventListItem, EventTypeCode, EventWhen} from '@/lib/api-types';
import {loadMoreEvents} from '@/app/[locale]/events/actions';
import {EventCard} from './EventCard';
import {LoadMoreButton, useLoadMore} from './LoadMore';

/** Сетка мероприятий + «Загрузить ещё». На странице ставится с key по фильтрам. */
export function EventList({
  initial,
  when,
  type,
  hasMore
}: {
  initial: EventListItem[];
  when: EventWhen;
  type?: EventTypeCode;
  hasMore: boolean;
}) {
  const locale = useLocale();
  const t = useTranslations('Events');
  const {items, more, pending, failed, loadMore} = useLoadMore(initial, hasMore, (page) =>
    loadMoreEvents(locale, when, type, page)
  );

  return (
    <>
      {items.length ? (
        <ul data-reveal-stagger className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <li key={item.id} className="flex [&>*]:flex-1">
              <EventCard item={item} />
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-muted">{t('empty')}</p>
      )}
      {more && (
        <LoadMoreButton
          pending={pending}
          failed={failed}
          onClick={loadMore}
          label={t('loadMore')}
          loadingLabel={t('loading')}
        />
      )}
    </>
  );
}
