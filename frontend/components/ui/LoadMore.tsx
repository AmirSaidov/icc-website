'use client';

import {useState, useTransition} from 'react';
import {useTranslations} from 'next-intl';
import type {Paginated} from '@/lib/api-types';
import {Button} from './Button';

/**
 * «Загрузить ещё» для пагинированных списков (новости, мероприятия).
 * Сбой сети не роняет страницу: под кнопкой появляется сообщение, можно нажать ещё раз.
 * Записи, съехавшие на следующую страницу из-за новой публикации, не дублируются.
 */
export function useLoadMore<T extends {id: number}>(
  initial: T[],
  hasMore: boolean,
  load: (page: number) => Promise<Paginated<T>>
) {
  const [items, setItems] = useState(initial);
  const [page, setPage] = useState(2);
  const [more, setMore] = useState(hasMore);
  const [failed, setFailed] = useState(false);
  const [pending, start] = useTransition();

  const loadMore = () =>
    start(async () => {
      setFailed(false);
      try {
        const next = await load(page);
        setItems((current) => {
          const seen = new Set(current.map((item) => item.id));
          return [...current, ...next.results.filter((item) => !seen.has(item.id))];
        });
        setPage((value) => value + 1);
        setMore(Boolean(next.next));
      } catch (error) {
        console.error('[LoadMore]', error);
        setFailed(true);
      }
    });

  return {items, more, pending, failed, loadMore};
}

export function LoadMoreButton({
  pending,
  failed,
  onClick,
  label,
  loadingLabel
}: {
  pending: boolean;
  failed: boolean;
  onClick: () => void;
  label: string;
  loadingLabel: string;
}) {
  const t = useTranslations('Common');
  return (
    <div className="mt-8 text-center">
      <Button disabled={pending} onClick={onClick}>
        {pending ? loadingLabel : label}
      </Button>
      {failed && (
        <p role="alert" className="mt-3 text-sm text-danger">
          {t('loadError')}
        </p>
      )}
    </div>
  );
}
